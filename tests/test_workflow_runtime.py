import asyncio

import multi_agent_team.monitoring.workflow_engine as engine
from multi_agent_team.monitoring.workflow_engine import PILOT_STAGES, WorkflowRuntime


def fake_agent(agent_id, title, objective, context):
    result = {"agent_id": agent_id, "title": title, "objective": objective, "validated": True}
    if agent_id == "cloud_infrastructure_engineer":
        result["terraform_files"] = {"main.tf": "terraform { required_version = \">= 1.3.0\" }\n"}
    return result


def passing_terraform(_root):
    return {"passed": True, "results": []}


def test_pilot_workflow_exposes_model_routing_and_completes():
    runtime = WorkflowRuntime(agent_executor=fake_agent, terraform_validator=passing_terraform)
    events = []
    runtime.subscribe(events.append)
    run = runtime.create_run("Provision a test environment")

    assert len(run["tasks"]) == len(PILOT_STAGES)
    assert run["tasks"][0]["model_policy"] == "senior_reasoning"
    assert run["tasks"][-1]["agent_id"] == "engineering_orchestrator"

    async def execute():
        await runtime.start_run(run["id"])
        while runtime.get_run(run["id"])["status"] != "completed":
            await asyncio.sleep(0.01)

    asyncio.run(execute())
    completed = runtime.get_run(run["id"])
    assert completed["status"] == "completed"
    assert completed["progress"] == 100
    assert completed["tasks"][-1]["status"] == "completed"
    assert len(completed["artifacts"]) >= len(PILOT_STAGES)
    assert all(gate["status"] == "passed" for gate in completed["gates"])
    assert events[-1]["type"] == "workflow_completed"


def test_workflow_blocks_on_terraform_gate_and_persists_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "_root", lambda: tmp_path)
    calls = []

    def failing_agent(agent_id, title, objective, context):
        calls.append(agent_id)
        result = {"agent_id": agent_id, "validated": True}
        if agent_id == "cloud_infrastructure_engineer":
            result["terraform_files"] = {"main.tf": "terraform { required_version = \">= 1.3.0\" }\n"}
        return result

    runtime = WorkflowRuntime(
        agent_executor=failing_agent,
        terraform_validator=lambda root: {"passed": False, "reason": "validation failed"},
    )
    run = runtime.create_run("Validate infrastructure")

    async def execute():
        await runtime.start_run(run["id"])
        while runtime.get_run(run["id"])["status"] not in {"completed", "blocked", "failed", "cancelled"}:
            await asyncio.sleep(0.01)

    asyncio.run(execute())
    completed = runtime.get_run(run["id"])
    assert len(calls) == len(PILOT_STAGES)
    assert completed["status"] == "blocked"
    assert any(gate["name"] == "implementation" and gate["status"] == "failed" for gate in completed["gates"])
    assert (tmp_path / "data" / "workflows" / run["id"] / "gate-implementation.json").exists()


def test_provisioning_requires_human_approval(monkeypatch):
    monkeypatch.delenv("WORKFLOW_HUMAN_APPROVED", raising=False)
    runtime = WorkflowRuntime(agent_executor=fake_agent, terraform_validator=passing_terraform)
    run = runtime.create_run("Provision a test environment", provision=True)

    async def execute():
        await runtime.start_run(run["id"])
        while runtime.get_run(run["id"])["status"] not in {"completed", "blocked", "failed", "cancelled"}:
            await asyncio.sleep(0.01)

    asyncio.run(execute())
    completed = runtime.get_run(run["id"])
    assert completed["status"] == "blocked"
    assert completed["provisioning"]["status"] == "blocked"


def test_leadership_agents_have_distinct_deliverable_personas(monkeypatch):
    prompts = {}

    class FakeResponse:
        content = "persona output"
        response_metadata = {}

    class FakeModel:
        def invoke(self, prompt):
            prompts[prompt] = True
            return FakeResponse()

    monkeypatch.setattr(engine, "get_model", lambda _policy: FakeModel())

    outputs = [
        engine.invoke_specialist(agent_id, title, "Build a GCP service", {"model_policy": "senior_reasoning"})
        for agent_id, title in [
            ("product_owner", "Shape the requirement"),
            ("project_manager", "Plan delivery and dependencies"),
            ("engineering_orchestrator", "Decompose the engineering workflow"),
            ("engineering_orchestrator", "Package evidence and close the workflow"),
        ]
    ]

    document_types = [output["document_type"] for output in outputs]
    assert document_types == [
        "product_requirements_and_acceptance_criteria",
        "project_plan_spec",
        "engineering_workflow_and_evidence_plan",
        "workflow_closeout_and_evidence_summary",
    ]
    assert len(set(document_types)) == len(document_types)
    assert len(prompts) == 3