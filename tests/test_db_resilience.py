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

# ── the checkout grace ──────────────────────────────────────────────────────
#
# Testing every checkout cost a round trip, and one dashboard render borrows a
# connection thirteen times within a few milliseconds — about 158ms of pure
# overhead per page. A connection handed back moments ago cannot have died of
# an idle timeout in between, so the check is skipped inside a short grace.
#
# That alone would weaken exactly what this file exists to prove, which is why
# the retry below exists. Both halves are checked: the grace has to be short
# enough that a genuinely slept connection is still tested, and the retry has
# to catch the case the grace lets through.
ok("there is a checkout grace at all", hasattr(D, "CHECK_GRACE_SECONDS"),
   f"{getattr(D, 'CHECK_GRACE_SECONDS', None)}s")
ok("...far shorter than Neon's suspend, so a slept connection is still tested",
   0 < D.CHECK_GRACE_SECONDS <= 60, f"{D.CHECK_GRACE_SECONDS}s")
ok("...and shorter than the pool's own idle timeout",
   D.CHECK_GRACE_SECONDS < 300, f"{D.CHECK_GRACE_SECONDS}s vs max_idle=300")

# A connection that has never been returned carries no stamp and must be
# checked — otherwise a brand new pool would hand out untested connections.
class _Unstamped:
    pass


_checked = {"n": 0}
_real_check = D.ConnectionPool.check_connection
D.ConnectionPool.check_connection = staticmethod(
    lambda conn: _checked.__setitem__("n", _checked["n"] + 1))
try:
    D._check_if_idle(_Unstamped())
    ok("a connection with no return stamp is checked", _checked["n"] == 1)

    fresh = _Unstamped()
    fresh._telos_returned_at = D.time.monotonic()
    D._check_if_idle(fresh)
    ok("...one returned moments ago is not", _checked["n"] == 1)

    stale = _Unstamped()
    stale._telos_returned_at = D.time.monotonic() - D.CHECK_GRACE_SECONDS - 1
    D._check_if_idle(stale)
    ok("...and one idle past the grace is", _checked["n"] == 2)
finally:
    D.ConnectionPool.check_connection = _real_check

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


# ── the retry that makes the grace safe ─────────────────────────────────────
#
# The kill above happens milliseconds after the connection was returned, so it
# lands inside the grace and the pre-emptive check is skipped. That the query
# still worked is the retry doing its job, not the check. These pin the rule
# that keeps the retry honest: it may only fire before any statement has
# succeeded, because after that there is a transaction in progress and
# replaying one statement of it against a fresh connection is worse than the
# error.
conn = D.get_db()
ok("a fresh connection has not been used yet", conn._used is False)
conn.execute("SELECT 1").fetchone()
ok("...and is marked used once a statement succeeds", conn._used is True)
conn.close()


class _DeadOnce:
    """Fails the first statement the way a terminated backend does."""

    def __init__(self):
        self.calls = 0

    def cursor(self, **kw):
        self.calls += 1
        if self.calls == 1:
            raise D.psycopg.OperationalError("terminating connection")
        return _real_cursor_of_a_live_connection()


live = D.get_db()
_real_cursor_of_a_live_connection = lambda **kw: live._conn.cursor(
    row_factory=D._row_factory)

probe = D.Connection(_DeadOnce(), D._get_pool())
try:
    row = probe.execute("SELECT 1 AS one").fetchone()
    check("a dead connection is replaced and the statement retried",
          row["one"], 1)
except Exception as e:
    ok("a dead connection is replaced and the statement retried", False,
       f"{type(e).__name__}: {e}")

# Mid-transaction, the same failure must surface rather than be retried.
probe2 = D.Connection(_DeadOnce(), D._get_pool())
probe2._used = True
try:
    probe2.execute("SELECT 1")
    ok("a dead connection mid-transaction is NOT retried", False,
       "the error was swallowed")
except D.psycopg.OperationalError:
    ok("a dead connection mid-transaction is NOT retried", True)
except Exception as e:
    ok("a dead connection mid-transaction is NOT retried", False,
       f"wrong error: {type(e).__name__}")
live.close()

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
