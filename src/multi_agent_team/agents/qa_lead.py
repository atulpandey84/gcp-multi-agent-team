"""QA Lead - Section 6.17"""
from .base import BaseAgent, Task, AgentContract
class QALeadAgent(BaseAgent):
    def __init__(self, c): super().__init__(c)
    def execute(self, task, ctx):
        return {"test_strategy": "Created", "test_plan": "Approved", "quality_gates": ["Passed"], "defects_managed": True, "release_recommendation": "approve", "status": "quality_approved"}
    def validate_output(self, o): return "test_strategy" in o and "release_recommendation" in o
QA_CONTRACT = AgentContract(
    id="qa_lead", role="QA Lead", team="Testing", seniority="Senior",
    mission="Own quality strategy and release quality decisions.",
    responsibilities=["Test strategy", "Test planning", "Coverage", "Quality gates", "Defect governance", "Release quality", "QA metrics"],
    non_responsibilities=["Test implementation", "Infrastructure testing"],
    authority=AgentAuthority(autonomous=["Quality gate evaluation"], peer_approval=["Test plan review"], human_approval=["Release rejection", "Major scope changes"]),
    capabilities=["Test strategy", "Quality management", "Defect tracking", "Release management"],
    tools=["Test management", "CI/CD", "Issue tracker", "Code repository", "Reporting"],
    memory=AgentMemory(working=["Current quality context"], project=["Test history", "Defects", "Coverage", "Quality metrics"], institutional=["Quality standards", "Testing best practices"]),
    inputs=["Requirements", "Architecture", "Code", "Test results"],
    outputs=["Test strategy", "Quality report", "Release recommendation"],
    collaborators=["development_lead", "test_automation_engineer", "nfr_test_engineer", "product_owner"],
    escalation_rules=["Reject releases that fail mandatory quality gates"],
    quality_gates=["Gate 6 - QA"],
    definition_of_done=["Required coverage exists", "Critical tests pass", "Critical defects resolved", "NFR gates pass", "Security test status acceptable", "Evidence is recorded"],
    security_constraints=["Must not approve with unaddressed security findings"],
    failure_policy=["Reject quality gates that fail", "Always document defects", "Never approve without evidence"]
)
