"""
Telos: migrate telos.db (SQLite) -> Neon Postgres.

Reads whatever schema is actually in your telos.db, builds the Postgres
equivalent, and copies every row across. You don't have to hand-write DDL.

Usage:
    set DATABASE_URL=postgresql://...neon.tech/telos?sslmode=require
    python migrate_to_postgres.py --sqlite telos.db

    # see the DDL without touching Postgres:
    python migrate_to_postgres.py --sqlite telos.db --dry-run

    # wipe and redo (destructive, dev only):
    python migrate_to_postgres.py --sqlite telos.db --drop-existing

Strategy: create all tables WITHOUT foreign keys, copy data, then add the
FK constraints and indexes at the end. Avoids dependency-ordering pain.
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys

import psycopg
from psycopg import sql

# --------------------------------------------------------------------------
# Type mapping
# --------------------------------------------------------------------------
TYPE_MAP = [
    (r"^\s*$", "TEXT"),                       # SQLite lets you omit the type
    (r"INT8|BIGINT", "BIGINT"),
    (r"INT", "INTEGER"),
    (r"CHAR|CLOB|TEXT|VARCHAR", "TEXT"),
    (r"BLOB", "BYTEA"),
    (r"REAL|FLOA|DOUB", "DOUBLE PRECISION"),
    (r"NUMERIC|DECIMAL", "NUMERIC"),
    (r"BOOL", "INTEGER"),                     # keep 0/1 — app code compares to 1
    (r"DATETIME|TIMESTAMP", "TIMESTAMPTZ"),
    (r"^DATE$", "DATE"),
    (r"^TIME$", "TIME"),
]


def pg_type(sqlite_type: str) -> str:
    t = (sqlite_type or "").upper()
    for pattern, target in TYPE_MAP:
        if re.search(pattern, t):
            return target
    return "TEXT"


def pg_default(default, coltype: str):
    """Translate a SQLite column default into Postgres, or None to skip."""
    if default is None:
        return None
    d = str(default).strip()
    up = d.upper()
    if up in ("CURRENT_TIMESTAMP", "CURRENT_DATE", "CURRENT_TIME"):
        # SQLite happily stores these on TEXT columns; Postgres refuses to
        # assign a timestamptz default to a text column (no implicit cast).
        # Emit a text-typed default in UTC so the stored format matches what
        # SQLite wrote (and old rows stay consistent with new ones).
        if coltype == "TEXT":
            fmt = {
                "CURRENT_TIMESTAMP": "YYYY-MM-DD HH24:MI:SS",
                "CURRENT_DATE": "YYYY-MM-DD",
                "CURRENT_TIME": "HH24:MI:SS",
            }[up]
            return f"to_char(now() AT TIME ZONE 'UTC', '{fmt}')"
        return up
    if up in ("NULL",):
        return None
    if re.fullmatch(r"-?\d+(\.\d+)?", d):
        return d
    if d.startswith("'") and d.endswith("'"):
        return d
    if up in ("TRUE", "FALSE"):
        return "1" if up == "TRUE" else "0"
    if up.startswith("(") or "(" in up:
        return None  # expression default — port by hand if you need it
    return None


IDENT_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


def q(name: str) -> str:
    """Quote an identifier only when it needs it."""
    return name if IDENT_RE.match(name) else '"' + name.replace('"', '""') + '"'


# --------------------------------------------------------------------------
# Introspection
# --------------------------------------------------------------------------
def read_sqlite_schema(path: str):
    if not os.path.exists(path):
        sys.exit(f"SQLite file not found: {path}")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row

    tables = []
    rows = con.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()

    for r in rows:
        name, create_sql = r["name"], r["sql"] or ""
        cols = [dict(c) for c in con.execute(f'PRAGMA table_info("{name}")')]
        fks = [dict(f) for f in con.execute(f'PRAGMA foreign_key_list("{name}")')]

        pk_cols = [c["name"] for c in sorted(cols, key=lambda c: c["pk"]) if c["pk"]]
        # INTEGER PRIMARY KEY (with or without AUTOINCREMENT) is a rowid alias
        autoinc = None
        if len(pk_cols) == 1:
            only = next(c for c in cols if c["name"] == pk_cols[0])
            if "INT" in (only["type"] or "").upper():
                autoinc = only["name"]

        indexes = []
        for idx in con.execute(f'PRAGMA index_list("{name}")'):
            idx = dict(idx)
            if idx["origin"] != "c":   # skip pk/unique-constraint indexes
                continue
            icols = [
                dict(i)["name"]
                for i in con.execute(f'PRAGMA index_info("{idx["name"]}")')
            ]
            if icols:
                indexes.append(
                    {"name": idx["name"], "cols": icols, "unique": bool(idx["unique"])}
                )

        uniques = []
        for idx in con.execute(f'PRAGMA index_list("{name}")'):
            idx = dict(idx)
            if idx["origin"] == "u" and idx["unique"]:
                icols = [
                    dict(i)["name"]
                    for i in con.execute(f'PRAGMA index_info("{idx["name"]}")')
                ]
                if icols:
                    uniques.append(icols)

        tables.append(
            {
                "name": name,
                "cols": cols,
                "pk": pk_cols,
                "autoinc": autoinc,
                "fks": fks,
                "indexes": indexes,
                "uniques": uniques,
                "create_sql": create_sql,
            }
        )

    con.close()
    return tables


# --------------------------------------------------------------------------
# DDL generation
# --------------------------------------------------------------------------
def create_table_ddl(t) -> str:
    lines = []
    for c in t["cols"]:
        name, typ = c["name"], pg_type(c["type"])
        if t["autoinc"] == name:
            # GENERATED BY DEFAULT (not ALWAYS) so the data copy can supply ids
            piece = f"{q(name)} BIGINT GENERATED BY DEFAULT AS IDENTITY"
        else:
            piece = f"{q(name)} {typ}"
            if c["notnull"]:
                piece += " NOT NULL"
            dflt = pg_default(c["dflt_value"], typ)
            if dflt is not None:
                piece += f" DEFAULT {dflt}"
        lines.append(piece)

    if t["pk"]:
        lines.append("PRIMARY KEY (" + ", ".join(q(c) for c in t["pk"]) + ")")
    for u in t["uniques"]:
        lines.append("UNIQUE (" + ", ".join(q(c) for c in u) + ")")

    body = ",\n    ".join(lines)
    return f"CREATE TABLE IF NOT EXISTS {q(t['name'])} (\n    {body}\n);"


def fk_ddl(t):
    out = []
    # PRAGMA foreign_key_list returns one row per column in composite keys
    by_id = {}
    for fk in t["fks"]:
        by_id.setdefault(fk["id"], []).append(fk)
    for fid, parts in by_id.items():
        parts.sort(key=lambda p: p["seq"])
        local = ", ".join(q(p["from"]) for p in parts)
        remote = ", ".join(q(p["to"] or "id") for p in parts)
        target = parts[0]["table"]
        on_del = (parts[0].get("on_delete") or "NO ACTION").upper()
        cname = f"fk_{t['name']}_{fid}"
        out.append(
            f"ALTER TABLE {q(t['name'])} ADD CONSTRAINT {q(cname)} "
            f"FOREIGN KEY ({local}) REFERENCES {q(target)} ({remote}) "
            f"ON DELETE {on_del};"
        )
    return out


def index_ddl(t):
    out = []
    for idx in t["indexes"]:
        uniq = "UNIQUE " if idx["unique"] else ""
        cols = ", ".join(q(c) for c in idx["cols"])
        out.append(
            f"CREATE {uniq}INDEX IF NOT EXISTS {q(idx['name'])} "
            f"ON {q(t['name'])} ({cols});"
        )
    return out


# --------------------------------------------------------------------------
# Data copy
# --------------------------------------------------------------------------
def copy_data(sqlite_path, pgconn, tables, batch=1000):
    src = sqlite3.connect(sqlite_path)
    src.row_factory = sqlite3.Row
    totals = {}

    for t in tables:
        name = t["name"]
        colnames = [c["name"] for c in t["cols"]]
        rows = src.execute(f'SELECT * FROM "{name}"').fetchall()
        if not rows:
            totals[name] = 0
            continue

        target = sql.SQL("COPY {} ({}) FROM STDIN").format(
            sql.Identifier(name),
            sql.SQL(", ").join(sql.Identifier(c) for c in colnames),
        )
        with pgconn.cursor() as cur:
            with cur.copy(target) as cp:
                for r in rows:
                    cp.write_row(tuple(r[c] for c in colnames))
        totals[name] = len(rows)

    src.close()
    return totals


def reset_sequences(pgconn, tables):
    with pgconn.cursor() as cur:
        for t in tables:
            if not t["autoinc"]:
                continue
            col = t["autoinc"]
            cur.execute(
                f"SELECT setval("
                f"  pg_get_serial_sequence('{t['name']}', '{col}'),"
                f"  COALESCE((SELECT MAX({q(col)}) FROM {q(t['name'])}), 0) + 1,"
                f"  false)"
            )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqlite", default="telos.db")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--drop-existing", action="store_true")
    ap.add_argument("--schema-only", action="store_true")
    ap.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args()

    tables = read_sqlite_schema(args.sqlite)
    if not tables:
        sys.exit("No tables found in the SQLite file.")

    print(f"Found {len(tables)} tables: {', '.join(t['name'] for t in tables)}\n")

    ddl = [create_table_ddl(t) for t in tables]
    post = []
    for t in tables:
        post += index_ddl(t)
        post += fk_ddl(t)

    if args.dry_run:
        print("-- CREATE TABLES --")
        print("\n\n".join(ddl))
        print("\n-- INDEXES AND FOREIGN KEYS --")
        print("\n".join(post))
        return

    if not args.database_url:
        sys.exit("DATABASE_URL not set (or pass --database-url).")

    url = args.database_url
    if "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"

    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            if args.drop_existing:
                print("Dropping existing tables...")
                for t in reversed(tables):
                    cur.execute(f"DROP TABLE IF EXISTS {q(t['name'])} CASCADE")

            print("Creating tables...")
            for stmt in ddl:
                cur.execute(stmt)
        conn.commit()

        if not args.schema_only:
            print("Copying rows...")
            totals = copy_data(args.sqlite, conn, tables)
            conn.commit()
            for name, n in totals.items():
                print(f"  {name:<24} {n:>7} rows")

            print("Resetting id sequences...")
            reset_sequences(conn, tables)
            conn.commit()

        print("Adding indexes and foreign keys...")
        with conn.cursor() as cur:
            for stmt in post:
                try:
                    cur.execute(stmt)
                    conn.commit()
                except psycopg.errors.DuplicateObject:
                    conn.rollback()
                except psycopg.Error as exc:
                    conn.rollback()
                    print(f"  SKIPPED: {stmt}\n    -> {exc}")

    print("\nDone. Verify with: SELECT COUNT(*) FROM <table>;")


if __name__ == "__main__":
    main()
