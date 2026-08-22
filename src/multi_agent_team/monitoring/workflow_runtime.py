import asyncio
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


PILOT_STAGES = [
    ("product_owner", "Product", "Shape the requirement & acceptance criteria", "senior_reasoning", "Approved business requirements & acceptance criteria"),
    ("project_manager", "Delivery", "Plan delivery timeline, risks & dependencies", "fast_agent", "RAID log and delivery schedule created"),
    ("engineering_orchestrator", "Engineering Governance", "Decompose engineering tasks and select specialist agents", "architecture_critical", "Task graph & agent delegation plan finalized"),
    ("solution_architect", "Architecture", "Design solution architecture & NFR matrix", "architecture_critical", "HLD, API contract & NFR matrix drafted"),
    ("platform_architect", "Architecture", "Assess Landing Zone fit & network topology", "architecture_critical", "Shared VPC & Terraform module design approved"),
    ("security_architect", "Architecture", "Conduct threat model & establish Zero Trust controls", "senior_reasoning", "Security controls & KMS encryption policy verified"),
    ("finops_engineer", "DevOps", "Assess cloud cost & budget impact", "fast_agent", "Cost estimate & resource optimization approved"),
    ("devops_lead", "DevOps", "Define GitOps deployment strategy", "senior_reasoning", "Deployment standards & environment gates set"),
    ("cloud_infrastructure_engineer", "DevOps", "Draft Terraform IaC modules for cloud resources", "coding", "Terraform / IaC modules validated with static checks"),
    ("cicd_engineer", "DevOps", "Configure CI/CD promotion pipelines & artifact registry", "fast_coding", "Cloud Build pipelines and security scans ready"),
    ("sre_observability_engineer", "DevOps", "Configure SLOs, alerts & monitoring dashboards", "senior_reasoning", "Cloud Monitoring dashboards & alert policies configured"),
    ("qa_lead", "Testing", "Verify quality gates & automated test suites", "senior_reasoning", "All functional and regression test gates passed"),
    ("application_management_lead", "Application Management", "Confirm operational readiness & support runbooks", "fast_agent", "Operational readiness checklist approved"),
    ("engineering_orchestrator", "Engineering Governance", "Package evidence, verify audit trail & complete release", "architecture_critical", "Landing Zone application environment fully provisioned"),
]


@dataclass
class WorkflowTask:
    id: str
    agent_id: str
    team: str
    title: str
    model_policy: str
    output_summary: str = ""
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

        is_azure = "azure" in objective.lower()
        cloud_provider = "Azure" if is_azure else ("GCP" if "gcp" in objective.lower() else "Cloud")

        custom_stages = []
        for agent_id, team, title, model, output_summary in PILOT_STAGES:
            c_title = title.replace("GCP", cloud_provider).replace("cloud", cloud_provider.lower())
            c_summary = output_summary.replace("GCP", cloud_provider)
            if is_azure and "Shared VPC" in c_summary:
                c_summary = c_summary.replace("Shared VPC", "Azure VNet / Hub-and-Spoke")
            custom_stages.append((agent_id, team, c_title, model, c_summary))

        tasks = [
            WorkflowTask(
                id=f"{run_id[:8]}-{index + 1}",
                agent_id=agent_id,
                team=team,
                title=title,
                model_policy=model,
                output_summary=output_summary,
            )
            for index, (agent_id, team, title, model, output_summary) in enumerate(custom_stages)
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
            for index, task in enumerate(run.tasks):
                run.current_task_id = task.id
                task.status = "running"
                task.started_at = datetime.now(timezone.utc).isoformat()
                self._emit(run, "task_started", {"task_id": task.id, "agent_id": task.agent_id, "team": task.team})

                next_task = run.tasks[index + 1] if index + 1 < len(run.tasks) else None
                collaboration_msg = {
                    "sender": task.agent_id,
                    "sender_team": task.team,
                    "receiver": next_task.agent_id if next_task else "system",
                    "receiver_team": next_task.team if next_task else "Governance",
                    "action": task.title,
                    "artifact": task.output_summary,
                }
                self._emit(run, "collaboration_message", collaboration_msg)

                for progress in range(25, 101, 25):
                    await asyncio.sleep(0.12)
                    task.progress = progress
                    run.progress = round(((index + progress / 100) / len(run.tasks)) * 100)
                    self._emit(run, "task_progress", {"task_id": task.id, "agent_id": task.agent_id, "progress": progress})

                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc).isoformat()
                self._emit(run, "task_completed", {"task_id": task.id, "agent_id": task.agent_id, "output": task.output_summary})
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
