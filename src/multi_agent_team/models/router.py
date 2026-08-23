from pathlib import Path
import os
import time
import yaml
import urllib.request
import json
import logging
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]

logger = logging.getLogger(__name__)

def _load_active_models() -> dict:
    active_path = ROOT / "config" / "models_active.yaml"
    source_path = active_path if active_path.exists() else (ROOT / "config" / "models.yaml")
    with source_path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("models", {})


def select_best_ollama_instance() -> dict:
    """Evaluate local and remote Ollama instances based on latency, responsiveness, and GPU/CPU resource load."""
    local_url = os.getenv("OLLAMA_LOCAL_URL", "http://192.168.31.135:11434").rstrip("/")
    remote_url = os.getenv("OLLAMA_REMOTE_URL", "http://192.168.31.63:11434").rstrip("/")

    candidates = [
        {"url": local_url, "label": f"Local GPU/CPU ({local_url.replace('http://', '')})", "is_gpu": True, "score": 0},
        {"url": remote_url, "label": f"Remote CPU ({remote_url.replace('http://', '')})", "is_gpu": False, "score": 0}
    ]

    best = None
    best_score = -999

    for cand in candidates:
        try:
            start = time.time()
            req = urllib.request.Request(f"{cand['url']}/api/tags", headers={'User-Agent': 'MultiAgent/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                elapsed = time.time() - start
                if resp.status == 200:
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
    return {"url": local_url, "label": f"Fallback Local ({local_url})", "is_gpu": True, "score": 0}


class SmartFallbackModel:
    """Attempts invocation on NVIDIA NIM endpoints first, falling back to best Ollama instance if NVIDIA fails."""

    def __init__(self, policy: str, nvidia_model, policy_cfg: dict):
        self.policy = policy
        self.nvidia_model = nvidia_model
        self.policy_cfg = policy_cfg

    def invoke(self, prompt: str):
        try:
            if not os.getenv("NVIDIA_API_KEY"):
                raise RuntimeError("NVIDIA_API_KEY is not configured")
            res = self.nvidia_model.invoke(prompt)
            # Annotate response with provider metadata
            if hasattr(res, "response_metadata"):
                res.response_metadata["model_provider"] = "NVIDIA NIM Cloud"
                res.response_metadata["model_name"] = self.policy_cfg.get("model")
                res.response_metadata["model_location"] = "NVIDIA Cloud Endpoints"
            return res
        except Exception as exc:
            logger.warning(f"NVIDIA API failed for policy {self.policy}: {exc}. Routing to Ollama fallback...")
            ollama_inst = select_best_ollama_instance()
            model_name = self.policy_cfg.get("ollama_model", "llama3")
            ollama_model = ChatOllama(base_url=ollama_inst["url"], model=model_name, temperature=self.policy_cfg.get("temperature", 0.1))
            res = ollama_model.invoke(prompt)
            if hasattr(res, "response_metadata"):
                res.response_metadata["model_provider"] = "Ollama Local/Remote"
                res.response_metadata["model_name"] = model_name
                res.response_metadata["model_location"] = ollama_inst["label"]
            return res


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
