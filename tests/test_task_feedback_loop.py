import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from multi_agent_team.monitoring.app import app, workflow_runtime

client = TestClient(app)

@pytest.mark.asyncio
async def test_persona_documents_approval_and_retrigger():
    workflow_runtime.clear_runs()

    # Dummy specialist return mock
    async def mock_executor(agent_id, title, objective, context):
        doc_type = "requirement_understanding_and_plan"
        doc_title = "Detailed Requirement Understanding & Implementation Plan Document"
        if agent_id in ("solution_architect", "platform_architect"):
            doc_type = "detailed_architectural_design"
            doc_title = "Detailed Solution Architecture & Security Design Specification Document"
        elif agent_id == "cloud_infrastructure_engineer":
            doc_type = "test_plan_and_implementation_spec"
            doc_title = "Detailed Test Suite, Technical Implementation Spec & Code Review Request"

        return {
            "agent_id": agent_id,
            "assignment": title,
            "document_type": doc_type,
            "document_title": doc_title,
            "document_content": f"# Document for {agent_id}\n\nDetailed specifications and review request.",
            "review_requested": True,
            "result": f"Output content for {agent_id}",
            "validated": True,
            "model_name": "mock-nemotron",
            "model_provider": "Mock NIM",
            "model_location": "Local test"
        }

    workflow_runtime._agent_executor = mock_executor

    # 1. Create run without auto_approve
    run = workflow_runtime.create_run("Build GCP Landing Zone", auto_approve=False)
    run_id = run["id"]
    task1_id = run["tasks"][0]["id"]

    # Start run asynchronously
    await workflow_runtime.start_run(run_id)
    await asyncio.sleep(0.3)

    snap = workflow_runtime.get_run(run_id)
    task1 = snap["tasks"][0]
    assert task1["status"] == "awaiting_approval"
    assert task1["document_type"] == "requirement_understanding_and_plan"
    assert task1["review_requested"] is True

    # 2. Reject task with feedback
    res_reject = client.post(
        f"/api/workflows/{run_id}/tasks/{task1_id}/reject",
        json={"comment": "Please add VPC Service Controls detail"},
        headers={"x-api-key": "dev-key"}
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["ok"] is True

    await asyncio.sleep(0.3)

    snap = workflow_runtime.get_run(run_id)
    task1_retriggered = snap["tasks"][0]
    assert len(task1_retriggered["feedback_history"]) == 1
    assert task1_retriggered["feedback_history"][0]["comment"] == "Please add VPC Service Controls detail"
    assert task1_retriggered["status"] == "awaiting_approval"

    # 3. Approve task
    res_approve = client.post(
        f"/api/workflows/{run_id}/tasks/{task1_id}/approve",
        headers={"x-api-key": "dev-key"}
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["ok"] is True

    await asyncio.sleep(0.2)
    snap = workflow_runtime.get_run(run_id)
    assert snap["tasks"][0]["status"] == "completed"

def test_workflow_start_fresh_and_continue():
    workflow_runtime.clear_runs()
    run = workflow_runtime.create_run("Build Azure Landing Zone", auto_approve=False)
    run_id = run["id"]

    # Test start fresh endpoint
    res_fresh = client.post(f"/api/workflows/{run_id}/start_fresh", headers={"x-api-key": "dev-key"})
    assert res_fresh.status_code == 200
    assert res_fresh.json()["action"] == "started_fresh"

    # Test continue endpoint
    res_cont = client.post(f"/api/workflows/{run_id}/continue", headers={"x-api-key": "dev-key"})
    assert res_cont.status_code == 200
    assert res_cont.json()["action"] == "continued"
