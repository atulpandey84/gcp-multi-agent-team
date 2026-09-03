"""
Pydantic models for all API request/response contracts.
Standardized schemas for cross-module communication.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AgentRole(str, Enum):
    """Clear role definitions for all 22 agents to prevent ambiguity."""
    # Product & Delivery
    PRODUCT_OWNER = "product_owner"
    PROJECT_MANAGER = "project_manager"
    
    # Architecture & Design
    PLATFORM_ARCHITECT = "platform_architect"
    SOLUTION_ARCHITECT = "solution_architect"
    SECURITY_ARCHITECT = "security_architect"
    
    # DevOps & Infrastructure
    DEVOPS_LEAD = "devops_lead"
    CLOUD_INFRASTRUCTURE_ENGINEER = "cloud_infrastructure_engineer"
    CICD_ENGINEER = "cicd_engineer"
    SRE_OBSERVABILITY_ENGINEER = "sre_observability_engineer"
    FINOPS_ENGINEER = "finops_engineer"
    
    # Development
    DEVELOPMENT_LEAD = "development_lead"
    FRONTEND_ENGINEER = "frontend_engineer"
    BACKEND_ENGINEER = "backend_engineer"
    INTEGRATION_ENGINEER = "integration_engineer"
    AI_AUTOMATION_ENGINEER = "ai_automation_engineer"
    
    # Testing & Quality
    QA_LEAD = "qa_lead"
    TEST_AUTOMATION_ENGINEER = "test_automation_engineer"
    NFR_TEST_ENGINEER = "nfr_test_engineer"
    
    # Application Management & Reliability
    APPLICATION_MANAGEMENT_LEAD = "application_management_lead"
    APPLICATION_SUPPORT_ENGINEER = "application_support_engineer"
    PRODUCTION_RELIABILITY_ENGINEER = "production_reliability_engineer"
    
    # Engineering Governance
    ENGINEERING_ORCHESTRATOR = "engineering_orchestrator"


class Team(str, Enum):
    """Functional teams in the organization."""
    PRODUCT_DELIVERY = "product_delivery"
    ARCHITECTURE_DESIGN = "architecture_design"
    DEVOPS_INFRASTRUCTURE = "devops_infrastructure"
    DEVELOPMENT = "development"
    TESTING_QUALITY = "testing_quality"
    APPLICATION_MANAGEMENT_RELIABILITY = "application_management_reliability"
    ENGINEERING_GOVERNANCE = "engineering_governance"


class AuthorityLevel(str, Enum):
    """Authority levels per Section 7 of specification."""
    AUTONOMOUS = "autonomous"
    PEER_APPROVAL = "peer_approval"
    HUMAN_APPROVAL = "human_approval"


class Environment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class TaskStatus(str, Enum):
    """Task lifecycle statuses per Section 23."""
    CREATED = "CREATED"
    TRIAGED = "TRIAGED"
    PLANNED = "PLANNED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_DEPENDENCY = "WAITING_FOR_DEPENDENCY"
    REVIEW = "REVIEW"
    QUALITY_GATE = "QUALITY_GATE"
    APPROVAL = "APPROVAL"
    READY_FOR_RELEASE = "READY_FOR_RELEASE"
    RELEASED = "RELEASED"
    VALIDATED = "VALIDATED"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    CANCELLED = "CANCELLED"


class RiskLevel(str, Enum):
    """Risk levels for approval routing."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


# Base schemas for all communications
class BaseSchema(BaseModel):
    """Base schema with common fields."""
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentIdentity(BaseSchema):
    """Agent identification for all communications."""
    agent_id: AgentRole
    agent_name: str
    team: Team
    seniority: str


class TaskInput(BaseSchema):
    """Standardized task input for all agents."""
    task_id: str
    objective: str
    context: Dict[str, Any] = Field(default_factory=dict)
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    deadline: Optional[datetime] = None
    assigned_agent: Optional[AgentRole] = None
    dependencies: List[str] = Field(default_factory=list)


class TaskOutput(BaseSchema):
    """Standardized task output from all agents."""
    task_id: str
    status: TaskStatus
    agent_id: AgentRole
    result: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    completed_at: Optional[datetime] = None
    quality_gate_results: List[Dict[str, Any]] = Field(default_factory=list)


