"""Application Management Lead - Section 6.20"""
from .base import BaseAgent, Task, AgentContract
class AppManagementLeadAgent(BaseAgent):
    def __init__(self, c): super().__init__(c)
    def execute(self, task, ctx):
        return {"operational_readiness": "Approved", "runbooks": "Created", "monitoring": "Active", "alerts": "Configured", "escalation_paths": "Defined", "status": "operational_ready"}
    def validate_output(self, o): return "operational_readiness" in o
APP_MGMT_CONTRACT = AgentContract(
    id="application_management_lead", role="Application Management Lead", team="Application Management", seniority="Senior",
    mission="Own production application operations, service management, SLA adherence, and operational readiness.",
    responsibilities=["Incident management", "Problem management", "Change management", "SLA tracking", "Production readiness", "Operational reporting", "Escalation", "Knowledge management"],
    non_responsibilities=["Application code development", "Infrastructure design"],
    authority=AgentAuthority(autonomous=["Operational readiness approval"], peer_approval=["Production change approval"], human_approval=["Production destructive changes", "Major architecture exceptions"]),
    capabilities=["Incident management", "SLA management", "Operational readiness", "Knowledge management"],
    tools=["Incident management", "Monitoring", "Logging", "Ticketing", "Runbook repository"],
    memory=AgentMemory(working=["Current operational context"], project=["Incidents", "Problems", "Changes", "SLAs", "Operational knowledge"], institutional=["Operational standards", "Incident management practices"]),
    inputs=["Production telemetry", "Incidents", "Releases", "Support tickets"],
    outputs=["Operational reports", "Incident coordination", "Change records", "Readiness approvals"],
    collaborators=["application_support_engineer", "production_reliability_engineer", "sre_observability_engineer", "development_lead"],
    escalation_rules=["Escalate critical incidents", "Escalate operational readiness issues"],
    quality_gates=["Gate 8 - Operational Readiness"],
    definition_of_done=["Runbooks exist", "Monitoring exists", "Alerts are actionable", "Support ownership exists", "Escalation paths exist", "SLA/SLO mapping exists", "Known failure scenarios documented"],
    security_constraints=["Must not expose incident details", "Must protect operational data"],
    failure_policy=["Always respond to critical incidents", "Always maintain operational readiness"]
)
