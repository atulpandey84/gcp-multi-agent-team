"""
Memory management for the Multi-Agent Engineering Organization.
Implements three-tier memory architecture per Section 11 of the specification:
- Workflow-level: Execution checkpoints (ephemeral)
- Agent-level: Decision history (persistent, PostgreSQL)
- Organization-level: ADRs and policies (durable artifacts)
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
from contextlib import asynccontextmanager

from src.multi_agent_team.schemas.contracts import AgentRole, TaskStatus, WorkflowState
from src.multi_agent_team.monitoring.models_sa import Base, Audit, Approval
from sqlalchemy import create_engine, Column, String, Text, Integer, TIMESTAMP, JSON, ForeignKey, select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import os


class MemoryTier(str, Enum):
    """Memory tiers per Section 11."""
    WORKING = "working"      # Short-lived task context
    PROJECT = "project"      # Persistent project-specific
    INSTITUTIONAL = "institutional"  # Reusable engineering knowledge
    EPISODIC = "episodic"    # What happened (event log)
    SEMANTIC = "semantic"    # Searchable technical knowledge


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tier: MemoryTier = MemoryTier.WORKING
    agent_id: Optional[AgentRole] = None
    task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    key: str = ""
    value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class SessionContext:
    """Session context for workflow execution."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    active_agents: List[AgentRole] = field(default_factory=list)
    current_task: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class MemoryManager:
    """
    Central memory manager implementing three-tier architecture.
    Handles session boundaries, persistence, and retrieval.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.environ.get(
            "DATABASE_URL", 
            "postgresql://user:password@localhost:5432/multi_agent_team"
        )
        self.engine = None
        self.SessionLocal = None
        self._working_memory: Dict[str, Any] = {}  # In-memory working memory
        self._session_contexts: Dict[str, SessionContext] = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            self.engine = create_engine(self.database_url, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(bind=self.engine)
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            # Log warning but continue with in-memory only
            print(f"Warning: Database connection failed, using in-memory only: {e}")
            self.engine = None
            self.SessionLocal = None
    
    @asynccontextmanager
    async def session(self):
        """Get a database session."""
        if self.SessionLocal is None:
            yield None
            return
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # Working Memory (ephemeral, in-memory)
    def set_working(self, key: str, value: Any, agent_id: Optional[AgentRole] = None, 
                    task_id: Optional[str] = None, workflow_id: Optional[str] = None):
        """Set a value in working memory."""
        entry = MemoryEntry(
            tier=MemoryTier.WORKING,
            agent_id=agent_id,
            task_id=task_id,
            workflow_id=workflow_id,
            key=key,
            value=value,
        )
        self._working_memory[key] = entry
    
    def get_working(self, key: str) -> Optional[Any]:
        """Get a value from working memory."""
        entry = self._working_memory.get(key)
        if entry and entry.expires_at and entry.expires_at < datetime.utcnow():
            del self._working_memory[key]
            return None
        return entry.value if entry else None
    
    def delete_working(self, key: str):
        """Delete a value from working memory."""
        self._working_memory.pop(key, None)
    
    def clear_working(self, agent_id: Optional[AgentRole] = None, 
                      task_id: Optional[str] = None, workflow_id: Optional[str] = None):
        """Clear working memory for a specific scope."""
        keys_to_delete = []
        for key, entry in self._working_memory.items():
            if agent_id and entry.agent_id != agent_id:
                continue
            if task_id and entry.task_id != task_id:
                continue
            if workflow_id and entry.workflow_id != workflow_id:
                continue
            keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._working_memory[key]
    
    # Project Memory (persistent, database)
    async def set_project(self, key: str, value: Any, project_id: str,
                          agent_id: Optional[AgentRole] = None):
        """Set a value in project memory (persisted to database)."""
        if self.SessionLocal is None:
            # Fallback to in-memory
            self.set_working(f"project:{project_id}:{key}", value, agent_id)
            return
        
        async with self.session() as session:
            if session is None:
                return
            
            # Store as audit entry for persistence
            audit = Audit(
                action=f"memory_set:{key}",
                agent_id=agent_id.value if agent_id else None,
                details=json.dumps({
                    "project_id": project_id,
                    "key": key,
                    "value": value,
                    "tier": MemoryTier.PROJECT.value,
                })
            )
            session.add(audit)
    
    async def get_project(self, key: str, project_id: str) -> Optional[Any]:
        """Get a value from project memory."""
        if self.SessionLocal is None:
            entry = self._working_memory.get(f"project:{project_id}:{key}")
            return entry.value if entry else None
        
        async with self.session() as session:
            if session is None:
                return None
            
            result = await session.execute(
                select(Audit).where(
                    Audit.action == f"memory_set:{key}",
                    Audit.details.contains(f'"project_id": "{project_id}"')
                ).order_by(Audit.timestamp.desc()).limit(1)
            )
            audit = result.scalar_one_or_none()
            if audit:
                try:
                    details = json.loads(audit.details)
                    return details.get("value")
                except Exception:
                    pass
            return None
    
    # Institutional Memory (persistent, database)
    async def set_institutional(self, key: str, value: Any, 
                                category: str = "general",
                                agent_id: Optional[AgentRole] = None):
        """Set a value in institutional memory (persisted to database)."""
        if self.SessionLocal is None:
            self.set_working(f"institutional:{category}:{key}", value, agent_id)
            return
        
        async with self.session() as session:
            if session is None:
                return
            
            audit = Audit(
                action=f"institutional_set:{category}:{key}",
                agent_id=agent_id.value if agent_id else None,
                details=json.dumps({
                    "category": category,
                    "key": key,
                    "value": value,
                    "tier": MemoryTier.INSTITUTIONAL.value,
                })
            )
            session.add(audit)
    
    async def get_institutional(self, key: str, category: str = "general") -> Optional[Any]:
        """Get a value from institutional memory."""
        if self.SessionLocal is None:
            entry = self._working_memory.get(f"institutional:{category}:{key}")
            return entry.value if entry else None
        
        async with self.session() as session:
            if session is None:
                return None
            
            result = await session.execute(
                select(Audit).where(
                    Audit.action == f"institutional_set:{category}:{key}"
                ).order_by(Audit.timestamp.desc()).limit(1)
            )
            audit = result.scalar_one_or_none()
            if audit:
                try:
                    details = json.loads(audit.details)
                    return details.get("value")
                except Exception:
                    pass
            return None
    
    async def search_institutional(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search institutional memory."""
        if self.SessionLocal is None:
            return []
        
        async with self.session() as session:
            if session is None:
                return []
            
            stmt = select(Audit).where(Audit.action.like("institutional_set:%"))
            if category:
                stmt = stmt.where(Audit.action.like(f"institutional_set:{category}:%"))
            
            result = await session.execute(stmt.order_by(Audit.timestamp.desc()).limit(50))
            audits = result.scalars().all()
            
            results = []
            for audit in audits:
                try:
                    details = json.loads(audit.details)
                    if query.lower() in str(details.get("value", "")).lower() or \
                       query.lower() in details.get("key", "").lower():
                        results.append(details)
                except Exception:
                    pass
            return results
    
    # Episodic Memory (event log)
    async def record_event(self, event_type: str, agent_id: AgentRole,
                           task_id: Optional[str] = None, workflow_id: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None):
        """Record an event to episodic memory."""
        if self.SessionLocal is None:
            return
        
        async with self.session() as session:
            if session is None:
                return
            
            audit = Audit(
                action=event_type,
                agent_id=agent_id.value,
                details=json.dumps({
                    "task_id": task_id,
                    "workflow_id": workflow_id,
                    "details": details or {},
                    "tier": MemoryTier.EPISODIC.value,
                })
            )
            session.add(audit)
    
    async def get_events(self, agent_id: Optional[AgentRole] = None,
                         task_id: Optional[str] = None,
                         workflow_id: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get events from episodic memory."""
        if self.SessionLocal is None:
            return []
        
        async with self.session() as session:
            if session is None:
                return []
            
            stmt = select(Audit).where(Audit.action.like("%"))
            if agent_id:
                stmt = stmt.where(Audit.agent_id == agent_id.value)
            
            result = await session.execute(stmt.order_by(Audit.timestamp.desc()).limit(limit))
            audits = result.scalars().all()
            
            events = []
            for audit in audits:
                try:
                    details = json.loads(audit.details)
                    if task_id and details.get("task_id") != task_id:
                        continue
                    if workflow_id and details.get("workflow_id") != workflow_id:
                        continue
                    events.append({
                        "id": audit.id,
                        "timestamp": audit.timestamp.isoformat() if audit.timestamp else None,
                        "action": audit.action,
                        "agent_id": audit.agent_id,
                        "details": details,
                    })
                except Exception:
                    pass
            return events
    
    # Session Context Management
    def create_session(self, workflow_id: Optional[str] = None,
                       active_agents: Optional[List[AgentRole]] = None) -> SessionContext:
        """Create a new session context."""
        session = SessionContext(
            workflow_id=workflow_id,
            active_agents=active_agents or [],
        )
        self._session_contexts[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get a session context by ID."""
        session = self._session_contexts.get(session_id)
        if session and session.expires_at and session.expires_at < datetime.utcnow():
            del self._session_contexts[session_id]
            return None
        return session
    
    def update_session(self, session_id: str, **kwargs) -> Optional[SessionContext]:
        """Update a session context."""
        session = self.get_session(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = datetime.utcnow()
        return session
    
    def end_session(self, session_id: str) -> bool:
        """End a session context."""
        if session_id in self._session_contexts:
            del self._session_contexts[session_id]
            return True
        return False
    
    def list_active_sessions(self) -> List[SessionContext]:
        """List all active sessions."""
        now = datetime.utcnow()
        active = []
        for session in self._session_contexts.values():
            if not session.expires_at or session.expires_at > now:
                active.append(session)
        return active
    
    # Workflow State Persistence
    async def save_workflow_state(self, state: WorkflowState):
        """Save workflow state to database."""
        if self.SessionLocal is None:
            return
        
        async with self.session() as session:
            if session is None:
                return
            
            audit = Audit(
                action="workflow_state_save",
                agent_id=state.active_agents[0].value if state.active_agents else None,
                details=json.dumps(state.model_dump())
            )
            session.add(audit)
    
    async def load_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state from database."""
        if self.SessionLocal is None:
            return None
        
        async with self.session() as session:
            if session is None:
                return None
            
            result = await session.execute(
                select(Audit).where(
                    Audit.action == "workflow_state_save",
                    Audit.details.contains(f'"workflow_id": "{workflow_id}"')
                ).order_by(Audit.timestamp.desc()).limit(1)
            )
            audit = result.scalar_one_or_none()
            if audit:
                try:
                    data = json.loads(audit.details)
                    return WorkflowState(**data)
                except Exception:
                    pass
            return None
    
    # Tool Usage Logging
    async def log_tool_usage(self, tool_id: str, agent_id: AgentRole,
                             task_id: str, workflow_id: str,
                             parameters: Dict[str, Any],
                             result: Dict[str, Any],
                             success: bool,
                             execution_time_ms: int):
        """Log tool usage to database."""
        if self.SessionLocal is None:
            return
        
        async with self.session() as session:
            if session is None:
                return
            
            audit = Audit(
                action=f"tool_usage:{tool_id}",
                agent_id=agent_id.value,
                details=json.dumps({
                    "task_id": task_id,
                    "workflow_id": workflow_id,
                    "parameters": parameters,
                    "result": result,
                    "success": success,
                    "execution_time_ms": execution_time_ms,
                })
            )
            session.add(audit)
    
    # Cleanup
    def cleanup_expired(self):
        """Clean up expired entries from working memory and sessions."""
        now = datetime.utcnow()
        
        # Clean working memory
        keys_to_delete = [
            key for key, entry in self._working_memory.items()
            if entry.expires_at and entry.expires_at < now
        ]
        for key in keys_to_delete:
            del self._working_memory[key]
        
        # Clean sessions
        sessions_to_delete = [
            sid for sid, session in self._session_contexts.items()
            if session.expires_at and session.expires_at < now
        ]
        for sid in sessions_to_delete:
            del self._session_contexts[sid]


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def initialize_memory(database_url: Optional[str] = None) -> MemoryManager:
    """Initialize the global memory manager."""
    global _memory_manager
    _memory_manager = MemoryManager(database_url)
    return _memory_manager