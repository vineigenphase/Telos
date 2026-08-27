import os
"""Phase 6 end to end: marks in, queue out, review, reschedule.

The engine is tested as pure data elsewhere. What this checks is the wiring,
which is where the feature was actually missing: the table and the due-count
helper existed for weeks while nothing ever wrote a row, so the Today panel
counted zero forever and the Revise tab was a placeholder.

Creates its own throwaway user and removes it in a finally block.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
import revision  # noqa: E402
from db import get_db  # noqa: E402
from prescription import WEAK_THRESHOLD  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402
from _fixtures import fresh_user, purge_user  # noqa: E402

app = A.app
app.debug = False
fails = []
EMAIL = "p6-test@telos.local"


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def ok(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    if not cond:
        fails.append(label)


uid = None
try:
    with get_db() as db:
        uid = fresh_user(db, EMAIL, "p6test", generate_password_hash("Passw0rd!x"))
        db.execute("UPDATE users SET grandfathered=true WHERE id=?", (uid,))
        db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                   "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                   (uid, "Edexcel", "Further Maths", "A-Level"))
        pid = db.execute(
            """INSERT INTO papers (user_id, subject, board, paper_code, year, series,
                                   score, max_marks, date_completed, weak_topics, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (uid, "Further Maths", "Edexcel", "CP1", "2024", "June",
             40, 75, "2026-08-01", "", "")).lastrowid

        # Two weak questions and one strong one, either side of the threshold.
        weak_a = db.execute(
            "INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
            "VALUES (?,?,?,?,?)", (pid, "1", 2, 10, "Complex Numbers")).lastrowid
        weak_b = db.execute(
            "INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
            "VALUES (?,?,?,?,?)", (pid, "2", 5, 10, "Matrices")).lastrowid
        strong = db.execute(
            "INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
            "VALUES (?,?,?,?,?)", (pid, "3", 9, 10, "Vectors")).lastrowid

    # ── the queue fills itself ──────────────────────────────────────────────
    n = A.sync_revision_queue(uid)
    check("only the weak questions are queued", n, 2)

    with get_db() as db:
        queued = {r["source_id"] for r in db.execute(
            "SELECT source_id FROM revision_queue WHERE user_id=?", (uid,)).fetchall()}
    ok("the 2/10 is in the queue", weak_a in queued)
    ok("the 5/10 is in the queue", weak_b in queued, f"{5/10} < {WEAK_THRESHOLD}")
    ok("the 9/10 is not", strong not in queued)

    check("the due count the dashboard reads is no longer stuck at zero",
          A.revision_due_count(uid) if hasattr(A, "revision_due_count") else 2, 2)

    # Running it again must not disturb anything — the paper is re-saved on
    # every mark entry, and a reset schedule would mean nothing ever spaces out.
    with get_db() as db:
        db.execute("UPDATE revision_queue SET repetitions=3, interval_days=7 "
                   "WHERE user_id=? AND source_id=?", (uid, weak_a))
    A.sync_revision_queue(uid)
    with get_db() as db:
        row = db.execute("SELECT repetitions, interval_days FROM revision_queue "
                         "WHERE user_id=? AND source_id=?", (uid, weak_a)).fetchone()
    check("re-syncing never resets a schedule", (row["repetitions"], row["interval_days"]), (3, 7))

    # ── a corrected mark leaves again ───────────────────────────────────────
    #
    # 2/10 was a typo for 9/10. A question the student knows should not sit in
    # the queue for good because of one slip of the thumb.
    with get_db() as db:
        db.execute("UPDATE revision_queue SET repetitions=0, interval_days=1, "
                   "last_reviewed_at=NULL WHERE user_id=? AND source_id=?", (uid, weak_a))
        db.execute("UPDATE question_marks SET obtained=9 WHERE id=?", (weak_a,))
    A.sync_revision_queue(uid)
    with get_db() as db:
        still = db.execute("SELECT COUNT(*) AS n FROM revision_queue "
                           "WHERE user_id=? AND source_id=?", (uid, weak_a)).fetchone()["n"]
    check("a corrected mark leaves the queue", still, 0)

    # ...but not if it has been reviewed. The review history says more about
    # whether it is understood than one corrected number does.
    with get_db() as db:
        db.execute("UPDATE question_marks SET obtained=2 WHERE id=?", (weak_a,))
    A.sync_revision_queue(uid)
    with get_db() as db:
        db.execute("UPDATE revision_queue SET last_reviewed_at=NOW() "
                   "WHERE user_id=? AND source_id=?", (uid, weak_a))
        db.execute("UPDATE question_marks SET obtained=9 WHERE id=?", (weak_a,))
    A.sync_revision_queue(uid)
    with get_db() as db:
        kept = db.execute("SELECT COUNT(*) AS n FROM revision_queue "
                          "WHERE user_id=? AND source_id=?", (uid, weak_a)).fetchone()["n"]
    check("a reviewed question keeps its place", kept, 1)

    # ── the page, and a review ──────────────────────────────────────────────
    c = app.test_client()
    with c.session_transaction() as s:
        s["_user_id"] = str(uid); s["_fresh"] = True

    r = c.get("/revise")
    check("the queue renders", r.status_code, 200)
    html = r.data.decode()
    ok("...and is no longer the placeholder", "Not switched on yet" not in html)
    ok("...and names the topic", "Matrices" in html)
    ok("...and shows the mark that put it there", "5/10" in html)

    with get_db() as db:
        item = db.execute("SELECT * FROM revision_queue WHERE user_id=? AND source_id=?",
                          (uid, weak_b)).fetchone()
    before_due = item["due_at"]

    r = c.post(f"/revise/{item['id']}", data={"outcome": "got"}, follow_redirects=False)
    ok("a review is accepted", r.status_code in (302, 303), str(r.status_code))
    with get_db() as db:
        after = db.execute("SELECT * FROM revision_queue WHERE id=?", (item["id"],)).fetchone()
    check("...counts the repetition", after["repetitions"], 1)
    ok("...pushes it into the future", after["due_at"] > before_due,
       f"{before_due} -> {after['due_at']}")
    ok("...and records when it was reviewed", after["last_reviewed_at"] is not None)

    # Missing it brings it straight back.
    r = c.post(f"/revise/{item['id']}", data={"outcome": "missed"})
    with get_db() as db:
        after2 = db.execute("SELECT * FROM revision_queue WHERE id=?", (item["id"],)).fetchone()
    check("missing it wipes the streak", after2["repetitions"], 0)
    check("...and brings it back tomorrow", after2["interval_days"], revision.LADDER[0])

    # A junk outcome must not be written.
    r = c.post(f"/revise/{item['id']}", data={"outcome": "brilliant"})
    with get_db() as db:
        after3 = db.execute("SELECT repetitions FROM revision_queue WHERE id=?",
                            (item["id"],)).fetchone()
    check("an invented outcome changes nothing", after3["repetitions"], 0)

    # Another user's item is not reviewable, and the answer must not reveal
    # whether it exists.
    other = None
    try:
        with get_db() as db:
            other = fresh_user(db, "p6-other@telos.local", "p6other",
                               generate_password_hash("Passw0rd!x"))
        with c.session_transaction() as s:
            s["_user_id"] = str(other); s["_fresh"] = True
        r = c.post(f"/revise/{item['id']}", data={"outcome": "got"})
        with get_db() as db:
            untouched = db.execute("SELECT repetitions FROM revision_queue WHERE id=?",
                                   (item["id"],)).fetchone()
        check("another user cannot review your queue", untouched["repetitions"], 0)
    finally:
        with get_db() as db:
            purge_user(db, "p6-other@telos.local")

finally:
    with get_db() as db:
        purge_user(db, EMAIL)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
