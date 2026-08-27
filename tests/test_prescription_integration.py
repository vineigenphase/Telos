import os
"""Phase 4 integration: DB wiring, question bank parsing, gating, Today panel."""
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402
from _fixtures import fresh_user, purge_user  # noqa: E402

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
upload_id = None
c = app.test_client()
try:
    with get_db() as db:
        uid = fresh_user(db, "p4-test@telos.local", "p4test",
                         generate_password_hash("Passw0rd!x"))
        # Give the account a subject. Every app page redirects a signed-in
        # student with no subjects to setup, so a test user without one
        # never reaches the page it is trying to assert on.
        db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                   "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                   (uid, "Edexcel", "Further Maths", "A-Level"))
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
            return cur.lastrowid

    def add_mark(pid, q_num, got, mx, topic):
        with get_db() as db:
            db.execute("INSERT INTO question_marks (paper_id, q_num, obtained, max_marks, topic) "
                       "VALUES (?,?,?,?,?)", (pid, q_num, got, mx, topic))

    # 1. No marks at all -> a stated empty state, not a crash
    res = A.build_prescriptions(uid)
    check("no data is not ready", res["ready"], False)
    check("no data explains itself", res["reason"], "no_topics")

    # 2. Marks across three papers produce a ranking and picks
    p1 = add_paper("CP1", "2023", 40, date="2026-08-01")
    p2 = add_paper("CP2", "2023", 45, date="2026-08-05")
    p3 = add_paper("FM1", "2023", 50, date="2026-08-10")
    for pid in (p1, p2, p3):
        add_mark(pid, "1", 3, 10, "Complex Numbers")   # 30% — bad and frequent
        add_mark(pid, "2", 9, 10, "Matrices")          # strong
        add_mark(pid, "3", 4, 10, "Proof")             # weak
    res = A.build_prescriptions(uid)
    check("prescribes from real rows", res["ready"], True)
    check("three picks", len(res["picks"]), 3)
    check("weakest frequent topic leads", res["topics"][0]["topic"], "Complex Numbers")
    check("strong topic never prescribed",
          "Matrices" in {p["topic"] for p in res["picks"]}, False)
    check("with no bank everything is a redo", {p["kind"] for p in res["picks"]}, {"redo"})
    check("redo picks link to a real paper",
          all(p.get("paper_id") in pids for p in res["picks"] if p["kind"] == "redo"), True)

    # 3. Untagged marks are ignored rather than crashing the panel
    add_mark(p1, "9", 1, 10, None)
    res = A.build_prescriptions(uid)
    check("untagged marks don't break it", res["ready"], True)

    # 4. A tagged question bank supplies unattempted questions, and its
    #    JSON topics column is parsed on the way through
    with get_db() as db:
        cur = db.execute(
            """INSERT INTO uploads (user_id, filename, orig_name, subject, board,
                                    paper_code, year, file_type, file_size)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (uid, "p4.pdf", "p4.pdf", "Further Maths", "Edexcel", "CP3", "2021",
             "question_paper", 1000))
        upload_id = cur.lastrowid
        db.execute(
            """INSERT INTO question_bank (upload_id, user_id, q_num, page_num,
                                          topics, keywords, max_marks, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (upload_id, uid, "7", 3, json.dumps(["Complex Numbers"]), "", 12, None))
    res = A.build_prescriptions(uid)
    check("bank question is preferred over a redo", res["picks"][0]["kind"], "new")
    check("bank pick names its source", res["picks"][0]["source"], "2021 CP3 Q7")
    check("bank pick keeps its id", res["picks"][0]["bank_id"] is not None, True)

    # 5. A malformed topics column must not take the dashboard down
    with get_db() as db:
        db.execute("UPDATE question_bank SET topics=? WHERE upload_id=?",
                   ("not json at all", upload_id))
    res = A.build_prescriptions(uid)
    check("unparseable bank topics degrade to untagged", res["ready"], True)
    check("...and fall back to redos", res["picks"][0]["kind"], "redo")
    with get_db() as db:
        db.execute("UPDATE question_bank SET topics=? WHERE upload_id=?",
                   (json.dumps(["Complex Numbers"]), upload_id))

    # 6. Free user: the Today panel must not leak, and the teaser must appear
    with c.session_transaction() as s:
        s["_user_id"] = str(uid)
        s["_fresh"] = True
    html = c.get("/").data.decode()
    check("free user sees the upgrade teaser", "Unlock with Pro" in html, True)
    check("free user does not see the Next up card", 'class="nextup"' in html, False)
    check("free user does not see a prescription", "rx-item" in html, False)

    # 7. Pro user gets the panel, and every pick shows its reason
    with get_db() as db:
        db.execute("UPDATE users SET grandfathered=true WHERE id=?", (uid,))
    html = c.get("/").data.decode()
    check("pro user sees the Next up card", 'class="nextup"' in html, True)
    # Match the heading element, not the bare word: "Today" also appears as a
    # timeline day label, which made the old assertion pass for the wrong
    # reason once the panel it was checking for no longer existed.
    check("section is headed Next up",
          '<h2 class="section-title">Next up</h2>' in html, True)
    # The lead pick is the Next up card; picks 2 and 3 are compact rows.
    check("the two follow-up picks are rendered",
          html.count('class="rx-item"'), 2)
    check("stat row is rendered", 'class="statrow"' in html, True)
    # Jinja escapes the apostrophe in "You're", so match past it.
    check("the why line is shown", "at 30% on Complex Numbers" in html, True)
    check("the per-paper cost is shown", "marks/paper" in html, True)
    check("a new-question pick is tagged", "rx-tag new" in html, True)

    # 8. The panel is driven by the data, not hardcoded — fix the weak topic
    #    and it must drop out of the recommendations
    with get_db() as db:
        db.execute("UPDATE question_marks SET obtained=10 WHERE topic='Complex Numbers' "
                   "AND paper_id IN (SELECT id FROM papers WHERE user_id=?)", (uid,))
    res = A.build_prescriptions(uid)
    check("a fixed topic stops being prescribed",
          "Complex Numbers" in {p["topic"] for p in res["picks"]}, False)

    # 9. Revision due count reads the Phase 6 table without needing Phase 6
    check("due count is zero before Phase 6", A.revision_due_count(uid), 0)
finally:
    with get_db() as db:
        if uid:
            db.execute("DELETE FROM question_bank WHERE user_id=?", (uid,))
            if upload_id:
                db.execute("DELETE FROM uploads WHERE id=?", (upload_id,))
            db.execute("DELETE FROM grade_predictions WHERE user_id=?", (uid,))
            for pid in pids:
                db.execute("DELETE FROM question_marks WHERE paper_id=?", (pid,))
            db.execute("DELETE FROM papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
            print(f"cleaned up test user {uid}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
