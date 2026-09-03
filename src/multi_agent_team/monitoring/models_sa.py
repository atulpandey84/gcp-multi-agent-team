from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, JSON, ForeignKey, Boolean, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class Agent(Base):
    """Agent profiles - stores all 22 agent definitions and runtime state."""
    __tablename__ = 'agents'
    id = Column(String, primary_key=True)  # AgentRole enum value
    role = Column(String, nullable=False)
    team = Column(String, nullable=False)
    mission = Column(Text)
    seniority = Column(String)
    status = Column(String, default="idle")  # idle, busy, blocked, offline
    capabilities = Column(JSON, default=list)
    tools = Column(JSON, default=list)
    authority_autonomous = Column(JSON, default=list)
    authority_peer_approval = Column(JSON, default=list)
    authority_human_approval = Column(JSON, default=list)
    last_seen = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class Audit(Base):
    """Audit log for all system events."""
    __tablename__ = 'audit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    action = Column(String, nullable=False, index=True)
    agent_id = Column(String, ForeignKey('agents.id', ondelete='SET NULL'), index=True)
    task_id = Column(String, index=True)
    workflow_id = Column(String, index=True)
    details = Column(Text)
    success = Column(Boolean, default=True)
    error_message = Column(Text)


class Approval(Base):
    """Approval requests and decisions."""
    __tablename__ = 'approvals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    requester = Column(String, nullable=False)
    action = Column(String, nullable=False)
    agent_id = Column(String, ForeignKey('agents.id', ondelete='SET NULL'))
    details = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected, consumed
    approver = Column(String)
    approver_comments = Column(Text)
    decision_timestamp = Column(TIMESTAMP(timezone=True))
    risk_level = Column(String, default="medium")
    affected_components = Column(JSON, default=list)
    implementation_plan = Column(Text)
    validation_plan = Column(Text)
    rollback_plan = Column(Text)
    security_impact = Column(Text)
    cost_impact = Column(Text)
    monitoring_plan = Column(Text)


class ChatHistory(Base):
    """Chat history / memory for agent conversations."""
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    session_id = Column(String, index=True)
    workflow_id = Column(String, index=True)
    agent_id = Column(String, ForeignKey('agents.id', ondelete='SET NULL'), index=True)
    message_type = Column(String)  # user, agent, system, tool
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    message_metadata = Column(JSON, default=dict)
    tokens_used = Column(Integer, default=0)
    model_used = Column(String)


class ToolUsageLog(Base):
    """Tool usage logs for analytics and debugging."""
    __tablename__ = 'tool_usage_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    tool_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, ForeignKey('agents.id', ondelete='SET NULL'), index=True)
    task_id = Column(String, index=True)
    workflow_id = Column(String, index=True)
    action = Column(String)
    parameters = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    execution_time_ms = Column(Integer, default=0)
    approval_required = Column(Boolean, default=False)
    approval_id = Column(Integer, ForeignKey('approvals.id', ondelete='SET NULL'))


class OrchestrationMetadata(Base):
    """Orchestration metadata for workflow tracking."""
    __tablename__ = 'orchestration_metadata'
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, unique=True, nullable=False, index=True)
    objective = Column(Text)
    status = Column(String, default="created")  # created, running, completed, failed, cancelled
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))
    active_agents = Column(JSON, default=list)
    pending_tasks = Column(JSON, default=list)
    completed_tasks = Column(JSON, default=list)
    artifacts = Column(JSON, default=list)
    decisions = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    approvals = Column(JSON, default=dict)
    evidence_collected = Column(Integer, default=0)
    quality_gates_passed = Column(Integer, default=0)
    risks_identified = Column(Integer, default=0)
    final_response = Column(Text)
    total_execution_time_ms = Column(Integer, default=0)
    parent_workflow_id = Column(String, ForeignKey('orchestration_metadata.workflow_id', ondelete='SET NULL'))


class QualityGateResult(Base):
    """Quality gate evaluation results."""
    __tablename__ = 'quality_gate_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    workflow_id = Column(String, ForeignKey('orchestration_metadata.workflow_id', ondelete='CASCADE'), index=True)
    task_id = Column(String, index=True)
    gate_name = Column(String, nullable=False)
    passed = Column(Boolean, default=False)
    owner = Column(String, ForeignKey('agents.id', ondelete='SET NULL'))
    checks = Column(JSON, default=list)
    evidence = Column(JSON, default=list)
    reason = Column(Text)
    metrics = Column(JSON, default=dict)


class AgentTask(Base):
    """Individual agent tasks within workflows."""
    __tablename__ = 'agent_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, unique=True, nullable=False, index=True)
    workflow_id = Column(String, ForeignKey('orchestration_metadata.workflow_id', ondelete='CASCADE'), index=True)
    agent_id = Column(String, ForeignKey('agents.id', ondelete='SET NULL'), index=True)
    objective = Column(Text)
    status = Column(String, default="created")  # created, assigned, in_progress, review, done, failed, blocked
    dependencies = Column(JSON, default=list)
    inputs = Column(JSON, default=dict)
    outputs = Column(JSON, default=dict)
    evidence = Column(JSON, default=list)
    approvals = Column(JSON, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    assigned_at = Column(TIMESTAMP(timezone=True))
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    task_metadata = Column(JSON, default=dict)


# Indexes for better query performance
Index('ix_audit_agent_timestamp', Audit.agent_id, Audit.timestamp)
Index('ix_audit_workflow_timestamp', Audit.workflow_id, Audit.timestamp)
Index('ix_chat_session_timestamp', ChatHistory.session_id, ChatHistory.timestamp)
Index('ix_tool_usage_agent_timestamp', ToolUsageLog.agent_id, ToolUsageLog.timestamp)
Index('ix_tool_usage_workflow_timestamp', ToolUsageLog.workflow_id, ToolUsageLog.timestamp)
Index('ix_orchestration_status', OrchestrationMetadata.status)
Index('ix_quality_gate_workflow', QualityGateResult.workflow_id, QualityGateResult.gate_name)
Index('ix_agent_task_workflow', AgentTask.workflow_id, AgentTask.status)
