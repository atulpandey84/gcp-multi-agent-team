MIGRATIONS
==========

This project includes a small SQL-based migration runner for the monitoring service.

Usage
-----


Alembic (recommended)
----------------------

This project now includes an Alembic scaffold. Alembic is recommended for Postgres-managed schema evolution.

Basic workflow:

```bash
pip install alembic
export MONITORING_DATABASE_URL="postgresql://user:pass@host:5432/dbname"
alembic revision --autogenerate -m "add foo"
alembic upgrade head
```

Notes
-----
- `alembic/env.py` imports SQLAlchemy models from `src.multi_agent_team.monitoring.models_sa` so autogeneration uses the declared models.
- For simple SQL migrations the old `migrate.py` runner remains available; it records applied migrations in `applied_migrations`.
- Add new SQL migrations to `src/multi_agent_team/monitoring/migrations/` if you prefer the SQL runner.
