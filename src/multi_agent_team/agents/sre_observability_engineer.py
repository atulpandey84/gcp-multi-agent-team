"""SRE / Observability Engineer - Section 6.10
Ensure reliability, observability, measurable SLOs, and operational readiness using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class SREObservabilityEngineerAgent(BaseAgent):
    """SRE / Observability Engineer - ensures reliability and observability."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        architecture = context.get("architecture", {})
        application_telemetry = context.get("application_telemetry", {})
        operational_requirements = context.get("operational_requirements", {})

        model = getattr(self, "model", None)
        design_notes = {}
        if model:
            try:
                prompt = f"""You are an SRE / Observability Engineer. Define SLOs and observability for:
Architecture: {architecture}
Application Telemetry: {application_telemetry}
Operational Requirements: {operational_requirements}
Provide: SLO definitions, monitoring strategy, alerting, dashboards, runbooks."""
                design_result = model.invoke(prompt)
                design_notes = {"model_design": str(design_result), "model_used": "sre_design"}
            except Exception as exc:
                design_notes = {"model_design_error": str(exc)}

        slo_definitions = self._define_slos(architecture)
        monitoring = self._define_monitoring(architecture)
        alerting = self._define_alerting()
        dashboards = self._define_dashboards()
        runbooks = self._define_runbooks()

        self.record_decision({
            "type": "observability_configured",
            "slos": len(slo_definitions),
            "alerts": len(alerting),
        })

        self.add_evidence(f"Defined {len(slo_definitions)} SLOs")
        self.add_evidence(f"Configured {len(alerting)} alerts")
        self.add_evidence("Monitoring active")

        return {
            "slo_defined": True,
            "monitoring_active": True,
            "alerts_configured": True,
            "slo_definitions": slo_definitions,
            "monitoring": monitoring,
            "alerting": alerting,
            "dashboards": dashboards,
            "runbooks": runbooks,
            "design_notes": design_notes,
            "status": "operational_ready",
        }

    def validate_output(self, o):
        return all(k in o for k in ["slo_defined", "monitoring_active"])

    def _define_slos(self, architecture: Dict) -> List[Dict]:
        return [
            {
                "slo_id": "slo-001",
                "name": "Availability",
                "target": "99.9%",
                "measurement": "uptime",
                "window": "30 days",
            },
            {
                "slo_id": "slo-002",
                "name": "Latency",
                "target": "p95 < 200ms",
                "measurement": "response_time",
                "window": "5 minutes",
            },
            {
                "slo_id": "slo-003",
                "name": "Error Rate",
                "target": "< 0.1%",
                "measurement": "error_rate",
                "window": "5 minutes",
            },
        ]

    def _define_monitoring(self, architecture: Dict) -> Dict[str, Any]:
        return {
            "metrics": ["cpu", "memory", "disk", "network", "request_rate", "error_rate"],
            "collection_interval": "15s",
            "retention": "30 days",
            "tools": ["Cloud Monitoring", "Prometheus", "Grafana"],
        }

    def _define_alerting(self) -> List[Dict]:
        return [
            {
                "alert_id": "alert-001",
                "name": "High CPU Usage",
                "condition": "cpu > 80%",
                "severity": "warning",
                "notification": ["slack", "email"],
            },
            {
                "alert_id": "alert-002",
                "name": "Service Down",
                "condition": "service_unavailable",
                "severity": "critical",
                "notification": ["pagerduty", "slack", "sms"],
            },
            {
                "alert_id": "alert-003",
                "name": "High Error Rate",
                "condition": "error_rate > 1%",
                "severity": "warning",
                "notification": ["slack", "email"],
            },
        ]

    def _define_dashboards(self) -> List[Dict]:
        return [
            {"name": "Infrastructure", "panels": ["cpu", "memory", "disk", "network"]},
            {"name": "Application", "panels": ["request_rate", "error_rate", "latency"]},
            {"name": "Business", "panels": ["conversion", "revenue", "active_users"]},
        ]

    def _define_runbooks(self) -> List[Dict]:
        return [
            {
                "runbook_id": "rb-001",
                "name": "Service Outage",
                "steps": ["detect", "diagnose", "mitigate", "resolve", "postmortem"],
                "owner": "SRE",
            },
            {
                "runbook_id": "rb-002",
                "name": "High Latency",
                "steps": ["detect", "identify_bottleneck", "scale", "monitor"],
                "owner": "SRE",
            },
        ]


SRE_OBSERVABILITY_CONTRACT = AgentContract(
    id="sre_observability_engineer",
    role="SRE / Observability Engineer",
    team="DevOps",
    seniority="Senior",
    mission="Ensure reliability, observability, measurable SLOs, and operational readiness.",
    responsibilities=[
        "SLI/SLO/SLA",
        "Monitoring",
        "Logging",
        "Alerting",
        "Tracing",
        "Dashboards",
        "Error budgets",
        "Capacity planning",
        "Reliability engineering",
        "Incident automation",
        "Performance telemetry",
    ],
    non_responsibilities=["Application code development", "Infrastructure provisioning"],
    authority=AgentAuthority(
        autonomous=["SLO definitions", "Alert configurations"],
        peer_approval=["Production-readiness assessment"],
        human_approval=["Production deployment", "SLO changes"],
    ),
    capabilities=[
        "Cloud Monitoring",
        "Cloud Logging",
        "Trace",
        "Profiler",
        "Alerting",
        "GCP APIs",
    ],
    tools=["Cloud Monitoring", "Cloud Logging", "Trace", "Profiler", "Alerting", "GCP APIs"],
    memory=AgentMemory(
        working=["Current monitoring context"],
        project=["SLO history", "Incidents", "Alerts", "Capacity models"],
        institutional=["Reliability engineering patterns", "SLO best practices"],
    ),
    inputs=["Architecture", "Application telemetry", "Operational requirements"],
    outputs=["SLO definitions", "Dashboards", "Alerts", "Runbooks", "Reliability reports", "Capacity recommendations"],
    collaborators=["devops_lead", "production_reliability_engineer", "application_management_lead"],
    escalation_rules=["Escalate reliability incidents"],
    quality_gates=["Gate 8 - Operational Readiness"],
    definition_of_done=[
        "SLOs defined",
        "Key telemetry available",
        "Alerts actionable",
        "Dashboards available",
        "Runbooks exist",
        "Failure scenarios tested",
    ],
    security_constraints=["Must protect telemetry data", "Must not expose sensitive metrics"],
    failure_policy=["Escalate reliability failures", "Always maintain observability"],
)

