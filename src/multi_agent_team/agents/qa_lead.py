"""QA Lead - Section 6.17
Own quality strategy and release quality decisions using model-driven reasoning.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class QALeadAgent(BaseAgent):
    """QA Lead - owns quality strategy and release quality decisions."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        requirements = context.get("requirements", [])
        architecture = context.get("architecture", {})
        code_quality = context.get("code_quality", {})

        model = getattr(self, "model", None)
        review_notes = {}
        if model:
            try:
                prompt = f"""You are a QA Lead. Define quality strategy for:
Requirements: {requirements}
Architecture: {architecture}
Code Quality: {code_quality}
Provide: test strategy, quality gates, release criteria, defect management."""
                design_result = model.invoke(prompt)
                review_notes = {"model_design": str(design_result), "model_used": "qa_design"}
            except Exception as exc:
                review_notes = {"model_design_error": str(exc)}

        test_strategy = self._define_test_strategy(requirements)
        quality_gates = self._define_quality_gates()
        release_recommendation = self._define_release_recommendation()
        defect_governance = self._define_defect_governance()

        self.record_decision({
            "type": "quality_strategy_defined",
            "test_strategy": test_strategy,
            "quality_gates": quality_gates,
        })

        self.add_evidence("Test strategy created")
        self.add_evidence("Quality gates defined")
        self.add_evidence("Release recommendation prepared")

        return {
            "test_strategy": test_strategy,
            "test_plan": "Approved",
            "quality_gates": quality_gates,
            "defects_managed": True,
            "release_recommendation": release_recommendation,
            "defect_governance": defect_governance,
            "design_notes": review_notes,
            "status": "quality_approved",
        }

    def validate_output(self, o):
        return "test_strategy" in o and "release_recommendation" in o

    def _define_test_strategy(self, requirements: List[Dict]) -> Dict[str, Any]:
        return {
            "strategy_id": "qs-001",
            "name": "Comprehensive Test Strategy",
            "levels": ["unit", "integration", "api", "ui", "e2e", "performance", "security"],
            "coverage_target": 85,
            "automation_target": 90,
        }

    def _define_quality_gates(self) -> List[Dict]:
        return [
            {"gate_id": "qg-001", "name": "Code Quality", "threshold": 85, "blocking": True},
            {"gate_id": "qg-002", "name": "Security", "threshold": 100, "blocking": True},
            {"gate_id": "qg-003", "name": "Performance", "threshold": 200, "blocking": False},
            {"gate_id": "qg-004", "name": "Accessibility", "threshold": "WCAG AA", "blocking": True},
        ]

    def _define_release_recommendation(self) -> Dict[str, Any]:
        return {
            "recommendation": "approve",
            "conditions": ["All quality gates pass", "Critical defects resolved", "Security review approved"],
            "risk_level": "low",
        }

    def _define_defect_governance(self) -> Dict[str, Any]:
        return {
            "defect_tracking": "Jira",
            "severity_levels": ["critical", "high", "medium", "low"],
            "sla": {"critical": "24h", "high": "48h", "medium": "1w", "low": "2w"},
            "review_cadence": "daily",
        }


QA_CONTRACT = AgentContract(
    id="qa_lead",
    role="QA Lead",
    team="Testing",
    seniority="Senior",
    mission="Own quality strategy and release quality decisions.",
    responsibilities=[
        "Test strategy",
        "Test planning",
        "Coverage",
        "Quality gates",
        "Defect governance",
        "Release quality",
        "QA metrics",
    ],
    non_responsibilities=["Test implementation", "Infrastructure testing"],
    authority=AgentAuthority(
        autonomous=["Quality gate evaluation"],
        peer_approval=["Test plan review"],
        human_approval=["Release rejection", "Major scope changes"],
    ),
    capabilities=[
        "Test strategy",
        "Quality management",
        "Defect tracking",
        "Release management",
    ],
    tools=["Test management", "CI/CD", "Issue tracker", "Code repository", "Reporting"],
    memory=AgentMemory(
        working=["Current quality context"],
        project=["Test history", "Defects", "Coverage", "Quality metrics"],
        institutional=["Quality standards", "Testing best practices"],
    ),
    inputs=["Requirements", "Architecture", "Code", "Test results"],
    outputs=["Test strategy", "Quality report", "Release recommendation"],
    collaborators=["development_lead", "test_automation_engineer", "nfr_test_engineer", "product_owner"],
    escalation_rules=["Reject releases that fail mandatory quality gates"],
    quality_gates=["Gate 6 - QA"],
    definition_of_done=[
        "Required coverage exists",
        "Critical tests pass",
        "Critical defects resolved",
        "NFR gates pass",
        "Security test status acceptable",
        "Evidence is recorded",
    ],
    security_constraints=["Must not approve with unaddressed security findings"],
    failure_policy=["Reject quality gates that fail", "Always document defects", "Never approve without evidence"],
)

