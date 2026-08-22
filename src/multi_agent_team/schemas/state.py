from typing import Any, TypedDict

class EngineeringState(TypedDict, total=False):
    task_id: str
    project_id: str
    objective: str
    requirements: list[str]
    assumptions: list[str]
    constraints: list[str]
    architecture: dict[str, Any]
    security_assessment: dict[str, Any]
    cost_assessment: dict[str, Any]
    implementation_plan: dict[str, Any]
    test_plan: dict[str, Any]
    operational_plan: dict[str, Any]
    artifacts: list[str]
    decisions: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    approvals: dict[str, Any]
    active_agents: list[str]
    pending_tasks: list[dict[str, Any]]
    completed_tasks: list[dict[str, Any]]
    status: str
    final_response: str
