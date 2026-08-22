import os

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
