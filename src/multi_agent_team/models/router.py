from pathlib import Path
import os
import time
import yaml
import urllib.request
import json
import logging
from dotenv import load_dotenv

try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
except ImportError:  # pragma: no cover - optional dependency for local/runtime environments
    class ChatNVIDIA:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("langchain_nvidia_ai_endpoints is not installed in this environment")

try:
    from langchain_ollama import ChatOllama
except ImportError:  # pragma: no cover - optional dependency for local/runtime environments
    class ChatOllama:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("langchain_ollama is not installed in this environment")

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]

logger = logging.getLogger(__name__)

def _load_active_models() -> dict:
    active_path = ROOT / "config" / "models_active.yaml"
    source_path = active_path if active_path.exists() else (ROOT / "config" / "models.yaml")
    with source_path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("models", {})


def fetch_ollama_tags(url: str) -> list[str]:
    """Fetch installed models on a target Ollama host."""
    try:
        req = urllib.request.Request(f"{url}/api/tags", headers={'User-Agent': 'MultiAgent/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode('utf-8'))
                models = body.get("models", [])
                return [m.get("name", "") for m in models if isinstance(m, dict)]
    except Exception:
        pass
    return []


def trigger_ollama_pull(url: str, model_name: str) -> bool:
    """Attempt auto-download of requested missing model on target host."""
    try:
        data = json.dumps({"name": model_name, "stream": False}).encode("utf-8")
        req = urllib.request.Request(f"{url}/api/pull", data=data, headers={"Content-Type": "application/json", "User-Agent": "MultiAgent/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except Exception as exc:
        logger.warning(f"Auto-download model {model_name} failed on host {url}: {exc}")
        return False


def select_best_ollama_instance() -> dict:
    """Evaluate local and remote Ollama instances based on latency, responsiveness, and GPU/CPU resource load."""
    local_url = os.getenv("OLLAMA_LOCAL_URL", "http://192.168.31.135:11434").rstrip("/")
    remote_url = os.getenv("OLLAMA_REMOTE_URL", "http://192.168.31.63:11434").rstrip("/")

    candidates = [
        {"url": local_url, "label": f"Local GPU/CPU ({local_url.replace('http://', '')})", "is_gpu": True, "score": 0, "available_models": []},
        {"url": remote_url, "label": f"Remote CPU ({remote_url.replace('http://', '')})", "is_gpu": False, "score": 0, "available_models": []}
    ]

    best = None
    best_score = -999

    for cand in candidates:
        try:
            start = time.time()
            models = fetch_ollama_tags(cand["url"])
            elapsed = time.time() - start
            cand["available_models"] = models
            score = 100 - (elapsed * 20)
            if cand["is_gpu"]:
                score += 30  # Prefer GPU instance for speed
            cand["score"] = score
            if score > best_score:
                best_score = score
                best = cand
        except Exception:
            continue

    if best:
        return best
    return {"url": local_url, "label": f"Fallback Local ({local_url})", "is_gpu": True, "score": 0, "available_models": []}


class SmartFallbackModel:
    """Attempts invocation on NVIDIA NIM endpoints first, falling back to best Ollama instance if NVIDIA fails."""

    def __init__(self, policy: str, nvidia_model, policy_cfg: dict):
        self.policy = policy
        self.nvidia_model = nvidia_model
        self.policy_cfg = policy_cfg

    def invoke(self, prompt: str):
        nvidia_err = None
        max_retries = int(os.getenv("MODEL_MAX_RETRIES", "2"))

        for attempt in range(max_retries):
            try:
                if not os.getenv("NVIDIA_API_KEY"):
                    raise RuntimeError("NVIDIA_API_KEY environment variable is missing or empty")
                res = self.nvidia_model.invoke(prompt)
                if hasattr(res, "response_metadata"):
                    res.response_metadata["model_provider"] = "NVIDIA NIM Cloud"
                    res.response_metadata["model_name"] = self.policy_cfg.get("model")
                    res.response_metadata["model_location"] = "NVIDIA Cloud Endpoints"
                return res
            except Exception as exc:
                nvidia_err = str(exc)
                logger.warning(f"NVIDIA API attempt {attempt + 1}/{max_retries} failed for policy {self.policy}: {exc}.")
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (attempt + 1))

        logger.warning(f"All NVIDIA API retries exhausted for policy {self.policy}. Routing to Ollama fallback...")

        ollama_inst = select_best_ollama_instance()
        target_url = ollama_inst["url"]
        requested_model = self.policy_cfg.get("ollama_model", "llama3")
        available_models = ollama_inst.get("available_models") or fetch_ollama_tags(target_url)

        # 1. Check if model is already installed
        chosen_model = None
        if any(requested_model in m for m in available_models):
            chosen_model = requested_model
        else:
            # 2. Attempt auto-pull model on missing system host
            logger.info(f"Model '{requested_model}' missing on host {target_url}. Attempting auto-download...")
            pulled = trigger_ollama_pull(target_url, requested_model)
            if pulled:
                chosen_model = requested_model
            elif available_models:
                # 3. Select alternate installed model on target host
                chosen_model = available_models[0].split(":")[0]
                logger.info(f"Auto-pull failed. Selected alternate model '{chosen_model}' installed on host {target_url}.")

        if not chosen_model:
            raise RuntimeError(
                f"Model Provider Failure: NVIDIA API Error ({nvidia_err}). "
                f"System Host '{target_url}' is missing requested model '{requested_model}' "
                f"and auto-download failed with no available alternate models installed."
            )

        try:
            ollama_model = ChatOllama(base_url=target_url, model=chosen_model, temperature=self.policy_cfg.get("temperature", 0.1))
            res = ollama_model.invoke(prompt)
            if hasattr(res, "response_metadata"):
                res.response_metadata["model_provider"] = f"Ollama ({chosen_model})"
                res.response_metadata["model_name"] = chosen_model
                res.response_metadata["model_location"] = ollama_inst["label"]
            return res
        except Exception as ollama_exc:
            raise RuntimeError(
                f"Model Provider Failure: NVIDIA Cloud ({nvidia_err}) and "
                f"System Host '{target_url}' ({chosen_model}) failed: {ollama_exc}"
            )


def get_model(policy: str):
    models = _load_active_models()
    if policy not in models:
        raise ValueError(f"Unknown model policy: {policy}")
    cfg = models[policy]
    timeout = cfg.get("timeout", int(os.getenv("MODEL_TIMEOUT", "120")))
    kw = {"model": cfg["model"], "temperature": cfg.get("temperature", 0.1), "timeout": timeout}
    if "max_completion_tokens" in cfg:
        kw["max_completion_tokens"] = cfg.get("max_completion_tokens")
    else:
        kw["max_tokens"] = cfg.get("max_tokens", 4096)

    try:
        nvidia_model = ChatNVIDIA(**kw)
    except TypeError:
        nvidia_model = ChatNVIDIA(model=cfg["model"], temperature=cfg.get("temperature", 0.1), max_tokens=cfg.get("max_tokens", 4096), timeout=timeout)

    return SmartFallbackModel(policy, nvidia_model, cfg)


def list_active_models() -> list:
    return list(_load_active_models().keys())
