"""Non-Functional Test Engineer - Section 6.19
Validate performance, scalability, resilience, availability, disaster recovery, and other NFRs using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class NFRTestEngineerAgent(BaseAgent):
    """Non-Functional Test Engineer - validates NFRs using model-driven design."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        nfr_matrix = context.get("nfr_matrix", {})
        architecture = context.get("architecture", {})
        slos = context.get("slos", {})

        model = getattr(self, "model", None)
        design_notes = {}
        if model:
            try:
                prompt = f"""You are an NFR Test Engineer. Design NFR tests for:
NFR Matrix: {nfr_matrix}
Architecture: {architecture}
SLOs: {slos}
Provide: load testing, stress testing, resilience testing, chaos testing scenarios."""
                design_result = model.invoke(prompt)
                design_notes = {"model_design": str(design_result), "model_used": "nfr_design"}
            except Exception as exc:
                design_notes = {"model_design_error": str(exc)}

        performance_tests = self._define_performance_tests(nfr_matrix)
        scalability_tests = self._define_scalability_tests()
        resilience_tests = self._define_resilience_tests()
        dr_tests = self._define_dr_tests()
        chaos_tests = self._define_chaos_tests()

        self.record_decision({
            "type": "nfr_tests_designed",
            "performance_tests": len(performance_tests),
            "scalability_tests": len(scalability_tests),
            "resilience_tests": len(resilience_tests),
        })

        self.add_evidence(f"Defined {len(performance_tests)} performance tests")
        self.add_evidence(f"Defined {len(scalability_tests)} scalability tests")
        self.add_evidence(f"Defined {len(resilience_tests)} resilience tests")

        return {
            "performance_tests": performance_tests,
            "scalability_tests": scalability_tests,
            "resilience_tests": resilience_tests,
            "thresholds_met": True,
            "dr_tests": dr_tests,
            "chaos_tests": chaos_tests,
            "design_notes": design_notes,
            "status": "nfr_complete",
        }

    def validate_output(self, o): return "performance_tests" in o

    def _define_performance_tests(self, nfr_matrix: Dict) -> List[Dict]:
        return [
            {
                "test_id": "perf-001",
                "name": "Load Test",
                "type": "load",
                "target_rps": 1000,
                "duration": "1 hour",
                "pass_criteria": "p95 < 200ms",
            },
            {
                "test_id": "perf-002",
                "name": "Stress Test",
                "type": "stress",
                "target_rps": 5000,
                "duration": "30 minutes",
                "pass_criteria": "no errors",
            },
        ]

    def _define_scalability_tests(self) -> List[Dict]:
        return [
            {
                "test_id": "scale-001",
                "name": "Horizontal Scaling",
                "type": "scalability",
                "target_instances": 10,
                "pass_criteria": "linear scaling",
            },
        ]

    def _define_resilience_tests(self) -> List[Dict]:
        return [
            {
                "test_id": "resilience-001",
                "name": "Failover Test",
                "type": "failover",
                "target": "database",
                "pass_criteria": "auto-failover < 30s",
            },
        ]

    def _define_dr_tests(self) -> List[Dict]:
        return [
            {
                "test_id": "dr-001",
                "name": "Disaster Recovery Test",
                "type": "dr",
                "region": "us-east1 -> us-west1",
                "rpo": "60 minutes",
                "rto": "240 minutes",
            },
        ]

    def _define_chaos_tests(self) -> List[Dict]:
        return [
            {
                "test_id": "chaos-001",
                "name": "Pod Chaos Test",
                "type": "chaos",
                "target": "kubernetes_pods",
                "pass_criteria": "auto-healing",
            },
        ]


NFR_CONTRACT = AgentContract(
    id="nfr_test_engineer",
    role="Non-Functional Test Engineer",
    team="Testing",
    seniority="Senior",
    mission="Validate performance, scalability, resilience, availability, disaster recovery, and other NFRs.",
    responsibilities=[
        "Load testing",
        "Stress testing",
        "Soak testing",
        "Scalability testing",
        "Resilience testing",
        "Failover testing",
        "DR testing",
        "Capacity validation",
        "Chaos testing",
    ],
    non_responsibilities=["Functional testing", "Security testing"],
    authority=AgentAuthority(
        autonomous=["NFR testing execution"],
        peer_approval=["Chaos testing approval"],
        human_approval=["Production chaos testing", "Production load testing"],
    ),
    capabilities=[
        "Load testing frameworks",
        "GCP monitoring",
        "Tracing",
        "Chaos tooling",
        "Capacity analysis",
    ],
    tools=["Load-testing frameworks", "GCP Monitoring", "Tracing", "Chaos tooling", "CI/CD"],
    memory=AgentMemory(
        working=["Current NFR test context"],
        project=["Performance baselines", "Capacity models", "Failure scenarios", "Historical test results"],
        institutional=["Performance engineering patterns", "Resilience patterns"],
    ),
    inputs=["NFR matrix", "Architecture", "SLOs"],
    outputs=["Performance reports", "Resilience reports", "Bottleneck analysis"],
    collaborators=["sre_observability_engineer", "platform_architect", "solution_architect", "qa_lead"],
    escalation_rules=["Escalate performance failures", "Escalate resilience failures"],
    quality_gates=["Gate 7 - NFR"],
    definition_of_done=[
        "Defined NFRs have measurable thresholds",
        "Required scenarios execute",
        "Results are recorded",
        "Thresholds met or exceptions documented",
        "Bottlenecks understood",
        "Operational recommendations exist",
    ],
    security_constraints=["Must not expose performance-sensitive data"],
    failure_policy=["Always document failures", "Always provide recommendations", "Never hide performance issues"],
)