class AgentMessage(BaseSchema):
    """Structured agent communication per Section 5."""
    message_id: str
    task_id: str
    sender: AgentRole
    recipients: List[AgentRole]
    message_type: Literal["request", "response", "review", "approval", "escalation", "status"]
    objective: str
    context: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    requested_action: str = ""
    expected_output: str = ""
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CanonicalMessagePayload(BaseSchema):
    """
    Universal contract for all inter-agent communication.
    
    This canonical representation decouples agents from each other's specific
    output formats. The Orchestrator translates agent-specific outputs into
    this canonical format before passing to downstream agents.
    
    Per architectural review: Prevents "Dependency Hell" by ensuring agents
    only depend on this stable contract, not on each other's internal formats.
    """
    payload_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    step_number: int
    source_agent: AgentRole
    target_agents: List[AgentRole]
    payload_type: Literal[
        "architecture_decision",
        "design_specification", 
        "implementation_plan",
        "test_plan",
        "security_assessment",
        "cost_estimate",
        "operational_readiness",
        "deployment_plan",
        "incident_report",
        "quality_gate_result",
        "approval_request",
        "escalation",
        "status_update",
        "artifact_reference"
    ]
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Canonical content - structured, validated, and versioned
    content: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata for routing and processing
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality and validation
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_status: Literal["pending", "validated", "rejected"] = "pending"
    validator_notes: Optional[str] = None
    
    # Traceability
    parent_payload_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Approval chain for sensitive payloads
    requires_approval: bool = False
    approval_chain: List[AgentRole] = Field(default_factory=list)
    approval_status: Literal["not_required", "pending", "approved", "rejected"] = "not_required"


class ApprovalRequest(BaseSchema):
    """Human approval request per Section 2.3 and Section 18."""
    approval_id: str
    requester: AgentRole
    action: str
    agent_id: Optional[AgentRole] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    risk: RiskLevel = RiskLevel.MEDIUM
    affected_components: List[str] = Field(default_factory=list)
    implementation_plan: str = ""
    validation_plan: str = ""
    rollback_plan: str = ""
    security_impact: str = ""
    cost_impact: str = ""
    monitoring_plan: str = ""
    status: Literal["pending", "approved", "rejected", "consumed"] = "pending"
    approver: Optional[AgentRole] = None
    approver_comments: Optional[str] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None


class QualityGateResult(BaseSchema):
    """Quality gate evaluation result per Section 15."""
    gate_name: str
    passed: bool
    owner: AgentRole
    checks: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None


class ToolInvocation(BaseSchema):
    """Standardized tool invocation request."""
    tool_id: str
    agent_id: AgentRole
    task_id: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseSchema):
    """Standardized tool execution result."""
    tool_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    execution_time_ms: int = 0
    audit_log: Dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseSchema):
    """Complete workflow state for persistence."""
    workflow_id: str
    objective: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    active_agents: List[AgentRole] = Field(default_factory=list)
    pending_tasks: List[TaskInput] = Field(default_factory=list)
    completed_tasks: List[TaskOutput] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    approvals: Dict[str, Any] = Field(default_factory=dict)
    evidence_collected: int = 0
    quality_gates_passed: int = 0
    risks_identified: int = 0
    final_response: Optional[str] = None


class HealthCheckResponse(BaseSchema):
    """Health check response for monitoring."""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Dict[str, str] = Field(default_factory=dict)
    active_workflows: int = 0
    registered_agents: int = 0


# API-specific schemas
class WorkflowRequest(BaseSchema):
    """Request to start a new workflow."""
    objective: str
    project_id: Optional[str] = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    context: Dict[str, Any] = Field(default_factory=dict)
    assigned_agents: Optional[List[AgentRole]] = None


class WorkflowResponse(BaseSchema):
    """Response from workflow execution."""
    workflow_id: str
    status: TaskStatus
    message: str
    estimated_duration_seconds: Optional[int] = None


class AgentStatusResponse(BaseSchema):
    """Agent status for monitoring."""
    agent_id: AgentRole
    role: str
    team: Team
    status: Literal["idle", "busy", "blocked", "offline"]
    current_task: Optional[str] = None
    last_activity: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_failed: int = 0


class MetricsResponse(BaseSchema):
    """System metrics for monitoring."""
    total_workflows: int
    active_workflows: int
    completed_workflows: int
    failed_workflows: int
    average_completion_time_seconds: float
    agent_utilization: Dict[str, float]
    quality_gate_pass_rate: float
    approval_rate: float


# Export all schemas
__all__ = [
    "AgentRole",
    "Team",
    "AuthorityLevel",
    "Environment",
    "TaskStatus",
    "RiskLevel",
    "BaseSchema",
    "AgentIdentity",
    "TaskInput",
    "TaskOutput",
    "AgentMessage",
    "CanonicalMessagePayload",
    "ApprovalRequest",
    "QualityGateResult",
    "ToolInvocation",
    "ToolResult",
    "WorkflowState",
    "HealthCheckResponse",
    "WorkflowRequest",
    "WorkflowResponse",
    "AgentStatusResponse",
    "MetricsResponse",
]