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


def test_dynamic_chat_returns_terraform_bucket_script():
    res = client.post(
        "/api/chat",
        json={"message": "Create a Terraform script to create a GCP bucket with any defaults"},
        headers={"x-api-key": "dev-key"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["artifact_type"] == "terraform"
    assert "resource \"google_storage_bucket\" \"app\"" in data["response"]
    assert "hello_world.py" not in data["response"]


def test_dynamic_chat_understands_attached_text_requirement():
    res = client.post(
        "/api/chat",
        files={"requirement_file": ("requirements.txt", b"Create a private GCP bucket with 30 day retention.", "text/plain")},
        data={"message": "Please review the attached requirements."},
        headers={"x-api-key": "dev-key"}
    )
    assert res.status_code == 200
    data = res.json()
    # Product Owner should acknowledge the bucket requirement and ask clarifying questions
    assert "bucket" in data["response"].lower()
    # Should not be frozen yet - should be asking clarifying questions
    assert data.get("requirement_frozen") is False


def test_dynamic_chat_accepts_file_without_message():
    res = client.post(
        "/api/chat",
        files={"requirement_file": ("requirements.txt", b"Create a private GCP bucket.", "text/plain")},
        headers={"x-api-key": "dev-key"}
    )
    assert res.status_code == 200
    assert "bucket" in res.json()["frozen_objective"].lower()

def test_session_state_restoration():
    workflow_runtime.clear_runs()
    run = workflow_runtime.create_run("Build an AI chatbot microservice platform on AWS")
    run_id = run["id"]

    res = client.get(f"/api/workflows/{run_id}", headers={"x-api-key": "dev-key"})
    assert res.status_code == 200
    fetched = res.json()
    assert fetched["id"] == run_id
    assert fetched["objective"] == "Build an AI chatbot microservice platform on AWS"
