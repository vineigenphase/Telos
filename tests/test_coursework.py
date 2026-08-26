import os
"""Components that are marked as a whole rather than question by question.

Geography's fieldwork investigation and the three MFL speaking exams were
originally left out of the catalogue, on the rule that a paper belongs here if
a student can sit and mark it alone. That rule was wrong for these four: they
count toward the grade, so leaving them out meant a Geography prediction was
built from 80% of the qualification and an MFL prediction from 70%, and nothing
said so.

The test that would have caught it is the last one here — compare the sum of a
qualification's components against the total the awarding body actually grades
out of. A missing component is invisible in every other way: the papers that
are there look perfectly correct.

Creates its own throwaway user and removes it in a finally block.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402
from db import get_db  # noqa: E402
from paper_templates import TEMPLATES, paper_options  # noqa: E402
from _fixtures import fresh_user, purge_user  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

app = A.app
app.debug = False
fails = []


def ok(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    if not cond:
        fails.append(label)


def check(label, got, want):
    ok(label, got == want, f"{got!r}" + ("" if got == want else f"  (want {want!r})"))


# Every component that is not a written paper, as the catalogue declares it.
non_exam = [(b, s, p) for b, subjects in TEMPLATES.items()
            for s, cfg in subjects.items()
            for p in cfg["papers"] if p.get("assessment", "exam") != "exam"]

# The AS languages carry a speaking exam too, and it is the same 60 marks
# awarded as one number — so the count grows with the AS load rather than
# staying at the original four.
ok("the catalogue has non-exam components", len(non_exam) >= 4,
   f"{len(non_exam)}: " + ", ".join(f"{s}/{p['code']}" for _b, s, p in non_exam))

bad_kind = [(s, p["code"], p["assessment"]) for _b, s, p in non_exam
            if p["assessment"] not in ("coursework", "oral")]
ok("every non-exam component declares a kind the form knows", not bad_kind, f"{bad_kind}")

# The mark for one of these comes from a teacher as a single number, so the
# entry form must not ask for a breakdown — and must not leave hidden question
# rows behind to be posted when it switches.
js = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "static", "js", "telos.js"), encoding="utf-8").read()
html = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "templates", "papers_entry.html"), encoding="utf-8").read()
ok("the form can hide the question breakdown", 'id="q-breakdown"' in html)
ok("...and the entry script drives it from the component's kind",
   "applyAssessment" in js and "info.assessment" in js)
ok("...and clears stale rows so nothing hidden is submitted",
   "#q-rows .q-row" in js and "remove()" in js)

with get_db() as db:
    rows = [dict(r) for r in db.execute(
        "SELECT board, subject, paper_code, year, a_star, a_boundary,"
        "       b_boundary, c_boundary FROM grade_boundaries").fetchall()]
have = {(r["board"], r["subject"], r["paper_code"]) for r in rows}
missing = [k for k in ((b, s, p["code"]) for b, s, p in non_exam) if k not in have]
ok("every non-exam component has its own boundaries", not missing, f"{missing}")

# ── the check that would have caught the omission ───────────────────────────
#
# Totals the awarding body grades the whole qualification out of, read from the
# specification. Only the qualifications whose totals have been confirmed are
# listed; a subject absent here is untested, not asserted correct.
QUAL_TOTALS = {
    ("AQA", "Geography"):  300,    # 120 + 120 written + 60 investigation
    ("AQA", "French"):     240,    # 100 + 80 + 60 speaking
    ("AQA", "German"):     240,
    ("AQA", "Spanish"):    240,
    ("AQA", "Philosophy"): 200,    # 100 + 100
    ("AQA", "Physics"):    250,    # 85 + 85 + 45 + one 35-mark option
    ("AQA", "Chemistry"):  300,    # 105 + 105 + 90
    ("AQA", "Biology"):    260,    # 91 + 91 + 78
    ("AQA", "Economics"):  240,    # 80 x 3
    # AS-levels. Not the A-level at a smaller total: AS Maths is two papers of
    # 80 where the A-level is three of 100, and the AS MFL writing paper is 50
    # against the A-level's 80.
    ("AQA", "Maths (AS)"):         160,   # 80 + 80
    ("AQA", "Further Maths (AS)"): 160,   # 80 + two 40-mark options
    ("AQA", "Physics (AS)"):       140,   # 70 + 70
    ("AQA", "Chemistry (AS)"):     160,   # 80 + 80
    ("AQA", "Biology (AS)"):       150,   # 75 + 75
    ("AQA", "Geography (AS)"):     160,   # 80 + 80
    ("AQA", "Economics (AS)"):     140,   # 70 + 70
    ("AQA", "French (AS)"):        200,   # 90 + 50 + 60 speaking
    ("AQA", "German (AS)"):        200,
    ("AQA", "Spanish (AS)"):       200,
    ("OCR A", "Maths (AS)"):          150,   # 75 + 75
    ("OCR A", "Further Maths (AS)"):  180,   # 60 + two 60-mark options
    ("OCR A", "Physics (AS)"):        140,   # 70 + 70
    ("OCR A", "Chemistry (AS)"):      140,
    ("OCR A", "Biology (AS)"):        140,
    ("Edexcel", "Maths (AS)"):          160,  # 100 Pure + 60 Stats/Mechanics
    ("Edexcel", "Further Maths (AS)"):  160,  # 80 + two 40-mark options
    ("Edexcel", "Physics (AS)"):        160,  # 80 + 80
    ("Edexcel", "Chemistry (AS)"):      160,
    ("Edexcel", "Biology (AS)"):        160,
    # SQA Advanced Highers. These totals are the check that matters most here:
    # the component max marks come from one SQA publication and the course
    # maximum from another, and the load refuses unless they agree.
    ("SQA", "Biology (AH)"):    160,   # 24 + 96 + 40 project
    ("SQA", "Chemistry (AH)"):  160,   # 27 + 93 + 40 project
    ("SQA", "Physics (AH)"):    160,   # 120 + 40 project
    ("SQA", "Maths (AH)"):      115,   # 35 non-calculator + 80 calculator
    ("SQA", "Economics (AH)"):  120,   # 80 + 40 project
    ("SQA", "Geography (AH)"):  150,   # 50 + 60 study + 40 issue
    ("SQA", "French (AH)"):     200,   # 50 + 70 + 50 talking + 30 portfolio
    ("SQA", "German (AH)"):     200,
    ("SQA", "Spanish (AH)"):    200,
    ("SQA", "English (AH)"):    100,   # 20 + 20 + 30 portfolio + 30 dissertation
    # SQA Highers, same two-source check.
    ("SQA", "Biology (H)"):    150,   # 25 + 95 + 30 assignment
    ("SQA", "Chemistry (H)"):  150,
    ("SQA", "Physics (H)"):    150,
    ("SQA", "Maths (H)"):      120,   # 55 non-calculator + 65 calculator
    ("SQA", "Economics (H)"):  120,   # 90 + 30 assignment
    ("SQA", "Geography (H)"):  110,   # 50 + 30 + 30 assignment
    ("SQA", "French (H)"):     120,   # 30 + 30 + 15 + 30 talking + 15 assignment
    ("SQA", "German (H)"):     120,
    ("SQA", "Spanish (H)"):    120,
    ("SQA", "English (H)"):    100,   # 30 RUAE + 40 critical reading + 30 portfolio
}
for (board, subject), want in sorted(QUAL_TOTALS.items()):
    cfg = TEMPLATES.get(board, {}).get(subject)
    if not cfg:
        ok(f"{board} {subject} is in the catalogue", False)
        continue
    # Optional papers are alternatives, so only the number a student sits
    # counts. They are interchangeable in mark value, so the first will do.
    mandatory, optional, choose_n = paper_options(board, subject)
    got = sum(p["max_marks"] for p in mandatory)
    if optional:
        got += (choose_n or 1) * optional[0]["max_marks"]
    check(f"{board} {subject} components sum to the graded total", got, want)

# ── a coursework mark posts and predicts like any other ─────────────────────
uid = None
try:
    with get_db() as db:
        uid = fresh_user(db, "coursework-test@telos.local", "cwtest",
                         generate_password_hash("Passw0rd!x"))
        # A signed-in student with no subjects is redirected to pick them, so
        # give this one the subject it is about to log against.
        db.execute("INSERT INTO user_subjects (user_id, board, subject, level)"
                   " VALUES (?,?,?,?)", (uid, "AQA", "Geography", "A-Level"))

    # A GET off the canonical host is 301'd to it, which the test client cannot
    # follow, so every request here is made as the real domain — including the
    # one that plants the session, or its cookie would be scoped to localhost
    # and the post would arrive signed out.
    CANON = "https://telosapp.co.uk"
    c = app.test_client()
    with c.session_transaction(base_url=CANON) as s:
        s["_user_id"] = str(uid); s["_fresh"] = True

    # No q_num[] at all — exactly what the form posts once the breakdown is
    # hidden. The mark must survive on score_direct alone.
    r = c.post("/papers/add", data={
        "board": "AQA", "subject": "Geography", "paper_code": "NEA",
        "year": "2024", "series": "June", "max_marks": "60",
        "score_direct": "48",
    }, base_url=CANON, follow_redirects=True)
    ok("a single-mark component posts", r.status_code == 200, str(r.status_code))

    with get_db() as db:
        p = db.execute("SELECT * FROM papers WHERE user_id=? AND paper_code='NEA'",
                       (uid,)).fetchone()
    ok("...and is stored with its mark", p is not None and float(p["score"]) == 48.0,
       "" if p is None else f"score={p['score']}")

    # 48/60 is 80%. The prediction must be graded against the NEA's own 2024
    # boundaries (A* 52, A 49) and not fall back to a median of the written
    # papers, whose marks are on a different scale entirely.
    from prediction import select_boundaries  # noqa: E402
    b, source = select_boundaries(rows, "AQA", "Geography", "NEA", "2024")
    ok("the NEA is graded against its own boundaries, not a fallback",
       source == "exact" and b["a_boundary"] == 49,
       f"source={source}, A={b['a_boundary']}, A*={b['a_star']}")

finally:
    with get_db() as db:
        purge_user(db, "coursework-test@telos.local")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
