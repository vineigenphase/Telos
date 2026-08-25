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

    # ── catalogue integrity ────────────────────────────────────────────────
    # Every paper needs a topic list. A paper without one can be logged for a
    # score but produces no heatmap and no prescriptions, which is the half of
    # Telos that is free — so it fails silently in exactly the way that matters.
    from paper_templates import TEMPLATES  # noqa: E402
    missing_topics = []
    for board, subjects in TEMPLATES.items():
        for subject, cfg in subjects.items():
            for paper in cfg["papers"]:
                if not cfg.get("topics", {}).get(paper["code"]):
                    missing_topics.append(f"{board}/{subject}/{paper['code']}")
    check("every paper has a topic list", missing_topics, [])

    dup = []
    for board, subjects in TEMPLATES.items():
        for subject, cfg in subjects.items():
            codes = [p["code"] for p in cfg["papers"]]
            if len(codes) != len(set(codes)):
                dup.append(f"{board}/{subject}")
    check("no duplicate paper codes within a subject", dup, [])

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

    # ── setup redirect ──────────────────────────────────────────────────────
    # A signed-in student with no subjects is sent to choose them. The
    # dashboard, papers and heatmap are all built around their subjects and are
    # close to meaningless without them.
    with get_db() as db:
        db.execute("DELETE FROM user_subjects WHERE user_id=?", (uid,))
    for path in ("/", "/papers", "/heatmap"):
        r = c.get(path)
        check("%s redirects to setup when no subjects are chosen" % path,
              (r.status_code, (r.headers.get("Location") or "").endswith("/welcome")),
              (302, True))
    check("...but onboarding itself stays reachable", c.get("/welcome").status_code, 200)
    check("...and so does the manage screen", c.get("/subjects").status_code, 200)
    c.post("/welcome", data={"qualification": [key]})

    # ── optional modules ────────────────────────────────────────────────────
    # Some qualifications are bigger than any one student's timetable: Edexcel
    # Further Maths is ten papers of which four are sat. A student says which
    # options they take, and the rest of the app stops offering the other six.
    from paper_templates import paper_options  # noqa: E402

    opt_q = next((q for q in quals if q["optional"]), None)
    check("some qualification has optional papers", opt_q is not None, True)

    if opt_q:
        board, subject, level = opt_q["board"], opt_q["subject"], opt_q["level"]
        mandatory, optional, choose_n = paper_options(board, subject)
        qkey = f"{board}|{subject}|{level}"

        # No choice yet means the compulsory papers only. Showing all ten of
        # Edexcel Further Maths by default buried Core Pure 1 and 2 among eight
        # options belonging to someone else's timetable; the compulsory papers
        # are the ones every student on the qualification definitely sits.
        check("with no choice made, only the compulsory papers are visible",
              A.visible_papers(uid, board, subject),
              {p["code"] for p in mandatory})

        picked = [optional[0]["code"], optional[1]["code"]]
        c.post("/subjects", data={
            "qualification": [qkey],
            "paper": [f"{qkey}|{picked[0]}", f"{qkey}|{picked[1]}",
                      f"{qkey}|{mandatory[0]['code']}",   # compulsory
                      f"{qkey}|NOT_A_PAPER"],             # unreal
        })

        check("only the chosen options are added to the compulsory papers",
              A.visible_papers(uid, board, subject),
              {p["code"] for p in mandatory} | set(picked))

        stored = A.get_user_papers(uid).get((board, subject, level), set())
        check("compulsory papers are not stored as choices",
              mandatory[0]["code"] in stored, False)
        check("an unreal paper code is dropped", "NOT_A_PAPER" in stored, False)

        # The matrix follows the same rule.
        block_rows = [b for b in A.paper_matrix(uid)
                      if b["board"] == board and b["subject"] == subject]
        codes = {r["paper"]["code"] for b in block_rows for r in b["rows"]}
        check("the paper matrix shows only those papers",
              codes, {p["code"] for p in mandatory} | set(picked))

        # A paper with logged work stays visible even if it is not chosen.
        dropped = optional[2]["code"] if len(optional) > 2 else None
        if dropped:
            with get_db() as db:
                db.execute(
                    "INSERT INTO papers (user_id, board, subject, paper_code, year, "
                    "series, score, max_marks) VALUES (?,?,?,?,?,?,?,?)",
                    (uid, board, subject, dropped, "2023", "June", 40, 75))
            block_rows = [b for b in A.paper_matrix(uid)
                          if b["board"] == board and b["subject"] == subject]
            codes = {r["paper"]["code"] for b in block_rows for r in b["rows"]}
            check("an unchosen paper with logged work stays in the matrix",
                  dropped in codes, True)

    # A qualification with no options is unaffected by any of this.
    plain = next((q for q in quals if not q["optional"]), None)
    if plain:
        check("a qualification without options shows all its papers",
              A.visible_papers(uid, plain["board"], plain["subject"]),
              {p["code"] for p in plain["papers"]})

finally:
    with get_db() as db:
        if uid:
            db.execute("DELETE FROM papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM user_papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM user_subjects WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
