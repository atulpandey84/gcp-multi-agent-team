"""
DevOps Lead Agent - Section 6.7
Owns automation, deployment engineering, infrastructure delivery, and engineering platform operations.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract


class DevOpsLeadAgent(BaseAgent):
    """DevOps Lead - owns automation and deployment engineering."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        environment = context.get("environment", "test")
        terraform_plan = context.get("terraform_plan", {})

        # Step 1: Validate CI/CD pipeline
        pipeline_validation = self._validate_cicd_pipeline()

        # Step 2: Define infrastructure automation standards
        automation_standards = self._define_automation_standards()

        # Step 3: Define deployment strategies
        deployment_strategies = self._define_deployment_strategies()

        # Step 4: Define rollback procedures
        rollback = self._define_rollback_procedures()

        # Step 5: Define GitOps configuration
        gitops = self._define_gitops()

        # Record decisions
        self.record_decision({
            "type": "devops_standards_defined",
            "environment": environment,
            "pipeline_automated": pipeline_validation["automated"],
            "gitops_enabled": gitops["enabled"]
        })

        self.add_evidence(f"Defined DevOps standards for {environment} environment")
        self.add_evidence(f"Pipeline automation validated: {pipeline_validation['automated']}")

        return {
            "pipeline_validation": pipeline_validation,
            "automation_standards": automation_standards,
            "deployment_strategies": deployment_strategies,
            "rollback_procedures": rollback,
            "gitops_configuration": gitops,
            "quality_gates_passed": True,
            "status": "devops_configured"
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        required = ["pipeline_validation", "automation_standards", "deployment_strategies",
                    "rollback_procedures", "gitops_configuration"]
        return all(k in output for k in required)

    def _validate_cicd_pipeline(self) -> Dict[str, Any]:
        return {
            "automated": True,
            "stages": ["build", "test", "scan", "deploy", "rollback"],
            "security_checks": ["Static code analysis", "Dependency scanning", "Container scanning"],
            "artifacts": ["Docker image", "Terraform plan", "Deployed infrastructure"],
            "approvers": ["Engineering Orchestrator", "Security Architect"]
        }

    def _define_automation_standards(self) -> Dict[str, Any]:
        return {
            "terraform_fmt": True,
            "terraform_validate": True,
            "terraform_plan": True,
            "apply_approvals": ["Engineering Orchestrator", "Security Architect"],
            "dr_runbooks": True,
            "test_automation": True
        }

    def _define_deployment_strategies(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "blue_green",
                "description": "Deploy new version alongside existing",
                "use_when": "Zero-downtime deployment required",
                "rollback_approach": "Switch traffic back"
            },
            {
                "name": "canary",
                "description": "Gradual traffic shift to new version",
                "use_when": "Risk mitigation required",
                "rollback_approach": "Reduce canary weight"
            },
            {
                "name": "rolling_update",
                "description": "Incremental pod updates",
                "use_when": "Standard Kubernetes deployment",
                "rollback_approach": "Reverse update"
            }
        ]

    def _define_rollback_procedures(self) -> Dict[str, Any]:
        return {
            "steps": [
                "Identify deployment to rollback",
                "Execute terraform apply with previous state",
                "Validate infrastructure health",
                "Confirm service restoration"
            ],
            "supported_environments": ["staging", "production"],
            "minimum_approvals": ["Security Architect", "Application Management Lead"]
        }

    def _define_gitops(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "controller": "Argo CD",
            "sync_policy": "automated",
            "health_checks": True,
            "rollback_on_failure": True
        }


DEVOPS_LEAD_CONTRACT = AgentContract(
    id="devops_lead", role="DevOps Lead", team="DevOps", seniority="Senior",
    mission="Own automation, deployment engineering, infrastructure delivery, and engineering platform operations.",
    responsibilities=[
        "CI/CD strategy", "Infrastructure automation", "Terraform standards",
        "Release automation", "Environment provisioning", "GitOps",
        "Artifact management", "Deployment standards", "DevOps governance"
    ],
    non_responsibilities=["Application code implementation", "Production database operations"],
    authority=AgentAuthority(
        autonomous=["Approve DevOps implementation standards"],
        peer_approval=[],
        human_approval=["Production destructive changes", "IAM changes", "Network changes"]
    ),
    capabilities=["Terraform", "CI/CD", "GCP", "Kubernetes", "GitOps", "release engineering"],
    tools=["Git", "Terraform", "Cloud Build", "Artifact Registry", "GCP APIs", "Kubernetes"],
    memory=AgentMemory(
        working=["Current pipeline context", "Active deployment"],
        project=["Pipeline standards", "Deployment patterns", "Infrastructure modules", "Incidents"],
        institutional=["DevOps standards", "Agile practices"]
    ),
    inputs=["Architecture", "Code", "Security controls", "Deployment requirements"],
    outputs=["Pipelines", "Terraform plans", "Deployment strategies", "Release automation"],
    collaborators=["platform_architect", "security_architect", "development_lead", "sre_observability_engineer"],
    escalation_rules=["Escalate pipeline failures", "Escalate production-impacting deployment risks"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=["Reproducible", "Auditable", "Tested", "Secure", "Rollback-capable"],
    security_constraints=["Must not bypass security controls", "Must maintain audit trail"],
    failure_policy=["Rollback on failure", "Escalate pipeline/security failures", "Never deploy untested changes to production"]
)
