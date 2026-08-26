import os
from typing import Any

def requires_human_approval(risk: str, tool: str | None = None) -> bool:
    if risk in {"high", "critical", "catastrophic"}:
        return True
    return tool in {"terraform_apply", "iam_policy_change", "project_delete", "production_deployment"}

def mutations_allowed() -> bool:
    return os.getenv("ALLOW_GCP_MUTATIONS", "false").lower() == "true"

def terraform_apply_allowed() -> bool:
    return os.getenv("ALLOW_TERRAFORM_APPLY", "false").lower() == "true"

def production_deployment_allowed() -> bool:
    return os.getenv("ALLOW_PRODUCTION_DEPLOYMENT", "false").lower() == "true"

def validate_separation_of_duties(author_id: str, reviewer_id: str, action_type: str) -> dict[str, Any]:
    """Enforce Separation of Duties (SoD): Author cannot self-approve high-risk infrastructure, IAM, or deployment changes."""
    high_risk_actions = {"iam_policy_change", "terraform_apply", "production_deployment", "security_exception", "architecture_approval"}
    if action_type in high_risk_actions and author_id == reviewer_id:
        return {
            "allowed": False,
            "reason": f"Separation of Duties violation: Author '{author_id}' cannot self-approve action '{action_type}'."
        }
    return {"allowed": True, "reason": "Separation of Duties check passed."}

def validate_quality_gates(gate_name: str, metrics: dict[str, Any]) -> dict[str, Any]:
    """Enforce quality gate metrics (e.g. test coverage, security vulnerabilities, cost estimation)."""
    if gate_name == "security":
        critical_vulnerabilities = metrics.get("critical_vulnerabilities", 0)
        if critical_vulnerabilities > 0:
            return {"passed": False, "reason": f"Security quality gate failed: {critical_vulnerabilities} critical vulnerabilities found."}
    elif gate_name == "testing":
        coverage = metrics.get("test_coverage", 0.0)
        if coverage < 80.0:
            return {"passed": False, "reason": f"Testing quality gate failed: coverage {coverage}% is below threshold 80.0%."}
    elif gate_name == "finops":
        estimated_cost = metrics.get("monthly_cost", 0.0)
        budget_limit = metrics.get("budget_limit", 10000.0)
        if estimated_cost > budget_limit:
            return {"passed": False, "reason": f"FinOps quality gate failed: cost ${estimated_cost} exceeds budget limit ${budget_limit}."}
    return {"passed": True, "reason": f"Quality gate '{gate_name}' passed successfully."}
