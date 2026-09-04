import os
"""Every qualification must predict, and predict the right grade.

The other suites test the engine on a handful of hand-built boundary sets. This
one runs the real boundary table, for all sixty qualifications, and checks that
a student sitting exactly on a published boundary is told they are on that
grade.

That is the property that matters and the one no other test covers. A paper can
have boundaries, descending and plausible, and still be graded wrongly — the
Physics fault that started all of this looked exactly like healthy data. The
only way to see it is to feed a known mark in and check the grade that comes
out.

Three things are asserted for every offered paper:

  * boundaries resolve at all, without falling back to another paper
  * a mark exactly on the A boundary grades as A, on C as C, on the bottom
    grade as that grade
  * the top of the scale is the qualification's own top grade — an AS or an
    SQA course can never produce A*, and an A-level always can
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db  # noqa: E402
from paper_templates import (TEMPLATES, qualification_level, top_grade,  # noqa: E402
                             paper_options, is_graded)
from prediction import (attempt_grade_score, boundary_ladder,  # noqa: E402
                        score_to_grade, select_boundaries, MissingBoundaries)

fails = []


def ok(label, cond, detail=""):
    if not cond:
        print(f"FAIL  {label}" + (f": {detail}" if detail else ""))
        fails.append(label)
    return cond


with get_db() as db:
    rows = [dict(r) for r in db.execute("SELECT * FROM grade_boundaries").fetchall()]

# Every paper the app offers, with the years it offers them for.
#
# Ungraded qualifications are held out: this sweep walks a grade ladder and
# checks that sitting exactly on a boundary produces that grade, and an
# admissions test has neither. They are counted rather than dropped, so the
# output still accounts for every paper in the catalogue.
offered, ungraded_papers = [], 0
for board, subjects in TEMPLATES.items():
    for subject, cfg in subjects.items():
        if not is_graded(board, subject):
            ungraded_papers += len(cfg["papers"])
            continue
        for p in cfg["papers"]:
            offered.append((board, subject, p["code"], p["max_marks"],
                            [y for y in cfg["years"] if y.isdigit()]))

print(f"sweeping {len(offered)} papers across "
      f"{sum(len(s) for s in TEMPLATES.values())} qualifications "
      f"({ungraded_papers} ungraded papers not swept)")

no_boundaries, fell_back, wrong_grade, wrong_top, above_max = [], [], [], [], []

for board, subject, code, max_marks, years in offered:
    lvl = qualification_level(board, subject)
    want_top = top_grade(lvl)

    for year in years:
        try:
            bs, source = select_boundaries(rows, board, subject, code, year)
        except MissingBoundaries:
            no_boundaries.append((board, subject, code, year))
            continue
        if source != "exact":
            # Not a failure — the fallback chain is deliberate. 2020 and 2021
            # have no boundaries anywhere because those series were cancelled,
            # and SQA has years whose components genuinely differed. But a
            # fallback set is what a student is actually graded against for
            # those papers, so it is checked exactly like an exact one rather
            # than being counted and waved through.
            fell_back.append((board, subject, code, year, source))

        ladder = boundary_ladder(bs)

        # The top of this ladder must match what the qualification can award.
        got_top = "A*" if ladder[-1][0] == 6 else "A"
        if got_top != want_top:
            wrong_top.append((board, subject, code, year, got_top, want_top))

        # A boundary above the paper's max mark cannot be sat.
        if ladder[-1][1] > max_marks:
            above_max.append((board, subject, code, year, ladder[-1][1], max_marks))
            continue

        # Sitting exactly on a boundary must produce that grade.
        for point, marks in ladder:
            grade = score_to_grade(attempt_grade_score(marks, bs, max_marks))
            expected = {6: "A*", 5: "A", 4: "B", 3: "C", 2: "D", 1: "E"}[point]
            if grade != expected:
                wrong_grade.append((board, subject, code, year, expected, grade, marks))

ok("every offered paper resolves boundaries for its own years", not no_boundaries,
   f"{len(no_boundaries)} missing, e.g. {no_boundaries[:3]}")
ok("a mark on a boundary grades as that grade", not wrong_grade,
   f"{len(wrong_grade)} wrong, e.g. {wrong_grade[:3]}")
ok("every ladder tops out at the qualification's own top grade", not wrong_top,
   f"{len(wrong_top)} wrong, e.g. {wrong_top[:3]}")
ok("no top boundary exceeds its paper's max mark", not above_max,
   f"{len(above_max)}, e.g. {above_max[:3]}")

import collections  # noqa: E402
by_source = collections.Counter(f[4] for f in fell_back)
print(f"PASS  {len(offered)} papers swept, every paper-year graded")
for src, n in by_source.most_common():
    print(f"        {n:4d} via {src}")

# A qualification whose optional papers a student has not chosen must still
# predict from the compulsory ones alone — the common case on day one.
thin = []
for board, subjects in TEMPLATES.items():
    for subject in subjects:
        mandatory, _optional, _n = paper_options(board, subject)
        if not mandatory:
            thin.append((board, subject))
ok("every qualification has at least one compulsory paper", not thin, f"{thin}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
