https://integrate.api.nvidia.com/v1"""
Project Manager Agent - Section 6.2
Owns delivery coordination, planning, dependency management, risk management, milestones, and delivery reporting.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseAgent, Task, AgentContract, AgentMessage, AgentAuthority, AgentMemory, TaskStatus


class ProjectManagerAgent(BaseAgent):
    """Project Manager - coordinates delivery and tracks progress."""
    
    def __init__(self, contract: AgentContract):
        super().__init__(contract)
    
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project management responsibilities."""
        epics = context.get("epics", [])
        requirements = context.get("requirements", [])
        
        # Step 1: Create delivery plan
        delivery_plan = self._create_delivery_plan(epics, requirements)
        
        # Step 2: Break into milestones
        milestones = self._create_milestones(delivery_plan)
        
        # Step 3: Track dependencies
        dependency_map = self._track_dependencies(requirements, context.get("dependencies", []))
        
        # Step 4: Create RAID log (Risks, Assumptions, Issues, Decisions)
        raid_log = self._create_raid_log(context)
        
        # Step 5: Create sprint plan
        sprint_plan = self._create_sprint_plan(milestones)
        
        # Record decisions
        self.record_decision({
            "type": "delivery_plan_created",
            "milestones": len(milestones),
            "sprints": len(sprint_plan),
            "dependencies": len(dependency_map)
        })
        
        self.add_evidence(f"Created delivery plan with {len(milestones)} milestones")
        self.add_evidence(f"Tracked {len(dependency_map)} dependencies")
        self.add_evidence(f"Identified {len(raid_log['risks'])} risks")
        
        return {
            "delivery_plan": delivery_plan,
            "milestones": milestones,
            "sprint_plan": sprint_plan,
            "dependency_map": dependency_map,
            "raid_log": raid_log,
            "status": "planning_complete"
        }
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output meets Definition of Done per Section 6.2."""
        checks = [
            "delivery_plan" in output,
            "milestones" in output and len(output["milestones"]) > 0,
            "sprint_plan" in output,
            "dependency_map" in output,
            "raid_log" in output
        ]
        return all(checks)
    
    def _create_delivery_plan(self, epics: List[Dict], requirements: List[Dict]) -> Dict[str, Any]:
        """Create comprehensive delivery plan."""
        total_story_points = sum(
            sum(story["points"] for story in epic.get("stories", []))
            for epic in epics
        )
        
        # Estimate 8 hours per story point, 40 hours per week
        weeks_estimated = (total_story_points * 8) / 40
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=weeks_estimated)
        
        return {
            "id": "PLAN-001",
            "title": "GCP Landing Zone Application Environment Provisioning",
            "total_story_points": total_story_points,
            "estimated_weeks": weeks_estimated,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "epics": [e["id"] for e in epics],
            "requirements": [r["id"] for r in requirements]
        }
    
    def _create_milestones(self, delivery_plan: Dict) -> List[Dict[str, Any]]:
        """Break delivery plan into milestones."""
        return [
            {
                "id": "M1",
                "title": "Requirements & Architecture Approval",
                "epics": ["EPIC-001", "EPIC-002"],
                "target_date": (datetime.now() + timedelta(weeks=1)).isoformat(),
                "status": "planned",
                "stories": ["STORY-001", "STORY-002", "STORY-006"],
                "dependencies": ["Architecture Review", "Security Review"],
                "deliverables": [
                    "Approved requirements document",
                    "Approved architecture design",
                    "Approved threat model"
                ]
            },
            {
                "id": "M2",
                "title": "Infrastructure Foundation",
                "epics": ["EPIC-001"],
                "target_date": (datetime.now() + timedelta(weeks=3)).isoformat(),
                "status": "planned",
                "stories": ["STORY-002", "STORY-003", "STORY-004"],
                "dependencies": ["M1 completion"],
                "deliverables": [
                    "GCP project created",
                    "Shared VPC configured",
                    "IAM implemented",
                    "Terraform modules deployed"
                ]
            },
            {
                "id": "M3",
                "title": "Security & Compliance",
                "epics": ["EPIC-002"],
                "target_date": (datetime.now() + timedelta(weeks=4)).isoformat(),
                "status": "planned",
                "stories": ["STORY-006", "STORY-007", "STORY-008", "STORY-009"],
                "dependencies": ["M2 completion"],
                "deliverables": [
                    "VPC Service Controls configured",
                    "Secret management implemented",
                    "Security scanning in CI/CD",
                    "Security approval obtained"
                ]
            },
            {
                "id": "M4",
                "title": "Observability & Operations",
                "epics": ["EPIC-003"],
                "target_date": (datetime.now() + timedelta(weeks=5)).isoformat(),
                "status": "planned",
                "stories": ["STORY-010", "STORY-011", "STORY-012", "STORY-013", "STORY-014"],
                "dependencies": ["M2 completion"],
                "deliverables": [
                    "SLOs defined",
                    "Dashboards deployed",
                    "Alerts configured",
                    "Runbooks created",
                    "Operational readiness approved"
                ]
            },
            {
                "id": "M5",
                "title": "Testing & Validation",
                "epics": ["EPIC-001", "EPIC-002", "EPIC-003"],
                "target_date": (datetime.now() + timedelta(weeks=6)).isoformat(),
                "status": "planned",
                "stories": ["STORY-005"],
                "dependencies": ["M2", "M3", "M4 completion"],
                "deliverables": [
                    "Terratest validation passed",
                    "Security tests passed",
                    "NFR tests passed",
                    "All quality gates cleared"
                ]
            },
            {
                "id": "M6",
                "title": "Production Release",
                "epics": ["EPIC-001", "EPIC-002", "EPIC-003"],
                "target_date": (datetime.now() + timedelta(weeks=7)).isoformat(),
                "status": "planned",
                "dependencies": ["M5 completion", "Human approval for production"],
                "deliverables": [
                    "Human approval obtained",
                    "Deployment to production",
                    "Post-deployment validation",
                    "Go-live announcement"
                ]
            }
        ]
    
    def _track_dependencies(self, requirements: List[Dict], existing_deps: List[Dict]) -> Dict[str, Any]:
        """Create dependency map for all work items."""
        dependency_map = {}
        
        for req in requirements:
            req_deps = [d for d in existing_deps if req["id"] in str(d)]
            dependency_map[req["id"]] = {
                "required": req_deps,
                "blocked_by": [d["id"] for d in req_deps if d.get("status") == "blocked"],
                "ready": all(d.get("status") != "blocked" for d in req_deps)
            }
        
        return dependency_map
    
    def _create_raid_log(self, context: Dict[str, Any]) -> Dict[str, List]:
        """Create RAID log (Risks, Assumptions, Issues, Decisions)."""
        return {
            "risks": [
                {
                    "id": "RISK-001",
                    "description": "Security Architect review may identify additional controls",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Schedule security review early in sprint 1",
                    "owner": "security_architect"
                },
                {
                    "id": "RISK-002",
                    "description": "Terraform module compatibility issues with existing infrastructure",
                    "probability": "low",
                    "impact": "high",
                    "mitigation": "Early integration testing in development environment",
                    "owner": "cloud_infrastructure_engineer"
                },
                {
                    "id": "RISK-003",
                    "description": "Cost estimates may exceed budget with current resource sizing",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "FinOps review before architecture finalization",
                    "owner": "finops_engineer"
                }
            ],
            "assumptions": [
                {
                    "id": "ASSUM-001",
                    "description": "Existing Landing Zone modules are approved and available",
                    "confidence": "high"
                },
                {
                    "id": "ASSUM-002",
                    "description": "GCP project quota is available for new environment",
                    "confidence": "high"
                },
                {
                    "id": "ASSUM-003",
                    "description": "Network connectivity to existing VPC is available",
                    "confidence": "medium"
                }
            ],
            "issues": [],
            "decisions": [
                {
                    "id": "DEC-001",
                    "description": "Use Terraform for all infrastructure provisioning",
                    "rationale": "Industry standard, version control, auditability",
                    "approved_by": "platform_architect"
                },
                {
                    "id": "DEC-002",
                    "description": "Implement GitOps deployment pattern",
                    "rationale": "Reproducible, auditable deployments",
                    "approved_by": "devops_lead"
                }
            ]
        }
    
    def _create_sprint_plan(self, milestones: List[Dict]) -> List[Dict[str, Any]]:
        """Break milestones into sprints."""
        return [
            {
                "id": "SPRINT-1",
                "title": "Foundation & Architecture",
                "duration_weeks": 2,
                "milestones": ["M1"],
                "goals": [
                    "Finalize requirements with Product Owner",
                    "Complete architecture design",
                    "Obtain security and FinOps approval",
                    "Set up development environment"
                ],
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(weeks=2)).isoformat()
            },
            {
                "id": "SPRINT-2",
                "title": "Infrastructure Core",
                "duration_weeks": 2,
                "milestones": ["M2"],
                "goals": [
                    "Deploy GCP project and VPC",
                    "Implement IAM configuration",
                    "Deploy base Terraform modules",
                    "Complete infrastructure testing"
                ],
                "start_date": (datetime.now() + timedelta(weeks=2)).isoformat(),
                "end_date": (datetime.now() + timedelta(weeks=4)).isoformat()
            },
            {
                "id": "SPRINT-3",
                "title": "Security & Observability",
                "duration_weeks": 2,
                "milestones": ["M3", "M4"],
                "goals": [
                    "Implement security controls",
                    "Configure monitoring and alerting",
                    "Create operational runbooks",
                    "Complete security review"
                ],
                "start_date": (datetime.now() + timedelta(weeks=4)).isoformat(),
                "end_date": (datetime.now() + timedelta(weeks=6)).isoformat()
            },
            {
                "id": "SPRINT-4",
                "title": "Validation & Release",
                "duration_weeks": 1,
                "milestones": ["M5", "M6"],
                "goals": [
                    "Complete all testing phases",
                    "Obtain quality gate approvals",
                    "Execute production deployment",
                    "Conduct post-deployment validation"
                ],
                "start_date": (datetime.now() + timedelta(weeks=6)).isoformat(),
                "end_date": (datetime.now() + timedelta(weeks=7)).isoformat()
            }
        ]


