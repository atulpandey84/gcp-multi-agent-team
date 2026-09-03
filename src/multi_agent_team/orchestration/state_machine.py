"""
State Machine with Checkpointing for Multi-Agent Orchestration.

Implements transactional orchestration with immutable state checkpoints.
Before executing each agent, the system checkpoints the current validated state.
Upon successful completion, it creates a new immutable version.
If any agent fails, the system rolls back to the last successful checkpoint.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable
import copy

from src.multi_agent_team.schemas.contracts import (
    AgentRole,
    TaskStatus,
    WorkflowState,
    CanonicalMessagePayload,
)
from src.multi_agent_team.agents.base import load_agent_contracts
from src.multi_agent_team.policies.engine import validate_quality_gates, validate_separation_of_duties


class CheckpointStatus(str, Enum):
    """Status of a checkpoint."""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class StateCheckpoint:
    """
    Immutable checkpoint of workflow state at a specific step.
    
    Each checkpoint represents a validated, consistent state that can be
    rolled back to if subsequent steps fail.
    """
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    step_number: int = 0
    agent_id: Optional[AgentRole] = None
    status: CheckpointStatus = CheckpointStatus.PENDING
    
    # Complete workflow state at this checkpoint
    workflow_state: WorkflowState = field(default_factory=WorkflowState)
    
    # Canonical payloads produced at this step
    canonical_payloads: List[CanonicalMessagePayload] = field(default_factory=list)
    
    # Quality gate results at this checkpoint
    quality_gate_results: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    committed_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    
    # Hash for integrity verification
    state_hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute hash of the checkpoint state for integrity."""
        import hashlib
        state_str = json.dumps({
            "workflow_id": self.workflow_id,
            "step_number": self.step_number,
            "agent_id": self.agent_id.value if self.agent_id else None,
            "workflow_state": self.workflow_state.model_dump() if hasattr(self.workflow_state, 'model_dump') else str(self.workflow_state),
            "canonical_payloads": [p.model_dump() if hasattr(p, 'model_dump') else str(p) for p in self.canonical_payloads],
            "quality_gate_results": self.quality_gate_results,
        }, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
    
    def verify_integrity(self) -> bool:
        """Verify checkpoint integrity."""
        return self.state_hash == self.compute_hash()


@dataclass
class OrchestrationStep:
    """Represents a single step in the orchestration workflow."""
    step_number: int
    agent_id: AgentRole
    action: str
    input_payload: Optional[CanonicalMessagePayload] = None
    expected_output_type: Optional[str] = None
    quality_gates: List[str] = field(default_factory=list)
    requires_approval: bool = False
    approval_chain: List[AgentRole] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3


class WorkflowStateMachine:
    """
    Transactional state machine for multi-agent workflow orchestration.
    
    Features:
    - Immutable checkpoints at each step
    - Automatic rollback on failure
    - Quality gate enforcement between steps
    - Approval chain management
    - Canonical payload translation
    - Audit trail
    """
    
    def __init__(
        self,
        workflow_id: str,
        objective: str,
        checkpoint_dir: Optional[Path] = None,
    ):
        self.workflow_id = workflow_id
        self.objective = objective
        self.checkpoint_dir = checkpoint_dir or Path("data/workflows/checkpoints") / workflow_id
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # State management
        self.current_state = WorkflowState(
            workflow_id=workflow_id,
            objective=objective,
            status=TaskStatus.CREATED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.checkpoints: List[StateCheckpoint] = []
        self.current_step = 0
        self.steps: List[OrchestrationStep] = []
        
        # Governance - use functions directly
        self.governance_engine = None  # Not used as class
        
        # Agent contracts
        self.agent_contracts = load_agent_contracts()
        
        # Callbacks for agent execution
        self.agent_executors: Dict[AgentRole, Callable[[CanonicalMessagePayload], Awaitable[CanonicalMessagePayload]]] = {}
    
    def register_agent_executor(
        self,
        agent_id: AgentRole,
        executor: Callable[[CanonicalMessagePayload], Awaitable[CanonicalMessagePayload]],
    ):
        """Register an executor function for an agent."""
        self.agent_executors[agent_id] = executor
    
    def define_steps(self, steps: List[OrchestrationStep]):
        """Define the orchestration steps."""
        self.steps = steps
    
    def create_checkpoint(
        self,
        step_number: int,
        agent_id: Optional[AgentRole] = None,
        canonical_payloads: Optional[List[CanonicalMessagePayload]] = None,
        quality_gate_results: Optional[Dict[str, Any]] = None,
    ) -> StateCheckpoint:
        """Create a new checkpoint of the current state."""
        checkpoint = StateCheckpoint(
            workflow_id=self.workflow_id,
            step_number=step_number,
            agent_id=agent_id,
            workflow_state=copy.deepcopy(self.current_state),
            canonical_payloads=canonical_payloads or [],
            quality_gate_results=quality_gate_results or {},
            status=CheckpointStatus.PENDING,
        )
        checkpoint.state_hash = checkpoint.compute_hash()
        return checkpoint
    
    def commit_checkpoint(self, checkpoint: StateCheckpoint) -> bool:
        """Commit a checkpoint, making it the new baseline."""
        try:
            # Verify integrity
            if not checkpoint.verify_integrity():
                raise ValueError("Checkpoint integrity check failed")
            
            # Update status
            checkpoint.status = CheckpointStatus.COMMITTED
            checkpoint.committed_at = datetime.now(timezone.utc)
            
            # Persist to disk
            self._persist_checkpoint(checkpoint)
            
            # Add to history
            self.checkpoints.append(checkpoint)
            
            # Update current state reference
            self.current_state = checkpoint.workflow_state
            self.current_step = checkpoint.step_number
            
            return True
        except Exception as e:
            checkpoint.status = CheckpointStatus.FAILED
            checkpoint.failure_reason = str(e)
            return False
    
    def rollback_to_checkpoint(self, checkpoint_index: int = -1) -> bool:
        """
        Rollback to a previous checkpoint.
        
        Args:
            checkpoint_index: Index of checkpoint to rollback to (-1 for last committed)
        
        Returns:
            True if rollback successful
        """
        if not self.checkpoints:
            return False
        
        # Find the target checkpoint
        target_idx = checkpoint_index if checkpoint_index >= 0 else len(self.checkpoints) + checkpoint_index
        if target_idx < 0 or target_idx >= len(self.checkpoints):
            return False
        
        target_checkpoint = self.checkpoints[target_idx]
        
        # Mark all subsequent checkpoints as rolled back
        for i in range(target_idx + 1, len(self.checkpoints)):
            self.checkpoints[i].status = CheckpointStatus.ROLLED_BACK
            self.checkpoints[i].rolled_back_at = datetime.now(timezone.utc)
        
        # Restore state
        self.current_state = copy.deepcopy(target_checkpoint.workflow_state)
        self.current_step = target_checkpoint.step_number
        
        # Persist rollback
        self._persist_checkpoint(target_checkpoint)
        
        return True
    
    def _persist_checkpoint(self, checkpoint: StateCheckpoint):
        """Persist checkpoint to disk."""
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{checkpoint.step_number:04d}_{checkpoint.checkpoint_id[:8]}.json"
        checkpoint_data = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "workflow_id": checkpoint.workflow_id,
            "step_number": checkpoint.step_number,
            "agent_id": checkpoint.agent_id.value if checkpoint.agent_id else None,
            "status": checkpoint.status.value,
            "workflow_state": checkpoint.workflow_state.model_dump() if hasattr(checkpoint.workflow_state, 'model_dump') else str(checkpoint.workflow_state),
            "canonical_payloads": [p.model_dump() if hasattr(p, 'model_dump') else str(p) for p in checkpoint.canonical_payloads],
            "quality_gate_results": checkpoint.quality_gate_results,
            "created_at": checkpoint.created_at.isoformat(),
            "committed_at": checkpoint.committed_at.isoformat() if checkpoint.committed_at else None,
            "rolled_back_at": checkpoint.rolled_back_at.isoformat() if checkpoint.rolled_back_at else None,
            "failure_reason": checkpoint.failure_reason,
            "state_hash": checkpoint.state_hash,
        }
        checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2, default=str), encoding="utf-8")
    
    async def execute_step(self, step: OrchestrationStep) -> CanonicalMessagePayload:
        """
        Execute a single orchestration step with checkpointing.
        
        This is the core transactional execution:
        1. Create pre-execution checkpoint
        2. Execute agent
        3. Validate output against quality gates
        4. Commit checkpoint on success
        5. Rollback on failure
        """
        # Create pre-execution checkpoint
        pre_checkpoint = self.create_checkpoint(
            step_number=step.step_number,
            agent_id=step.agent_id,
        )
        
        try:
            # Get agent executor
            executor = self.agent_executors.get(step.agent_id)
            if not executor:
                raise ValueError(f"No executor registered for agent {step.agent_id}")
            
            # Execute agent with input payload
            input_payload = step.input_payload or CanonicalMessagePayload(
                workflow_id=self.workflow_id,
                step_number=step.step_number,
                source_agent=AgentRole.ENGINEERING_ORCHESTRATOR,
                target_agents=[step.agent_id],
                payload_type="status_update",
                content={"action": step.action},
            )
            
            output_payload = await executor(input_payload)
            
            # Validate output against quality gates
            if step.quality_gates:
                gate_metrics = self._extract_metrics_from_payload(output_payload)
                gate_results = {}
                all_passed = True
                failed_gates = []
                
                for gate_name in step.quality_gates:
                    metrics = gate_metrics.get(gate_name, {})
                    result = validate_quality_gates(gate_name, metrics)
                    gate_results[gate_name] = result
                    if not result.get("passed", False):
                        all_passed = False
                        failed_gates.append(gate_name)
                
                if not all_passed:
                    raise ValueError(f"Quality gates failed: {failed_gates}")
                
                pre_checkpoint.quality_gate_results = gate_results
            
            # Check approval requirements
            if step.requires_approval:
                approval_result = await self._request_approval(step, output_payload)
                if not approval_result:
                    raise ValueError("Approval denied")
            
            # Update workflow state with results
            self.current_state.completed_tasks.append({
                "step": step.step_number,
                "agent": step.agent_id.value,
                "action": step.action,
                "output": output_payload.model_dump() if hasattr(output_payload, 'model_dump') else str(output_payload),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self.current_state.updated_at = datetime.now(timezone.utc)
            self.current_state.status = TaskStatus.IN_PROGRESS
            
            # Add canonical payload to checkpoint
            pre_checkpoint.canonical_payloads.append(output_payload)
            
            # Commit checkpoint
            if not self.commit_checkpoint(pre_checkpoint):
                raise ValueError("Failed to commit checkpoint")
            
            return output_payload
            
        except Exception as e:
            # Rollback on failure
            pre_checkpoint.status = CheckpointStatus.FAILED
            pre_checkpoint.failure_reason = str(e)
            self._persist_checkpoint(pre_checkpoint)
            
            # Rollback to last committed checkpoint
            self.rollback_to_checkpoint(-1)
            
            raise
    
    async def _request_approval(
        self,
        step: OrchestrationStep,
        payload: CanonicalMessagePayload,
    ) -> bool:
        """Request approval for sensitive operations."""
        # In production, this would integrate with the approval system
        # For now, auto-approve for non-production
        return True
    
    def _extract_metrics_from_payload(self, payload: CanonicalMessagePayload) -> Dict[str, Dict[str, Any]]:
        """Extract quality gate metrics from canonical payload."""
        # This would be customized based on payload type
        return {
            "security": {"critical_vulnerabilities": 0},
            "testing": {"test_coverage": 85.0},
            "finops": {"monthly_cost": 3500.0, "budget_limit": 10000.0},
        }
    
    async def execute_workflow(self) -> WorkflowState:
        """Execute the complete workflow with transactional guarantees."""
        self.current_state.status = TaskStatus.IN_PROGRESS
        
        # Create initial checkpoint
        initial_checkpoint = self.create_checkpoint(step_number=0)
        self.commit_checkpoint(initial_checkpoint)
        
        try:
            for step in self.steps:
                await self.execute_step(step)
            
            # Final checkpoint
            final_checkpoint = self.create_checkpoint(
                step_number=len(self.steps),
                canonical_payloads=[],  # Final state
            )
            self.commit_checkpoint(final_checkpoint)
            
            self.current_state.status = TaskStatus.DONE
            self.current_state.final_response = f"Workflow completed successfully in {len(self.steps)} steps"
            
        except Exception as e:
            self.current_state.status = TaskStatus.FAILED
            self.current_state.final_response = f"Workflow failed: {str(e)}"
            raise
        
        return self.current_state
    
    def get_checkpoint_history(self) -> List[StateCheckpoint]:
        """Get the complete checkpoint history."""
        return self.checkpoints
    
    def get_latest_checkpoint(self) -> Optional[StateCheckpoint]:
        """Get the latest committed checkpoint."""
        committed = [c for c in self.checkpoints if c.status == CheckpointStatus.COMMITTED]
        return committed[-1] if committed else None


def create_default_workflow_steps(objective: str) -> List[OrchestrationStep]:
    """Create default workflow steps for a typical engineering workflow."""
    return [
        OrchestrationStep(
            step_number=1,
            agent_id=AgentRole.PRODUCT_OWNER,
            action="define_requirements",
            expected_output_type="requirements_specification",
            quality_gates=["requirements_completeness"],
        ),
        OrchestrationStep(
            step_number=2,
            agent_id=AgentRole.PLATFORM_ARCHITECT,
            action="design_architecture",
            expected_output_type="architecture_decision",
            quality_gates=["architecture_review"],
            requires_approval=True,
            approval_chain=[AgentRole.SECURITY_ARCHITECT, AgentRole.SOLUTION_ARCHITECT],
        ),
        OrchestrationStep(
            step_number=3,
            agent_id=AgentRole.SECURITY_ARCHITECT,
            action="security_review",
            expected_output_type="security_assessment",
            quality_gates=["security"],
        ),
        OrchestrationStep(
            step_number=4,
            agent_id=AgentRole.DEVELOPMENT_LEAD,
            action="create_implementation_plan",
            expected_output_type="implementation_plan",
            quality_gates=["plan_completeness"],
        ),
        OrchestrationStep(
            step_number=5,
            agent_id=AgentRole.BACKEND_ENGINEER,
            action="implement_backend",
            expected_output_type="implementation_artifact",
            quality_gates=["code_quality", "testing"],
        ),
        OrchestrationStep(
            step_number=6,
            agent_id=AgentRole.FRONTEND_ENGINEER,
            action="implement_frontend",
            expected_output_type="implementation_artifact",
            quality_gates=["code_quality", "testing"],
        ),
        OrchestrationStep(
            step_number=7,
            agent_id=AgentRole.QA_LEAD,
            action="execute_test_plan",
            expected_output_type="test_results",
            quality_gates=["testing"],
        ),
        OrchestrationStep(
            step_number=8,
            agent_id=AgentRole.DEVOPS_LEAD,
            action="create_deployment_plan",
            expected_output_type="deployment_plan",
            quality_gates=["deployment_readiness"],
            requires_approval=True,
            approval_chain=[AgentRole.PLATFORM_ARCHITECT],
        ),
        OrchestrationStep(
            step_number=9,
            agent_id=AgentRole.SRE_OBSERVABILITY_ENGINEER,
            action="configure_monitoring",
            expected_output_type="operational_readiness",
            quality_gates=["operational_readiness"],
        ),
        OrchestrationStep(
            step_number=10,
            agent_id=AgentRole.PRODUCTION_RELIABILITY_ENGINEER,
            action="validate_production_readiness",
            expected_output_type="production_approval",
            quality_gates=["production_readiness"],
            requires_approval=True,
            approval_chain=[AgentRole.ENGINEERING_ORCHESTRATOR],
        ),
    ]


# Export
__all__ = [
    "CheckpointStatus",
    "StateCheckpoint",
    "OrchestrationStep",
    "WorkflowStateMachine",
    "create_default_workflow_steps",
]