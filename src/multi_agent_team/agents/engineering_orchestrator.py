"""Engineering Orchestrator Agent - Section 6.3
Central engineering coordination and task-decomposition agent using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class EngineeringOrchestratorAgent(BaseAgent):
    """Engineering Orchestrator - central coordination and task decomposition."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        objective = context.get("objective", task.objective)
        available_agents = context.get("available_agents", [])
        architecture = context.get("architecture", {})

        model = getattr(self, "model", None)
        orchestration_notes = {}
        if model:
            try:
                prompt = f"""You are an Engineering Orchestrator. Decompose work for:
Objective: {objective}
Available Agents: {available_agents}
Architecture: {architecture}
Provide: task decomposition, agent assignments, dependencies, quality gates, sequencing."""
                design_result = model.invoke(prompt)
                orchestration_notes = {"model_design": str(design_result), "model_used": "orchestration_design"}
            except Exception as exc:
                orchestration_notes = {"model_design_error": str(exc)}

        task_decomposition = self._decompose_tasks(objective, available_agents)
        agent_assignments = self._assign_agents(task_decomposition, available_agents)
        dependencies = self._define_dependencies(task_decomposition)
        quality_gates = self._define_quality_gates()
        sequencing = self._define_sequencing(task_decomposition, dependencies)

        self.record_decision({
            "type": "orchestration_completed",
            "tasks": len(task_decomposition),
            "agents_assigned": len(agent_assignments),
            "quality_gates": len(quality_gates),
        })

        self.add_evidence(f"Decomposed into {len(task_decomposition)} tasks")
        self.add_evidence(f"Assigned to {len(agent_assignments)} agents")
        self.add_evidence(f"Defined {len(quality_gates)} quality gates")

        return {
            "status": "orchestrated",
            "task_decomposition": task_decomposition,
            "agent_assignments": agent_assignments,
            "dependencies": dependencies,
            "quality_gates": quality_gates,
            "sequencing": sequencing,
            "orchestration_notes": orchestration_notes,
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return all(k in output for k in ["task_decomposition", "agent_assignments", "quality_gates", "sequencing"])

    def _decompose_tasks(self, objective: str, agents: List[str]) -> List[Dict]:
        return [
            {"task_id": "task-001", "name": "Requirements Analysis", "agent": "product_owner", "phase": "discovery"},
            {"task_id": "task-002", "name": "Platform Architecture", "agent": "platform_architect", "phase": "design"},
            {"task_id": "task-003", "name": "Security Architecture", "agent": "security_architect", "phase": "design"},
            {"task_id": "task-004", "name": "Solution Design", "agent": "solution_architect", "phase": "design"},
            {"task_id": "task-005", "name": "Backend Implementation", "agent": "backend_engineer", "phase": "implementation"},
            {"task_id": "task-006", "name": "Frontend Implementation", "agent": "frontend_engineer", "phase": "implementation"},
            {"task_id": "task-007", "name": "Integration", "agent": "integration_engineer", "phase": "implementation"},
            {"task_id": "task-008", "name": "CI/CD Pipeline", "agent": "devops_lead", "phase": "deployment"},
            {"task_id": "task-009", "name": "Infrastructure", "agent": "cloud_infrastructure_engineer", "phase": "deployment"},
            {"task_id": "task-010", "name": "QA Testing", "agent": "qa_lead", "phase": "testing"},
            {"task_id": "task-011", "name": "Test Automation", "agent": "test_automation_engineer", "phase": "testing"},
            {"task_id": "task-012", "name": "NFR Testing", "agent": "nfr_test_engineer", "phase": "testing"},
            {"task_id": "task-013", "name": "SRE/Observability", "agent": "sre_observability_engineer", "phase": "operations"},
            {"task_id": "task-014", "name": "FinOps Review", "agent": "finops_engineer", "phase": "operations"},
        ]

    def _assign_agents(self, tasks: List[Dict], available: List[str]) -> Dict[str, str]:
        return {t["task_id"]: t["agent"] for t in tasks if t["agent"] in available}

    def _define_dependencies(self, tasks: List[Dict]) -> List[Dict]:
        return [
            {"task_id": "task-002", "depends_on": ["task-001"]},
            {"task_id": "task-003", "depends_on": ["task-001"]},
            {"task_id": "task-004", "depends_on": ["task-002", "task-003"]},
            {"task_id": "task-005", "depends_on": ["task-004"]},
            {"task_id": "task-006", "depends_on": ["task-004"]},
            {"task_id": "task-007", "depends_on": ["task-005", "task-006"]},
            {"task_id": "task-008", "depends_on": ["task-005", "task-006"]},
            {"task_id": "task-009", "depends_on": ["task-002"]},
            {"task_id": "task-010", "depends_on": ["task-007"]},
            {"task_id": "task-011", "depends_on": ["task-007"]},
            {"task_id": "task-012", "depends_on": ["task-007"]},
            {"task_id": "task-013", "depends_on": ["task-008", "task-009"]},
            {"task_id": "task-014", "depends_on": ["task-009"]},
        ]

    def _define_quality_gates(self) -> List[Dict]:
        return [
            {"gate_id": "gate-1", "name": "Architecture Review", "required_for": ["task-002", "task-003", "task-004"]},
            {"gate_id": "gate-2", "name": "Security Review", "required_for": ["task-003", "task-005", "task-006"]},
            {"gate_id": "gate-3", "name": "Quality Assurance", "required_for": ["task-010", "task-011", "task-012"]},
            {"gate_id": "gate-4", "name": "Operational Readiness", "required_for": ["task-013", "task-014"]},
        ]

    def _define_sequencing(self, tasks: List[Dict], dependencies: List[Dict]) -> List[str]:
        return ["discovery", "design", "implementation", "deployment", "testing", "operations"]


ENGINEERING_ORCHESTRATOR_CONTRACT = AgentContract(
    id="engineering_orchestrator",
    role="Engineering Orchestrator",
    team="Engineering Governance",
    seniority="Senior",
    mission="Central engineering coordination and task-decomposition agent.",
    responsibilities=[
        "Task decomposition",
        "Agent assignment",
        "Dependency management",
        "Quality gate definition",
        "Workflow sequencing",
        "Cross-team coordination",
        "Progress tracking",
        "Escalation management",
    ],
    non_responsibilities=["Implementation of individual tasks", "Direct code writing"],
    authority=AgentAuthority(
        autonomous=["Task decomposition", "Agent assignment within scope"],
        peer_approval=["Cross-team dependency decisions"],
        human_approval=["Major architectural exceptions", "Resource allocation changes"],
    ),
    capabilities=[
        "Task decomposition",
        "Agent orchestration",
        "Dependency management",
        "Workflow design",
    ],
    tools=["Project tracker", "Git", "Documentation", "CI/CD status", "Monitoring dashboards"],
    memory=AgentMemory(
        working=["Current orchestration context", "Active workflows"],
        project=["Task decompositions", "Agent assignments", "Dependency maps", "Quality gate results"],
        institutional=["Orchestration patterns", "Engineering best practices"],
    ),
    inputs=["Objective", "Available agents", "Architecture", "Constraints"],
    outputs=["Task decomposition", "Agent assignments", "Dependencies", "Quality gates", "Sequencing"],
    collaborators=["product_owner", "platform_architect", "security_architect", "devops_lead", "qa_lead"],
    escalation_rules=["Escalate cross-team conflicts", "Escalate resource constraints"],
    quality_gates=["Gate 9 - Release"],
    definition_of_done=[
        "All tasks decomposed",
        "All agents assigned",
        "Dependencies mapped",
        "Quality gates defined",
        "Sequencing established",
    ],
    security_constraints=["Must not expose internal agent assignments"],
    failure_policy=["Escalate orchestration failures", "Never hide task blockers"],
)

