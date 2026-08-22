-- Postgres-native adjustments: use SERIAL ids and FK constraints
-- This migration is intended to be applied only to Postgres databases.

BEGIN;

CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  role TEXT,
  team TEXT,
  mission TEXT,
  status TEXT,
  last_seen TEXT
);

CREATE TABLE IF NOT EXISTS audit (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE,
  action TEXT NOT NULL,
  agent_id TEXT NULL,
  details TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE,
  requester TEXT,
  action TEXT,
  agent_id TEXT,
  details JSONB NULL,
  status TEXT,
  approver TEXT,
  approver_comments TEXT,
  decision_timestamp TIMESTAMP WITH TIME ZONE,
  CONSTRAINT fk_agent FOREIGN KEY(agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit(agent_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit(action);

COMMIT;
