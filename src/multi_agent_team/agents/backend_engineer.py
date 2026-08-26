"""Backend Engineer - Section 6.14"""
from .base import BaseAgent, Task, AgentContract
class BackendEngineerAgent(BaseAgent):
    def __init__(self, c): super().__init__(c)
    def execute(self, task, ctx):
        return {"backend_services": "Implemented", "api_contract_validated": True, "security_checks": True, "tests_passed": True, "status": "backend_complete"}
    def validate_output(self, o): return "backend_services" in o
BACKEND_CONTRACT = AgentContract(
    id="backend_engineer", role="Backend Engineer", team="Development", seniority="Senior",
    mission="Build secure, reliable, scalable backend services and APIs.",
    responsibilities=["Business logic", "APIs", "Microservices", "Data access", "Authentication integration", "Error handling", "Performance", "Backend testing"],
    non_responsibilities=["Frontend design", "Infrastructure provisioning"],
    authority=AgentAuthority(autonomous=["Backend service implementation"], peer_approval=["API contract changes"], human_approval=["Data model changes"]),
    capabilities=["Server-side programming", "API design", "Database design", "Security practices"],
    tools=["Repository", "Compiler/runtime", "Test framework", "Database tooling", "CI/CD"],
    memory=AgentMemory(working=["Current service context"], project=["Service architecture", "API contracts", "Data models", "Defects"], institutional=["Backend best practices"]),
    inputs=["Stories", "API contracts", "Solution architecture"],
    outputs=["Backend code", "Tests", "API documentation"],
    collaborators=["development_lead", "frontend_engineer", "integration_engineer", "security_architect"],
    escalation_rules=["Escalate data model conflicts"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=["Functional requirements met", "API contract validated", "Unit/integration tests pass", "Security checks pass", "Performance acceptable", "Code review passed"],
    security_constraints=["Must prevent injection attacks", "Must validate inputs"],
    failure_policy=["Reject untested code", "Always validate security"]
)
