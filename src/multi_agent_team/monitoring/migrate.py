import os
from pathlib import Path
from .db import IS_PG


MIGRATIONS_DIR = Path(__file__).parent / 'migrations'


def run_migrations(database_url: str | None = None):
    # if PG available and DATABASE_URL provided, use it; otherwise apply to sqlite file
    files = sorted([p for p in MIGRATIONS_DIR.iterdir() if p.name.endswith('.sql')])
    if not files:
        print('No migrations found')
        return
    if IS_PG and (database_url or os.environ.get('MONITORING_DATABASE_URL') or os.environ.get('DATABASE_URL')):
        import psycopg
        url = database_url or os.environ.get('MONITORING_DATABASE_URL') or os.environ.get('DATABASE_URL')
        conn = psycopg.connect(url)
        cur = conn.cursor()
        # create migrations table if not exists
        cur.execute("CREATE TABLE IF NOT EXISTS applied_migrations (name TEXT PRIMARY KEY, applied_at TEXT)")
        applied = set()
        cur.execute("SELECT name FROM applied_migrations")
        for r in cur.fetchall():
            applied.add(r[0])
        applied_count = 0
        for f in files:
            if f.name in applied:
                continue
            sql = f.read_text()
            cur.execute(sql)
            cur.execute("INSERT INTO applied_migrations(name, applied_at) VALUES (%s, %s)", (f.name, __import__('datetime').datetime.utcnow().isoformat()))
            applied_count += 1
        conn.commit()
        conn.close()
        print('Applied', applied_count, 'new migrations to Postgres')
    else:
        # apply to sqlite file used by the project
        import sqlite3
        from pathlib import Path
        db_path = Path('data') / 'monitor.db'
        db_path.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # create migrations table
        cur.execute("CREATE TABLE IF NOT EXISTS applied_migrations (name TEXT PRIMARY KEY, applied_at TEXT)")
        cur.execute("SELECT name FROM applied_migrations")
        applied = {r[0] for r in cur.fetchall()}
        applied_count = 0
        for f in files:
            if f.name in applied:
                continue
            sql = f.read_text()
            cur.executescript(sql)
            cur.execute("INSERT INTO applied_migrations(name, applied_at) VALUES (?, ?)", (f.name, __import__('datetime').datetime.utcnow().isoformat()))
            applied_count += 1
        conn.commit()
        conn.close()
        print('Applied', applied_count, 'new migrations to SQLite at', db_path)


if __name__ == '__main__':
    run_migrations()
