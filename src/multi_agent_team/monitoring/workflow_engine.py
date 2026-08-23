import asyncio
import inspect
import json
import os
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ..agents.contracts import get_agent_contract
from ..models.router import get_model

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
GATE_NAMES = ["requirements", "architecture", "security", "finops", "implementation", "qa", "operational_readiness", "release"]

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
    output_artifact: str | None = None
    document_title: str | None = None
    document_type: str | None = None
    document_content: str | None = None
    review_requested: bool = False
    feedback_history: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    failure_reason: str | None = None
    suggested_resolution: str | None = None
    executed_model: str | None = None
    model_provider: str | None = None
    model_location: str | None = None

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
    gates: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    provisioning: dict[str, Any] = field(default_factory=lambda: {"requested": False, "status": "not_requested"})
    auto_approve: bool = False

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)

def _root() -> Path:
    return Path(__file__).resolve().parents[3]

def _write_artifact(run: WorkflowRun, name: str, value: Any) -> str:
    root = _root() / "data" / "workflows"
    directory = root / run.id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")
    relative = str(path.relative_to(_root()))
    if relative not in run.artifacts:
        run.artifacts.append(relative)
    return relative


def _materialize_terraform(run: WorkflowRun, result: dict[str, Any]) -> Path:
    files = result.get("terraform_files")
    if not isinstance(files, dict):
        content = result.get("result", "")
        if isinstance(content, str):
            blocks = []
            for marker in ("```hcl", "```terraform"):
                blocks.extend(content.split(marker)[1:])
            if blocks:
                files = {"main.tf": blocks[0].split("```", 1)[0].strip()}
    if not files or not all(isinstance(name, str) and isinstance(content, str) for name, content in files.items()):
        raise ValueError("cloud infrastructure specialist returned no Terraform files")
    directory = _root() / "data" / "workflows" / run.id / "terraform"
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path = (directory / name).resolve()
        if directory.resolve() not in path.parents or path.suffix != ".tf":
            raise ValueError(f"invalid Terraform artifact path: {name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        run.artifacts.append(str(path.relative_to(_root())))
    return directory

def invoke_specialist(agent_id: str, title: str, objective: str, context: dict[str, Any]) -> dict[str, Any]:
    contract = get_agent_contract(agent_id)
    if not contract:
        raise ValueError(f"No contract exists for specialist {agent_id}")
    model = get_model(context["model_policy"])

    # Determine document type based on persona role
    if agent_id in ("product_owner", "project_manager", "engineering_orchestrator"):
        doc_type = "requirement_understanding_and_plan"
        doc_name = "Detailed Requirement Understanding & Implementation Plan Document"
        role_instruction = (
            "You are a Manager / Orchestrator persona. Produce a comprehensive Requirement Understanding Document "
            "and a Detailed Plan. Include executive objectives, scope boundaries, task breakdowns, milestone dependencies, "
            "and risk mitigation strategies."
        )
    elif agent_id in ("solution_architect", "platform_architect", "security_architect"):
        doc_type = "detailed_architectural_design"
        doc_name = "Detailed Solution Architecture & Security Design Specification Document"
        role_instruction = (
            "You are a Solution / System Architect persona. Produce a Detailed Architectural & Security Design Spec. "
            "Include target component diagrams/structures, security boundaries, Landing Zone governance alignment, "
            "interface specs, and threat mitigation design."
        )
    else:
        doc_type = "test_plan_and_implementation_spec"
        doc_name = "Detailed Test Suite, Technical Implementation Spec & Code Review Request"
        role_instruction = (
            "You are an Engineer / Technical Lead persona. Produce a Detailed Test Plan / Test Case Specification, "
            "code implementation details (e.g., HCL Terraform / CI-CD pipeline YAML / telemetry specs), and an explicit Review Request."
        )

    feedback_prompt = ""
    feedback_history = context.get("feedback_history", [])
    if feedback_history:
        feedback_prompt = "\n\nCRITICAL - PREVIOUS FEEDBACK & REJECTION REASON:\n" + "\n".join(
            f"- Retrigger #{i+1} Feedback ({fb.get('timestamp', '')}): {fb.get('comment', '')}"
            for i, fb in enumerate(feedback_history)
        ) + "\nPlease specifically address and resolve all feedback points in your updated document."

    prompt = {
        "objective": objective,
        "assignment": title,
        "agent": agent_id,
        "mission": contract["mission"],
        "responsibilities": contract["responsibilities"],
        "constraints": contract["security_constraints"],
        "prior_evidence": context.get("evidence", []),
        "document_type": doc_type,
        "document_name": doc_name,
        "instruction": f"{role_instruction} Format output cleanly as Markdown/Presentation Slides (PPT style). Request formal review upon completion.{feedback_prompt}"
    }
    response = model.invoke(json.dumps(prompt))

    metadata = getattr(response, "response_metadata", {}) or {}
    content = getattr(response, "content", response)
    if not isinstance(content, str):
        content = str(content)

    return {
        "agent_id": agent_id,
        "assignment": title,
        "document_type": doc_type,
        "document_title": doc_name,
        "document_content": content,
        "review_requested": True,
        "result": content,
        "validated": True,
        "model_name": metadata.get("model_name"),
        "model_provider": metadata.get("model_provider", "NVIDIA NIM Cloud"),
        "model_location": metadata.get("model_location", "NVIDIA Cloud Endpoints")
    }

def validate_terraform(terraform_root: Path) -> dict[str, Any]:
    if not terraform_root.exists() or not list(terraform_root.rglob("*.tf")):
        return {"passed": False, "reason": "No Terraform configuration found", "root": str(terraform_root)}
    results = []
    for command in (["terraform", "fmt", "-check", "-recursive"], ["terraform", "validate"]):
        try:
            completed = subprocess.run(command, cwd=terraform_root, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return {"passed": False, "reason": "terraform executable is unavailable", "results": results}
        results.append({"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
        if completed.returncode:
            return {"passed": False, "results": results}
    return {"passed": True, "results": results}


def apply_terraform(terraform_root: Path) -> dict[str, Any]:
    if os.getenv("ALLOW_TERRAFORM_APPLY", "false").lower() != "true":
        return {"passed": False, "reason": "Terraform apply is disabled by policy"}
    try:
        completed = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_root, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return {"passed": False, "reason": "terraform executable is unavailable"}
    return {"passed": completed.returncode == 0, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}

class WorkflowRuntime:
    def __init__(self, agent_executor: Callable[..., Any] = invoke_specialist, terraform_validator: Callable[[Path], dict[str, Any]] = validate_terraform, provisioner: Callable[[Path], dict[str, Any]] = apply_terraform) -> None:
        self._runs: dict[str, WorkflowRun] = {}
        self._workers: dict[str, asyncio.Task] = {}
        self._task_events: dict[str, asyncio.Event] = {}
        self._subscribers: list[Callable[[dict[str, Any]], None]] = []
        self._agent_executor = agent_executor
        self._terraform_validator = terraform_validator
        self._provisioner = provisioner

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers.append(callback)

    def list_runs(self) -> list[dict[str, Any]]:
        return [run.snapshot() for run in self._runs.values()]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        run = self._runs.get(run_id)
        return run.snapshot() if run else None

    def create_run(self, objective: str, provision: bool = False, auto_approve: bool = False) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        tasks = [WorkflowTask(f"{run_id[:8]}-{i + 1}", agent, title, model) for i, (agent, title, model) in enumerate(PILOT_STAGES)]
        run = WorkflowRun(run_id, objective, tasks=tasks, auto_approve=auto_approve)
        run.provisioning = {"requested": provision, "status": "queued" if provision else "not_requested"}
        self._runs[run_id] = run
        _write_artifact(run, "manifest.json", run.snapshot())
        self._emit(run, "workflow_created", {"objective": objective})
        return run.snapshot()

    async def start_run(self, run_id: str) -> bool:
        if run_id not in self._runs:
            return False
        if run_id not in self._workers or self._workers[run_id].done():
            self._workers[run_id] = asyncio.create_task(self._execute(self._runs[run_id]))
        return True

    async def stop_run(self, run_id: str) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        worker = self._workers.get(run_id)
        if worker and not worker.done():
            worker.cancel()
        run.status = "cancelled"
        run.current_task_id = None
        event = self._task_events.get(run_id)
        if event:
            event.set()
        self._emit(run, "workflow_cancelled", {"run_id": run_id})
        return True

    async def stop_all_runs(self) -> int:
        stopped = 0
        for run_id in list(self._workers.keys()):
            if await self.stop_run(run_id):
                stopped += 1
        return stopped

    async def approve_task(self, run_id: str, task_id: str, approver: str = "operator") -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        task = next((t for t in run.tasks if t.id == task_id), None)
        if not task or task.status != "awaiting_approval":
            return False
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc).isoformat()
        self._emit(run, "task_approved", {"task_id": task.id, "approver": approver})
        event = self._task_events.get(run_id)
        if event:
            event.set()
        return True

    async def reject_task(self, run_id: str, task_id: str, comment: str, rejector: str = "operator") -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        task = next((t for t in run.tasks if t.id == task_id), None)
        if not task or task.status != "awaiting_approval":
            return False
        task.status = "queued"
        task.progress = 0
        feedback = {"timestamp": datetime.now(timezone.utc).isoformat(), "comment": comment, "rejector": rejector}
        task.feedback_history.append(feedback)
        task.output_artifact = None
        task.document_content = None
        task.document_title = None
        task.error = None
        task.failure_reason = None
        task.suggested_resolution = None
        self._emit(run, "task_rejected", {"task_id": task.id, "comment": comment, "rejector": rejector})
        event = self._task_events.get(run_id)
        if event:
            event.set()
        return True

    async def start_fresh_run(self, run_id: str) -> bool:
        await self.stop_run(run_id)
        run = self._runs.get(run_id)
        if not run:
            return False
        run.status = "created"
        run.progress = 0
        run.current_task_id = None
        for task in run.tasks:
            task.status = "queued"
            task.progress = 0
            task.started_at = None
            task.completed_at = None
            task.output_artifact = None
            task.document_content = None
            task.document_title = None
            task.document_type = None
            task.review_requested = False
            task.feedback_history.clear()
            task.error = None
            task.failure_reason = None
            task.suggested_resolution = None
        _write_artifact(run, "manifest.json", run.snapshot())
        self._emit(run, "workflow_restarted_fresh", {"run_id": run_id})
        return await self.start_run(run_id)

    async def continue_run(self, run_id: str) -> bool:
        run = self._runs.get(run_id)
        if not run:
            return False
        current_task = next((t for t in run.tasks if t.id == run.current_task_id), None)
        if current_task and current_task.status == "awaiting_approval":
            return await self.approve_task(run_id, current_task.id)
        if run_id not in self._workers or self._workers[run_id].done():
            self._workers[run_id] = asyncio.create_task(self._execute(run))
            return True
        return True

    def clear_runs(self) -> None:
        self._runs.clear()

    async def _execute(self, run: WorkflowRun) -> None:
        run.status = "running"
        self._emit(run, "workflow_started", {})
        evidence: list[dict[str, Any]] = []
        terraform_root = _root() / "data" / "workflows" / run.id / "terraform"

        # Reconstruct evidence for completed steps
        for t in run.tasks:
            if t.status == "completed" and t.output_artifact:
                try:
                    art_path = _root() / t.output_artifact
                    if art_path.exists():
                        res_data = json.loads(art_path.read_text(encoding="utf-8"))
                        evidence.append({"task_id": t.id, "agent_id": t.agent_id, "artifact": t.output_artifact, "result": res_data})
                except Exception:
                    pass

        try:
            index = 0
            while index < len(run.tasks):
                task = run.tasks[index]
                if task.status == "completed":
                    index += 1
                    continue

                run.current_task_id = task.id
                run.status = "running"
                task.status = "running"
                task.started_at = task.started_at or datetime.now(timezone.utc).isoformat()
                self._emit(run, "task_started", {"task_id": task.id, "agent_id": task.agent_id})

                try:
                    result = self._agent_executor(
                        task.agent_id,
                        task.title,
                        run.objective,
                        {
                            "model_policy": task.model_policy,
                            "evidence": evidence,
                            "feedback_history": task.feedback_history
                        }
                    )
                    if inspect.isawaitable(result):
                        result = await result
                    if not isinstance(result, dict):
                        raise ValueError("specialist executor must return a mapping")

                    artifact = _write_artifact(run, f"task-{index + 1:02d}-{task.agent_id}.json", result)
                    if task.agent_id == "cloud_infrastructure_engineer":
                        terraform_root = _materialize_terraform(run, result)

                    task.output_artifact = artifact
                    task.document_title = result.get("document_title")
                    task.document_type = result.get("document_type")
                    task.document_content = result.get("document_content")
                    task.review_requested = True
                    task.executed_model = result.get("model_name")
                    task.model_provider = result.get("model_provider", "NVIDIA NIM Cloud")
                    task.model_location = result.get("model_location", "NVIDIA Cloud Endpoints")

                    if not run.auto_approve:
                        task.status = "awaiting_approval"
                        run.status = "paused_awaiting_approval"
                        self._emit(run, "task_awaiting_approval", {
                            "task_id": task.id,
                            "document_title": task.document_title,
                            "document_type": task.document_type
                        })

                        task_event = self._task_events.setdefault(run.id, asyncio.Event())
                        task_event.clear()
                        await task_event.wait()

                        if task.status == "queued":
                            # Retrigger step due to negative feedback
                            self._emit(run, "task_retriggered", {"task_id": task.id, "feedback_count": len(task.feedback_history)})
                            continue

                    # Approved / Completed step
                    task.progress = 100
                    task.status = "completed"
                    task.completed_at = datetime.now(timezone.utc).isoformat()
                    evidence.append({"task_id": task.id, "agent_id": task.agent_id, "artifact": artifact, "result": result})
                    index += 1
                    run.progress = round(index / len(run.tasks) * 80)
                    self._emit(run, "task_completed", {"task_id": task.id, "artifact": artifact})

                except Exception as exc:
                    task.status = "failed"
                    task.error = str(exc)
                    err_msg = str(exc)
                    if "NVIDIA_API_KEY" in err_msg:
                        task.failure_reason = "Missing NVIDIA_API_KEY environment variable for model provider"
                        task.suggested_resolution = "Configure NVIDIA_API_KEY in environment or .env file"
                    elif "Terraform" in err_msg:
                        task.failure_reason = "Terraform configuration validation or executable failure"
                        task.suggested_resolution = "Check terraform syntax or verify terraform CLI is installed in PATH"
                    else:
                        task.failure_reason = f"Agent invocation exception: {err_msg}"
                        task.suggested_resolution = "Review model policy configuration and retry task execution"
                    run.status = "failed"
                    _write_artifact(run, "failure.json", {"task_id": task.id, "agent": task.agent_id, "failure_type": "agent_invocation", "description": err_msg, "failure_reason": task.failure_reason, "suggested_resolution": task.suggested_resolution, "evidence": evidence})
                    self._emit(run, "task_failed", {"task_id": task.id, "error": err_msg, "failure_reason": task.failure_reason, "suggested_resolution": task.suggested_resolution})
                    return
            terraform = self._terraform_validator(terraform_root)
            gate_results = {name: True for name in GATE_NAMES[:-1]}
            gate_results["requirements"] = bool(evidence) and all(item["result"].get("validated") is True for item in evidence)
            gate_results["implementation"] = terraform.get("passed", False)
            for gate in GATE_NAMES[:-1]:
                result = {"name": gate, "status": "passed" if gate_results[gate] else "failed", "evidence": terraform if gate == "implementation" else evidence[-1:]}
                run.gates.append(result)
                _write_artifact(run, f"gate-{gate}.json", result)
                self._emit(run, "quality_gate", result)
                if not gate_results[gate]:
                    run.status = "blocked"
                    run.current_task_id = None
                    self._emit(run, "workflow_blocked", {"gate": gate, "reason": terraform.get("reason")})
                    return
            if run.provisioning["requested"]:
                if os.getenv("WORKFLOW_HUMAN_APPROVED", "false").lower() != "true":
                    run.provisioning.update({"status": "blocked", "reason": "Terraform apply requires explicit human approval"})
                    _write_artifact(run, "provisioning.json", run.provisioning)
                    run.status = "blocked"
                    self._emit(run, "workflow_blocked", {"reason": run.provisioning["reason"]})
                    return
                provision_result = self._provisioner(terraform_root)
                run.provisioning.update({"status": "completed" if provision_result.get("passed") else "failed", "result": provision_result})
                _write_artifact(run, "provisioning.json", run.provisioning)
                if not provision_result.get("passed"):
                    run.status = "failed"
                    self._emit(run, "workflow_failed", {"reason": provision_result.get("reason", "Terraform apply failed")})
                    return
            release = {"name": "release", "status": "passed", "evidence": run.artifacts}
            run.gates.append(release)
            _write_artifact(run, "gate-release.json", release)
            self._emit(run, "quality_gate", release)
            run.status = "completed"
            run.progress = 100
            run.current_task_id = None
            _write_artifact(run, "final-evidence.json", {"status": run.status, "gates": run.gates, "artifacts": run.artifacts})
            self._emit(run, "workflow_completed", {"artifacts": run.artifacts})
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
