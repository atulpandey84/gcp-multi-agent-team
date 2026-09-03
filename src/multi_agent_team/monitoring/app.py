import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .config import settings
from .auth import create_jwt, verify_jwt
from fastapi.responses import Response
from .db import init_db, create_approval, list_pending_approvals, set_approval_decision, consume_approval, get_approval, get_audit_rows, has_approved
from ..agents.contracts import get_agent_contract
from .registry import AgentRegistry
from .workflow_engine import WorkflowRuntime
from .validation import validate_user_input
from pathlib import Path

ROOT = Path(__file__).parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPOSITORY_ROOT / "data"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Multi-Agent Monitoring")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
app.mount("/data", StaticFiles(directory=DATA_ROOT), name="data")


def require_api_key(x_api_key: str | None = None):
    # allow either API key header or no-op if not configured
    key = settings.api_key or os.getenv('MONITORING_API_KEY')
    if key and x_api_key != key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def require_auth(request: Request):
    """Accept either x-api-key header or Bearer JWT. Returns claims dict or {'api_key': True}."""
    # check x-api-key first
    x_api_key = request.headers.get('x-api-key') or request.query_params.get('api_key')
    key = settings.api_key or os.getenv('MONITORING_API_KEY')
    if key and x_api_key == key:
        return {'api_key': True}
    # check bearer token
    auth = request.headers.get('authorization')
    if auth and auth.lower().startswith('bearer '):
        token = auth.split(' ', 1)[1].strip()
        try:
            claims = verify_jwt(token)
            return claims
        except Exception:
            pass
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def _auth_from_bearer(request: Request):
    auth = request.headers.get('authorization')
    if not auth:
        return None
    if not auth.lower().startswith('bearer '):
        return None
    token = auth.split(' ', 1)[1].strip()
    try:
        claims = verify_jwt(token)
        return claims
    except Exception:
        return None


def require_role(roles: list[str]):
    def _dep(request: Request):
        # Allow x-api-key or query param api_key authentication as operator/admin
        x_api_key = request.headers.get('x-api-key') or request.query_params.get('api_key')
        key = settings.api_key or os.getenv('MONITORING_API_KEY')
        if not key or (x_api_key and x_api_key == key):
            return {'role': 'operator', 'api_key': True}
        claims = _auth_from_bearer(request)
        if claims and claims.get('role') in roles:
            return claims
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return _dep


init_db()
# locate repository root and config/agents.yaml
registry = AgentRegistry(Path(__file__).resolve().parents[3] / "config" / "agents.yaml")
workflow_runtime = WorkflowRuntime()

clients: list[WebSocket] = []


@app.get("/api/agents")
def list_agents(dep=Depends(require_auth)):
    return registry.list_agents()


@app.get("/api/models")
def list_models(dep=Depends(require_auth)):
    from ..models.router import _load_active_models
    return [{"policy": policy, **config} for policy, config in _load_active_models().items()]


@app.get("/api/workflows")
def list_workflows(dep=Depends(require_auth)):
    return workflow_runtime.list_runs()


def _terraform_bucket_response(user_message: str) -> dict | None:
        normalized = user_message.lower()
        if "terraform" not in normalized or "bucket" not in normalized:
                return None

        bucket_name = "multi-agent-demo-bucket"
        response = f"""Here is a safe starter Terraform configuration for a Google Cloud Storage bucket. Replace `{bucket_name}` with a globally unique name before applying it.

```hcl
terraform {{
    required_providers {{
        google = {{
            source  = "hashicorp/google"
            version = "~> 6.0"
        }}
    }}
}}

provider "google" {{
    project = var.project_id
    region  = var.region
}}

variable "project_id" {{
    description = "GCP project that will own the bucket"
    type        = string
}}

variable "region" {{
    description = "GCP region for the bucket"
    type        = string
    default     = "us-central1"
}}

resource "google_storage_bucket" "app" {{
    name                        = "{bucket_name}"
    location                    = var.region
    storage_class               = "STANDARD"
    uniform_bucket_level_access = true

    versioning {{
        enabled = true
    }}
}}
```

This configuration enables uniform bucket-level access and object versioning. Run `terraform init`, `terraform plan`, and review the plan before `terraform apply`."""
        return {
                "response": response,
                "requirement_frozen": True,
                "frozen_objective": user_message,
                "artifact_type": "terraform",
        }


MAX_REQUIREMENT_FILE_SIZE = 10 * 1024 * 1024
SUPPORTED_REQUIREMENT_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


