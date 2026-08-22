from pathlib import Path
import os
import yaml
import logging
import time
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
try:
    from openai import OpenAI
except Exception:
    OpenAI = None
import httpx

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]
MODELS_PATH = ROOT / "config" / "models.yaml"
ACTIVE_PATH = ROOT / "config" / "models_active.yaml"
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
# Allow explicit proxy override for NVIDIA API (example: socks5://user:pass@host:port)
NVIDIA_PROXY = os.getenv("NVIDIA_PROXY")
if NVIDIA_PROXY:
    os.environ.setdefault("HTTP_PROXY", NVIDIA_PROXY)
    os.environ.setdefault("HTTPS_PROXY", NVIDIA_PROXY)
    os.environ.setdefault("ALL_PROXY", NVIDIA_PROXY)
    logging.info("Using NVIDIA_PROXY from environment for outbound requests")

logging.basicConfig(level=logging.INFO)


def _instantiate(cfg: dict):
    # Prefer newer 'max_completion_tokens' if supported, fall back to 'max_tokens'
    kw = {"model": cfg["model"], "temperature": cfg.get("temperature", 0.1)}
    if "max_completion_tokens" in cfg:
        kw["max_completion_tokens"] = cfg.get("max_completion_tokens")
    else:
        kw["max_tokens"] = cfg.get("max_tokens", 4096)
    try:
        return ChatNVIDIA(**kw)
    except TypeError:
        # older client may expect max_tokens
        kw = {"model": cfg["model"], "temperature": cfg.get("temperature", 0.1), "max_tokens": cfg.get("max_tokens", 4096)}
        return ChatNVIDIA(**kw)


def _socks_support_available() -> bool:
    # If environment requires SOCKS proxy support, ensure socksio/httpx[socks] is present
    socks_env = any(os.getenv(v) for v in ("ALL_PROXY", "all_proxy", "SOCKS_PROXY", "socks_proxy"))
    if not socks_env:
        return True
    try:
        import socksio  # type: ignore
        return True
    except Exception:
        return False


def _validate_via_httpx(cfg: dict) -> bool:
    """Validate against NVIDIA OpenAI-compatible endpoint using an explicit httpx client with per-host proxy support."""
    if not NVIDIA_API_KEY:
        return False
    base = os.getenv("NVIDIA_API_BASE", "https://integrate.api.nvidia.com/v1").rstrip("/")
    url = f"{base}/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": "Ping"}],
        "temperature": 0,
        "max_tokens": 1,
    }
    proxies = None
    if NVIDIA_PROXY:
        proxies = {"http://": NVIDIA_PROXY, "https://": NVIDIA_PROXY}
    try:
        client_kwargs = {"timeout": 10}
        if proxies:
            client_kwargs["proxies"] = proxies
        try:
            with httpx.Client(**client_kwargs) as client:
                resp = client.post(url, headers=headers, json=body)
                if resp.status_code < 400:
                    return True
                logging.warning("httpx probe returned %s for %s: %s", resp.status_code, cfg.get("model"), resp.text[:200])
                # If proxy rejected (403), attempt a direct connection once
                if resp.status_code == 403 and proxies:
                    logging.info("Proxy returned 403; retrying httpx probe without proxy")
                    with httpx.Client(timeout=10) as direct_client:
                        direct_resp = direct_client.post(url, headers=headers, json=body)
                        if direct_resp.status_code < 400:
                            return True
                        logging.warning("Direct httpx probe returned %s for %s", direct_resp.status_code, cfg.get("model"))
                return False
        except Exception as e:
            logging.warning("httpx validation error (maybe proxy): %s", str(e))
            # If we had proxies configured, try direct once
            if proxies:
                try:
                    with httpx.Client(timeout=10) as direct_client:
                        direct_resp = direct_client.post(url, headers=headers, json=body)
                        if direct_resp.status_code < 400:
                            return True
                        logging.warning("Direct httpx probe returned %s for %s", direct_resp.status_code, cfg.get("model"))
                except Exception as e2:
                    logging.warning("Direct httpx probe also failed: %s", str(e2))
            return False
    except Exception as e:
        logging.warning("httpx validation failed for %s: %s", cfg.get("model"), str(e))
        return False


