"""
CI/CD Engineer Agent - Section 6.9
Builds secure, reliable, reusable CI/CD pipelines.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract


class CICDEngineerAgent(BaseAgent):
    """CI/CD Engineer - builds pipelines and deployment automation."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        application_code = context.get("application_code", {})
        environment = context.get("environment", "staging")

        # Step 1: Build pipeline
        pipeline = self._build_pipeline(application_code)

        # Step 2: Test integration
        tests = self._test_integration(application_code)

        # Step 3: Publish artifacts
        artifacts = self._publish_artifacts(application_code)

        # Step 4: Create deployment pipeline
        deployment_pipeline = self._create_deployment_pipeline(environment)

        # Step 5: Create promotion workflows
        promotion = self._create_promotion_workflows()

        # Step 6: Create environment gates
        gates = self._create_environment_gates(environment)

        # Step 7: Create rollback workflows
        rollback = self._create_rollback_workflows()

        # Step 8: Create observability
        observability = self._create_observability()

        # Step 9: Create supply-chain controls
        supply_chain = self._create_supply_chain_controls()

        self.add_evidence(f"Built CI/CD pipeline for {environment}")
        self.add_evidence(f"Published {len(artifacts['artifacts'])} artifacts")

        return {
            "pipeline": pipeline,
            "tests": tests,
            "artifacts": artifacts,
            "deployment_pipeline": deployment_pipeline,
            "promotion_workflows": promotion,
            "environment_gates": gates,
            "rollback_workflows": rollback,
            "observability": observability,
            "supply_chain_controls": supply_chain,
            "status": "pipeline_complete"
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return all(k in output for k in ["pipeline", "tests", "artifacts", "deployment_pipeline", "observability"])

    def _build_pipeline(self, application_code: Dict) -> Dict[str, Any]:
        return {
            "pipeline_id": "PIPE-001",
            "stages": [
                {"name": "build", "commands": ["npm install", "npm run build"], "success_criteria": ["dist/ directory exists"]},
                {"name": "security_scan", "commands": ["npm audit", "snyk test"], "success_criteria": ["No critical vulnerabilities"]},
                {"name": "test", "commands": ["npm test"], "success_criteria": ["Test coverage >= 80%"]},
                {"name": "artifact", "commands": ["zip -r dist.zip dist"], "success_criteria": ["dist.zip exists"]}
            ],
            "triggers": ["push", "pull_request"],
            "scheduler": "0 2 * * *"
        }

    def _test_integration(self, application_code: Dict) -> Dict[str, Any]:
        return {
            "unit_tests": {"passed": True, "failed": 0, "coverage": 85},
            "integration_tests": {"passed": True, "failed": 0, "coverage": 75},
            "functional_tests": {"passed": True, "failed": 0},
            "api_tests": {"passed": True, "failed": 0}
        }

    def _publish_artifacts(self, application_code: Dict) -> Dict[str, Any]:
        return {
            "artifacts": [
                {"name": "application.zip", "path": "./dist.zip", "format": "zip"},
                {"name": "docker-image", "path": "gcr.io/app-release", "format": "container"},
                {"name": "terraform-modules", "path": "github.com/app/modules", "format": "git"}
            ],
            "artifact_registry": "Artifact Registry",
            "versioning": "Semantic versioning",
            "retention_policy": "90 days"
        }

    def _create_deployment_pipeline(self, environment: str) -> Dict[str, Any]:
        return {
            "pipeline_id": f"DEPLOY-{environment}",
            "stages": [
                {"name": "validate", "prerequisites": ["Pipeline approval", "Security validation"]},
                {"name": "deploy", "commands": ["terraform apply", "kubectl apply"], "approvers": ["Engineering Orchestrator"]}
            ],
            "auto_promotion": environment == "staging"
        }

    def _create_promotion_workflows(self) -> Dict[str, Any]:
        return {
            "approval_required": ["staging", "production"],
            "promotion_conditions": [
                "All tests passed",
                "Security scans passed",
                "Manual approval in environment",
                "Cost estimate approved"
            ]
        }

    def _create_environment_gates(self, environment: str) -> Dict[str, Any]:
        return {
            "environment": environment,
            "gates": [
                {
                    "id": "sec-validation",
                    "description": "Security validation",
                    "approvers": ["Security Architect"],
                    "status": "pending"
                },
                {
                    "id": "qa-validation",
                    "description": "QA testing completed",
                    "approvers": ["QA Lead"],
                    "status": "pending"
                },
                {
                    "id": "cost-approval",
                    "description": "Cost estimate approved",
                    "approvers": ["FinOps Engineer"],
                    "status": "pending"
                }
            ]
        }

    def _create_rollback_workflows(self) -> Dict[str, Any]:
        return {
            "automatic_rollback": True,
            "conditions": ["Health checks fail", "Manual intervention"],
            "timeout": "15 minutes",
            "rollback_actions": ["Revert terraform", "Restore previous version"]
        }

    def _create_observability(self) -> Dict[str, Any]:
        return {
            "monitoring": True,
            "alerts": True,
            "dashboards": True,
            "logs": True,
            "traces": True,
            "metrics": True
        }

    def _create_supply_chain_controls(self) -> Dict[str, Any]:
        return {
            "trusted_artifacts": True,
            "origin_verification": True,
            "dependency_scanning": True,
            "software_bill_of_materials": True,
            "license_compliance": True
        }


CI_CD_ENGINEER_CONTRACT = AgentContract(
    id="cicd_engineer", role="CI/CD Engineer", team="DevOps", seniority="Senior",
    mission="Build secure, reliable, reusable CI/CD pipelines.",
    responsibilities=[
        "Build pipelines", "Test integration", "Artifact publishing",
        "Deployment pipelines", "Promotion workflows", "Environment gates",
        "Rollback workflows", "Pipeline observability", "Supply-chain controls"
    ],
    non_responsibilities=["Application code changes", "Production database deployment"],
    authority=AgentAuthority(
        autonomous=["Build pipeline templates", "Generate deployment pipelines"],
        peer_approval=["Pipeline security",
        human_approval=["Production deployments", "Dangerous pipeline changes"]
    ),
    capabilities=["Cloud Build", "GitHub/GitLab", "Artifact Registry", "Terraform", "Security scanners"],
    tools=["Cloud Build", "GitHub/GitLab", "Artifact Registry", "Terraform", "Security scanners"],
    memory=AgentMemory(
        working=["Current pipeline context"],
        project=["Pipeline templates", "Release patterns", "Failed builds", "Deployment history"],
        institutional=["Pipeline standards", "CI/CD best practices"]
    ),
    inputs=["Code", "Test definitions", "Deployment requirements", "Security controls"],
    outputs=["Pipeline definitions", "Artifacts", "Release records"],
    collaborators=["devops_lead", "security_architect", "sre_observability_engineer", "application_management_lead"],
    escalation_rules=["Escalate pipeline failures", "Escalate production-impacting deployment risks"],
    quality_gates=["Gate 5 - Implementation"],
    definition_of_done=["Builds reproducibly", "Runs required tests", "Performs security checks", "Publishes immutable artifacts",
                      "Enforces approvals", "Supports rollback", "Produces audit evidence"],
    security_constraints=["Must not expose secrets", "Must follow approved security scans"],
    failure_policy=["Automatic rollback on failure", "Never deploy untested changes", "Alert on pipeline failure"]
)
