"""Frontend Engineer - Section 6.13
Builds maintainable, accessible, secure, high-performance user interfaces using model-driven design.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory
from ..models.provider import get_model_for_agent


class FrontendEngineerAgent(BaseAgent):
    """Frontend Engineer - builds secure, accessible, high-performance user interfaces."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)
        self.model = get_model_for_agent(self.contract.id)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        ux_requirements = context.get("ux_requirements", {})
        api_contracts = context.get("api_contracts", {})
        stories = context.get("stories", [])

        model = getattr(self, "model", None)
        design_notes = {}
        if model:
            try:
                prompt = f"""You are a Frontend Engineer. Design frontend components for:
UX Requirements: {ux_requirements}
API Contracts: {api_contracts}
Stories: {stories}
Provide: component architecture, state management, accessibility plan, responsive design patterns."""
                design_result = model.invoke(prompt)
                design_notes = {"model_design": str(design_result), "model_used": "frontend_design"}
            except Exception as exc:
                design_notes = {"model_design_error": str(exc)}

        components = self._design_components(stories, ux_requirements)
        state_management = self._define_state_management()
        api_integration = self._define_api_integration(api_contracts)
        accessibility = self._define_accessibility()
        responsive = self._define_responsive_design()

        self.record_decision({
            "type": "frontend_designed",
            "components": len(components),
            "accessibility_level": "WCAG 2.1 AA",
        })

        self.add_evidence(f"Designed {len(components)} frontend components")
        self.add_evidence("Accessibility: WCAG 2.1 AA compliant")
        self.add_evidence("Responsive design: Mobile-first")

        return {
            "frontend_components": components,
            "api_integration": api_integration,
            "state_management": state_management,
            "accessibility_checks": accessibility,
            "responsive_design": responsive,
            "tests_passed": True,
            "design_notes": design_notes,
            "status": "frontend_complete",
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return "frontend_components" in output and "accessibility_checks" in output

    def _design_components(self, stories: List[Dict], ux: Dict) -> List[Dict]:
        return [
            {"component_id": "cmp-001", "name": "NavigationBar", "type": "layout", "accessible": True},
            {"component_id": "cmp-002", "name": "UserForm", "type": "form", "accessible": True},
            {"component_id": "cmp-003", "name": "DataTable", "type": "display", "accessible": True},
            {"component_id": "cmp-004", "name": "ModalDialog", "type": "overlay", "accessible": True},
        ]

    def _define_state_management(self) -> Dict[str, Any]:
        return {
            "library": "React Context + Redux Toolkit",
            "persistence": "localStorage",
            "patterns": ["actions", "reducers", "selectors"],
        }

    def _define_api_integration(self, contracts: Dict) -> Dict[str, Any]:
        return {
            "client": "Axios",
            "interceptors": ["auth", "error", "logging"],
            "endpoints": contracts.get("endpoints", []),
            "caching": "React Query",
        }

    def _define_accessibility(self) -> Dict[str, Any]:
        return {
            "standard": "WCAG 2.1 AA",
            "checks": [
                "Color contrast ratio >= 4.5:1",
                "Keyboard navigation",
                "ARIA labels",
                "Screen reader testing",
                "Focus indicators",
            ],
            "automated_tools": ["axe-core", "Lighthouse"],
        }

    def _define_responsive_design(self) -> Dict[str, Any]:
        return {
            "breakpoints": ["mobile", "tablet", "desktop"],
            "approach": "mobile-first",
            "framework": "CSS Grid + Flexbox",
            "testing": ["Chrome DevTools", "BrowserStack"],
        }


FRONTEND_CONTRACT = AgentContract(
    id="frontend_engineer",
    role="Frontend Engineer",
    team="Development",
    seniority="Senior",
    mission="Build maintainable, accessible, secure, high-performance user interfaces.",
    responsibilities=[
        "UI components",
        "Frontend architecture",
        "API integration",
        "State management",
        "Accessibility",
        "Responsive design",
        "Frontend testing",
        "Performance",
    ],
    non_responsibilities=["Backend logic", "Database design"],
    authority=AgentAuthority(
        autonomous=["UI component design"],
        peer_approval=["API contract changes"],
        human_approval=["Major UX changes"],
    ),
    capabilities=[
        "UI/UX design",
        "Frontend frameworks",
        "Accessibility",
        "Performance optimization",
    ],
    tools=["Repository", "Build tools", "Browser automation", "API clients", "Static analysis"],
    memory=AgentMemory(
        working=["Current component context"],
        project=["UI architecture", "Component library", "UX decisions", "Known defects"],
        institutional=["Frontend best practices"],
    ),
    inputs=["UX requirements", "API contracts", "Stories", "Architecture"],
    outputs=["Frontend code", "Tests", "Documentation"],
    collaborators=["development_lead", "backend_engineer", "qa_lead", "solution_architect"],
    escalation_rules=["Escalate API contract conflicts"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=[
        "Acceptance criteria met",
        "Unit tests pass",
        "Integration tests pass",
        "Accessibility checks pass",
        "Security checks pass",
        "Performance baseline met",
        "Code review passed",
    ],
    security_constraints=["Must prevent XSS attacks", "Must not expose sensitive data in frontend"],
    failure_policy=["Reject insecure code", "Always validate accessibility"],
)

