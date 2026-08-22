import os
from datetime import datetime, timezone
import psycopg
from .models import Agent

# Mandatory PostgreSQL configuration
DATABASE_URL = os.environ.get('MONITORING_DATABASE_URL') or os.environ.get('DATABASE_URL') or 'postgresql://agent:change-me@localhost:5432/agent_memory'


def init_db() -> None:
    try:
        conn = psycopg.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                role TEXT,
                team TEXT,
                mission TEXT,
                status TEXT,
                last_seen TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS audit (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                action TEXT,
                agent_id TEXT,
                details TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS approvals (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                requester TEXT,
                action TEXT,
                agent_id TEXT,
                details TEXT,
                status TEXT,
                approver TEXT,
                approver_comments TEXT,
                decision_timestamp TEXT
            )
            """
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        print(f"[Warning] PostgreSQL init_db failed ({exc}). Ensure PostgreSQL is running at {DATABASE_URL}.")


def _conn():
    return psycopg.connect(DATABASE_URL)


def upsert_agent(agent: Agent) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO agents(id, role, team, mission, status, last_seen) VALUES (%s, %s, %s, %s, %s, %s) "
        "ON CONFLICT (id) DO UPDATE SET role=EXCLUDED.role, team=EXCLUDED.team, mission=EXCLUDED.mission, status=EXCLUDED.status, last_seen=EXCLUDED.last_seen",
        (agent.id, agent.role, agent.team, agent.mission, agent.status, agent.last_seen),
    )
    conn.commit()
    conn.close()


def get_all_agents() -> list[Agent]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, role, team, mission, status, last_seen FROM agents")
    rows = cur.fetchall()
    conn.close()
    return [Agent(id=r[0], role=r[1], team=r[2], mission=r[3], status=r[4], last_seen=r[5]) for r in rows]


def append_audit(action: str, agent_id: str | None, details: str | None) -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO audit(timestamp, action, agent_id, details) VALUES (%s, %s, %s, %s)", (datetime.now(timezone.utc).isoformat(), action, agent_id, details))
    conn.commit()
    conn.close()


def create_approval(requester: str, action: str, agent_id: str | None, details: str | None) -> int:
    conn = _conn()
    cur = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute("INSERT INTO approvals(timestamp, requester, action, agent_id, details, status) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (ts, requester, action, agent_id, details, 'pending'))
    id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    try:
        append_audit('approval_requested', agent_id, f'approval:{id} requester:{requester} action:{action} details:{details}')
    except Exception:
        pass
    return id


def list_pending_approvals() -> list[dict]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, requester, action, agent_id, details, status, approver, approver_comments, decision_timestamp FROM approvals ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        entry = {'id': r[0], 'timestamp': r[1], 'requester': r[2], 'action': r[3], 'agent_id': r[4], 'details': r[5], 'status': r[6], 'approver': r[7], 'approver_comments': r[8], 'decision_timestamp': r[9]}
        try:
            conn2 = _conn()
            cur2 = conn2.cursor()
            like = f'%approval:{r[0]}%'
            cur2.execute("SELECT id, timestamp, action, agent_id, details FROM audit WHERE details LIKE %s ORDER BY id DESC", (like,))
            audits = cur2.fetchall()
            conn2.close()
            entry['audits'] = [{'id': a[0], 'timestamp': a[1], 'action': a[2], 'agent_id': a[3], 'details': a[4]} for a in audits]
        except Exception:
            entry['audits'] = []
        out.append(entry)
    return out


def set_approval_decision(approval_id: int, approver: str, decision: str, comments: str | None) -> bool:
    if decision not in ('approved', 'rejected'):
        raise ValueError('decision must be approved or rejected')
    conn = _conn()
    cur = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute("UPDATE approvals SET status=%s, approver=%s, approver_comments=%s, decision_timestamp=%s WHERE id=%s AND status='pending'", (decision, approver, comments, ts, approval_id))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if changed > 0:
        try:
            append_audit('approval_decision', None, f'approval:{approval_id} decision:{decision} approver:{approver} comments:{comments}')
        except Exception:
            pass
    return changed > 0


def consume_approval(approval_id: int) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE approvals SET status='consumed' WHERE id=%s AND status='approved'", (approval_id,))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed > 0


def get_approval(approval_id: int):
    conn = _conn()
    cur = conn.cursor()
    cur.execute('SELECT action, agent_id, details FROM approvals WHERE id=%s', (approval_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_audit_rows(action: str | None = None, agent_id: str | None = None, since: str | None = None, until: str | None = None, limit: int = 100, offset: int = 0):
    conn = _conn()
    cur = conn.cursor()
    clauses = []
    params: list = []
    if action:
        clauses.append("action = %s")
        params.append(action)
    if agent_id:
        clauses.append("agent_id = %s")
        params.append(agent_id)
    if since:
        clauses.append("timestamp >= %s")
        params.append(since)
    if until:
        clauses.append("timestamp <= %s")
        params.append(until)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    order = " ORDER BY id DESC "
    lim_off = f" LIMIT {int(limit)} OFFSET {int(offset)}"
    sql = f'SELECT id, timestamp, action, agent_id, details FROM audit{where}{order}{lim_off}'
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'timestamp': r[1], 'action': r[2], 'agent_id': r[3], 'details': r[4]} for r in rows]


def has_approved(action: str, agent_id: str | None) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM approvals WHERE action=%s AND agent_id=%s AND status='approved' LIMIT 1", (action, agent_id))
    found = cur.fetchone() is not None
    conn.close()
    return found
