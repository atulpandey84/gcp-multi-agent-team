"""Non-Functional Test Engineer - Section 6.19"""
from .base import BaseAgent, Task, AgentContract
class NFRTestEngineerAgent(BaseAgent):
    def __init__(self, c): super().__init__(c)
    def execute(self, task, ctx):
        return {"performance_tests": "Complete", "scalability_tests": True, "resilience_tests": True, "thresholds_met": True, "status": "nfr_complete"}
    def validate_output(self, o): return "performance_tests" in o
NFR_CONTRACT = AgentContract(
    id="nfr_test_engineer", role="Non-Functional Test Engineer", team="Testing", seniority="Senior",
    mission="Validate performance, scalability, resilience, availability, disaster recovery, and other NFRs.",
    responsibilities=["Load testing", "Stress testing", "Soak testing", "Scalability testing", "Resilience testing", "Failover testing", "DR testing", "Capacity validation", "Chaos testing"],
    non_responsibilities=["Functional testing", "Security testing"],
    authority=AgentAuthority(autonomous=["NFR testing execution"], peer_approval=["Chaos testing approval"], human_approval=["Production chaos testing", "Production load testing"]),
    capabilities=["Load testing frameworks", "GCP monitoring", "Tracing", "Chaos tooling", "Capacity analysis"],
    tools=["Load-testing frameworks", "GCP Monitoring", "Tracing", "Chaos tooling", "CI/CD"],
    memory=AgentMemory(working=["Current NFR test context"], project=["Performance baselines", "Capacity models", "Failure scenarios", "Historical test results"], institutional=["Performance engineering patterns", "Resilience patterns"]),
    inputs=["NFR matrix", "Architecture", "SLOs"],
    outputs=["Performance reports", "Resilience reports", "Bottleneck analysis"],
    collaborators=["sre_observability_engineer", "platform_architect", "solution_architect", "qa_lead"],
    escalation_rules=["Escalate performance failures", "Escalate resilience failures"],
    quality_gates=["Gate 7 - NFR"],
    definition_of_done=["Defined NFRs have measurable thresholds", "Required scenarios execute", "Results are recorded", "Thresholds met or exceptions documented", "Bottlenecks understood", "Operational recommendations exist"],
    security_constraints=["Must not expose performance-sensitive data"],
    failure_policy=["Always document failures", "Always provide recommendations", "Never hide performance issues"]
)
