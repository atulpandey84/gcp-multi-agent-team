from multi_agent_team.policies.engine import requires_human_approval

def test_critical_actions_require_approval():
    assert requires_human_approval("critical")
    assert requires_human_approval("low", tool="terraform_apply")
