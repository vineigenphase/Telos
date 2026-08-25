import os
"""Neon scales to zero; the pool must survive it.

Reproduces the real failure rather than trusting the fix: take a connection,
kill its backend from a second connection the way Neon's shutdown does, put it
back, then ask the pool for a connection and run a query. Without
`check=ConnectionPool.check_connection` on the pool this raises AdminShutdown
(or OperationalError on a closed socket) and the user gets a 500.

Worth a suite of its own because the symptom is invisible in normal testing:
everything passes against a warm database, and the failure only appears after
the app has been idle long enough for Neon to sleep — which is to say, in front
of a real user, and never in front of a developer.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db as D  # noqa: E402

fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def ok(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# The pool is configured to test connections on checkout.
pool = D._get_pool()
ok("the pool checks connections on checkout",
   getattr(pool, "_check", None) is not None,
   "check=" + repr(getattr(pool, "_check", None)))

# A baseline query, and the backend pid behind it.
with D.get_db() as conn:
    pid = conn.execute("SELECT pg_backend_pid() AS pid").fetchone()["pid"]
ok("a normal query works", bool(pid), f"backend pid {pid}")

# Kill that backend from a separate connection — this is what Neon's
# scale-to-zero does to every connection the pool is holding.
with D.get_db() as killer:
    killer.execute("SELECT pg_terminate_backend(?)", (pid,))
print(f"      (terminated backend {pid})")

# The pool still believes it holds a live connection. Asking for one must
# transparently produce a working connection rather than handing over the
# corpse.
try:
    with D.get_db() as conn:
        row = conn.execute("SELECT 1 AS one").fetchone()
    check("a query after the backend was killed still works", row["one"], 1)
except Exception as e:
    ok("a query after the backend was killed still works", False,
       f"{type(e).__name__}: {e}")

# And the app is genuinely usable afterwards, not merely non-crashing.
try:
    with D.get_db() as conn:
        n = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    ok("real queries work after a wake-up", n >= 0, f"{n} users")
except Exception as e:
    ok("real queries work after a wake-up", False, f"{type(e).__name__}: {e}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
