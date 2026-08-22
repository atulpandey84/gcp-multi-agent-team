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
- `POST /api/workflows`: starts the non-production Landing Zone pilot; requires operator/admin authorization.
- `GET /api/workflows`: current workflow snapshots.
- `GET /api/workflows/{run_id}`: one workflow snapshot with its event history.
- `WS /ws/agents`: authenticated live status and workflow events.

The pilot is deliberately provider-agnostic at the monitoring layer. Its stages map each specialist to a model policy from `models_active.yaml`; execution events are visible even when cloud mutation tools remain disabled by policy.