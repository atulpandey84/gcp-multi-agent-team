from pathlib import Path
import os
import yaml
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()
ROOT = Path(__file__).resolve().parents[3]


def get_model(policy: str) -> ChatNVIDIA:
    with (ROOT / "config" / "models.yaml").open() as fh:
        models = yaml.safe_load(fh)["models"]
    if policy not in models:
        raise ValueError(f"Unknown model policy: {policy}")
    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError("NVIDIA_API_KEY is not configured")
    cfg = models[policy]
    return ChatNVIDIA(model=cfg["model"], temperature=cfg.get("temperature", 0.1), max_tokens=cfg.get("max_tokens", 4096))
