import os
"""Migration 005: question_marks timestamps, prediction history, stat deltas.

The interesting cases here are the *absent* ones. A delta must be None when
there is nothing to compare against, never 0 — a new account has no trend, and
rendering that as "+0 this week" is a lie the dashboard would tell every new
user on their first day.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

app = A.app
app.debug = False
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


uid = None
pids = []
try:
    with get_db() as db:
        cur = db.execute("INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
                         ("delta-test@telos.local", "deltatest",
                          generate_password_hash("Passw0rd!x")))
        uid = cur.lastrowid
        db.execute("UPDATE users SET grandfathered=true WHERE id=?", (uid,))

    # 1. Schema actually landed
    with get_db() as db:
        col = db.execute(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name='question_marks' AND column_name='created_at'").fetchone()
        check("question_marks.created_at exists", col is not None, True)
        tbl = db.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name='grade_prediction_history'").fetchone()
        check("grade_prediction_history exists", tbl is not None, True)

    # 2. Empty account: values are zero, deltas are None (not 0)
    s = A.dashboard_stats(uid)
    check("no papers yet", s["papers"]["value"], 0)
    check("no papers delta", s["papers"]["delta"], None)
    check("no questions delta", s["questions"]["delta"], None)
    check("no accuracy value", s["accuracy"]["value"], None)
    check("no accuracy delta", s["accuracy"]["delta"], None)
    check("no grade yet", s["grade"]["value"], None)
    check("no grade delta", s["grade"]["delta_letters"], None)

    def add_paper(code, year, score, mx=75, date="2026-08-20"):
        with get_db() as db:
            cur = db.execute(
                """INSERT INTO papers (user_id, subject, board, paper_code, year, series,
                                       score, max_marks, date_completed, weak_topics, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (uid, "Further Maths", "Edexcel", code, year, "June", score, mx, date, "", ""))
            pids.append(cur.lastrowid)
            return cur.lastrowid

    # 3. Marks get a timestamp automatically
    p1 = add_paper("CP1", "2023", 48)
    with get_db() as db:
        db.execute("INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                   "VALUES (?,?,?,?,?)", (p1, "1", 6, 10, "Proof"))
        stamped = db.execute(
            "SELECT created_at FROM question_marks WHERE paper_id=?", (p1,)).fetchone()
    check("new marks are stamped without being told to",
          stamped["created_at"] is not None, True)

    s = A.dashboard_stats(uid)
    check("questions counted", s["questions"]["value"], 1)
    check("questions delta counts this week", s["questions"]["delta"], 1)
    check("accuracy computed", s["accuracy"]["value"], 60.0)
    # Only one window has data, so there is still no week-on-week comparison.
    check("accuracy delta needs both windows", s["accuracy"]["delta"], None)

    # 4. Accuracy delta appears once a prior window exists
    with get_db() as db:
        db.execute("INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic, "
                   "created_at) VALUES (?,?,?,?,?, NOW() - INTERVAL '10 days')",
                   (p1, "2", 2, 10, "Proof"))          # 20% ten days ago
    s = A.dashboard_stats(uid)
    check("accuracy delta appears with both windows", s["accuracy"]["delta"], 40.0)

    # 5. Papers delta only counts the trend window
    add_paper("CP2", "2023", 52, date="2020-01-01")     # long ago
    s = A.dashboard_stats(uid)
    check("all papers counted", s["papers"]["value"], 2)
    check("old paper excluded from the delta", s["papers"]["delta"], 1)

    # 6. History records a genuine move, and only a genuine move
    add_paper("FM1", "2023", 55)
    A.recompute_predictions(uid)
    with get_db() as db:
        n1 = db.execute("SELECT COUNT(*) AS n FROM grade_prediction_history "
                        "WHERE user_id=?", (uid,)).fetchone()["n"]
    check("first prediction is recorded", n1, 1)

    A.recompute_predictions(uid)                        # nothing changed
    with get_db() as db:
        n2 = db.execute("SELECT COUNT(*) AS n FROM grade_prediction_history "
                        "WHERE user_id=?", (uid,)).fetchone()["n"]
    check("an unchanged recompute adds no row", n2, 1)

    with get_db() as db:
        db.execute("UPDATE papers SET score=? WHERE id=?", (70, pids[-1]))
    A.recompute_predictions(uid)
    with get_db() as db:
        n3 = db.execute("SELECT COUNT(*) AS n FROM grade_prediction_history "
                        "WHERE user_id=?", (uid,)).fetchone()["n"]
    check("a real move is recorded", n3, 2)

    # 7. Grade delta needs history older than the window
    s = A.dashboard_stats(uid)
    check("grade shows", s["grade"]["value"] in ("A*", "A", "B", "C", "D", "E", "U"), True)
    check("no delta from history inside the window", s["grade"]["delta_letters"], None)

    with get_db() as db:
        db.execute("UPDATE grade_prediction_history SET recorded_at = NOW() - "
                   "INTERVAL '30 days', grade_score = 3.0, predicted_grade='C' "
                   "WHERE user_id=? AND id = (SELECT MIN(id) FROM grade_prediction_history "
                   "WHERE user_id=?)", (uid, uid))
    s = A.dashboard_stats(uid)
    check("grade delta appears once history is old enough",
          s["grade"]["delta_letters"] is not None, True)
    check("grade delta is positive after improving",
          s["grade"]["delta_letters"] > 0, True)
    check("grade names its subject", s["grade"]["subject"], "Further Maths")
finally:
    with get_db() as db:
        if uid:
            db.execute("DELETE FROM grade_prediction_history WHERE user_id=?", (uid,))
            db.execute("DELETE FROM grade_predictions WHERE user_id=?", (uid,))
            for pid in pids:
                db.execute("DELETE FROM question_marks WHERE paper_id=?", (pid,))
            db.execute("DELETE FROM papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
            print(f"cleaned up test user {uid}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
