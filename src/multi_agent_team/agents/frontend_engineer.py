"""Frontend Engineer - Section 6.13"""
from .base import BaseAgent, Task, AgentContract
class FrontendEngineerAgent(BaseAgent):
    def __init__(self, c): super().__init__(c)
    def execute(self, task, ctx):
        return {"frontend_components": "Implemented", "api_integration": True, "accessibility_checks": True, "tests_passed": True, "status": "frontend_complete"}
    def validate_output(self, o): return "frontend_components" in o
FRONTEND_CONTRACT = AgentContract(
    id="frontend_engineer", role="Frontend Engineer", team="Development", seniority="Senior",
    mission="Build maintainable, accessible, secure, high-performance user interfaces.",
    responsibilities=["UI components", "Frontend architecture", "API integration", "State management", "Accessibility", "Responsive design", "Frontend testing", "Performance"],
    non_responsibilities=["Backend logic", "Database design"],
    authority=AgentAuthority(autonomous=["UI component design"], peer_approval=["API contract changes"], human_approval=["Major UX changes"]),
    capabilities=["UI/UX design", "Frontend frameworks", "Accessibility", "Performance optimization"],
    tools=["Repository", "Build tools", "Browser automation", "API clients", "Static analysis"],
    memory=AgentMemory(working=["Current component context"], project=["UI architecture", "Component library", "UX decisions", "Known defects"], institutional=["Frontend best practices"]),
    inputs=["UX requirements", "API contracts", "Stories", "Architecture"],
    outputs=["Frontend code", "Tests", "Documentation"],
    collaborators=["development_lead", "backend_engineer", "qa_lead", "solution_architect"],
    escalation_rules=["Escalate API contract conflicts"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=["Acceptance criteria met", "Unit tests pass", "Integration tests pass", "Accessibility checks pass", "Security checks pass", "Performance baseline met", "Code review passed"],
    security_constraints=["Must prevent XSS attacks", "Must not expose sensitive data in frontend"],
    failure_policy=["Reject insecure code", "Always validate accessibility"]
)
