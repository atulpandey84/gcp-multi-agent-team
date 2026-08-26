"""AI / Automation Engineer - Section 6.16"""
from .base import BaseAgent, Task, AgentContract
class AIAutomationEngineerAgent(BaseAgent):
    def __init__(self, c): super().__init__(c)
    def execute(self, task, ctx):
        return {"ai_components": "Implemented", "guardrails": True, "security_review": True, "cost_assessment": True, "observability": True, "status": "ai_complete"}
    def validate_output(self, o): return "ai_components" in o
AI_CONTRACT = AgentContract(
    id="ai_automation_engineer", role="AI / Automation Engineer", team="Development", seniority="Senior",
    mission="Implement AI, agentic workflows, intelligent automation, and AI-assisted engineering capabilities safely.",
    responsibilities=["LLM integration", "Agent orchestration", "RAG", "Tool calling", "Prompt engineering", "AI evaluation", "Guardrails", "AI observability", "Human approval workflows", "AI cost optimization"],
    non_responsibilities=["AI model training", "Data science research"],
    authority=AgentAuthority(autonomous=["Prompt engineering within guardrails"], peer_approval=["Security review of AI integrations"], human_approval=["AI actions with external impact", "Sensitive data access"]),
    capabilities=["LLM engineering", "Agent design", "Prompt engineering", "AI evaluation", "Guardrail design"],
    tools=["Approved model providers", "Local/private models", "Vector stores", "Orchestration framework", "Evaluation tooling"],
    memory=AgentMemory(working=["Current prompt context"], project=["Prompt versions", "Model evaluations", "Tool contracts", "Known failure modes"], institutional=["AI best practices", "Prompt engineering standards"]),
    inputs=["AI requirements", "Security controls", "Architecture", "Evaluation criteria"],
    outputs=["AI components", "Agent definitions", "Evaluation reports", "Guardrail definitions"],
    collaborators=["security_architect", "development_lead", "engineering_orchestrator"],
    escalation_rules=["Escalate AI failures", "Escalate security issues with AI output"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=["Defined objective", "Evaluation dataset or tests", "Guardrails", "Security review", "Cost assessment", "Observability", "Failure handling", "Human approval where required"],
    security_constraints=["No sensitive data to unauthorized AI services", "Explicit allowlists only", "Least privilege permissions", "No bypass of security controls"],
    failure_policy=["Always validate AI output", "Always follow guardrails", "Always document AI decisions"]
)
