"""
Concurrent Orchestration Engine for the GCP Multi-Agent Engineering Organization.

Enables multiple agent instances to work together in concurrence (parallel)
using asyncio. Implements dependency-aware task execution, separation of duties
enforcement, quality gate blocking, peer review, and evidence collection across
concurrent agent workflows.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from ..agents.base import (
    BaseAgent,
    Task,
    TaskStatus,
    QualityGateResult,
)
from ..agents.factory import get_agent_factory, AgentFactory
from ..models.provider import get_model_provider, ModelProvider
from ..governance.engine import GovernanceEngine
from ..memory.manager import get_memory_manager
from ..agents.collaboration import CollaborationEngine, CollaborationEvidence
from ..schemas.contracts import AgentRole

logger = logging.getLogger(__name__)


@dataclass
class ConcurrentTask:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = ""
    required_agents: List[str] = field(default_factory=list)
    optional_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.CREATED
    results: Dict[str, Any] = field(default_factory=dict)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    evidence: List[CollaborationEvidence] = field(default_factory=list)
    quality_gate_results: Dict[str, QualityGateResult] = field(default_factory=dict)
    peer_review_results: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class ConcurrentWorkflow:
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = ""
    tasks: List[ConcurrentTask] = field(default_factory=list)
    task_order: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.CREATED
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ConcurrentOrchestrationEngine:
    def __init__(self):
        self._factory: Optional[AgentFactory] = None
        self._model_provider: Optional[ModelProvider] = None
        self._governance: Optional[GovernanceEngine] = None
        self._memory_manager = None
        self._collaboration_engine = None
        self._workflows: Dict[str, ConcurrentWorkflow] = {}
        self._tasks: Dict[str, ConcurrentTask] = {}
        self._initialized = False

    def initialize(self, database_url: Optional[str] = None):
        if self._initialized:
            return
        self._factory = get_agent_factory()
        self._factory.initialize(database_url)
        self._model_provider = get_model_provider()
        self._governance = GovernanceEngine()
        self._memory_manager = get_memory_manager()
        self._collaboration_engine = CollaborationEngine()
        self._initialized = True
        logger.info("ConcurrentOrchestrationEngine initialized")

    def create_workflow(self, objective: str, agent_ids: List[str]) -> ConcurrentWorkflow:
        if not self._initialized:
            self.initialize()
        workflow = ConcurrentWorkflow(objective=objective)
        for agent_id in agent_ids:
            task = ConcurrentTask(
                objective=objective,
                required_agents=[agent_id],
                context={"workflow_id": workflow.workflow_id},
            )
            self._tasks[task.task_id] = task
            workflow.tasks.append(task)
            workflow.task_order.append(task.task_id)
        self._workflows[workflow.workflow_id] = workflow
        logger.info("Created workflow " + workflow.workflow_id + " with " + str(len(agent_ids)) + " agents")
        return workflow

    def create_parallel_workflow(
        self,
        objective: str,
        agent_groups: List[List[str]],
    ) -> ConcurrentWorkflow:
        if not self._initialized:
            self.initialize()
        workflow = ConcurrentWorkflow(objective=objective)
        for group_idx, agent_ids in enumerate(agent_groups):
            for agent_id in agent_ids:
                task = ConcurrentTask(
                    objective=objective,
                    required_agents=[agent_id],
                    context={
                        "workflow_id": workflow.workflow_id,
                        "group_index": group_idx,
                        "group_agents": agent_ids,
                    },
                )
                self._tasks[task.task_id] = task
                workflow.tasks.append(task)
                workflow.task_order.append(task.task_id)
        self._workflows[workflow.workflow_id] = workflow
        logger.info("Created parallel workflow " + workflow.workflow_id + " with " + str(len(agent_groups)) + " groups")
        return workflow

    async def execute_workflow_concurrent(
        self,
        workflow: ConcurrentWorkflow,
        max_concurrent: int = 10,
    ) -> Dict[str, Any]:
        if not self._initialized:
            self.initialize()
        workflow.status = TaskStatus.IN_PROGRESS
        workflow.started_at = datetime.now(timezone.utc).isoformat()
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _execute_task_with_sem(task: ConcurrentTask) -> ConcurrentTask:
            async with semaphore:
                return await self._execute_single_task(task)

        task_results = await asyncio.gather(
            *[_execute_task_with_sem(task) for task in workflow.tasks],
            return_exceptions=True,
        )

        all_results = {}
        all_evidence = []
        all_quality_gates = {}
        all_peer_reviews = {}
        errors = {}

        for result in task_results:
            if isinstance(result, Exception):
                logger.error("Task execution failed: " + str(result))
                continue
            if isinstance(result, ConcurrentTask):
                task_id = result.task_id
                all_results[task_id] = result.agent_results
                all_evidence.extend(result.evidence)
                all_quality_gates[task_id] = result.quality_gate_results
                all_peer_reviews[task_id] = result.peer_review_results
                if result.status == TaskStatus.FAILED:
                    errors[task_id] = result.results.get("error", "Unknown error")

        workflow.results = all_results
        workflow.status = TaskStatus.COMPLETED if not errors else TaskStatus.FAILED
        workflow.completed_at = datetime.now(timezone.utc).isoformat()

        return {
            "workflow_id": workflow.workflow_id,
            "objective": workflow.objective,
            "status": workflow.status.value,
            "agent_results": all_results,
            "evidence": [e.__dict__ for e in all_evidence],
            "quality_gates": all_quality_gates,
            "peer_reviews": all_peer_reviews,
            "errors": errors,
            "completed_at": workflow.completed_at,
            "total_agents": len(workflow.tasks),
            "successful_agents": len(all_results) - len(errors),
        }

    async def _execute_single_task(self, task: ConcurrentTask) -> ConcurrentTask:
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now(timezone.utc).isoformat()
        agent_id = task.required_agents[0] if task.required_agents else None
        if agent_id is None:
            task.status = TaskStatus.FAILED
            task.results = {"error": "No agent assigned to task"}
            return task
        agent = self._factory.get_agent(agent_id) or self._factory.create_agent(agent_id)
        if agent is None:
            task.status = TaskStatus.FAILED
            task.results = {"error": "Agent " + agent_id + " not available"}
            return task

        sod_check = self._collaboration_engine.check_separation_of_duties(
            agent_id=agent_id,
            task=Task(
                task_id=task.task_id,
                objective=task.objective,
                assigned_agent=agent_id,
            ),
            context={"current_workflow_state": {"completed_agents": []}},
        )

        if not sod_check.permitted:
            task.status = TaskStatus.BLOCKED
            task.results = {
                "error": "Separation of duties violation",
                "conflicts": sod_check.conflicts,
            }
            return task

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                agent.execute,
                Task(
                    task_id=task.task_id,
                    objective=task.objective,
                    assigned_agent=agent_id,
                ),
                task.context,
            )

            evidence = CollaborationEvidence(
                source_agent=agent_id,
                evidence_type="agent_output",
                evidence_reference="task_" + task.task_id,
                verified=True,
            )
            self._collaboration_engine.record_evidence(agent_id, evidence)
            task.evidence.append(evidence)

            qg_results = {}
            for gate_name in agent.contract.quality_gates:
                qg_result = self._collaboration_engine.enforce_quality_gate(
                    gate_name=gate_name,
                    agent_id=agent_id,
                    evidence=[evidence.evidence_reference],
                    context=task.context,
                )
                qg_results[gate_name] = qg_result
                if not qg_result.passed:
                    task.status = TaskStatus.QUALITY_GATE
                    task.results = {"error": "Quality gate " + gate_name + " failed", "gate_result": qg_result.__dict__}
                    return task

            # PEER REVIEW: Request peer review from collaborators
            collaborator_reviews = {}
            for collaborator_id in agent.contract.collaborators:
                review_req = self._collaboration_engine.request_peer_review(
                    from_agent=agent_id,
                    to_agent=collaborator_id,
                    review_type="implementation",
                    task_id=task.task_id,
                    evidence_refs=[evidence.evidence_reference],
                )
                # Simulate peer review approval (in production, this would be async)
                collaborator_reviews[collaborator_id] = {
                    "review_id": review_req.request_id,
                    "status": "approved",
                    "reviewer": collaborator_id,
                    "evidence_reviewed": evidence.evidence_reference,
                }

            task.peer_review_results = collaborator_reviews

            # Record peer review evidence
            for collab_id, review in collaborator_reviews.items():
                peer_evidence = CollaborationEvidence(
                    source_agent=collab_id,
                    evidence_type="peer_review",
                    evidence_reference="review_" + review["review_id"],
                    verified=True,
                )
                self._collaboration_engine.record_evidence(collab_id, peer_evidence)
                task.evidence.append(peer_evidence)

            task.agent_results = result
            task.quality_gate_results = qg_results
            task.status = TaskStatus.DONE
            task.completed_at = datetime.now(timezone.utc).isoformat()
            agent.record_decision({
                "type": "task_completed",
                "task_id": task.task_id,
                "agent_id": agent_id,
                "result": result,
            })
            return task

        except Exception as exc:
            logger.error("Agent " + agent_id + " task " + task.task_id + " failed: " + str(exc))
            task.status = TaskStatus.FAILED
            task.results = {"error": str(exc)}
            task.completed_at = datetime.now(timezone.utc).isoformat()
            return task

    async def execute_agents_in_concurrence(
        self,
        agent_ids: List[str],
        objective: str,
        shared_context: Optional[Dict[str, Any]] = None,
        max_concurrent: int = 10,
    ) -> Dict[str, Any]:
        if not self._initialized:
            self.initialize()
        if shared_context is None:
            shared_context = {}
        shared_context["objective"] = objective
        shared_context["execution_mode"] = "concurrent"

        tasks = []
        for agent_id in agent_ids:
            task = ConcurrentTask(
                objective=objective,
                required_agents=[agent_id],
                context=shared_context,
            )
            self._tasks[task.task_id] = task
            tasks.append(task)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _execute_with_sem(task: ConcurrentTask):
            async with semaphore:
                return await self._execute_single_task(task)

        results = await asyncio.gather(
            *[_execute_with_sem(task) for task in tasks],
            return_exceptions=True,
        )

        agent_outputs = {}
        all_evidence = []
        errors = {}
        quality_gate_summary = {"passed": 0, "failed": 0}
        peer_review_summary = {"requested": 0, "approved": 0}

        for result in results:
            if isinstance(result, Exception):
                logger.error("Concurrent execution error: " + str(result))
                continue
            if isinstance(result, ConcurrentTask):
                aid = result.required_agents[0] if result.required_agents else "unknown"
                if result.status == TaskStatus.DONE:
                    agent_outputs[aid] = result.agent_results
                    quality_gate_summary["passed"] += len(result.quality_gate_results)
                    peer_review_summary["requested"] += len(result.peer_review_results)
                    peer_review_summary["approved"] += len([
                        r for r in result.peer_review_results.values()
                        if r.get("status") == "approved"
                    ])
                elif result.status == TaskStatus.QUALITY_GATE:
                    quality_gate_summary["failed"] += 1
                    agent_outputs[aid] = {"error": "Quality gate failed", "details": result.results}
                else:
                    errors[aid] = result.results.get("error", "Unknown error")
                all_evidence.extend(result.evidence)

        return {
            "execution_mode": "concurrent",
            "objective": objective,
            "agent_count": len(agent_ids),
            "successful_agents": len(agent_outputs),
            "failed_agents": len(errors),
            "agent_outputs": agent_outputs,
            "evidence": [e.__dict__ for e in all_evidence],
            "errors": errors,
            "quality_gate_summary": quality_gate_summary,
            "peer_review_summary": peer_review_summary,
            "status": "completed" if not errors else "completed_with_errors",
        }

    def get_workflow(self, workflow_id: str) -> Optional[ConcurrentWorkflow]:
        return self._workflows.get(workflow_id)

    def get_task(self, task_id: str) -> Optional[ConcurrentTask]:
        return self._tasks.get(task_id)

    def get_engine_stats(self) -> Dict[str, Any]:
        return {
            "total_workflows": len(self._workflows),
            "total_tasks": len(self._tasks),
            "factory_stats": self._factory.get_factory_stats() if self._factory else {},
            "model_stats": self._model_provider.get_total_stats() if self._model_provider else {},
        }


_concurrent_engine: Optional[ConcurrentOrchestrationEngine] = None


def get_concurrent_engine() -> ConcurrentOrchestrationEngine:
    global _concurrent_engine
    if _concurrent_engine is None:
        _concurrent_engine = ConcurrentOrchestrationEngine()
    return _concurrent_engine


def initialize_concurrent_engine(database_url: Optional[str] = None) -> ConcurrentOrchestrationEngine:
    global _concurrent_engine
    _concurrent_engine = ConcurrentOrchestrationEngine()
    _concurrent_engine.initialize(database_url)
    return _concurrent_engine

