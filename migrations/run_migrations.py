"""
Apply pending SQL migrations in this directory, in filename order.

Tracks applied files in a `schema_migrations` table, so it is safe to re-run:
already-applied files are skipped. Every migration file must itself be
idempotent (IF NOT EXISTS / ON CONFLICT) as a second line of defence.

    set DATABASE_URL=postgresql://...neon.tech/...
    python migrations/run_migrations.py
"""
import glob
import os
import sys

import psycopg

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL not set")

    con = psycopg.connect(url)
    with con.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "  filename   TEXT PRIMARY KEY,"
            "  applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
            ")"
        )
    con.commit()

    with con.cursor() as cur:
        cur.execute("SELECT filename FROM schema_migrations")
        applied = {r[0] for r in cur.fetchall()}

    files = sorted(glob.glob(os.path.join(HERE, "[0-9]*.sql")))
    pending = [f for f in files if os.path.basename(f) not in applied]
    if not pending:
        print("No pending migrations.")
        con.close()
        return

    for path in pending:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            sql = fh.read()
        print(f"applying {name} ...")
        with con.cursor() as cur:
            cur.execute(sql)               # psycopg3 runs multi-statement, no params
        with con.cursor() as cur:
            cur.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (name,))
        con.commit()
        print("  ok")

    con.close()


if __name__ == "__main__":
    main()
