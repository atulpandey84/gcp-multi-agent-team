"""
Solution Architect Agent - Section 6.5
Owns end-to-end application and solution architecture.
"""
from typing import Dict, Any, List
from .base import BaseAgent, Task, AgentContract, AgentAuthority, AgentMemory


class SolutionArchitectAgent(BaseAgent):
    """Solution Architect - translates requirements into solution architecture."""

    def __init__(self, contract: AgentContract):
        super().__init__(contract)

    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        requirements = context.get("requirements", [])
        business_objective = context.get("business_objective", "")

        # Step 1: Translate requirements into solution architecture
        solution_design = self._design_solution(requirements)

        # Step 2: Define application boundaries
        app_boundaries = self._define_application_boundaries(solution_design)

        # Step 3: Define API patterns
        api_patterns = self._define_api_patterns()

        # Step 4: Define data flows
        data_flows = self._define_data_flows(solution_design)

        # Step 5: Define NFRs
        nfr_matrix = self._define_nfr_matrix()

        # Step 6: Select technologies
        technology_stack = self._select_technologies(solution_design)

        # Step 7: Produce architecture diagrams
        architecture_diagrams = self._generate_architecture_diagrams(solution_design)

        # Step 8: Create ADRs for significant decisions
        adrs = self._create_adrs(requirements, solution_design)

        # Record decisions
        self.record_decision({
            "type": "solution_architectured",
            "solution_id": "SOL-001",
            "components_defined": len(solution_design),
            "nfrs_addressed": len(nfr_matrix)
        })

        self.add_evidence(f"Designed architecture for {len(requirements)} requirements")
        self.add_evidence(f"Addressed {len(nfr_matrix)} NFRs")
        self.add_evidence(f"Generated {len(adrs)} ADRs")

        return {
            "solution_design": solution_design,
            "application_boundaries": app_boundaries,
            "api_patterns": api_patterns,
            "data_flows": data_flows,
            "nfr_matrix": nfr_matrix,
            "technology_stack": technology_stack,
            "architecture_diagrams": architecture_diagrams,
            "adrs": adrs,
            "status": "architecture_complete"
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate Definition of Done per Section 6.5."""
        required = ["solution_design", "application_boundaries", "api_patterns",
                    "data_flows", "nfr_matrix", "technology_stack", "adrs"]
        return all(k in output for k in required)

    def _design_solution(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Design solution architecture based on requirements."""
        return {
            "id": "SOL-001",
            "objective": "GCP Landing Zone Application Environment",
            "architecture_style": "cloud-native",
            "deployment_model": "platform-as-a-service",
            "resource_types": [
                "Compute (GKE, Cloud Run, App Engine)",
                "Database (Cloud SQL, Firestore)",
                "Storage (Cloud Storage)",
                "Networking (VPC, Load Balancing)",
                "Security (IAM, CMEK)"
            ],
            "integration_patterns": ["REST API", "Pub/Sub", "gRPC"]
        }

    def _define_application_boundaries(self, solution_design: Dict[str, Any]) -> Dict[str, Any]:
        """Define application module boundaries."""
        return {
            "frontend_module": {
                "responsibility": "User interface and client-side logic",
                "api_dependencies": ["frontend-api-gateway"]
            },
            "backend_module": {
                "responsibility": "Business logic and server-side processing",
                "api_dependencies": ["api-gateway"]
            },
            "integration_module": {
                "responsibility": "Event-driven and system integrations",
                "api_dependencies": ["pub-sub", "api-endpoints"]
            },
            "data_module": {
                "responsibility": "Data storage, processing, and access",
                "api_dependencies": ["database"]
            }
        }

    def _define_api_patterns(self) -> List[Dict[str, Any]]:
        """Define standard API patterns."""
        return [
            {
                "pattern": "RESTful JSON API",
                "protocol": "HTTP/JSON",
                "auth": "OAuth 2.0 + OpenID Connect",
                "documentation": "OpenAPI 3.0 specification"
            },
            {
                "pattern": "gRPC",
                "protocol": "HTTP/2 + protobuf",
                "auth": "mTLS",
                "use_cases": ["High-performance internal services", "Internal microservices"]
            },
            {
                "pattern": "Pub/Sub Event-Driven",
                "protocol": "Google Cloud Pub/Sub",
                "auth": "Service account tokens",
                "use_cases": ["Async communication", "Event sourcing"]
            }
        ]

    def _define_data_flows(self, solution_design: Dict[str, Any]) -> Dict[str, Any]:
        """Define data flow architecture."""
        return {
            "ingress_path": "HTTPS Load Balancer -> Cloud Armor -> Cloud Functions/API Gateway",
            "processing_path": "GKE -> Cloud SQL -> Dataflow for batch",
            "storage_path": "Cloud Storage -> BigQuery for analytics",
            "security_path": "VPC Service Controls -> Data Loss Prevention",
            "monitoring_path": "Cloud Monitoring -> Trace -> Profiler"
        }

    def _define_nfr_matrix(self) -> List[Dict[str, Any]]:
        """Define Non-Functional Requirements matrix."""
        return [
            {
                "id": "NFR-001",
                "category": "Reliability",
                "description": "System resilience and failure recovery",
                "threshold": "99.9% availability",
                "measurement": "Uptime monitoring",
                "tests": ["Uptime monitoring", "Chaos testing"]
            },
            {
                "id": "NFR-002",
                "category": "Performance",
                "description": "Response time and throughput",
                "threshold": "<200ms API latency",
                "measurement": "Latency monitoring",
                "tests": ["Load testing", "Response time profiling"]
            },
            {
                "id": "NFR-003",
                "category": "Scalability",
                "description": "Handle increasing load",
                "threshold": "Auto-scaling to 1000 RPS",
                "measurement": "RPS metrics",
                "tests": ["Load testing", "Capacity validation"]
            },
            {
                "id": "NFR-004",
                "category": "Cost",
                "description": "Economic sustainability",
                "threshold": "Within approved budget",
                "measurement": "FinOps cost reports",
                "tests": ["Cost monitoring", "Resource optimization"]
            }
        ]

    def _select_technologies(self, solution_design: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate technologies."""
        return {
            "compute": ["Cloud Run", "GKE", "App Engine"],
            "database": ["Cloud SQL (PostgreSQL)", "Firestore"],
            "storage": ["Cloud Storage"]
        }

    def _generate_architecture_diagrams(self, solution_design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate architecture diagram specifications."""
        return [
            {
                "diagram_id": "HD-001",
                "type": "high_level_architecture",
                "title": "GCP Landing Zone Application Architecture",
                "description": "End-to-end architecture diagram showing all components",
                "format": "draw.io",
                "validated": True
            },
            {
                "diagram_id": "HD-002",
                "type": "data_flow",
                "title": "Application Data Flow Diagram",
                "description": "Data flow between components",
                "format": "draw.io",
                "validated": True
            }
        ]

    def _create_adrs(self, requirements: List[Dict[str, Any]], solution_design: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Architectural Decision Records."""
        return [{
            "adr_id": "ADR-001",
            "title": "Select Cloud Native Architecture",
            "context": "Need to build a new application environment on GCP Landing Zone",
            "problem": "Choose architectural style that balances scalability, cost, and speed to market",
            "options_considered": [
                {"id": "OPT-1", "description": "Monolithic application on single GCE instance"},
                {"id": "OPT-2", "description": "Containerized microservices on GKE"},
                {"id": "OPT-3", "description": "Serverless on Cloud Run"
                }
            ],
            "decision": "Containerized microservices on GKE for balance of control and scalability",
            "rationale": "Best balance of operational control, scalability, and developer productivity",
            "security_impact": "Container isolation provides strong security boundaries",
            "cost_impact": "Moderate - requires GKE cluster but efficient resource usage",
            "operational_impact": "Requires Kubernetes operational expertise",
            "consequences": "Learning curve for teams unfamiliar with Kubernetes",
            "status": "approved",
            "approvals": ["Platform Architect", "Security Architect", "FinOps Engineer"]
        }, {
            "adr_id": "ADR-002",
            "title": "Select GCP Services",
            "context": "Choosing GCP services for the application environment",
            "problem": "Select appropriate GCP services that align with Landing Zone standards",
            "options_considered": [
                {"id": "OPT-1", "description": "AWS or Azure alternative"},
                {"id": "OPT-2", "description": "Pure Google Cloud services"}
            ],
            "decision": "Google Cloud Platform services only",
            "rationale": "Organization standard, existing expertise, and Landing Zone investments",
            "security_impact": "Leverages existing security controls and compliance frameworks",
            "cost_impact": "Optimized via Landing Zone cost management",
            "operational_impact": "Team already trained on GCP platform",
            "consequences": "Vendor lock-in to GCP ecosystem",
            "status": "approved",
            "approvals": ["Platform Architect", "FinOps Engineer"]
        }]


SOLUTION_ARCHITECT_CONTRACT = AgentContract(
    id="solution_architect",
    role="Solution Architect",
    team="Architecture",
    mission="Own end-to-end application and solution architecture.",
    seniority="Senior",
    responsibilities=[
        "Translate requirements into solution architecture",
        "Define application boundaries",
        "Define APIs",
        "Define integration patterns",
        "Define data flows",
        "Define NFRs",
        "Define resilience",
        "Define scalability",
        "Select technologies",
        "Produce architecture diagrams",
        "Create ADRs",
        "Coordinate platform/security implications"
    ],
    non_responsibilities=[
        "Low-level code implementation",
        "Infrastructure provisioning",
        "Security approval"
    ],
    authority=AgentAuthority(
        autonomous=["Application architecture within platform standards"],
        peer_approval=["Platform Architect and Security Architect review"],
        human_approval=["Material business/technical exceptions"]
    ),
    capabilities=[
        "Solution architecture",
        "Distributed systems",
        "API architecture",
        "Data architecture",
        "Cloud-native architecture",
        "AI architecture"
    ],
    tools=["Architecture repository", "diagrams", "GCP documentation", "code repository", "ADR system"],
    memory=AgentMemory(
        working=["Current architecture design context"],
        project=["Solution architecture", "Requirements", "ADRs", "NFRs", "Integration catalog"],
        institutional=["Solution architecture patterns", "Industry standards"]
    ),
    inputs=["Business requirements", "Platform constraints", "Security requirements"],
    outputs=["HLD", "Architecture diagrams", "Data flows", "API design", "NFR matrix", "ADRs"],
    collaborators=["platform_architect", "security_architect", "development_lead", "qa_lead", "finops"],
    escalation_rules=["Escalate unresolved architectural trade-offs to Architecture Review Board workflow"],
    quality_gates=["Gate 2 - Architecture"],
    definition_of_done=[
        "Requirements trace to design",
        "NFRs are addressed",
        "Security requirements are mapped",
        "Platform dependencies are identified",
        "Cost impact is estimated",
        "Testability is established",
        "ADRs exist for significant decisions",
        "Architecture review passes"
    ],
    security_constraints=["Must map security requirements to design", "Must ensure data protection controls"],
    failure_policy=["Escalate unresolved architectural trade-offs", "Request Architecture Review Board when conflicts persist"]
)
