import os
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from multi_agent_team.monitoring.validation import validate_user_input, sanitize_input
from multi_agent_team.monitoring.config import Settings
from multi_agent_team.models.router import SmartFallbackModel

os.environ["MONITORING_API_KEY"] = "dev-key"
from multi_agent_team.monitoring.app import app

client = TestClient(app)

def test_validate_user_input_valid():
    result = validate_user_input("  Build a microservices architecture  ", field_name="Requirement")
    assert result == "Build a microservices architecture"

def test_validate_user_input_script_injection():
    with pytest.raises(HTTPException) as excinfo:
        validate_user_input("<script>alert('xss')</script>", field_name="Requirement")
    assert excinfo.value.status_code == 400
    assert "dangerous content" in excinfo.value.detail.lower()

def test_validate_user_input_exceeds_max_len():
    with pytest.raises(HTTPException) as excinfo:
        validate_user_input("a" * 2001, field_name="Requirement", max_len=2000)
    assert excinfo.value.status_code == 400
    assert "exceeds maximum length" in excinfo.value.detail.lower()

def test_endpoint_input_validation():
    # Chat endpoint script injection
    res = client.post(
        "/api/chat",
        json={"message": "<script>bad()</script>"},
        headers={"x-api-key": "dev-key"}
    )
    assert res.status_code == 400

    # Workflow objective script injection
    res2 = client.post(
        "/api/workflows",
        json={"objective": "javascript:alert(1)"},
        headers={"x-api-key": "dev-key"}
    )
    assert res2.status_code == 400

def test_settings_validation():
    s = Settings(api_key="test-key", port=8000, max_agents=22, model_timeout=120)
    validation = Settings.validate_settings(s)
    assert validation["valid_port"] is True
    assert validation["valid_agents"] is True
    assert validation["valid_timeout"] is True
    assert validation["has_api_key"] is True

class DummyNVIDIAFail:
    def __init__(self):
        self.attempts = 0
    def invoke(self, prompt):
        self.attempts += 1
        raise RuntimeError("Simulated transient network failure")

def test_smart_fallback_retry_attempts(monkeypatch):
    monkeypatch.setenv("MODEL_MAX_RETRIES", "2")
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")

    dummy_model = DummyNVIDIAFail()
    fallback = SmartFallbackModel("test_policy", dummy_model, {"ollama_model": "llama3"})

    with pytest.raises(RuntimeError) as excinfo:
        fallback.invoke("test prompt")

    assert dummy_model.attempts == 2
    assert "Model Provider Failure" in str(excinfo.value)
