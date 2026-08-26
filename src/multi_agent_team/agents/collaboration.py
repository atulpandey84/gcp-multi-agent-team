"""
Multi-agent collaboration framework implementing Sections 5, 9, and 21.
Evidence-based collaboration, peer review, quality gate enforcement,
and separation of duties.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .base import AgentMessage, Task, QualityGateResult, AgentMemory


@dataclass
class CollaborationEvidence:
    """Evidence package for collaboration per Section 2.4 (Evidence over assertions)."""
    source_agent: str
    evidence_type: str  # "repository", "test", "telemetry", "configuration", "document"
    evidence_reference: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    verified: bool = False


@dataclass
class PeerReviewRequest:
    """Peer approval request per Section 7 (Authority Model - Level 2)."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requesting_agent: str
    target_agent: str
    review_type: str  # "architecture", "security", "implementation", "operational"
    evidence_required: List[str] = field(default_factory=list)
    required_approvers: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, under_review, approved, rejected, escalated
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SeparationOfDutiesCheck:
    """Enforce no single agent can design+implement+approve+deploy+validate."""
    task_id: str
    agent_id: str
    action: str
    permitted: bool
    conflicts: List[str] = field(default_factory=list)


class CollaborationEngine:
    """
    Central collaboration engine implementing Section 9 (Collaboration Protocol)
    and Section 21 (Collaboration Patterns).
    
    All agents must communicate through structured tasks with:
    - Evidence collection
    - Peer review when required by authority model
    - Quality gate enforcement
    - Explicit separation of duties checks
    """
    
    def __init__(self):
        self.pending_reviews: Dict[str, PeerReviewRequest] = {}
        self.evidence_registry: Dict[str, List[CollaborationEvidence]] = {}
        self.duty_violations: List[Dict[str, Any]] = []
        self.collaboration_log: List[Dict[str, Any]] = []
    
    def request_peer_review(self, from_agent: str, to_agent: str, 
                           review_type: str, task_id: str,
                           evidence_refs: List[str]) -> PeerReviewRequest:
        """Initiate peer review per authority model Level 2."""
        req = PeerReviewRequest(
            requesting_agent=from_agent,
            target_agent=to_agent,
            review_type=review_type,
            evidence_required=evidence_refs,
            required_approvers=[to_agent]
        )
        self.pending_reviews[req.request_id] = req
        self.collaboration_log.append({
            "type": "peer_review_requested",
            "request_id": req.request_id,
            "from": from_agent,
            "to": to_agent,
            "review_type": review_type,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        return req
    
    def record_evidence(self, agent_id: str, evidence: CollaborationEvidence):
        """Record structured evidence per Section 2.4."""
        if agent_id not in self.evidence_registry:
            self.evidence_registry[agent_id] = []
        self.evidence_registry[agent_id].append(evidence)
    
    def check_separation_of_duties(self, agent_id: str, task: Task, 
                                   context: Dict[str, Any]) -> SeparationOfDutiesCheck:
        """
        Enforce separation of duties. No agent should design, implement,
        approve, deploy, and validate the same change.
        """
        # This is a structural check - in full implementation,
        # this would check the task history for conflicting actions
        conflicts = []
        permitted = True
        
        # Check if agent already performed design/approval/deployment
        # in this workflow context
        workflow_state = context.get("current_workflow_state", {})
        completed_agents = workflow_state.get("completed_agents", [])
        
        # For high-risk actions, require that different agents
        # have performed previous stages
        if task.objective and "deploy" in task.objective.lower():
            # Production deployment requires operational readiness
            # from different agent
            if "sre_observability_engineer" not in completed_agents:
                conflicts.append("missing_operational_readiness_review")
                permitted = False
        
        check = SeparationOfDutiesCheck(
            task_id=task.task_id,
            agent_id=agent_id,
            action="execute",
            permitted=permitted,
            conflicts=conflicts
        )
        
        if not permitted:
            self.duty_violations.append({
                "task_id": task.task_id,
                "agent": agent_id,
                "conflicts": conflicts,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return check
    
    def enforce_quality_gate(self, gate_name: str, agent_id: str,
                            evidence: List[str], context: Dict[str, Any]) -> QualityGateResult:
        """Enforce quality gate with evidence verification."""
        # Gather evidence from collaboration registry
        verified_evidence = []
        for ref in evidence:
            verified = False
            for agent_evidence in self.evidence_registry.values():
                for ev in agent_evidence:
                    if ev.evidence_reference == ref and ev.verified:
                        verified = True
                        verified_evidence.append(ref)
            if not verified:
                # Evidence not verified - flag for review
                verified_evidence.append(f"{ref}(unverified)")
        
        passed = len(verified_evidence) > 0 and all(
            "(unverified)" not in e for e in verified_evidence
        ) if evidence else False
        
        result = QualityGateResult(
            gate_name=gate_name,
            passed=passed,
            owner=agent_id,
            checks=[{
                "check": "evidence_verified",
                "passed": passed,
                "evidence_count": len(verified_evidence)
            }],
            evidence=verified_evidence
        )
        
        self.collaboration_log.append({
            "type": "quality_gate",
            "gate": gate_name,
            "agent": agent_id,
            "passed": passed,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return result
    
    def coordinate_multi_agent_review(self, task_id: str, required_reviewers: List[str],
                                     task_objective: str) -> Dict[str, Any]:
        """
        Coordinate review from multiple specialist agents per Section 6.
        This ensures architecture, security, and operational perspectives
        are all incorporated.
        """
        reviewers_status = {}
        for reviewer in required_reviewers:
            reviewers_status[reviewer] = "pending"
        
        return {
            "task_id": task_id,
            "objective": task_objective,
            "reviewers_required": required_reviewers,
            "reviewers_status": reviewers_status,
            "coordinated_by": "collaboration_engine",
            "timestamp": datetime.utcnow().isoformat()
        }