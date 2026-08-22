# Monitoring Dashboard

The FastAPI monitoring application provides a live control room for the 22-agent engineering team.

## Run

```bash
uvicorn src.multi_agent_team.monitoring.app:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`. Enter the configured monitoring API key to observe the team. To launch the pilot workflow, use an operator or admin bearer token in the second field. Tokens can be requested from `POST /api/token` using the monitoring API key.

## Workflow API

- `GET /api/agents`: registered team members and status.
- `GET /api/models`: active model policies and resolved provider IDs.
- `POST /api/workflows`: starts the non-production Landing Zone pilot; requires operator/admin authorization. Set `provision: true` to request provisioning; the run validates Terraform first and remains blocked until explicit human approval.
- `GET /api/workflows`: current workflow snapshots.
- `GET /api/workflows/{run_id}`: one workflow snapshot with its event history.
- `WS /ws/agents`: authenticated live status and workflow events.

The pilot invokes each specialist through its configured model policy from `models_active.yaml`. Every specialist result, generated Terraform file, quality gate, Terraform validation result, provisioning result, and final evidence bundle is written below `data/workflows/<run-id>/`. Missing model credentials, missing Terraform output, failed validation, or failed gates stop the run and preserve the failure evidence.

Provisioning requires both `ALLOW_TERRAFORM_APPLY=true` and `WORKFLOW_HUMAN_APPROVED=true`. The latter is an explicit operator-controlled approval signal and should only be set for a reviewed run in a controlled environment.