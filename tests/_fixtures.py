"""Shared setup for suites that create a throwaway user.

Each suite uses a fixed email so its rows are recognisable, and removes them in
a finally block. That is enough until a run is interrupted — Ctrl-C, a killed
process, a machine that sleeps — and the finally never runs. The next run then
fails on a unique-constraint violation whose message says nothing about the
interruption, in whichever suite happens to go first.

`fresh_user` clears any leftover under that email before inserting, so an
interrupted run costs one run rather than every run after it.

The tables to clear are read from the schema rather than listed here, because a
list would go stale silently: a new user-owned table would simply not be
cleaned, and the leftover would surface as an unrelated failure months later.
"""


def _owned_tables(db):
    """Tables with a user_id column, i.e. everything a user owns directly."""
    rows = db.execute(
        "SELECT table_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND column_name = 'user_id' "
        "ORDER BY table_name").fetchall()
    return [r["table_name"] for r in rows]


def purge_user(db, email):
    """Delete a fixture user and everything hanging off it. Safe if absent.

    No try/except around the deletes: in Postgres a failed statement aborts the
    whole transaction, so swallowing one error would only make the next
    statement fail for a reason that has nothing to do with the fixture.
    """
    row = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if not row:
        return
    uid = row["id"]
    # question_marks hangs off papers, not off the user, so it goes first or
    # the papers delete trips its foreign key.
    db.execute("DELETE FROM question_marks WHERE paper_id IN "
               "(SELECT id FROM papers WHERE user_id=?)", (uid,))
    for table in _owned_tables(db):
        db.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
    db.execute("DELETE FROM users WHERE id=?", (uid,))


def fresh_user(db, email, username, password_hash, **columns):
    """Insert a throwaway user, clearing any leftover of the same name first."""
    purge_user(db, email)
    cols = ["email", "username", "password_hash"] + list(columns)
    vals = [email, username, password_hash] + list(columns.values())
    return db.execute(
        f"INSERT INTO users ({','.join(cols)}) "
        f"VALUES ({','.join('?' for _ in cols)})", tuple(vals)).lastrowid
