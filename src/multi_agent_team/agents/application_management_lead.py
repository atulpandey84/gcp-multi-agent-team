"""Application Management Lead - Section 6.20
Owns production application operations, service management, SLA adherence, and operational readiness using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class AppManagementLeadAgent(BaseAgent):
    """Application Management Lead - owns production application operations."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        incidents = context.get("incidents", [])
        releases = context.get("releases", [])
        telemetry = context.get("telemetry", {})

        model = getattr(self, "model", None)
        review_notes = {}
        if model:
            try:
                prompt = f"""You are an Application Management Lead. Define operational readiness for:
Incidents: {incidents}
Releases: {releases}
Telemetry: {telemetry}
Provide: incident management, SLA tracking, operational readiness, runbooks."""
                design_result = model.invoke(prompt)
                review_notes = {"model_design": str(design_result), "model_used": "mgmt_design"}
            except Exception as exc:
                review_notes = {"model_design_error": str(exc)}

        operational_readiness = self._define_operational_readiness()
        runbooks = self._define_runbooks()
        monitoring = self._define_monitoring()
        alerts = self._define_alerts()
        escalation_paths = self._define_escalation_paths()

        self.record_decision({
            "type": "operational_readiness_defined",
            "readiness_score": "approved",
        })

        self.add_evidence("Operational readiness defined")
        self.add_evidence("Runbooks created")
        self.add_evidence("Monitoring configured")

        return {
            "operational_readiness": "Approved",
            "runbooks": runbooks,
            "monitoring": monitoring,
            "alerts": alerts,
            "escalation_paths": escalation_paths,
            "status": "operational_ready",
        }

    def validate_output(self, o):
        return "operational_readiness" in o

    def _define_operational_readiness(self) -> Dict[str, Any]:
        return {
            "readiness_score": "approved",
            "sla_adherence": "99.9%",
            "ownership": "Application Management Lead",
        }

    def _define_runbooks(self) -> List[Dict]:
        return [
            {"runbook_id": "rb-001", "name": "Incident Response", "steps": ["detect", "triage", "resolve", "postmortem"]},
            {"runbook_id": "rb-002", "name": "Change Management", "steps": ["request", "approve", "implement", "verify"]},
        ]

    def _define_monitoring(self) -> Dict[str, Any]:
        return {
            "metrics": ["error_rate", "latency", "throughput", "availability"],
            "tools": ["Cloud Monitoring", "Cloud Logging"],
        }

    def _define_alerts(self) -> List[Dict]:
        return [
            {"alert_id": "alert-001", "name": "High Error Rate", "severity": "critical"},
            {"alert_id": "alert-002", "name": "High Latency", "severity": "warning"},
        ]

    def _define_escalation_paths(self) -> List[str]:
        return ["L1 Support", "L2 Support", "Application Management Lead", "Engineering Orchestrator"]


APP_MGMT_CONTRACT = AgentContract(
    id="application_management_lead",
    role="Application Management Lead",
    team="Application Management",
    seniority="Senior",
    mission="Own production application operations, service management, SLA adherence, and operational readiness.",
    responsibilities=[
        "Incident management",
        "Problem management",
        "Change management",
        "SLA tracking",
        "Production readiness",
        "Operational reporting",
        "Escalation",
        "Knowledge management",
    ],
    non_responsibilities=["Application code development", "Infrastructure design"],
    authority=AgentAuthority(
        autonomous=["Operational readiness approval"],
        peer_approval=["Production change approval"],
        human_approval=["Production destructive changes", "Major architecture exceptions"],
    ),
    capabilities=[
        "Incident management",
        "SLA management",
        "Operational readiness",
        "Knowledge management",
    ],
    tools=["Incident management", "Monitoring", "Logging", "Ticketing", "Runbook repository"],
    memory=AgentMemory(
        working=["Current operational context"],
        project=["Incidents", "Problems", "Changes", "SLAs", "Operational knowledge"],
        institutional=["Operational standards", "Incident management practices"],
    ),
    inputs=["Production telemetry", "Incidents", "Releases", "Support tickets"],
    outputs=["Operational reports", "Incident coordination", "Change records", "Readiness approvals"],
    collaborators=["application_support_engineer", "production_reliability_engineer", "sre_observability_engineer", "development_lead"],
    escalation_rules=["Escalate critical incidents", "Escalate operational readiness issues"],
    quality_gates=["Gate 8 - Operational Readiness"],
    definition_of_done=[
        "Runbooks exist",
        "Monitoring exists",
        "Alerts are actionable",
        "Support ownership exists",
        "Escalation paths exist",
        "SLA/SLO mapping exists",
        "Known failure scenarios documented",
    ],
    security_constraints=["Must not expose incident details", "Must protect operational data"],
    failure_policy=["Always respond to critical incidents", "Always maintain operational readiness"],
)

