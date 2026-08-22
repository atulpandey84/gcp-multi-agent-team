import asyncio

from multi_agent_team.monitoring.workflow_runtime import PILOT_STAGES, WorkflowRuntime


def test_pilot_workflow_exposes_model_routing_and_completes():
    runtime = WorkflowRuntime()
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
    assert events[-1]["type"] == "workflow_completed"