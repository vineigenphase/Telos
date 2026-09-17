"""The admissions past-paper tracker, walked end to end.

A throwaway student goes tab -> test -> paper -> answers -> marked, and the rows
that come out the other side are checked against the official key.

The assertions worth keeping are the ones about those rows rather than about
the markup. An admissions paper is stored as an ordinary `papers` row with one
`question_marks` row per question at one mark each, precisely so the heatmap,
the prescription engine and the revision queue treat it like any other paper —
and the day that stops being true, all three go quiet about admissions papers
with no error raised anywhere. These check the shape they depend on.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
import app as A
import admissions_papers as AP
from db import get_db
from werkzeug.security import generate_password_hash
from _fixtures import fresh_user, purge_user

app = A.app; app.debug = False
PW = "tracker-check-pw"
EMAIL = "tracker@telos.test"
fails = []


def check(label, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + label + f": {got!r}"
          + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


try:
    with get_db() as db:
        uid = fresh_user(db, EMAIL, "trackeruser", generate_password_hash(PW))
    A.set_user_subjects(uid, ["UAT-UK|ENGAA (2019-2023)|Admissions test",
                              "UAT-UK|TMUA|Admissions test",
                              "UAT-UK|ESAT|Admissions test"])

    c = app.test_client()
    c.post("/login", data={"email": EMAIL, "password": PW})

    # ── the tab lists the tracked tests ─────────────────────────────────────
    body = c.get("/admissions").get_data(as_text=True)
    check("the tab offers past papers for a tracked test",
          "/admissions/engaa-2019-2023" in body, True)
    check("and says how many are marked for you", "10 marked for you" in body, True)
    # ESAT is the only self-marked test left: UAT-UK publishes no ESAT papers
    # at all, so there is nothing to extract a key from. TMUA used to be here
    # too, until its nine official keys were extracted.
    check("ESAT is offered as self-marked", "self-marked" in body, True)
    check("TMUA is marked for you", "18 papers · 18 marked for you" in body, True)

    # ── one test's paper list ───────────────────────────────────────────────
    r = c.get("/admissions/engaa-2019-2023")
    check("the paper list renders", r.status_code, 200)
    body = r.get_data(as_text=True)
    # Read from the year headings rather than from the whole page: "2019" also
    # appears in the title "ENGAA (2019-2023)", so searching the body finds the
    # era and reports the order backwards.
    heads = re.findall(r'class="exam-group-name">([^<]+)<', body)
    check("every year is listed, newest first", heads,
          ["2023", "2022", "2021", "2020", "2019"])
    check("an unknown test 404s", c.get("/admissions/not-a-test").status_code, 404)

    # ── entering a paper ────────────────────────────────────────────────────
    r = c.get("/admissions/engaa-2019-2023/2021/part-a")
    check("the entry grid renders", r.status_code, 200)
    grid = r.get_data(as_text=True)
    key = AP.answer_key("ENGAA (2019-2023)", "2021", "Part A")
    opts = AP.options_for(key)
    check("the keypad offers exactly the letters this key uses",
          sorted({m for m in re.findall(r'name="q1" value="([A-H])"', grid)}),
          opts)
    check("a part that does not exist 404s",
          c.get("/admissions/engaa-2019-2023/2021/part-z").status_code, 404)
    check("a year that does not exist 404s",
          c.get("/admissions/engaa-2019-2023/1999/part-a").status_code, 404)

    # Answer it: first 12 right, next 3 deliberately wrong, rest blank.
    form = {}
    for i, correct in enumerate(key):
        if i < 12:
            form[f"q{i + 1}"] = correct
        elif i < 15:
            form[f"q{i + 1}"] = next(o for o in opts if o != correct)
    r = c.post("/admissions/engaa-2019-2023/2021/part-a", data=form)
    check("marking returns the marked page", r.status_code, 200)
    marked = r.get_data(as_text=True)
    check("the score is what we answered", f"{12}<span" in marked, True)

    # ── what landed in the database ─────────────────────────────────────────
    with get_db() as db:
        paper = db.execute(
            "SELECT id, score, max_marks, paper_code, year FROM papers "
            "WHERE user_id=? AND board='UAT-UK' AND subject=?",
            (uid, "ENGAA (2019-2023)")).fetchall()
        check("exactly one paper row", len(paper), 1)
        pid = paper[0]["id"]
        check("the score is the raw mark", paper[0]["score"], 12.0)
        check("out of the paper's length", paper[0]["max_marks"], float(len(key)))
        qs = db.execute(
            "SELECT q_num, obtained, max_marks, answer_given FROM question_marks "
            "WHERE paper_id=? ORDER BY CAST(q_num AS INTEGER)", (pid,)).fetchall()
        check("one row a question", len(qs), len(key))
        check("every question is worth one mark",
              {q["max_marks"] for q in qs}, {1.0})
        check("right answers scored 1", qs[0]["obtained"], 1.0)
        check("wrong answers scored 0", qs[12]["obtained"], 0.0)
        check("the chosen letter is kept", qs[0]["answer_given"], key[0])
        check("a blank keeps no letter", qs[15]["answer_given"], None)

    # ── re-entering replaces rather than duplicates ─────────────────────────
    form2 = {f"q{i + 1}": correct for i, correct in enumerate(key)}
    c.post("/admissions/engaa-2019-2023/2021/part-a", data=form2)
    with get_db() as db:
        rows = db.execute(
            "SELECT id, score FROM papers WHERE user_id=? AND subject=?",
            (uid, "ENGAA (2019-2023)")).fetchall()
        check("still one paper row after re-entering", len(rows), 1)
        check("and the score is the new one", rows[0]["score"], float(len(key)))
        check("and the question rows were replaced, not appended",
              db.execute("SELECT COUNT(*) AS n FROM question_marks WHERE paper_id=?",
                         (rows[0]["id"],)).fetchone()["n"], len(key))

    # ── a self-marked test ──────────────────────────────────────────────────
    r = c.get("/admissions/esat/2024/mathematics-1")
    check("a test with no key renders the right/wrong grid", r.status_code, 200)
    tm = r.get_data(as_text=True)
    check("and offers right/wrong rather than letters",
          'value="right"' in tm and 'value="A"' not in tm, True)
    r = c.post("/admissions/esat/2024/mathematics-1",
               data={f"q{i}": ("right" if i <= 14 else "wrong")
                     for i in range(1, 28)})
    check("self-marking saves", r.status_code, 200)
    with get_db() as db:
        row = db.execute(
            "SELECT score, max_marks FROM papers WHERE user_id=? AND subject='ESAT'",
            (uid,)).fetchone()
        check("the self-marked score is what was tapped", row["score"], 14.0)
        check("out of the paper's length", row["max_marks"], 27.0)

    # ── the PDF route refuses anything it does not recognise ────────────────
    check("a traversal attempt 404s",
          c.get("/admissions/paper/..%2f..%2fapp.pdf").status_code, 404)
    check("an unknown stem 404s",
          c.get("/admissions/paper/NOPE_2021_S1.pdf").status_code, 404)

finally:
    with get_db() as db:
        purge_user(db, EMAIL)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