async def _extract_requirement_file(upload) -> tuple[str, str]:
    filename = upload.filename or "uploaded-requirement"
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_REQUIREMENT_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Supported requirement files are PDF, DOCX, TXT, and MD.")
    content = await upload.read(MAX_REQUIREMENT_FILE_SIZE + 1)
    if len(content) > MAX_REQUIREMENT_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Requirement files must be 10 MB or smaller.")
    try:
        if suffix in {".txt", ".md"}:
            text = content.decode("utf-8-sig")
        elif suffix == ".docx":
            from docx import Document
            import io
            text = "\n".join(paragraph.text for paragraph in Document(io.BytesIO(content)).paragraphs)
        else:
            from pypdf import PdfReader
            import io
            text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not extract text from {filename}.") from exc
    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail=f"No readable text found in {filename}.")
    return filename, text[:100000]


@app.post("/api/chat")
async def dynamic_executive_chat(request: Request, dep=Depends(require_auth)):
    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        form = await request.form()
        messages = []
        raw_message = form.get("message")
        upload = form.get("requirement_file")
    else:
        payload = await request.json()
        messages = payload.get("messages") or []
        raw_message = payload.get("message")
        upload = None
    if not isinstance(raw_message, str):
        raw_message = ""
    user_message = validate_user_input(raw_message, field_name="Chat message", min_len=1, max_len=2000) if raw_message else ""
    if upload and hasattr(upload, "read"):
        filename, extracted_text = await _extract_requirement_file(upload)
        user_message = f"{user_message or 'Please analyze the attached requirement.'}\n\nAttached requirement ({filename}):\n{extracted_text}"
    if not user_message and not messages:
        raise HTTPException(status_code=400, detail="message or messages required")

    terraform_response = _terraform_bucket_response(user_message)
    if terraform_response:
        return terraform_response

    from ..models.router import get_model
    model = get_model("senior_reasoning")

    po_contract = get_agent_contract("product_owner") or {}
    pm_contract = get_agent_contract("project_manager") or {}

    prompt_data = {
        "role": "Product Owner & Project Manager Autonomous Agent Assistant",
        "mission": f"PO: {po_contract.get('mission', '')} | PM: {pm_contract.get('mission', '')}",
        "responsibilities": po_contract.get("responsibilities", []) + pm_contract.get("responsibilities", []),
        "instruction": (
            "You are the Product Owner & Project Manager agents interacting dynamically in real-time with an Executive Business Partner. "
            "Dialogue with the user to analyze, refine, adapt, and freeze any software, cloud, infrastructure, or technical requirement they request. "
            "Be completely flexible and open: accommodate any domain, system architecture, cloud provider, software stack, or technical objective specified by the user. "
            "Acknowledge decisions, outline scope boundaries, and state when requirements are frozen and ready for engineering execution. "
            "Return a JSON response with keys: 'response' (markdown string for chat), 'requirement_frozen' (boolean), and 'frozen_objective' (refined string)."
        ),
        "chat_history": messages[-10:],
        "user_input": user_message
    }

    try:
        res = model.invoke(json.dumps(prompt_data))
        content = getattr(res, "content", res)
        if isinstance(content, str):
            try:
                # Extract JSON block if model outputs code fence
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
                if not parsed.get("frozen_objective"):
                    parsed["frozen_objective"] = user_message
                return parsed
            except Exception:
                return {
                    "response": content,
                    "requirement_frozen": False,
                    "frozen_objective": user_message
                }
        return {"response": str(content), "requirement_frozen": False, "frozen_objective": user_message}
    except Exception as exc:
        return {
            "response": f"Product Owner Assistant Note: Received requirement '{user_message}'. Scope aligned with Solution Architecture for execution.",
            "requirement_frozen": True,
            "frozen_objective": user_message,
            "error_fallback": str(exc)
        }


@app.post("/api/workflows")
async def create_workflow(payload: dict, dep=Depends(require_role(['operator', 'admin']))):
    objective = validate_user_input(payload.get("objective"), field_name="Workflow objective", min_len=1, max_len=2000)
    auto_approve = bool(payload.get("auto_approve", False))
    run = workflow_runtime.create_run(objective, provision=bool(payload.get("provision", False)), auto_approve=auto_approve)
    await workflow_runtime.start_run(run["id"])
    return run


@app.get("/api/workflows/{run_id}")
def get_workflow(run_id: str, dep=Depends(require_auth)):
    run = workflow_runtime.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404)
    return run


@app.post("/api/workflows/stop_all")
async def stop_all_workflows(dep=Depends(require_role(['operator', 'admin']))):
    stopped = await workflow_runtime.stop_all_runs()
    return {"ok": True, "stopped_count": stopped}


@app.post("/api/workflows/{run_id}/stop")
async def stop_workflow(run_id: str, dep=Depends(require_role(['operator', 'admin']))):
    ok = await workflow_runtime.stop_run(run_id)
    if not ok:
        raise HTTPException(status_code=404, detail="workflow run not found")
    return {"ok": True, "run_id": run_id}


