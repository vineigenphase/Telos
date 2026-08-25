import os
"""Subject selection: onboarding, the manage screen, and personalisation.

The behaviours worth pinning are the ones a student would find alarming if they
broke: that an unrecognised subject cannot be stored, that unticking a subject
never hides or deletes work already logged against it, and that a new account
is asked what it studies instead of landing on an empty dashboard.

Creates its own throwaway user and removes it in a finally block.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from paper_templates import all_qualifications, available_levels  # noqa: E402
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
try:
    with get_db() as db:
        uid = db.execute(
            "INSERT INTO users (email, username, password_hash) VALUES (?,?,?)",
            ("subj-test@telos.local", "subjtest",
             generate_password_hash("Passw0rd!x"))).lastrowid

    c = app.test_client()
    with c.session_transaction() as s:
        s["_user_id"] = str(uid); s["_fresh"] = True

    # ── the catalogue ───────────────────────────────────────────────────────
    quals = all_qualifications()
    check("the catalogue offers qualifications", bool(quals), True)
    check("every qualification declares a level",
          all(q.get("level") for q in quals), True)
    check("only levels with data are offered",
          set(available_levels()) <= {q["level"] for q in quals}, True)

    # ── onboarding ──────────────────────────────────────────────────────────
    r = c.get("/welcome")
    body = r.get_data(as_text=True)
    check("onboarding renders", r.status_code, 200)
    check("...with a pickable option per qualification",
          body.count('name="qualification"'), len(quals))
    check("...and is not indexable", 'name="robots"' in body, True)

    check("a new account has no subjects yet", A.get_user_subjects(uid), [])

    # Choosing nothing is refused rather than silently accepted.
    c.post("/welcome", data={"qualification": []})
    check("onboarding will not accept an empty choice",
          A.get_user_subjects(uid), [])

    first = quals[0]
    key = f"{first['board']}|{first['subject']}|{first['level']}"
    c.post("/welcome", data={"qualification": [key]})
    mine = A.get_user_subjects(uid)
    check("a chosen subject is stored", len(mine), 1)
    check("...with its board", mine[0]["board"], first["board"])
    check("...and its level", mine[0]["level"], first["level"])

    # ── the manage screen ───────────────────────────────────────────────────
    r = c.get("/subjects")
    check("the manage screen renders", r.status_code, 200)
    check("...and pre-ticks what is already chosen",
          r.get_data(as_text=True).count("pick-option on"), 1)

    # A subject that is not in the catalogue must never be stored: the value
    # comes from a form, and a subject with no papers behind it would be an
    # entry the rest of the app cannot render.
    c.post("/subjects", data={"qualification": [key, "Fake|Nonsense|A-Level"]})
    check("an unrecognised qualification is dropped",
          [s["subject"] for s in A.get_user_subjects(uid)], [first["subject"]])

    # ── unticking never destroys work ───────────────────────────────────────
    with get_db() as db:
        db.execute(
            "INSERT INTO papers (user_id, board, subject, paper_code, year, series, "
            "score, max_marks) VALUES (?,?,?,?,?,?,?,?)",
            (uid, first["board"], first["subject"], first["papers"][0]["code"],
             "2023", "June", 50, first["papers"][0]["max_marks"]))

    c.post("/subjects", data={"qualification": []})
    check("all subjects can be removed", A.get_user_subjects(uid), [])

    with get_db() as db:
        still = db.execute("SELECT COUNT(*) AS n FROM papers WHERE user_id=?",
                           (uid,)).fetchone()["n"]
    check("removing a subject does not delete logged papers", still, 1)

    body = c.get("/subjects").get_data(as_text=True)
    check("...and the manage screen says where that work went",
          "Papers outside your subjects" in body, True)

    # The matrix keeps a subject that has logged work, even when unticked.
    subjects_in_matrix = {row["subject"] for row in A.paper_matrix(uid)}
    check("the paper matrix still shows a subject with logged work",
          first["subject"] in subjects_in_matrix, True)

finally:
    with get_db() as db:
        if uid:
            db.execute("DELETE FROM papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM user_subjects WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
