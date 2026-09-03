"""
Agents package for the Multi-Agent Engineering Organization.
Provides base classes, contracts, and all 22 specialized agent implementations.
"""

from .base import (
    AgentRole,
    AuthorityLevel,
    TaskStatus,
    Environment,
    AgentMemory,
    AgentAuthority,
    AgentContract,
    AgentMessage,
    Task,
    QualityGateResult,
    ApprovalRequest,
    BaseAgent,
    load_agent_contracts,
)

__all__ = [
    "AgentRole",
    "AuthorityLevel",
    "TaskStatus",
    "Environment",
    "AgentMemory",
    "AgentAuthority",
    "AgentContract",
    "AgentMessage",
    "Task",
    "QualityGateResult",
    "ApprovalRequest",
    "BaseAgent",
    "load_agent_contracts",
]