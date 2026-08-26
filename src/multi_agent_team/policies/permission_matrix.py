# Tool Permission Matrix per Section 14 of MULTI_AGENT_TEAM_SPECIFICATION.md
# R = Read, W = Write, Gate = Controlled/Approval Required, - = No Access

PERMISSION_MATRIX = {
    "product_owner":     {"git": "R", "gcp_read": "R", "gcp_write": "-", "terraform": "-", "ci_cd": "R", "prod": "-", "billing": "R", "security": "R"},
    "project_manager":   {"git": "R", "gcp_read": "R", "gcp_write": "-", "terraform": "-", "ci_cd": "R", "prod": "-", "billing": "R", "security": "R"},
    "engineering_orchestrator": {"git": "R/W", "gcp_read": "R", "gcp_write": "Controlled", "terraform": "Controlled", "ci_cd": "Controlled", "prod": "Gate", "billing": "R", "security": "R"},
    "platform_architect": {"git": "R/W", "gcp_read": "R", "gcp_write": "Controlled", "terraform": "R/W", "ci_cd": "R", "prod": "Gate", "billing": "R", "security": "R"},
    "solution_architect": {"git": "R/W", "gcp_read": "R", "gcp_write": "-", "terraform": "R", "ci_cd": "R", "prod": "-", "billing": "R", "security": "R"},
    "security_architect": {"git": "R/W", "gcp_read": "R", "gcp_write": "Controlled", "terraform": "R", "ci_cd": "R", "prod": "Gate", "billing": "R", "security": "R/W"},
    "devops_lead":     {"git": "R/W", "gcp_read": "R", "gcp_write": "Controlled", "terraform": "R/W", "ci_cd": "R/W", "prod": "Gate", "billing": "R", "security": "R"},
    "cloud_infrastructure_engineer": {"git": "R/W", "gcp_read": "R/W", "gcp_write": "Controlled", "terraform": "R/W", "ci_cd": "R", "prod": "Gate", "billing": "R", "security": "R"},
    "cicd_engineer":    {"git": "R/W", "gcp_read": "R", "gcp_write": "Controlled", "terraform": "R/W", "ci_cd": "R/W", "prod": "Gate", "billing": "-", "security": "R"},
    "sre_observability_engineer": {"git": "R/W", "gcp_read": "R/W", "gcp_write": "Controlled", "terraform": "R", "ci_cd": "R/W", "prod": "Controlled", "billing": "R", "security": "R"},
    "finops_engineer":  {"git": "R", "gcp_read": "R", "gcp_write": "-", "terraform": "R", "ci_cd": "R", "prod": "-", "billing": "R/W", "security": "R"},
    "development_lead":  {"git": "R/W", "gcp_read": "R", "gcp_write": "-", "terraform": "R", "ci_cd": "R", "prod": "-", "billing": "-", "security": "R"},
    "frontend_engineer": {"git": "R/W", "gcp_read": "R", "gcp_write": "-", "terraform": "-", "ci_cd": "R", "prod": "-", "billing": "-", "security": "R"},
    "backend_engineer":  {"git": "R/W", "gcp_read": "R", "gcp_write": "-", "terraform": "-", "ci_cd": "R", "prod": "-", "billing": "-", "security": "R"},
    "integration_engineer": {"git": "R/W", "gcp_read": "R", "gcp_write": "-", "terraform": "-", "ci_cd": "R", "prod": "-", "billing": "-", "security": "R"},
    "ai_automation_engineer": {"git": "R/W", "gcp_read": "R", "gcp_write": "Controlled", "terraform": "R", "ci_cd": "R", "prod": "Gate", "billing": "R", "security": "R"},
    "qa_lead":        {"git": "R/W", "gcp_read": "R", "gcp_write": "-", "terraform": "R", "ci_cd": "R", "prod": "-", "billing": "-", "security": "R"},
    "test_automation_engineer": {"git": "R/W", "gcp_read": "R", "gcp_write": "Test", "terraform": "R", "ci_cd": "R/W", "prod": "-", "billing": "-", "security": "R"},
    "nfr_test_engineer": {"git": "R/W", "gcp_read": "R", "gcp_write": "Test", "terraform": "R", "ci_cd": "R/W", "prod": "-", "billing": "-", "security": "R"},
    "application_management_lead": {"git": "R", "gcp_read": "R/W", "gcp_write": "Controlled", "terraform": "R", "ci_cd": "R", "prod": "Gate", "billing": "R", "security": "R"},
    "application_support_engineer": {"git": "R", "gcp_read": "R/W", "gcp_write": "Controlled", "terraform": "R", "ci_cd": "R", "prod": "Gate", "billing": "-", "security": "R"},
    "production_reliability_engineer": {"git": "R", "gcp_read": "R/W", "gcp_write": "Controlled", "terraform": "R/W", "ci_cd": "R/W", "prod": "Gate", "billing": "R", "security": "R"},
}

# Environment permission model per Section 8
ENVIRONMENT_PERMISSIONS = {
    "development": {"create_branches": True, "build": True, "test": True, "deploy_isolated": True, "create_temporary_resources": True},
    "test": {"deploy_approved": True, "execute_automated_tests": True, "run_performance_tests": True},
    "staging": {"require_architecture_validation": True, "require_security_validation": True, "require_qa_approval": True, "deployment_gate": True},
    "production": {
        "require_product_approval": True,
        "require_security_approval": True,
        "require_qa_approval": True,
        "require_operational_readiness": True,
        "deployment_gate": True,
        "human_approval_for_destructive": True
    }
}
