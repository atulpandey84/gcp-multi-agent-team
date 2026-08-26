"""
Base agent classes and infrastructure for the Multi-Agent Engineering Organization.
Implements the shared agent contract from MULTI_AGENT_TEAM_SPECIFICATION.md Section 4.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal
from enum import Enum
import uuid
from datetime import datetime
import yaml
from pathlib import Path


class AuthorityLevel(Enum):
    AUTONOMOUS = "autonomous"
    PEER_APPROVAL = "peer_approval"
    HUMAN_APPROVAL = "human_approval"


class TaskStatus(Enum):
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


class Environment(Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class AgentMemory:
    """Layered memory architecture per Section 11."""
    working: Dict[str, Any] = field(default_factory=dict)  # Short-lived task context
    project: Dict[str, Any] = field(default_factory=dict)  # Persistent project-specific
    institutional: Dict[str, Any] = field(default_factory=dict)  # Reusable engineering knowledge
    episodic: List[Dict[str, Any]] = field(default_factory=list)  # What happened
    semantic: Dict[str, Any] = field(default_factory=dict)  # Searchable technical knowledge


@dataclass
class AgentAuthority:
    """Authority model per Section 7."""
    autonomous: List[str] = field(default_factory=list)
    peer_approval: List[str] = field(default_factory=list)
    human_approval: List[str] = field(default_factory=list)


@dataclass
class AgentContract:
    """Complete agent contract per Section 4."""
    id: str
    role: str
    team: str
    mission: str
    seniority: str
    responsibilities: List[str]
    non_responsibilities: List[str]
    authority: AgentAuthority
    capabilities: List[str]
    tools: List[str]
    memory: AgentMemory
    inputs: List[str]
    outputs: List[str]
    collaborators: List[str]
    escalation_rules: List[str]
    quality_gates: List[str]
    definition_of_done: List[str]
    security_constraints: List[str]
    failure_policy: List[str]


@dataclass
class AgentMessage:
    """Structured agent communication per Section 5."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    type: Literal["request", "response", "review", "approval", "escalation", "status"] = "request"
    objective: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    requested_action: str = ""
    expected_output: str = ""
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Task:
    """Task lifecycle per Section 23."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = ""
    status: TaskStatus = TaskStatus.CREATED
    assigned_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    approvals: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    assigned_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGateResult:
    """Quality gate evaluation result per Section 15."""
    gate_name: str
    passed: bool
    owner: str
    checks: List[Dict[str, Any]]
    evidence: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ApprovalRequest:
    """Human approval request per Section 2.3 and Section 18."""
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requester: str = ""
    action: str = ""
    agent_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    risk: str = "medium"
    affected_components: List[str] = field(default_factory=list)
    implementation_plan: str = ""
    validation_plan: str = ""
    rollback_plan: str = ""
    security_impact: str = ""
    cost_impact: str = ""
    monitoring_plan: str = ""
    status: Literal["pending", "approved", "rejected", "consumed"] = "pending"
    approver: Optional[str] = None
    approver_comments: Optional[str] = None
    requested_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    decided_at: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all agents implementing the shared contract (Section 4)
    and behavioral contract (Section 5).
    """
    
    def __init__(self, contract: AgentContract):
        self.contract = contract
        self.memory = AgentMemory()
        self._load_institutional_memory()
    
    @abstractmethod
    def execute(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary responsibility for a given task."""
        pass
    
    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output meets definition of done."""
        pass
    
    def can_act_autonomously(self, action: str) -> bool:
        """Check if agent can perform action without approval."""
        return action in self.contract.authority.autonomous
    
    def requires_peer_approval(self, action: str) -> bool:
        """Check if action requires peer approval."""
        return action in self.contract.authority.peer_approval
    
    def requires_human_approval(self, action: str) -> bool:
        """Check if action requires human approval."""
        return action in self.contract.authority.human_approval
    
    def _load_institutional_memory(self):
        """Load institutional memory from organizational knowledge base."""
        # This would load from the semantic knowledge base
        pass
    
    def record_decision(self, decision: Dict[str, Any]):
        """Record important decision to episodic memory."""
        self.memory.episodic.append({
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "agent": self.contract.id
        })
    
    def add_evidence(self, evidence: str):
        """Add evidence to working memory."""
        if "evidence" not in self.memory.working:
            self.memory.working["evidence"] = []
        self.memory.working["evidence"].append(evidence)
    
    def add_assumption(self, assumption: str):
        """Explicitly label assumption per Section 2.4."""
        if "assumptions" not in self.memory.working:
            self.memory.working["assumptions"] = []
        self.memory.working["assumptions"].append({
            "assumption": assumption,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.contract.id
        })
    
    def escalate(self, reason: str, target: str, context: Dict[str, Any]) -> AgentMessage:
        """Create escalation message per Section 10."""
        return AgentMessage(
            task_id=context.get("task_id", ""),
            sender=self.contract.id,
            recipients=[target],
            type="escalation",
            objective=f"Escalation: {reason}",
            context=context,
            evidence=self.memory.working.get("evidence", []),
            assumptions=self.memory.working.get("assumptions", []),
            requested_action="resolve_escalation",
            expected_output="resolution_or_guidance",
            priority="critical"
        )
    
    def communicate(self, recipients: List[str], message: AgentMessage) -> AgentMessage:
        """Send structured message to other agents."""
        message.sender = self.contract.id
        message.recipients = recipients
        return message


def load_agent_contracts() -> Dict[str, AgentContract]:
    """Load all agent contracts from config/agents_contracts.yaml."""
    contracts_path = Path(__file__).resolve().parents[3] / "config" / "agents_contracts.yaml"
    if not contracts_path.exists():
        raise FileNotFoundError(f"Contracts file not found: {contracts_path}")
    
    with open(contracts_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    
    contracts = {}
    for agent_data in data.get("agents", []):
        contract = _parse_contract(agent_data)
        contracts[contract.id] = contract
    
    return contracts


def _parse_contract(data: Dict[str, Any]) -> AgentContract:
    """Parse raw YAML data into AgentContract."""
    authority = AgentAuthority(
        autonomous=data.get("authority", {}).get("autonomous", []),
        peer_approval=data.get("authority", {}).get("peer_approval", []),
        human_approval=data.get("authority", {}).get("human_approval", [])
    )
    
    memory = AgentMemory(
        working=data.get("memory", {}).get("working", []),
        project=data.get("memory", {}).get("project", []),
        institutional=data.get("memory", {}).get("institutional", [])
    )
    
    return AgentContract(
        id=data["id"],
        role=data["role"],
        team=data["team"],
        mission=data["mission"],
        seniority=data["seniority"],
        responsibilities=data["responsibilities"],
        non_responsibilities=data["non_responsibilities"],
        authority=authority,
        capabilities=data["capabilities"],
        tools=data["tools"],
        memory=memory,
        inputs=data["inputs"],
        outputs=data["outputs"],
        collaborators=data["collaborators"],
        escalation_rules=data["escalation_rules"],
        quality_gates=data["quality_gates"],
        definition_of_done=data["definition_of_done"],
        security_constraints=data["security_constraints"],
        failure_policy=data["failure_policy"]
    )