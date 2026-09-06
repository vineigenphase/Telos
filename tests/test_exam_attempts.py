import os
"""Exam Mode attempt lifecycle — engine spec section 4.

The four tests phase 2 names, plus the ones the spec's own rules imply:

  * start -> answer -> submit computes raw and scaled correctly
  * a submit after ends_at yields status `expired`
  * a free user gets 402 on start
  * a second start on a live attempt resumes it

And, because section 6 is a promise rather than a preference, that a live
attempt's responses never carry an answer — the one failure here that would be
invisible until a student found it.

Timing is tested by moving `ends_at` in the database rather than by sleeping.
A test that waits 75 minutes does not get run.
"""
import json
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
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


pro_id = free_id = None
paper_id = None
made_paper = False

try:
    # ── fixtures ────────────────────────────────────────────────────────────
    with get_db() as db:
        pro_id = fresh_user(db, "exam-pro@telos.local", "exampro",
                            generate_password_hash("Passw0rd!x"))
        free_id = fresh_user(db, "exam-free@telos.local", "examfree",
                             generate_password_hash("Passw0rd!x"))
        db.execute("UPDATE users SET grandfathered=true WHERE id=?", (pro_id,))
        # A fresh user is already free — plan 'free', no subscription. Setting
        # subscription_status to NULL explicitly trips a check constraint, and
        # is not needed: the default IS the free state.
        db.execute("UPDATE users SET grandfathered=false WHERE id=?", (free_id,))

        # The setup gate redirects a signed-in student with no subjects to
        # onboarding, so without a subject every request here is a 302 and
        # nothing below is actually exercised.
        for uid in (pro_id, free_id):
            db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                       "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                       (uid, "Edexcel", "Further Maths", "A-Level"))

        # A published paper to sit. Prefer a real one; make a throwaway if the
        # Mock A papers are not loaded, so the suite does not depend on content.
        row = db.execute("SELECT id, question_count FROM exam_papers "
                         "WHERE family='TMUA' ORDER BY id LIMIT 1").fetchone()
        if row:
            paper_id = row["id"]
            db.execute("UPDATE exam_papers SET is_published=TRUE WHERE id=?", (paper_id,))
        else:
            made_paper = True
            paper_id = db.execute(
                "INSERT INTO exam_papers (paper_code, family, module, title, "
                "  duration_sec, question_count, is_published, family_marks) "
                "VALUES ('TEST-LIFECYCLE','TMUA','P1','Lifecycle test',4500,20,TRUE,40) "
                "RETURNING id").fetchone()["id"]
            for i in range(1, 21):
                db.execute(
                    "INSERT INTO exam_questions (paper_id, n, topic, spec_refs, "
                    "  stem_html, options, answer, traps) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (paper_id, i, "T", ["MM1.1"], f"<p>q{i}</p>",
                     json.dumps({c: c for c in "ABCDEF"}), "C",
                     json.dumps({c: "x" for c in "ABDEF"})))

        code = db.execute("SELECT paper_code FROM exam_papers WHERE id=?",
                          (paper_id,)).fetchone()["paper_code"]
        questions = db.execute(
            "SELECT id, n, answer FROM exam_questions WHERE paper_id=? ORDER BY n",
            (paper_id,)).fetchall()
        qs = [{"id": q["id"], "n": q["n"], "answer": q["answer"]} for q in questions]

    def client_for(uid):
        c = app.test_client()
        with c.session_transaction() as s:
            s["_user_id"] = str(uid)
            s["_fresh"] = True
        return c

    pro = client_for(pro_id)
    free = client_for(free_id)

    # ── 1. a free user gets 402 on start ────────────────────────────────────
    r = free.post(f"/exam/{code}/start")
    check("a free user cannot start a paper", r.status_code, 402)
    body = r.get_json() or {}
    check("and is told why", body.get("error"), "pro_required")
    check("and given somewhere to go", "upgrade_url" in body, True)

    # The list itself stays visible — section 3 gates the action, not the page.
    check("but the free user can still see the tab", free.get("/exam").status_code, 200)

    # ── 2. start is idempotent while an attempt is live ─────────────────────
    r1 = pro.post(f"/exam/{code}/start")
    check("a Pro user can start", r1.status_code, 200)
    a1 = r1.get_json()
    check("the first start is not a resume", a1["resumed"], False)

    r2 = pro.post(f"/exam/{code}/start")
    a2 = r2.get_json()
    check("a second start resumes rather than restarting", a2["resumed"], True)
    check("and returns the same attempt", a2["attempt_id"], a1["attempt_id"])

    attempt_id = a1["attempt_id"]
    check("the clock is the paper's duration", a1["remaining_sec"] > 4000, True)

    # ── 3. answering ────────────────────────────────────────────────────────
    #
    # Answer the first twelve correctly, three wrongly, leave five blank.
    for q in qs[:12]:
        pro.post(f"/exam/attempt/{attempt_id}/answer",
                 json={"question_id": q["id"], "selected": q["answer"]})
    wrong = {"A": "B", "B": "A", "C": "D", "D": "C", "E": "F", "F": "E"}
    for q in qs[12:15]:
        pro.post(f"/exam/attempt/{attempt_id}/answer",
                 json={"question_id": q["id"], "selected": wrong[q["answer"]]})

    r = pro.post(f"/exam/attempt/{attempt_id}/answer",
                 json={"question_id": qs[0]["id"], "selected": "Z"})
    check("an option outside A-H is refused", r.status_code, 400)

    r = pro.post(f"/exam/attempt/{attempt_id}/answer",
                 json={"question_id": 99999999, "selected": "A"})
    check("a question from another paper is refused", r.status_code, 400)

    # change_count counts changes of mind, not autosaves.
    with get_db() as db:
        before = db.execute("SELECT change_count FROM exam_responses "
                            "WHERE attempt_id=? AND question_id=?",
                            (attempt_id, qs[0]["id"])).fetchone()["change_count"]
    pro.post(f"/exam/attempt/{attempt_id}/answer",
             json={"question_id": qs[0]["id"], "selected": qs[0]["answer"]})
    with get_db() as db:
        same = db.execute("SELECT change_count FROM exam_responses "
                          "WHERE attempt_id=? AND question_id=?",
                          (attempt_id, qs[0]["id"])).fetchone()["change_count"]
    check("re-saving the same answer is not a change", same, before)

    pro.post(f"/exam/attempt/{attempt_id}/answer",
             json={"question_id": qs[0]["id"], "selected": wrong[qs[0]["answer"]]})
    with get_db() as db:
        after = db.execute("SELECT change_count FROM exam_responses "
                           "WHERE attempt_id=? AND question_id=?",
                           (attempt_id, qs[0]["id"])).fetchone()["change_count"]
    check("changing the answer is", after, before + 1)
    # put it back so the arithmetic below is predictable
    pro.post(f"/exam/attempt/{attempt_id}/answer",
             json={"question_id": qs[0]["id"], "selected": qs[0]["answer"]})

    # ── 4. time is clamped to the attempt window ────────────────────────────
    pro.post(f"/exam/attempt/{attempt_id}/time",
             json={"question_id": qs[0]["id"], "delta_sec": 999999})
    with get_db() as db:
        t = db.execute("SELECT time_sec FROM exam_responses WHERE attempt_id=? "
                       "AND question_id=?", (attempt_id, qs[0]["id"])).fetchone()["time_sec"]
    check("a client cannot report more time than the paper ran for", t <= 4500, True)

    # ── 5. results are refused while the attempt is live (section 6) ────────
    r = pro.get(f"/exam/attempt/{attempt_id}/results.json")
    check("results are refused while live", r.status_code, 409)

    # ── 6. submit marks and scales ──────────────────────────────────────────
    r = pro.post(f"/exam/attempt/{attempt_id}/submit")
    check("submit succeeds", r.status_code, 200)
    out = r.get_json()
    check("status is submitted", out["status"], "submitted")
    check("raw counts exactly the correct answers", out["raw"], 12)

    # 12/20 on TMUA -> 12 * 40/20 = 24 marks, which sits between the 20->4.5
    # and 26->6.0 anchors: 4.5 + 1.5 * 4/6 = 5.5.
    check("scaled is interpolated from the anchors", float(out["scaled"]), 5.5)

    # ── 7. the metrics the results page needs ───────────────────────────────
    r = pro.get(f"/exam/attempt/{attempt_id}/results.json")
    check("results are available once submitted", r.status_code, 200)
    data = r.get_json()
    m = data["metrics"]
    check("unanswered counted", m["unanswered"], 5)
    check("max is the question count", m["max"], 20)
    check("marks to 7.0 is the gap to 15/20", m["marks_to_7"], 3)
    check("the next whole grade above 5.5 is 6", m["next_whole_grade"], 6.0)
    check("the ladder covers 2 through 9", len(m["grade_ladder"]), 8)
    check("per-question rows for every question", len(m["per_question"]), 20)
    check("the estimate disclaimer is served", "estimate" in data["disclaimer"].lower(), True)

    # ── 8. anti-leak, section 6 ─────────────────────────────────────────────
    #
    # The failure this guards against is invisible until a student views source
    # mid-paper, so it is asserted rather than trusted.
    import exam as exam_mod
    check("the live column set excludes the answer",
          "answer" in exam_mod.LIVE_QUESTION_COLUMNS, False)
    check("and excludes the worked solution",
          "solution_html" in exam_mod.LIVE_QUESTION_COLUMNS, False)
    check("and excludes the traps",
          "traps" in exam_mod.LIVE_QUESTION_COLUMNS, False)
    check("while the graded set includes them",
          all(c in exam_mod.GRADED_QUESTION_COLUMNS
              for c in ("answer", "solution_html", "traps")), True)

    # ── 9. a submit after ends_at yields expired ────────────────────────────
    r = pro.post(f"/exam/{code}/start")
    late_id = r.get_json()["attempt_id"]
    pro.post(f"/exam/attempt/{late_id}/answer",
             json={"question_id": qs[0]["id"], "selected": qs[0]["answer"]})
    with get_db() as db:
        db.execute("UPDATE exam_attempts SET ends_at = NOW() - INTERVAL '1 minute' "
                   "WHERE id=?", (late_id,))

    r = pro.post(f"/exam/attempt/{late_id}/answer",
                 json={"question_id": qs[1]["id"], "selected": qs[1]["answer"]})
    check("an answer after the clock runs out is refused", r.status_code, 409)

    r = pro.post(f"/exam/attempt/{late_id}/submit")
    check("a late submit is accepted, not thrown away", r.status_code, 200)
    check("and is stamped expired", r.get_json()["status"], "expired")
    check("the work done inside the window still counts",
          r.get_json()["raw"], 1)

    # ── 10. one live attempt per paper, and a stale one does not block ──────
    r = pro.post(f"/exam/{code}/start")
    fresh = r.get_json()
    check("a new attempt starts once the old one expired", fresh["resumed"], False)
    check("and it is a different attempt", fresh["attempt_id"] != late_id, True)

    # ── 11. one user cannot touch another's attempt ─────────────────────────
    r = free.get(f"/exam/attempt/{attempt_id}/results.json")
    check("another user gets 404, not 403, on someone else's attempt",
          r.status_code, 404)

    # ── 12. the player page leaks nothing (section 6) ───────────────────────
    #
    # The check that matters most in this suite, because its failure mode is a
    # student pressing Ctrl-U mid-paper and reading the answer key. Asserted
    # against the real page source, not against the route's intentions.
    r = pro.post(f"/exam/{code}/start")
    play_id = r.get_json()["attempt_id"]
    page = pro.get(f"/exam/attempt/{play_id}")
    check("the player renders", page.status_code, 200)
    html = page.get_data(as_text=True)

    with get_db() as db:
        secrets = db.execute(
            "SELECT answer, solution_html, traps FROM exam_questions "
            "WHERE paper_id=? ORDER BY n", (paper_id,)).fetchall()

    # The worked solutions and the trap explanations are long, distinctive
    # strings. If any appears in the page, the anti-leak rule is broken.
    leaked = []
    for row in secrets:
        sol = (row["solution_html"] or "").strip()
        if len(sol) > 40 and sol[:40] in html:
            leaked.append("solution")
        for t in (row["traps"] or {}).values():
            t = str(t).strip()
            if len(t) > 25 and t[:25] in html:
                leaked.append("trap")
    check("no worked solution or trap reaches the player page",
          sorted(set(leaked)), [])

    # The answer key as an ordered string must not appear either.
    key = "".join(row["answer"] for row in secrets)
    check("the answer key is not in the page", key in html, False)

    # And the payload itself must carry no answer field at all.
    import re as _re
    blob = _re.search(r'id="exam-payload"[^>]*>(.*?)</script>', html, _re.S)
    check("the payload exists", blob is not None, True)
    if blob:
        payload = json.loads(blob.group(1))
        keys = set()
        for qq in payload["questions"]:
            keys |= set(qq)
        check("no question in the payload carries an answer", "answer" in keys, False)
        check("nor a solution", "solution_html" in keys, False)
        check("nor traps", "traps" in keys, False)
        check("but it does carry the stem", "stem_html" in keys, True)
        check("and the options", "options" in keys, True)
        check("and the server's own clock", "remaining_sec" in payload, True)

    # A finished attempt must not reopen in the player.
    pro.post(f"/exam/attempt/{play_id}/submit")
    r = pro.get(f"/exam/attempt/{play_id}", follow_redirects=False)
    check("a finished attempt redirects out of the player", r.status_code, 302)
    check("and goes to its results", "/results" in r.headers.get("Location", ""), True)


finally:
    with get_db() as db:
        for uid in (pro_id, free_id):
            if uid:
                db.execute("DELETE FROM exam_attempts WHERE user_id=?", (uid,))
                db.execute("DELETE FROM user_subjects WHERE user_id=?", (uid,))
        if made_paper and paper_id:
            db.execute("DELETE FROM exam_papers WHERE id=?", (paper_id,))
        # purge_user takes the EMAIL, not the id.
        for email in ("exam-pro@telos.local", "exam-free@telos.local"):
            purge_user(db, email)
    print("cleaned up")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
