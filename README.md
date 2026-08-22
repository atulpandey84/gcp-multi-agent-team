# GCP Multi-Agent Engineering Team

LangGraph + NVIDIA multi-agent engineering organization.

## Model policy
- Nemotron Ultra: critical architecture/orchestration
- Nemotron Super: senior reasoning
- DeepSeek V4 Pro: coding/implementation
- Nemotron Lightning: fast routine work
- DeepSeek V4 Flash: fast coding
- Nemotron Embed/Rerank: RAG

## Safety defaults
GCP mutations, Terraform apply and production deployment are disabled by default.
Implement tool authorization and human approval before enabling them.

## Run
```bash
# Linux/macOS
cp .env.example .env
./scripts/bootstrap.sh
.venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python -m multi_agent_team.main
```

Windows PowerShell:
```powershell
Copy-Item .env.example .env
.\scripts\bootstrap.ps1
.\.venv\Scripts\python.exe -m pytest -q
$env:PYTHONPATH = "src"; .\.venv\Scripts\python.exe -m multi_agent_team.main
```

The bootstrap scripts always create a native `.venv` for the current operating system. Do not copy `.venv` between Windows and Linux; recreate it with the matching bootstrap script. `make bootstrap`, `make test`, `make lint`, and `make run` also select the correct interpreter layout when GNU Make is available.

Add `NVIDIA_API_KEY` to `.env` before running model-backed workflows.

Verify exact model identifiers against the current NVIDIA Build catalog before production deployment.

## Monitoring UI

This repository includes a lightweight FastAPI-based monitoring UI (no Docker required) at `src/multi_agent_team/monitoring/app.py`.

Run the UI locally:
```bash
# install deps into your virtualenv
pip install -r requirements.txt
# set an API key in .env: API_KEY or MONITORING_API_KEY
export MONITORING_API_KEY=your_secret_key
# run
uvicorn src.multi_agent_team.monitoring.app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser. Use the API key to connect the UI and control agents.