# Agent Contract Definition
PROJECT_MANAGER_CONTRACT = AgentContract(
    id="project_manager",
    role="Project Manager",
    team="Delivery",
    mission="Own delivery coordination, planning, dependency management, risk management, milestones, and delivery reporting.",
    seniority="Senior",
    responsibilities=[
        "Create delivery plans",
        "Break work into milestones",
        "Track dependencies",
        "Track risks, assumptions, issues, and decisions",
        "Coordinate teams",
        "Track progress",
        "Identify schedule risks",
        "Manage release planning",
        "Produce status reports",
        "Coordinate ceremonies",
        "Maintain delivery governance"
    ],
    non_responsibilities=[
        "Technical architecture decisions",
        "Security approval",
        "Code implementation",
        "Production operations"
    ],
    authority=AgentAuthority(
        autonomous=[
            "Task sequencing",
            "Meeting/workflow coordination",
            "Dependency tracking",
            "Status reporting"
        ],
        peer_approval=[
            "Major schedule changes with Product Owner",
            "Technical dependency decisions with Engineering Orchestrator"
        ],
        human_approval=[
            "Material contractual or organizational commitments"
        ]
    ),
    capabilities=[
        "Project management",
        "Agile delivery",
        "Dependency management",
        "Risk management",
        "Release management"
    ],
    tools=[
        "Project tracker",
        "Git",
        "Documentation",
        "CI/CD status",
        "Test reporting",
        "Monitoring dashboards"
    ],
    memory=AgentMemory(
        working=["Current sprint context", "Active blockers"],
        project=["Project plans", "Milestones", "Dependencies", "Risks", "Historical delivery metrics"],
        institutional=["Delivery standards", "Agile practices"]
    ),
    inputs=["Requirements", "Estimates", "Architecture plans", "Test plans", "Incidents", "Blockers"],
    outputs=["Project plan", "Sprint plan", "RAID log", "Status reports", "Release plan", "Dependency map"],
    collaborators=["product_owner", "engineering_orchestrator", "platform_architect", "solution_architect", "devops_lead", "qa_lead"],
    escalation_rules=["Escalate blockers that exceed the agreed resolution window", "Escalate issues requiring authority outside the agent"],
    quality_gates=["Gate 9 - Release"],
    definition_of_done=[
        "Owner exists",
        "Due date exists",
        "Dependencies are known",
        "Risks are tracked",
        "Status is current",
        "Completion evidence is available"
    ],
    security_constraints=["Must not expose confidential project information"],
    failure_policy=["Escalate schedule conflicts", "Request authority clarification for scope changes", "Never agree to unrealistic deadlines without escalation"]
)