import os
"""Grade boundaries must be on the same scale as the paper they describe.

This suite exists because they were not. The OCR A Physics rows held the
OVERALL qualification boundary (out of 270, all three papers summed) under the
paper code "Overall", while students log one paper at a time out of 100 or 70 —
so an 85/100 was compared against an A boundary of 219 and graded U. The same
rows were also shifted a column, with the max mark sitting in a_star, which is
why a_star read 270 in every year.

Neither fault is visible by reading the numbers: they are plausible integers in
descending order. What gives them away is comparing them to the paper's max
mark, which is what these tests do.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as A  # noqa: E402
from db import get_db  # noqa: E402
from paper_templates import TEMPLATES  # noqa: E402

fails = []


def ok(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# Max marks for every paper the app offers, keyed the way boundaries are.
max_marks = {}
for board, subjects in TEMPLATES.items():
    for subject, cfg in subjects.items():
        for paper in cfg["papers"]:
            max_marks[(board, subject, paper["code"])] = paper["max_marks"]

with get_db() as db:
    rows = [dict(r) for r in db.execute("SELECT * FROM grade_boundaries").fetchall()]

ok("there are boundaries at all", bool(rows), f"{len(rows)} rows")

# 1. Every paper the app offers must have boundaries, or its predictions fall
#    back to a median of other papers without anyone noticing.
offered_without = sorted(k for k in max_marks
                         if not any((r["board"], r["subject"], r["paper_code"]) == k for r in rows))
ok("every paper the app offers has boundaries", not offered_without,
   "" if not offered_without else f"{offered_without}")

# The reverse is informational. Edexcel publishes boundaries for Further Maths
# option papers (FP1, FP2, FS2, FM2, D1, D2) that paper_templates.py does not
# offer, so a student taking those options cannot log them. Real data, missing
# feature — printed so it stays visible, not failed on.
orphans = sorted({(r["board"], r["subject"], r["paper_code"]) for r in rows
                  if (r["board"], r["subject"], r["paper_code"]) not in max_marks})
if orphans:
    print(f"NOTE  boundaries exist for {len(orphans)} papers the app does not offer: "
          + ", ".join(f"{b}/{s_}/{p}" for b, s_, p in orphans))

# 2. The scale check — the one that catches this whole class of bug.
too_big = [(r["subject"], r["paper_code"], r["year"], r["a_star"],
            max_marks.get((r["board"], r["subject"], r["paper_code"])))
           for r in rows
           if (r["board"], r["subject"], r["paper_code"]) in max_marks
           and r["a_star"] > max_marks[(r["board"], r["subject"], r["paper_code"])]]
ok("no A* boundary exceeds its paper's max mark", not too_big,
   "" if not too_big else f"{too_big[:3]}")

# 3. A boundary equal to the max mark means the max mark was stored as a grade.
equals_max = [(r["subject"], r["paper_code"], r["year"])
              for r in rows
              if (r["board"], r["subject"], r["paper_code"]) in max_marks
              and r["a_star"] == max_marks[(r["board"], r["subject"], r["paper_code"])]]
ok("no A* boundary equals its paper's max mark", not equals_max,
   "" if not equals_max else f"{equals_max[:3]}")

# 4. Ordering. A*/A/B/C must descend and stay positive.
bad_order = [(r["subject"], r["paper_code"], r["year"])
             for r in rows
             if not (r["a_star"] > r["a_boundary"] > r["b_boundary"] > r["c_boundary"] > 0)]
ok("A* > A > B > C > 0 on every row", not bad_order,
   "" if not bad_order else f"{bad_order[:3]}")

# 5. A floor. A C grade below a tenth of the paper means the scale is wrong.
#    Deliberately no upper bound on A*: an earlier version capped it at 95% of
#    the paper and flagged Further Mechanics 1 in 2025, where Pearson really did
#    publish A* at 72 out of 75. Optional papers run high. Checks 2 and 3 catch
#    the scale errors without guessing at what a "normal" boundary looks like.
implausible = []
for r in rows:
    mx = max_marks.get((r["board"], r["subject"], r["paper_code"]))
    if mx and r["c_boundary"] < mx * 0.10:
        implausible.append((r["subject"], r["paper_code"], r["year"], r["c_boundary"], mx))
ok("no C boundary below a tenth of its paper", not implausible,
   "" if not implausible else f"{implausible[:3]}")

# 6. Years with no exam series must not carry boundaries. Summer 2020 and 2021
#    were cancelled in England, so any row for them was invented.
cancelled = sorted({(r["subject"], r["year"]) for r in rows if r["year"] in ("2020", "2021")})
ok("no boundaries for the cancelled 2020/2021 series", not cancelled,
   "" if not cancelled else f"{cancelled}")

# 7. Published D and E, where present, must continue the ladder downward. A
#    D above its own C, or an E at zero, would place a weak script above a
#    strong one.
de_rows = [r for r in rows if r.get("d_boundary") is not None or r.get("e_boundary") is not None]
ok("D and E were actually loaded", bool(de_rows), f"{len(de_rows)} of {len(rows)} rows")

half = [(r["subject"], r["paper_code"], r["year"]) for r in de_rows
        if r["d_boundary"] is None or r["e_boundary"] is None]
ok("no row has one of D/E without the other", not half,
   "" if not half else f"{half[:3]}")

de_order = [(r["subject"], r["paper_code"], r["year"],
             r["c_boundary"], r["d_boundary"], r["e_boundary"])
            for r in de_rows
            if not (r["c_boundary"] > r["d_boundary"] > r["e_boundary"] > 0)]
ok("C > D > E > 0 wherever D/E are published", not de_order,
   "" if not de_order else f"{de_order[:3]}")

# 8. The ladder must prefer published values and infer only when it has to.
from prediction import boundary_ladder, infer_de  # noqa: E402

published = {"a_star": 74, "a_boundary": 65, "b_boundary": 54, "c_boundary": 43,
             "d_boundary": 32, "e_boundary": 22}
ladder = dict((g, m) for g, m in boundary_ladder(published))
ok("the ladder uses published D and E when present",
   (ladder[2], ladder[1]) == (32.0, 22.0), f"D={ladder[2]}, E={ladder[1]}")

bare = {"a_star": 88, "a_boundary": 74, "b_boundary": 61, "c_boundary": 48}
d_exp, e_exp = infer_de(88, 74, 61, 48)
ladder2 = dict((g, m) for g, m in boundary_ladder(bare))
ok("...and still infers them when they are absent",
   (round(ladder2[2], 3), round(ladder2[1], 3)) == (round(d_exp, 3), round(e_exp, 3)),
   f"D={ladder2[2]:.1f}, E={ladder2[1]:.1f}")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
