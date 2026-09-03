"""
Schemas package for the Multi-Agent Engineering Organization.
Provides standardized Pydantic models for all cross-module communication.
"""

from .contracts import (
    AgentRole,
    Team,
    AuthorityLevel,
    Environment,
    TaskStatus,
    RiskLevel,
    BaseSchema,
    AgentIdentity,
    TaskInput,
    TaskOutput,
    AgentMessage,
    ApprovalRequest,
    QualityGateResult,
    ToolInvocation,
    ToolResult,
    WorkflowState,
    HealthCheckResponse,
    WorkflowRequest,
    WorkflowResponse,
    AgentStatusResponse,
    MetricsResponse,
)

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