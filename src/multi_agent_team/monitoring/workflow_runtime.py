import asyncio
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


PILOT_STAGES = [
    ("product_owner", "Shape the requirement", "senior_reasoning"),
    ("project_manager", "Plan delivery and dependencies", "fast_agent"),
    ("engineering_orchestrator", "Decompose the engineering workflow", "architecture_critical"),
    ("solution_architect", "Design the application solution", "architecture_critical"),
    ("platform_architect", "Assess Landing Zone fit", "architecture_critical"),
    ("security_architect", "Review threats and controls", "senior_reasoning"),
    ("finops_engineer", "Assess cost and budget impact", "fast_agent"),
    ("devops_lead", "Define delivery automation", "senior_reasoning"),
    ("cloud_infrastructure_engineer", "Prepare infrastructure as code", "coding"),
    ("cicd_engineer", "Build the promotion pipeline", "fast_coding"),
    ("sre_observability_engineer", "Configure SLOs and telemetry", "senior_reasoning"),
    ("qa_lead", "Validate quality gates", "senior_reasoning"),
    ("application_management_lead", "Confirm operational readiness", "fast_agent"),
    ("engineering_orchestrator", "Package evidence and close the workflow", "architecture_critical"),
]


@dataclass
class WorkflowTask:
    id: str
    agent_id: str
    title: str
    model_policy: str
    status: str = "queued"
    progress: int = 0
    started_at: str | None = None
    completed_at: str | None = None


@dataclass
class WorkflowRun:
    id: str
    objective: str
    status: str = "created"
    progress: int = 0
    current_task_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tasks: list[WorkflowTask] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)


class WorkflowRuntime:
    def __init__(self) -> None:
        self._runs: dict[str, WorkflowRun] = {}
        self._workers: dict[str, asyncio.Task] = {}
        self._subscribers: list[Callable[[dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers.append(callback)

    def list_runs(self) -> list[dict[str, Any]]:
        return [run.snapshot() for run in self._runs.values()]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        run = self._runs.get(run_id)
        return run.snapshot() if run else None

    def create_run(self, objective: str) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        tasks = [
            WorkflowTask(id=f"{run_id[:8]}-{index + 1}", agent_id=agent_id, title=title, model_policy=model)
            for index, (agent_id, title, model) in enumerate(PILOT_STAGES)
        ]
        run = WorkflowRun(id=run_id, objective=objective, tasks=tasks)
        self._runs[run_id] = run
        self._emit(run, "workflow_created", {"objective": objective})
        return run.snapshot()

    async def start_run(self, run_id: str) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        if run_id not in self._workers:
            self._workers[run_id] = asyncio.create_task(self._execute(run))
        return True

    async def _execute(self, run: WorkflowRun) -> None:
        run.status = "running"
        self._emit(run, "workflow_started", {})
        try:
            for task in run.tasks:
                run.current_task_id = task.id
                task.status = "running"
                task.started_at = datetime.now(timezone.utc).isoformat()
                self._emit(run, "task_started", {"task_id": task.id})
                for progress in range(20, 101, 20):
                    await asyncio.sleep(0.25)
                    task.progress = progress
                    run.progress = round(((run.tasks.index(task) + progress / 100) / len(run.tasks)) * 100)
                    self._emit(run, "task_progress", {"task_id": task.id, "progress": progress})
                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc).isoformat()
                self._emit(run, "task_completed", {"task_id": task.id})
            run.status = "completed"
            run.progress = 100
            run.current_task_id = None
            self._emit(run, "workflow_completed", {})
        except asyncio.CancelledError:
            run.status = "cancelled"
            self._emit(run, "workflow_cancelled", {})
            raise
        finally:
            self._workers.pop(run.id, None)

    def _emit(self, run: WorkflowRun, event_type: str, details: dict[str, Any]) -> None:
        run.updated_at = datetime.now(timezone.utc).isoformat()
        event = {"type": event_type, "run_id": run.id, "details": details, "run": run.snapshot()}
        run.events.append(event)
        for callback in list(self._subscribers):
            try:
                callback(event)
            except Exception:
                continue
