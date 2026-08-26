"""
Platform Architect Agent - Section 6.4
Owns enterprise GCP platform and Landing Zone architecture.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory


class PlatformArchitectAgent(BaseAgent):
    """Platform Architect - designs GCP Landing Zone and platform architecture."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        environment_type = context.get("environment_type", "non-production")
        region = context.get("region", "us-central1")

        # Step 1: Define resource hierarchy
        resource_hierarchy = self._define_resource_hierarchy(environment_type)

        # Step 2: Design network architecture
        network_design = self._design_network(environment_type, region)

        # Step 3: Define IAM model
        iam_model = self._define_iam_model(environment_type)

        # Step 4: Define organization policies
        org_policies = self._define_org_policies()

        # Step 5: Design observability foundation
        observability = self._design_observability()

        # Step 6: Define Terraform module structure
        terraform_modules = self._define_terraform_modules()

        # Record decisions
        self.record_decision({
            "type": "platform_architecture_designed",
            "environment": environment_type,
            "region": region,
            "components": len(network_design["subnets"]) + len(iam_model["roles"])
        })

        self.add_evidence(f"Designed resource hierarchy for {environment_type}")
        self.add_evidence(f"Network design includes {len(network_design['subnets'])} subnets")
        self.add_evidence(f"IAM model defines {len(iam_model['roles'])} custom roles")

        return {
            "resource_hierarchy": resource_hierarchy,
            "network_design": network_design,
            "iam_model": iam_model,
            "org_policies": org_policies,
            "observability": observability,
            "terraform_modules": terraform_modules,
            "high_availability": self._define_ha_strategy(),
            "disaster_recovery": self._define_dr_strategy(environment_type),
            "status": "platform_designed"
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate Definition of Done per Section 6.4."""
        required = ["resource_hierarchy", "network_design", "iam_model", "org_policies",
                    "observability", "terraform_modules"]
        return all(k in output for k in required)

    def _define_resource_hierarchy(self, env_type: str) -> Dict[str, Any]:
        """Define GCP resource hierarchy."""
        return {
            "organization": "organizations/123456",
            "folders": {
                "landing_zone": "folders/landing-zone",
                "environments": {
                    "production": "folders/prod",
                    "non_production": "folders/non-prod",
                    "development": "folders/dev"
                }
            },
            "projects": {
                f"{env_type}-app-{i}": f"projects/{env_type}-app-{i}"
                for i in range(1, 4)
            },
            "project_labels": {
                "environment": env_type,
                "managed_by": "platform_architect",
                "landing_zone": "v1.0"
            }
        }

    def _design_network(self, env_type: str, region: str) -> Dict[str, Any]:
        """Design Shared VPC and network topology."""
        return {
            "vpc_type": "shared_vpc",
            "host_project": f"projects/{env_type}-network-host",
            "topology": "hub_and_spoke",
            "regions": [region],
            "subnets": [
                {
                    "name": f"{env_type}-subnet-app",
                    "cidr": "10.10.0.0/20",
                    "region": region,
                    "purpose": "Application workloads",
                    "flow_logs": True
                },
                {
                    "name": f"{env_type}-subnet-data",
                    "cidr": "10.10.16.0/20",
                    "region": region,
                    "purpose": "Data services",
                    "private_google_access": True
                },
                {
                    "name": f"{env_type}-subnet-mgmt",
                    "cidr": "10.10.32.0/20",
                    "region": region,
                    "purpose": "Management services",
                    "flow_logs": True
                }
            ],
            "firewall_rules": [
                {
                    "name": "allow-internal",
                    "direction": "INGRESS",
                    "source_ranges": ["10.10.0.0/16"],
                    "allowed": ["tcp:0-65535", "udp:0-65535"]
                },
                {
                    "name": "deny-all-ingress",
                    "direction": "INGRESS",
                    "priority": 65000,
                    "denied": ["all"]
                }
            ],
            "cloud_nat": {
                "enabled": True,
                "type": "auto",
                "min_ports_per_vm": 64
            },
            "private_google_access": True
        }

    def _define_iam_model(self, env_type: str) -> Dict[str, Any]:
        """Define IAM model with least privilege."""
        return {
            "principle": "least_privilege",
            "service_accounts": [
                {
                    "name": f"{env_type}-app-sa",
                    "purpose": "Application runtime",
                    "iam_bindings": [
                        "roles/cloudsql.client",
                        "roles/storage.objectViewer"
                    ]
                },
                {
                    "name": f"{env_type}-cicd-sa",
                    "purpose": "CI/CD pipeline",
                    "iam_bindings": [
                        "roles/run.admin",
                        "roles/artifactregistry.writer"
                    ]
                },
                {
                    "name": f"{env_type}-terraform-sa",
                    "purpose": "Terraform execution",
                    "iam_bindings": [
                        "roles/editor",
                        "roles/iam.serviceAccountUser"
                    ]
                }
            ],
            "workload_identity": True,
            "custom_roles": [
                {
                    "name": f"{env_type}_app_developer",
                    "permissions": [
                        "cloudsql.instances.connect",
                        "storage.objects.get",
                        "logging.logEntries.create"
                    ]
                }
            ]
        }

    def _define_org_policies(self) -> List[Dict[str, Any]]:
        """Define organization policy constraints."""
        return [
            {
                "constraint": "constraints/compute.disableInternetNetworkEndpointGroup",
                "enforced": True
            },
            {
                "constraint": "constraints/compute.requireShieldedVm",
                "enforced": True
            },
            {
                "constraint": "constraints/iam.allowedPolicyMemberDomains",
                "enforced": True
            },
            {
                "constraint": "constraints/sql.restrictPublicIp",
                "enforced": True
            },
            {
                "constraint": "constraints/storage.uniformBucketLevelAccess",
                "enforced": True
            },
            {
                "constraint": "constraints/gcp.resourceLocations",
                "allowed_values": ["in:us-locations"]
            }
        ]

    def _design_observability(self) -> Dict[str, Any]:
        """Design central logging and monitoring."""
        return {
            "central_logging": {
                "enabled": True,
                "log_sinks": [
                    {
                        "name": "central-audit-sink",
                        "destination": "bigquery.googleapis.com/projects/central-logs",
                        "filter": "logName:cloudaudit.googleapis.com"
                    },
                    {
                        "name": "central-archive-sink",
                        "destination": "storage.googleapis.com/log-archive",
                        "retention_days": 365
                    }
                ]
            },
            "central_monitoring": {
                "enabled": True,
                "notification_channels": ["email", "pagerduty", "slack"]
            },
            "metrics_scope": "all_projects",
            "uptime_checks": True
        }

    def _define_terraform_modules(self) -> Dict[str, Any]:
        """Define Terraform module structure."""
        return {
            "module_structure": {
                "network": "infrastructure/terraform/modules/network",
                "project": "infrastructure/terraform/modules/project",
                "iam": "infrastructure/terraform/modules/iam",
                "monitoring": "infrastructure/terraform/modules/monitoring",
                "security": "infrastructure/terraform/modules/security"
            },
            "remote_state": {
                "backend": "gcs",
                "bucket": "terraform-state-bucket",
                "encryption": "customer_managed_key"
            },
            "versioning": "terraform >= 1.5",
            "providers": ["google", "google-beta"]
        }

    def _define_ha_strategy(self) -> Dict[str, Any]:
        """Define high availability strategy."""
        return {
            "multi_zone": True,
            "load_balancing": "Global HTTPS Load Balancer",
            "auto_scaling": True,
            "health_checks": True,
            "sla_target": "99.9%"
        }

    def _define_dr_strategy(self, env_type: str) -> Dict[str, Any]:
        """Define disaster recovery strategy."""
        return {
            "rpo_minutes": 60 if env_type == "production" else 1440,
            "rto_minutes": 240 if env_type == "production" else 1440,
            "backup_strategy": "automated_daily",
            "cross_region_replication": env_type == "production",
            "disaster_recovery_region": "us-east1"
        }


PLATFORM_ARCHITECT_CONTRACT = AgentContract(
    id="platform_architect",
    role="Platform Architect",
    team="Architecture",
    mission="Own enterprise GCP platform and Landing Zone architecture.",
    seniority="Principal",
    responsibilities=[
        "Organization hierarchy",
        "Folder structure",
        "Project structure",
        "Shared VPC",
        "Networking",
        "IAM platform design",
        "Organization policies",
        "Service perimeter strategy",
        "DNS",
        "Hybrid connectivity",
        "Central logging",
        "Monitoring foundations",
        "Platform availability",
        "Terraform architecture",
        "Platform standards",
        "Environment strategy"
    ],
    non_responsibilities=[
        "Application code architecture",
        "Security policy approval",
        "Implementation details"
    ],
    authority=AgentAuthority(
        autonomous=["Architecture recommendations within approved standards"],
        peer_approval=["Security-sensitive platform designs require Security Architect review"],
        human_approval=["Organization-level policy changes", "Material platform exceptions"]
    ),
    capabilities=[
        "GCP architecture",
        "Networking",
        "IAM",
        "Terraform",
        "Cloud governance",
        "Landing Zones",
        "Resilience"
    ],
    tools=["GCP APIs", "Terraform", "Git", "Cloud Asset Inventory", "Cloud Logging", "Monitoring", "Architecture repository"],
    memory=AgentMemory(
        working=["Current architecture design context"],
        project=["Landing Zone blueprint", "Platform standards", "Network topology", "IAM model", "ADRs", "Approved exceptions"],
        institutional=["GCP architecture patterns", "Industry best practices"]
    ),
    inputs=["Requirements", "Solution Architecture", "Security requirements", "FinOps constraints"],
    outputs=["Platform HLD/LLD", "Network design", "Project hierarchy", "IAM design", "Terraform modules", "Platform standards", "ADRs"],
    collaborators=["solution_architect", "security_architect", "devops_lead", "finops_engineer", "sre_observability_engineer"],
    escalation_rules=["Escalate architectural conflicts with material security, cost, or availability impact"],
    quality_gates=["Gate 2 - Architecture"],
    definition_of_done=[
        "Resource hierarchy is defined",
        "Network design is defined",
        "IAM model is defined",
        "Security controls are mapped",
        "Terraform implementation approach exists",
        "Observability is defined",
        "Cost implications are understood",
        "Required architecture review passes"
    ],
    security_constraints=["Must follow least privilege", "Must validate against security policies"],
    failure_policy=["Escalate security conflicts", "Request Security Architect review for sensitive designs"]
)
