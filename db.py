"""
Telos database layer — Postgres (Neon) drop-in replacement for sqlite3.

Goal: change as little of app.py as possible. This module gives you a
connection object that behaves like the sqlite3 one you already use:

    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    row["email"]          # works
    row[0]                # also works (sqlite3.Row compatibility)
    db.execute("INSERT INTO papers (user_id) VALUES (?)", (uid,))
    db.commit()
    db.close()

What it handles for you:
  * `?` placeholders  ->  `%s`
  * sqlite3.Row-style rows (index access AND key access)
  * cursor.lastrowid on INSERT (via RETURNING)
  * connection pooling, so Neon's scale-to-zero doesn't cost you a cold
    start on every single request

Requires:  pip install "psycopg[binary,pool]"
Env var:   DATABASE_URL  (Neon gives you this; use the -pooler host)
"""

from __future__ import annotations

import os
import re
import threading

import psycopg
from psycopg import sql as _sql
from psycopg_pool import ConnectionPool

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy it from the Neon dashboard "
        "(use the connection string ending in -pooler for the app)."
    )

# Neon requires TLS. Add it if the URL doesn't already say so.
if "sslmode=" not in DATABASE_URL:
    DATABASE_URL += ("&" if "?" in DATABASE_URL else "?") + "sslmode=require"


# --------------------------------------------------------------------------
# Row: quacks like sqlite3.Row
# --------------------------------------------------------------------------
class Row(dict):
    """dict that also supports positional access, like sqlite3.Row."""

    __slots__ = ()

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        if isinstance(key, slice):
            return list(self.values())[key]
        return dict.__getitem__(self, key)

    def __getattr__(self, name):
        try:
            return dict.__getitem__(self, name)
        except KeyError as exc:
            raise AttributeError(name) from exc


def _row_factory(cursor):
    desc = cursor.description
    if desc is None:
        return lambda values: values
    cols = [c.name for c in desc]

    def make(values):
        return Row(zip(cols, values))

    return make


# --------------------------------------------------------------------------
# Placeholder translation:  ?  ->  %s   (but not inside string literals)
# --------------------------------------------------------------------------
_LITERAL_RE = re.compile(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"")


def translate(sql: str) -> str:
    """Replace ? placeholders with %s, ignoring anything inside quotes.

    Also escapes any literal % in the SQL so psycopg doesn't try to
    interpret it as a placeholder (matters for LIKE '%foo%').
    """
    out = []
    last = 0
    for m in _LITERAL_RE.finditer(sql):
        out.append(sql[last : m.start()].replace("%", "%%").replace("?", "%s"))
        out.append(m.group(0).replace("%", "%%"))
        last = m.end()
    out.append(sql[last:].replace("%", "%%").replace("?", "%s"))
    result = "".join(out)
    # undo the escaping we just did to our own placeholders
    return result.replace("%%s", "%s")


_INSERT_RE = re.compile(r"^\s*INSERT\s+INTO\s+([\"\w.]+)", re.IGNORECASE)
_HAS_RETURNING = re.compile(r"\bRETURNING\b", re.IGNORECASE)


# --------------------------------------------------------------------------
# Cursor wrapper
# --------------------------------------------------------------------------
class Cursor:
    def __init__(self, cur, conn):
        self._cur = cur
        self._conn = conn
        self.lastrowid = None

    def execute(self, sql, params=()):
        pg_sql = translate(sql)
        m = _INSERT_RE.match(sql)
        wants_id = bool(m) and not _HAS_RETURNING.search(sql)

        if wants_id:
            # Try to emulate sqlite3's cursor.lastrowid. Guarded by a
            # savepoint so a table with no `id` column doesn't poison
            # the surrounding transaction.
            try:
                self._cur.execute("SAVEPOINT _telos_lastrowid")
                self._cur.execute(pg_sql + " RETURNING id", params)
                row = self._cur.fetchone()
                self.lastrowid = row[0] if row else None
                self._cur.execute("RELEASE SAVEPOINT _telos_lastrowid")
                return self
            except psycopg.errors.UndefinedColumn:
                self._cur.execute("ROLLBACK TO SAVEPOINT _telos_lastrowid")
            except psycopg.errors.SyntaxError:
                # e.g. INSERT ... ON CONFLICT DO NOTHING RETURNING is fine,
                # but exotic statements may not be. Fall through.
                self._cur.execute("ROLLBACK TO SAVEPOINT _telos_lastrowid")

        self._cur.execute(pg_sql, params)
        return self

    def executemany(self, sql, seq):
        self._cur.executemany(translate(sql), seq)
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def fetchmany(self, size=None):
        return self._cur.fetchmany(size) if size else self._cur.fetchmany()

    def __iter__(self):
        return iter(self._cur)

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description

    def close(self):
        self._cur.close()


# --------------------------------------------------------------------------
# Connection wrapper
# --------------------------------------------------------------------------
class Connection:
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
        self._closed = False

    def execute(self, sql, params=()):
        cur = Cursor(self._conn.cursor(row_factory=_row_factory), self._conn)
        return cur.execute(sql, params)

    def executemany(self, sql, seq):
        cur = Cursor(self._conn.cursor(row_factory=_row_factory), self._conn)
        return cur.executemany(sql, seq)

    def executescript(self, script):
        """sqlite3 compatibility — runs a multi-statement script."""
        with self._conn.cursor() as cur:
            cur.execute(script)
        self._conn.commit()

    def cursor(self):
        return Cursor(self._conn.cursor(row_factory=_row_factory), self._conn)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self._conn.commit()
        except Exception:
            self._conn.rollback()
        self._pool.putconn(self._conn)

    # context-manager support: `with get_db() as db:`
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.rollback()
        self.close()
        return False


# --------------------------------------------------------------------------
# Pool
# --------------------------------------------------------------------------
_pool = None
_pool_lock = threading.Lock()


def _get_pool():
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ConnectionPool(
                    DATABASE_URL,
                    min_size=1,
                    max_size=int(os.environ.get("DB_POOL_MAX", "5")),
                    max_idle=300,
                    kwargs={"autocommit": False},
                    # Neon scales to zero. When it does, every connection the
                    # pool is holding is severed at the server, but the pool has
                    # no way to know that until something tries to use one — so
                    # the first request after an idle period died with
                    # "AdminShutdown: terminating connection due to
                    # administrator command", as a 500 in the user's face.
                    #
                    # It was never reliably just the first request, either. The
                    # pool holds several connections and each request borrows a
                    # different one, so a wake-up could produce a run of 500s
                    # until every dead connection had been handed out once.
                    #
                    # check_connection tests a connection on the way out of the
                    # pool and quietly replaces it if it is dead. The cost is a
                    # round-trip per checkout; the alternative is that waking
                    # the app looks like an outage.
                    check=ConnectionPool.check_connection,
                    open=True,
                )
    return _pool


def get_db():
    """Drop-in replacement for your old sqlite3 get_db()."""
    pool = _get_pool()
    return Connection(pool.getconn(), pool)


def close_db(e=None):
    """Register with app.teardown_appcontext if you store db on `g`."""
    from flask import g

    db = g.pop("db", None)
    if db is not None:
        db.close()
