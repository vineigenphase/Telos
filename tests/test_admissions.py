import os
"""Admissions scoring engine — the equating maths, on synthetic cohorts.

Pure functions, so no database and no fixture user. The distributions here are
invented ON PURPOSE: this suite checks the arithmetic, and inventing a cohort
to test against is fine in a way that inventing one to score a real student
with is not.

The properties that matter are the ones a wrong implementation would break
quietly. An off-by-one in the interpolation still returns a plausible number —
it just puts every student in slightly the wrong place — so these check
round-trips and orderings rather than eyeballing single values.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from admissions import (Distribution, MissingDistribution, equate,  # noqa: E402
                        percentile_of, raw_at_percentile, scale_score)

fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def close(label, got, want, tol=0.5):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got:.2f}" +
          ("" if ok else f"  (want {want} ±{tol})"))
    if not ok:
        fails.append(label)


# A published table: raw mark -> % of candidates at or below it.
TABLE = Distribution(
    test="ENGAA", year="2019", part="Part A", max_marks=20,
    source="synthetic — tests only",
    percentiles={0: 0.0, 5: 10.0, 10: 50.0, 15: 90.0, 20: 100.0},
)
# The same cohort described only by mean and sd.
NORMAL = Distribution(
    test="ESAT", year="2025", part="Mathematics 1", max_marks=27,
    source="synthetic — tests only", mean=13.5, sd=4.0,
)

# ── 1. the two grades of data are labelled ─────────────────────────────────
check("a percentile table is exact", TABLE.quality, "exact")
check("mean and sd is estimated", NORMAL.quality, "estimated")

try:
    Distribution(test="X", year="2020", part="P", max_marks=10, source="s")
    check("a distribution with no usable data is refused", "accepted", "rejected")
except ValueError:
    check("a distribution with no usable data is refused", "rejected", "rejected")

# sd of zero is not usable either — it would divide by zero on the normal path.
try:
    Distribution(test="X", year="2020", part="P", max_marks=10, source="s",
                 mean=5.0, sd=0.0)
    check("a zero standard deviation is refused", "accepted", "rejected")
except ValueError:
    check("a zero standard deviation is refused", "rejected", "rejected")

# ── 2. percentile lookup ───────────────────────────────────────────────────
close("a published mark reads straight off the table", percentile_of(10, TABLE), 50.0, 0.01)
close("below the bottom of the table clamps", percentile_of(-5, TABLE), 0.0, 0.01)
close("above the top clamps", percentile_of(99, TABLE), 100.0, 0.01)

# Halfway between 10 (50%) and 15 (90%) is 70%, not 50 and not 90. A step
# function would give one of those, which is the bug this catches.
close("between two published marks it interpolates", percentile_of(12.5, TABLE), 70.0, 0.01)

# The mean of a normal cohort is by definition the 50th percentile.
close("the mean sits at the 50th percentile", percentile_of(13.5, NORMAL), 50.0, 0.01)
close("one sd above the mean is ~84th", percentile_of(17.5, NORMAL), 84.1, 0.5)
close("one sd below the mean is ~16th", percentile_of(9.5, NORMAL), 15.9, 0.5)

# ── 3. the inverse round-trips ─────────────────────────────────────────────
for raw in (2, 7, 12.5, 18):
    back = raw_at_percentile(percentile_of(raw, TABLE), TABLE)
    close(f"table round-trip at {raw}", back, raw, 0.01)

for raw in (6, 13.5, 20):
    back = raw_at_percentile(percentile_of(raw, NORMAL), NORMAL)
    close(f"normal round-trip at {raw}", back, raw, 0.05)

# ── 4. equating ────────────────────────────────────────────────────────────
#
# The whole point: a mark is carried across by STANDING, not by proportion.
# 10/20 is the median in TABLE, so it must come out as the median of NORMAL —
# 13.5/27 — and emphatically not as 13.5 because "half of 27".
r = equate(10, TABLE, NORMAL)
close("the median carries to the median", r["equivalent_raw"], 13.5, 0.1)
close("and reports the percentile it went through", r["percentile"], 50.0, 0.1)

# 15/20 is the 90th percentile, which on the target cohort is mean + 1.28sd.
r90 = equate(15, TABLE, NORMAL)
close("the 90th percentile carries to the 90th", r90["percentile"], 90.0, 0.1)
close("which is mean + 1.28 sd", r90["equivalent_raw"], 13.5 + 1.2816 * 4.0, 0.1)

# Equating must be monotonic: a better raw score can never equate lower.
eq = [equate(x, TABLE, NORMAL)["equivalent_raw"] for x in range(0, 21)]
check("a higher mark never equates lower", eq == sorted(eq), True)

# ── 5. quality is the weaker of the two ends ───────────────────────────────
#
# Equating THROUGH an estimated distribution gives an estimated answer, however
# good the other end is. Reporting the better of the two would overstate it.
check("exact -> estimated is estimated", equate(10, TABLE, NORMAL)["quality"], "estimated")
check("estimated -> exact is estimated", equate(10, NORMAL, TABLE)["quality"], "estimated")
check("exact -> exact is exact", equate(10, TABLE, TABLE)["quality"], "exact")

# ── 6. missing data is refused, not invented ───────────────────────────────
try:
    equate(10, TABLE, None)
    check("equating without a target is refused", "returned", "raised")
except MissingDistribution:
    check("equating without a target is refused", "raised", "raised")

try:
    scale_score(10, TABLE, {})
    check("a scaled score with no published table is refused", "returned", "raised")
except MissingDistribution:
    check("a scaled score with no published table is refused", "raised", "raised")

# ── 7. the 1-9 scale ───────────────────────────────────────────────────────
SCALE = {0: 1.0, 5: 3.0, 10: 5.0, 15: 7.0, 20: 9.0}
close("a published scale point is read off", scale_score(10, TABLE, SCALE), 5.0, 0.01)
close("between points it interpolates", scale_score(12.5, TABLE, SCALE), 6.0, 0.01)
# The scale must not run past its own ends — a 9.0 ceiling is a real ceiling.
close("the top of the scale is a ceiling", scale_score(20, TABLE, SCALE), 9.0, 0.01)
close("and is not exceeded", scale_score(25, TABLE, SCALE), 9.0, 0.01)
close("the bottom is a floor", scale_score(-3, TABLE, SCALE), 1.0, 0.01)

# ── 8. the published 1-9 scale anchors ─────────────────────────────────────
#
# These are the numbers the whole module rests on, so they are asserted rather
# than trusted. An earlier draft used 9.0 for the 90th percentile, taken from a
# summary of the public results page; the technical report and the published
# percentile tables both say 7.0, and that error would have inflated every
# score. A test is cheaper than finding out from a student.
from admissions import (SCALE_ANCHORS, SCALE_REGIMES,  # noqa: E402
                        scale_from_percentile, equate_to_scale)

check("the current regime anchors the median at 4.5", SCALE_ANCHORS[0], (50.0, 4.5))
check("and the 90th percentile at 7.0, not 9.0", SCALE_ANCHORS[1], (90.0, 7.0))
close("so the median scores 4.5", scale_from_percentile(50), 4.5, 0.05)
close("and the 90th scores 7.0", scale_from_percentile(90), 7.0, 0.05)

# Monotonic, and clamped to the real ends of the scale.
seq = [scale_from_percentile(p) for p in range(1, 100)]
check("a higher percentile never scores lower", seq == sorted(seq), True)
check("nothing exceeds 9.0", max(seq) <= 9.0, True)
check("nothing falls below 1.0", min(seq) >= 1.0, True)

# The four regimes are recorded, because a scaled score means nothing without
# knowing which one issued it.
check("all four scale regimes are recorded", sorted(SCALE_REGIMES),
      ["2016", "2017-2023", "current", "engaa-nsaa"])

# equate_to_scale must carry the cohort caveat, not bury it.
r = equate_to_scale(15, TABLE)
close("a 90th-percentile raw mark reaches 7.0", r["scale_score"], 7.0, 0.1)
check("and the result states the cohort caveat", "cohort-relative" in r["caveat"], True)
check("and cites where its distribution came from", r["source"], TABLE.source)


print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
