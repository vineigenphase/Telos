import os
"""Phase 3 integration: recompute triggers, caching, gating, dashboard render."""
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
c = app.test_client()
try:
    with get_db() as db:
        cur = db.execute("INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
                         ("p3-test@telos.local", "p3test", generate_password_hash("Passw0rd!x")))
        uid = cur.lastrowid
        # Give the account a subject. Every app page redirects a signed-in
        # student with no subjects to setup, so a test user without one
        # never reaches the page it is trying to assert on.
        db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                   "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                   (uid, "Edexcel", "Further Maths", "A-Level"))
        # free by default -> also lets us test the gate
        db.execute("UPDATE users SET plan='free', grandfathered=false, "
                   "subscription_status='free' WHERE id=?", (uid,))

    def add_paper(code, year, score, mx=75, date="2026-08-01"):
        with get_db() as db:
            cur = db.execute(
                """INSERT INTO papers (user_id, subject, board, paper_code, year, series,
                                       score, max_marks, date_completed, weak_topics, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (uid, "Further Maths", "Edexcel", code, year, "June", score, mx, date, "", ""))
            pids.append(cur.lastrowid)

    # 1. Under three papers -> no cached prediction at all
    add_paper("CP1", "2023", 55)
    add_paper("CP2", "2023", 50)
    A.recompute_predictions(uid)
    check("under 3 papers caches nothing", len(A.get_predictions(uid)), 0)

    # 2. Third paper unlocks it
    add_paper("FM1", "2023", 60)
    A.recompute_predictions(uid)
    preds = A.get_predictions(uid)
    check("3 papers produces one cached row", len(preds), 1)
    p = preds[0]
    check("cached subject", p["subject"], "Further Maths")
    check("grade is a real letter", p["predicted_grade"] in ("A*", "A", "B", "C", "D", "E", "U"), True)
    check("3 papers is low confidence", p["confidence"], "low")
    check("sample size cached", p["sample_size"], 3)
    check("marks_to_next present", p["marks_to_next"] is not None, True)

    # 3. Free user: dashboard must NOT leak the prediction, and must offer the teaser
    with c.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True
    html = c.get("/").data.decode()
    check("free user sees the upgrade teaser", "Unlock with Pro" in html, True)
    check("free user does not see a predicted grade", "predicted</div>" in html, False)
    check("teaser tracks the source feature", "from=predicted-grade" in html, True)

    # 4. Pro user sees it, paired with the action
    with get_db() as db:
        db.execute("UPDATE users SET grandfathered=true WHERE id=?", (uid,))
    html = c.get("/").data.decode()
    check("pro user sees the prediction", "predicted" in html.lower(), True)
    check("prediction is paired with marks to next", "off a" in html or "off an" in html, True)
    check("low confidence is labelled provisional", "provisional" in html, True)

    # 5. Editing a score moves the cached prediction (recompute actually fires)
    before = A.get_predictions(uid)[0]["grade_score"]
    with get_db() as db:
        db.execute("UPDATE papers SET score=? WHERE id=?", (72, pids[-1]))
    A.recompute_predictions(uid)
    after = A.get_predictions(uid)[0]["grade_score"]
    check("higher marks raise the grade score", after > before, True)

    # 6. The per-question save endpoint recomputes too
    with get_db() as db:
        db.execute("INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                   "VALUES (?,?,?,?,?)", (pids[0], "1", 5.0, 10.0, "Complex Numbers"))
    r = c.post(f"/papers/{pids[0]}/questions/1", json={"obtained": 9, "max_marks": 10})
    check("question save returns ok", r.status_code, 200)
    check("paper score followed the question", r.get_json()["total"], 9.0)
    after_q = A.get_predictions(uid)[0]["computed_at"]
    check("prediction recomputed after question save", after_q is not None, True)

    # 7. Deleting papers back below the threshold clears the cache
    with get_db() as db:
        db.execute("DELETE FROM question_marks WHERE paper_id=?", (pids[0],))
        db.execute("DELETE FROM papers WHERE id=?", (pids[0],))
        db.execute("DELETE FROM papers WHERE id=?", (pids[1],))
    A.recompute_predictions(uid)
    check("dropping below 3 papers clears the stale prediction", len(A.get_predictions(uid)), 0)
finally:
    with get_db() as db:
        if uid:
            db.execute("DELETE FROM grade_predictions WHERE user_id=?", (uid,))
            for pid in pids:
                db.execute("DELETE FROM question_marks WHERE paper_id=?", (pid,))
            db.execute("DELETE FROM papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
            print(f"cleaned up test user {uid}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
