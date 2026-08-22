from pathlib import Path
import os
import yaml
import logging
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]


def _load_active_models() -> dict:
    active_path = ROOT / "config" / "models_active.yaml"
    source_path = active_path if active_path.exists() else (ROOT / "config" / "models.yaml")
    with source_path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("models", {})


def get_model(policy: str) -> ChatNVIDIA:
    models = _load_active_models()
    if policy not in models:
        raise ValueError(f"Unknown model policy: {policy}")
    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError("NVIDIA_API_KEY is not configured")
    cfg = models[policy]
    kw = {"model": cfg["model"], "temperature": cfg.get("temperature", 0.1)}
    if "max_completion_tokens" in cfg:
        kw["max_completion_tokens"] = cfg.get("max_completion_tokens")
    else:
        kw["max_tokens"] = cfg.get("max_tokens", 4096)
    try:
        return ChatNVIDIA(**kw)
    except TypeError:
        # Older client expects max_tokens
        return ChatNVIDIA(model=cfg["model"], temperature=cfg.get("temperature", 0.1), max_tokens=cfg.get("max_tokens", 4096))


def list_active_models() -> list:
    return list(_load_active_models().keys())