def _validate_via_openai(cfg: dict) -> bool:
    """Validate using NVIDIA's OpenAI-compatible client when available and usable."""
    if OpenAI is None or not NVIDIA_API_KEY:
        return False
    if not _socks_support_available():
        logging.warning("SOCKS proxy detected but socksio/httpx[socks] not installed; skipping OpenAI probe.")
        return False
    try:
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
        probe = "Ping"
        # lightweight single-token chat completion
        resp = client.chat.completions.create(
            model=cfg["model"],
            messages=[{"role": "user", "content": probe}],
            temperature=0,
            top_p=1,
            max_tokens=1,
        )
        logging.debug("OpenAI validation response: %s", getattr(resp, "choices", resp))
        return True
    except Exception as e:
        logging.warning("OpenAI client validation failed for %s: %s", cfg.get("model"), str(e))
        return False


def _validate(cfg: dict, timeout_sec: int = 10) -> bool:
    """Attempt a lightweight validation call to the provider. Returns True if model responds."""
    # Prefer NVIDIA OpenAI-compatible API probe when available
    try:
        if NVIDIA_API_KEY:
            # Prefer explicit httpx client (per-host proxy/auth) when possible
            ok = _validate_via_httpx(cfg)
            if ok:
                return True
            # Fallback to OpenAI client probe if httpx probe didn't succeed
            ok = _validate_via_openai(cfg)
            if ok:
                return True

        # Fallback to langchain ChatNVIDIA quick probes
        llm = _instantiate(cfg)
        probe = "Ping"
        # try common callable API
        try:
            result = llm(probe)
            logging.debug("Validation result callable: %s", getattr(result, "text", str(result)))
            return True
        except Exception:
            pass
        # try generate-like API
        try:
            if hasattr(llm, "generate"):
                _ = llm.generate([{"role": "user", "content": probe}])
                return True
        except Exception:
            pass
        # try chat-like API
        try:
            if hasattr(llm, "chat"):
                _ = llm.chat(probe)
                return True
        except Exception:
            pass
        return False
    except Exception as e:
        logging.warning("Model instantiation failed for %s: %s", cfg.get("model"), str(e))
        return False


def build_active_models() -> dict:
    with MODELS_PATH.open() as fh:
        models = yaml.safe_load(fh) or {}
    models = models.get("models", {})

    active = {}
    for name, cfg in models.items():
        provider = cfg.get("provider", "nvidia")
        logging.info("Validating model for policy '%s' -> %s", name, cfg.get("model"))
        if provider.lower() == "nvidia":
            if not NVIDIA_API_KEY:
                logging.warning("NVIDIA_API_KEY not set; skipping live validation for %s", name)
                active[name] = cfg
                continue
            ok = _validate(cfg)
            if ok:
                active[name] = cfg
                continue
            # fallback: try other models with same provider
            logging.warning("Primary model %s failed validation, searching fallback...", cfg.get("model"))
            found = False
            for alt_name, alt_cfg in models.items():
                if alt_name == name:
                    continue
                if alt_cfg.get("provider") != provider:
                    continue
                logging.info("Trying fallback candidate %s -> %s", alt_name, alt_cfg.get("model"))
                if _validate(alt_cfg):
                    logging.info("Falling back policy %s to model %s", name, alt_cfg.get("model"))
                    active[name] = alt_cfg
                    found = True
                    break
            if not found:
                logging.error("No working fallback found for policy %s; keeping original config", name)
                active[name] = cfg
        else:
            active[name] = cfg

    # Persist active mapping so runtime code can pick it up without probing every startup
    try:
        with ACTIVE_PATH.open("w") as fh:
            yaml.safe_dump({"models": active}, fh)
        logging.info("Wrote active models to %s", ACTIVE_PATH)
    except Exception as e:
        logging.error("Failed to write active models file: %s", str(e))

    return active


if __name__ == "__main__":
    start = time.time()
    active = build_active_models()
    elapsed = time.time() - start
    logging.info("Model bootstrap complete in %.2fs. Active policies: %s", elapsed, ",".join(active.keys()))
