Alembic scaffold
-----------------

This repo includes a minimal Alembic scaffold to generate and apply Postgres-specific migrations.

To use:

1. Install Alembic: `pip install alembic`
2. Set `MONITORING_DATABASE_URL` or `DATABASE_URL` env var to your Postgres connection string.
3. Generate a migration: `alembic revision --autogenerate -m "add foo"`
4. Apply migrations: `alembic upgrade head`

Notes: This scaffold is minimal and intended as a starting point. Consider using SQLAlchemy models and configuring the `target_metadata` in `alembic/env.py` for autogeneration.
