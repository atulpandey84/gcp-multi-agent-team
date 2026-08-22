-- initial schema for monitoring app (Postgres / SQLite compatible)

CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  role TEXT,
  team TEXT,
  mission TEXT,
  status TEXT,
  last_seen TEXT
);

CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  action TEXT,
  agent_id TEXT,
  details TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT,
  requester TEXT,
  action TEXT,
  agent_id TEXT,
  details TEXT,
  status TEXT,
  approver TEXT,
  approver_comments TEXT,
  decision_timestamp TEXT
);