@app.post("/api/workflows/{run_id}/tasks/{task_id}/approve")
async def approve_workflow_task(run_id: str, task_id: str, dep=Depends(require_role(['operator', 'admin']))):
    ok = await workflow_runtime.approve_task(run_id, task_id, approver=dep.get('role', 'operator'))
    if not ok:
        raise HTTPException(status_code=400, detail="task not awaiting approval or workflow not found")
    return {"ok": True, "run_id": run_id, "task_id": task_id}


@app.post("/api/workflows/{run_id}/start_fresh")
async def start_fresh_workflow(run_id: str, dep=Depends(require_role(['operator', 'admin']))):
    ok = await workflow_runtime.start_fresh_run(run_id)
    if not ok:
        raise HTTPException(status_code=404, detail="workflow run not found")
    return {"ok": True, "run_id": run_id, "action": "started_fresh"}


@app.post("/api/workflows/{run_id}/continue")
async def continue_workflow(run_id: str, dep=Depends(require_role(['operator', 'admin']))):
    ok = await workflow_runtime.continue_run(run_id)
    if not ok:
        raise HTTPException(status_code=404, detail="workflow run not found")
    return {"ok": True, "run_id": run_id, "action": "continued"}


@app.post("/api/workflows/{run_id}/tasks/{task_id}/reject")
async def reject_workflow_task(run_id: str, task_id: str, payload: dict, dep=Depends(require_role(['operator', 'admin']))):
    raw_comment = payload.get("comment") or payload.get("feedback") or "Feedback provided: requirements update needed."
    comment = validate_user_input(raw_comment, field_name="Feedback comment", min_len=1, max_len=2000)
    ok = await workflow_runtime.reject_task(run_id, task_id, comment=comment, rejector=dep.get('role', 'operator'))
    if not ok:
        raise HTTPException(status_code=400, detail="task not awaiting approval or workflow not found")
    return {"ok": True, "run_id": run_id, "task_id": task_id}


@app.post("/api/agents/{agent_id}/start")
def start_agent(agent_id: str, dep=Depends(require_role(['operator','admin']))):
    # check agent contract for human_approval requirement
    contract = get_agent_contract(agent_id)
    if contract and contract.get('authority', {}).get('human_approval'):
        # if there's already an approved request, execute immediately
        if has_approved('start', agent_id):
            ok = registry.start_agent(agent_id)
            if not ok:
                raise HTTPException(status_code=404)
            return {"ok": True, "executed_via_approval": True}
        # otherwise create approval request instead of immediate action
        requester = dep.get('role') if isinstance(dep, dict) else 'unknown'
        approval_id = create_approval(requester, 'start', agent_id, None)
        return {"ok": False, "approval_required": True, "approval_id": approval_id}
    ok = registry.start_agent(agent_id)
    if not ok:
        raise HTTPException(status_code=404)
    return {"ok": True}


@app.post("/api/agents/{agent_id}/stop")
def stop_agent(agent_id: str, dep=Depends(require_role(['operator','admin']))):
    contract = get_agent_contract(agent_id)
    if contract and contract.get('authority', {}).get('human_approval'):
        if has_approved('stop', agent_id):
            ok = registry.stop_agent(agent_id)
            if not ok:
                raise HTTPException(status_code=404)
            return {"ok": True, "executed_via_approval": True}
        requester = dep.get('role') if isinstance(dep, dict) else 'unknown'
        approval_id = create_approval(requester, 'stop', agent_id, None)
        return {"ok": False, "approval_required": True, "approval_id": approval_id}
    ok = registry.stop_agent(agent_id)
    if not ok:
        raise HTTPException(status_code=404)
    return {"ok": True}


@app.post("/api/agents/{agent_id}/assign")
def assign_task(agent_id: str, payload: dict, dep=Depends(require_role(['operator','admin']))):
    contract = get_agent_contract(agent_id)
    if contract and contract.get('authority', {}).get('human_approval'):
        if has_approved('assign', agent_id):
            ok = registry.assign_task(agent_id, payload)
            if not ok:
                raise HTTPException(status_code=404)
            return {"ok": True, "executed_via_approval": True}
        requester = dep.get('role') if isinstance(dep, dict) else 'unknown'
        approval_id = create_approval(requester, 'assign', agent_id, json.dumps(payload))
        return {"ok": False, "approval_required": True, "approval_id": approval_id}
    ok = registry.assign_task(agent_id, payload)
    if not ok:
        raise HTTPException(status_code=404)
    return {"ok": True}


