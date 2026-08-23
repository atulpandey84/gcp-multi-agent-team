import pytest
import os
from multi_agent_team.models.router import get_model, SmartFallbackModel

def test_model_router_ollama_fallback_host_error(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_LOCAL_URL", "http://192.168.31.135:11434")

    # Call get_model with senior_reasoning policy
    model = get_model("senior_reasoning")
    assert isinstance(model, SmartFallbackModel)

    # Invoking invoke should fail with explicit system host error diagnostics
    with pytest.raises(RuntimeError) as exc_info:
        model.invoke("Test prompt")

    err_msg = str(exc_info.value)
    assert "System Host" in err_msg or "NVIDIA_API_KEY" in err_msg
