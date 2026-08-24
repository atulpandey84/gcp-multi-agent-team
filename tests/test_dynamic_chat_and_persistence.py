import os
import pytest
from fastapi.testclient import TestClient

os.environ["MONITORING_API_KEY"] = "dev-key"
from multi_agent_team.monitoring.app import app, workflow_runtime

client = TestClient(app)

def test_dynamic_executive_chat_endpoint():
    res = client.post(
        "/api/chat",
        json={"message": "Build an AI chatbot microservice platform on AWS"},
        headers={"x-api-key": "dev-key"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "response" in data or "frozen_objective" in data

def test_session_state_restoration():
    workflow_runtime.clear_runs()
    run = workflow_runtime.create_run("Build an AI chatbot microservice platform on AWS")
    run_id = run["id"]

    res = client.get(f"/api/workflows/{run_id}", headers={"x-api-key": "dev-key"})
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["id"] == run_id
    assert fetched["objective"] == "Build an AI chatbot microservice platform on AWS"