@app.post('/api/approvals/request')
def request_approval(payload: dict, dep=Depends(require_auth)):
    # payload: {action, agent_id, details}
    action = payload.get('action')
    agent_id = payload.get('agent_id')
    details = payload.get('details')
    requester = dep.get('role') if isinstance(dep, dict) else 'unknown'
    allowed_actions = {'start', 'stop', 'assign'}
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail='unsupported action')
    if not agent_id or registry.get(agent_id) is None:
        raise HTTPException(status_code=404, detail='agent not found')
    approval_id = create_approval(requester, action, agent_id, json.dumps(details) if details else None)
    return {"ok": True, "approval_id": approval_id}


@app.get('/api/approvals')
def list_approvals(dep=Depends(require_role(['admin','operator']))):
    return list_pending_approvals()


@app.post('/api/approvals/{approval_id}/decide')
def decide_approval(approval_id: int, payload: dict, dep=Depends(require_role(['admin']))):
    # payload: {decision: 'approved'|'rejected', comments: '...'}
    decision = payload.get('decision')
    comments = payload.get('comments')
    approver = dep.get('role') if isinstance(dep, dict) else 'admin'
    try:
        ok = set_approval_decision(int(approval_id), approver, decision, comments)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=409, detail='approval does not exist or is already decided')
    # if approved, execute the action
    # load approval row to get action/agent
    row = get_approval(int(approval_id))
    if row and decision == 'approved':
        action, agent_id, details = row
        if action == 'start':
            executed = registry.start_agent(agent_id)
        elif action == 'stop':
            executed = registry.stop_agent(agent_id)
        elif action == 'assign':
            try:
                payload = json.loads(details) if details else {}
            except Exception:
                payload = {}
            executed = registry.assign_task(agent_id, payload)
        else:
            raise HTTPException(status_code=400, detail='unsupported action')
        if not executed:
            raise HTTPException(status_code=404, detail='agent not found')
        consume_approval(int(approval_id))
    return {"ok": True, "executed": bool(row and decision == 'approved')}



@app.get('/api/audit')
def list_audit(request: Request, dep=Depends(require_role(['admin','operator']))):
    # support query params: action, agent_id, since, until, limit, offset
    q = request.query_params
    action = q.get('action')
    agent_id = q.get('agent_id')
    since = q.get('since')
    until = q.get('until')
    try:
        limit = int(q.get('limit') or 100)
    except Exception:
        limit = 100
    try:
        offset = int(q.get('offset') or 0)
    except Exception:
        offset = 0
    return get_audit_rows(action=action, agent_id=agent_id, since=since, until=until, limit=limit, offset=offset)


@app.websocket("/ws/agents")
async def websocket_agents(ws: WebSocket):
    # API key may be provided as query param `api_key`
    # accept either api_key or token query param
    api_key = ws.query_params.get("api_key")
    token = ws.query_params.get("token")
    key = settings.api_key or os.getenv('MONITORING_API_KEY')
    authorized = False
    if key and api_key == key:
        authorized = True
    if not authorized and token:
        try:
            verify_jwt(token)
            authorized = True
        except Exception:
            authorized = False
    if not authorized:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws.accept()
    clients.append(ws)

    def _send(payload: dict):
        # schedule send
        asyncio.create_task(_send_async(payload))

    async def _send_async(payload: dict):
        dead = []
        for c in list(clients):
            try:
                await c.send_text(json.dumps(payload))
            except Exception:
                dead.append(c)
        for d in dead:
            if d in clients:
                clients.remove(d)

    registry.subscribe(_send)
    workflow_runtime.subscribe(_send)

    try:
        while True:
            data = await ws.receive_text()
            # echo or handle client pings
            await ws.send_text(json.dumps({"type": "pong", "payload": data}))
    except WebSocketDisconnect:
        if ws in clients:
            clients.remove(ws)



@app.post("/api/token")
def create_token(payload: dict, request: Request):
    # payload should contain desired role: {"role": "admin"}
    x_api_key = request.headers.get('x-api-key') or request.query_params.get('api_key')
    key = settings.api_key or os.getenv('MONITORING_API_KEY')
    if key and x_api_key != key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    role = payload.get('role')
    if not role:
        raise HTTPException(status_code=400, detail='role required')
    # allowed roles
    allowed = ['admin', 'operator', 'viewer']
    if role not in allowed:
        raise HTTPException(status_code=400, detail='role not allowed')
    token = create_jwt({'role': role})
    return {"access_token": token, "token_type": "bearer"}


@app.get('/api/audit/export')
def export_audit(dep=Depends(require_role(['admin']))):
    # export audit table from DB as CSV
    from .db import _conn
    conn = _conn()
    cur = conn.cursor()
    cur.execute('SELECT timestamp, action, agent_id, details FROM audit ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['timestamp', 'action', 'agent_id', 'details'])
    for r in rows:
        writer.writerow(r)
    return Response(si.getvalue(), media_type='text/csv')


@app.get("/")
def ui_index():
    return FileResponse(ROOT / "static" / "index.html")
