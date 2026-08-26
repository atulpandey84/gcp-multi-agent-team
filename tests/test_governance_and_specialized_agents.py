from multi_agent_team.policies.engine import validate_separation_of_duties, validate_quality_gates
from multi_agent_team.agents.specialized import IAMAgent, SecurityAgent, TerraformAgent, NetworkingAgent, ProjectAgent

def test_separation_of_duties_enforcement():
    # SoD violation when author attempts to self-approve high risk action
    sod_violation = validate_separation_of_duties("agent_01", "agent_01", "iam_policy_change")
    assert sod_violation["allowed"] is False
    assert "Separation of Duties violation" in sod_violation["reason"]

    # SoD pass when author and reviewer are distinct
    sod_pass = validate_separation_of_duties("agent_01", "agent_02", "iam_policy_change")
    assert sod_pass["allowed"] is True

def test_quality_gates_enforcement():
    # Security quality gate failure due to critical vulnerabilities
    sec_fail = validate_quality_gates("security", {"critical_vulnerabilities": 2})
    assert sec_fail["passed"] is False

    # Security quality gate pass
    sec_pass = validate_quality_gates("security", {"critical_vulnerabilities": 0})
    assert sec_pass["passed"] is True

    # Testing quality gate failure due to low coverage
    test_fail = validate_quality_gates("testing", {"test_coverage": 65.0})
    assert test_fail["passed"] is False

    # FinOps quality gate failure due to budget overrun
    fin_fail = validate_quality_gates("finops", {"monthly_cost": 15000.0, "budget_limit": 10000.0})
    assert fin_fail["passed"] is False

def test_specialized_agents_execution():
    iam_agent = IAMAgent()
    iam_res = iam_agent.execute("Provision IAM Admin roles", {"author_id": "agent_a", "reviewer_id": "agent_b"})
    assert iam_res["status"] == "completed"
    assert len(iam_res["iam_bindings"]) > 0

    net_agent = NetworkingAgent()
    net_res = net_agent.execute("Design Shared VPC Topology", {})
    assert net_res["status"] == "completed"
    assert "network_topology" in net_res

    sec_agent = SecurityAgent()
    sec_res = sec_agent.execute("Conduct Threat Modeling", {"metrics": {"critical_vulnerabilities": 0}})
    assert sec_res["status"] == "completed"
    assert "threat_model" in sec_res

    tf_agent = TerraformAgent()
    tf_res = tf_agent.execute("Generate Infrastructure IaC", {})
    assert tf_res["status"] == "completed"
    assert "main.tf" in tf_res["terraform_files"]

    proj_agent = ProjectAgent()
    proj_res = proj_agent.execute("Create Resource Hierarchy Plan", {})
    assert proj_res["status"] == "completed"
    assert "resource_hierarchy" in proj_res
