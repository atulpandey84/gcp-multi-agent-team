"""
Product Owner Agent - Section 6.1
Owns product vision, business value, scope, prioritization, acceptance, and stakeholder alignment.
"""

from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentMessage, QualityGateResult


class ProductOwnerAgent(BaseAgent):
    """Product Owner - translates business objectives into product requirements."""
    
    def __init__(self, contract: AgentContract):
        super().__init__(contract)
    
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute product owner responsibilities."""
        objective = task.objective
        
        # Step 1: Identify requirements from objective
        requirements = self._analyze_business_objective(objective)
        
        # Step 2: Define acceptance criteria
        acceptance_criteria = self._define_acceptance_criteria(requirements)
        
        # Step 3: Prioritize and create epics/stories
        epics = self._create_epics_and_stories(requirements)
        
        # Step 4: Identify dependencies and constraints
        dependencies = self._identify_dependencies(requirements, context)
        
        # Step 5: Record decisions
        self.record_decision({
            "type": "requirements_defined",
            "requirements": requirements,
            "acceptance_criteria": acceptance_criteria,
            "epics": epics
        })
        
        # Add evidence
        self.add_evidence(f"Analyzed objective: {objective}")
        self.add_evidence(f"Derived {len(requirements)} requirements")
        self.add_evidence(f"Created {len(epics)} epics with acceptance criteria")
        
        return {
            "requirements": requirements,
            "acceptance_criteria": acceptance_criteria,
            "epics": epics,
            "dependencies": dependencies,
            "priority": self._determine_priority(requirements),
            "status": "requirements_complete"
        }
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output meets Definition of Done per Section 6.1."""
        checks = [
            "requirements" in output and len(output["requirements"]) > 0,
            "acceptance_criteria" in output and len(output["acceptance_criteria"]) > 0,
            "epics" in output and len(output["epics"]) > 0,
            all("business_objective" in req for req in output.get("requirements", [])),
            all("testable" in str(ac).lower() for ac in output.get("acceptance_criteria", [])),
            "priority" in output
        ]
        return all(checks)
    
    def _analyze_business_objective(self, objective: str) -> List[Dict[str, Any]]:
        """Translate business objective into structured requirements."""
        # In production, this would use LLM with structured output
        # For now, return structured requirements
        return [
            {
                "id": "REQ-001",
                "title": "GCP Landing Zone Application Environment",
                "description": "Provision a new non-production GCP application environment using approved Landing Zone",
                "business_objective": "Enable development teams to deploy applications on standardized, secure GCP infrastructure",
                "priority": "high",
                "type": "functional"
            },
            {
                "id": "REQ-002",
                "title": "Security Controls Implementation",
                "description": "Implement all required security controls per Security Architect specifications",
                "business_objective": "Ensure compliance with organizational security policies",
                "priority": "critical",
                "type": "non-functional"
            },
            {
                "id": "REQ-003",
                "title": "Cost Optimization",
                "description": "Implement FinOps recommendations for cost-effective resource usage",
                "business_objective": "Minimize cloud spend while maintaining required capabilities",
                "priority": "high",
                "type": "non-functional"
            },
            {
                "id": "REQ-004",
                "title": "Operational Readiness",
                "description": "Ensure monitoring, alerting, runbooks, and support model are in place",
                "business_objective": "Enable reliable production operations from day one",
                "priority": "high",
                "type": "non-functional"
            }
        ]
    
    def _define_acceptance_criteria(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define testable acceptance criteria for each requirement."""
        criteria = []
        for req in requirements:
            if req["id"] == "REQ-001":
                criteria.extend([
                    {"requirement_id": "REQ-001", "criterion": "GCP project created in correct folder hierarchy", "testable": True},
                    {"requirement_id": "REQ-001", "criterion": "Shared VPC configured with correct subnets", "testable": True},
                    {"requirement_id": "REQ-001", "criterion": "IAM roles assigned per platform standards", "testable": True},
                    {"requirement_id": "REQ-001", "criterion": "Terraform plan passes validation and security checks", "testable": True}
                ])
            elif req["id"] == "REQ-002":
                criteria.extend([
                    {"requirement_id": "REQ-002", "criterion": "Security Architect approval obtained", "testable": True},
                    {"requirement_id": "REQ-002", "criterion": "No critical vulnerabilities in infrastructure", "testable": True},
                    {"requirement_id": "REQ-002", "criterion": "Secrets managed via Secret Manager", "testable": True},
                    {"requirement_id": "REQ-002", "criterion": "Audit logging enabled for all resources", "testable": True}
                ])
            elif req["id"] == "REQ-003":
                criteria.extend([
                    {"requirement_id": "REQ-003", "criterion": "FinOps cost estimate within budget", "testable": True},
                    {"requirement_id": "REQ-003", "criterion": "Resource sizing follows right-sizing recommendations", "testable": True},
                    {"requirement_id": "REQ-003", "criterion": "Commitment discounts applied where applicable", "testable": True}
                ])
            elif req["id"] == "REQ-004":
                criteria.extend([
                    {"requirement_id": "REQ-004", "criterion": "SLOs defined for all critical services", "testable": True},
                    {"requirement_id": "REQ-004", "criterion": "Dashboards and alerts deployed", "testable": True},
                    {"requirement_id": "REQ-004", "criterion": "Runbooks documented and accessible", "testable": True},
                    {"requirement_id": "REQ-004", "criterion": "Support escalation paths defined", "testable": True}
                ])
        return criteria
    
    def _create_epics_and_stories(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create epics and user stories from requirements."""
        return [
            {
                "id": "EPIC-001",
                "title": "GCP Landing Zone Environment Provisioning",
                "description": "Provision complete application environment using approved Terraform modules",
                "requirements": ["REQ-001", "REQ-002", "REQ-003"],
                "stories": [
                    {"id": "STORY-001", "title": "Create GCP project and folder structure", "points": 5},
                    {"id": "STORY-002", "title": "Configure Shared VPC and subnets", "points": 8},
                    {"id": "STORY-003", "title": "Implement IAM bindings and service accounts", "points": 5},
                    {"id": "STORY-004", "title": "Deploy Terraform modules for environment", "points": 13},
                    {"id": "STORY-005", "title": "Validate infrastructure with Terratest", "points": 8}
                ]
            },
            {
                "id": "EPIC-002",
                "title": "Security Hardening and Compliance",
                "description": "Implement and validate all security controls",
                "requirements": ["REQ-002"],
                "stories": [
                    {"id": "STORY-006", "title": "Configure VPC Service Controls", "points": 5},
                    {"id": "STORY-007", "title": "Implement secret management", "points": 3},
                    {"id": "STORY-008", "title": "Enable security scanning in CI/CD", "points": 5},
                    {"id": "STORY-009", "title": "Document security exceptions (if any)", "points": 2}
                ]
            },
            {
                "id": "EPIC-003",
                "title": "Observability and Operations Setup",
                "description": "Deploy monitoring, alerting, and operational documentation",
                "requirements": ["REQ-004"],
                "stories": [
                    {"id": "STORY-010", "title": "Define SLOs and error budgets", "points": 5},
                    {"id": "STORY-011", "title": "Deploy Cloud Monitoring dashboards", "points": 5},
                    {"id": "STORY-012", "title": "Configure alerting policies", "points": 5},
                    {"id": "STORY-013", "title": "Create operational runbooks", "points": 8},
                    {"id": "STORY-014", "title": "Conduct operational readiness review", "points": 3}
                ]
            }
        ]
    
    def _identify_dependencies(self, requirements: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify cross-team and external dependencies."""
        return [
            {"id": "DEP-001", "description": "Platform Architect must approve network design", "team": "Architecture", "status": "pending"},
            {"id": "DEP-002", "description": "Security Architect must approve threat model", "team": "Architecture", "status": "pending"},
            {"id": "DEP-003", "description": "FinOps must approve cost model", "team": "DevOps", "status": "pending"},
            {"id": "DEP-004", "description": "DevOps Lead must approve Terraform modules", "team": "DevOps", "status": "pending"},
            {"id": "DEP-005", "description": "SRE must approve monitoring design", "team": "DevOps", "status": "pending"},
            {"id": "DEP-006", "description": "Application Management must approve runbooks", "team": "Application Management", "status": "pending"}
        ]
    
    def _determine_priority(self, requirements: List[Dict[str, Any]]) -> str:
        """Determine overall priority based on requirements."""
        if any(r["priority"] == "critical" for r in requirements):
            return "critical"
        elif any(r["priority"] == "high" for r in requirements):
            return "high"
        return "medium"


# Agent Contract Definition
PRODUCT_OWNER_CONTRACT = AgentContract(
    id="product_owner",
    role="Product Owner",
    team="Product",
    mission="Own product vision, business value, scope, prioritization, acceptance, and stakeholder alignment.",
    seniority="Principal",
    responsibilities=[
        "Translate business objectives into product requirements",
        "Maintain product backlog",
        "Define epics and user stories",
        "Prioritize work",
        "Define acceptance criteria",
        "Define business outcomes",
        "Manage scope",
        "Participate in release planning",
        "Validate delivered functionality",
        "Resolve business-priority conflicts",
        "Maintain product roadmap"
    ],
    non_responsibilities=[
        "Detailed technical architecture",
        "Security approval",
        "Infrastructure implementation",
        "Code approval",
        "Production deployment"
    ],
    authority=AgentAuthority(
        autonomous=[
            "Backlog prioritization",
            "Story clarification",
            "Business acceptance criteria",
            "Scope sequencing"
        ],
        peer_approval=[
            "Major technical trade-offs with Solution Architect",
            "Major delivery changes with Project Manager"
        ],
        human_approval=[
            "Major budget increases",
            "Material business scope changes",
            "External contractual commitments"
        ]
    ),
    capabilities=[
        "Requirements engineering",
        "Product management",
        "Stakeholder analysis",
        "Prioritization",
        "Acceptance criteria",
        "Business case analysis"
    ],
    tools=[
        "Project management system",
        "Git repository read access",
        "Documentation system",
        "Requirements repository",
        "Cost reports",
        "Architecture summaries"
    ],
    memory=AgentMemory(
        working=["Current requirement and acceptance context"],
        project=["Product roadmap", "backlog", "accepted requirements", "business decisions"],
        institutional=["Product standards and historical priorities"]
    ),
    inputs=["Business requirements", "Stakeholder requests", "Operational feedback", "Architecture constraints", "Cost information", "Security constraints"],
    outputs=["Epics", "User stories", "Acceptance criteria", "Product roadmap", "Priorities", "Business decisions"],
    collaborators=["project_manager", "solution_architect", "engineering_orchestrator", "qa_lead", "application_management_lead"],
    escalation_rules=["Escalate to human stakeholders when business priority cannot be determined objectively or when scope/budget changes materially"],
    quality_gates=["Gate 1 - Requirements"],
    definition_of_done=[
        "Business objective is explicit",
        "Acceptance criteria are testable",
        "Priority is established",
        "Dependencies are identified",
        "Relevant architecture/security constraints are known",
        "Requirement is accepted by the responsible delivery workflow"
    ],
    security_constraints=["Must not expose business-sensitive information", "Must validate requirements against security policies"],
    failure_policy=["Request clarification for ambiguous requirements", "Escalate unresolvable priority conflicts", "Never assume requirements without stakeholder confirmation"]
)