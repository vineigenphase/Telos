import os
"""Exam Mode scoring — the port, checked against the reference implementation.

Pure, so no database. The important assertion is not that any single number is
right but that this Python and the standalone HTML players agree everywhere: a
student who sits the same paper in both must get the same score, and two
independent implementations of a piecewise interpolation will otherwise
disagree at a boundary with no way to say which is correct.

So the reference's own `scaledFrom40` and `minRawFor` are transcribed literally
below and diffed across every attainable raw mark.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exam_scoring import (DEFAULT_ANCHORS, compute_metrics, grade_ladder,  # noqa: E402
                          min_raw_for, scaled_for_raw, scaled_from_marks)

fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


# ── the reference, transcribed from player_template.html ───────────────────
def ref_scaled(m, anch):
    m = max(0, min(anch[len(anch) - 1][0], m))
    for i in range(1, len(anch)):
        m0, s0 = anch[i - 1]
        m1, s1 = anch[i]
        if m <= m1:
            return round((s0 + (s1 - s0) * (m - m0) / (m1 - m0)) * 10) / 10
    return 9.0


def ref_for_raw(r, n, fam, anch):
    return ref_scaled(r * fam / n, anch)


def ref_min_raw(t, n, fam, anch):
    for r in range(0, n + 1):
        if ref_for_raw(r, n, fam, anch) >= t - 1e-9:
            return r
    return None


TMUA, ESAT = DEFAULT_ANCHORS["TMUA"], DEFAULT_ANCHORS["ESAT"]

for label, n, fam, anch in [("TMUA paper", 20, 40, TMUA), ("ESAT module", 27, 27, ESAT)]:
    diffs = [r for r in range(n + 1)
             if abs(ref_for_raw(r, n, fam, anch) - scaled_for_raw(r, n, fam, anch)) > 1e-9]
    check(f"{label}: every raw mark matches the reference", diffs, [])
    rung = [g for g in range(2, 10)
            if ref_min_raw(float(g), n, fam, anch) != min_raw_for(float(g), n, fam, anch)]
    check(f"{label}: every ladder rung matches the reference", rung, [])

# ── the properties a student depends on ────────────────────────────────────
curve = [scaled_for_raw(r, 20, 40, TMUA) for r in range(21)]
check("a higher raw mark never scores lower", curve == sorted(curve), True)
check("zero is the floor", curve[0], 1.0)
check("full marks is the ceiling", curve[-1], 9.0)

# The spec's own target note for TMUA: "7+ candidates: 15+/20".
check("15/20 on TMUA reaches 7.0", scaled_for_raw(15, 20, 40, TMUA), 7.0)
check("and 14/20 does not", scaled_for_raw(14, 20, 40, TMUA) < 7.0, True)

# A single 20-question paper is put on the 40-mark sitting basis first.
check("10/20 doubles to 20 marks, the 4.5 anchor", scaled_for_raw(10, 20, 40, TMUA), 4.5)
# An ESAT module is scored on its own 27, not scaled up.
check("13/27 on ESAT is the 4.5 anchor", scaled_for_raw(13, 27, 27, ESAT), 4.5)

check("marks outside the range clamp low", scaled_from_marks(-5, TMUA), 1.0)
check("and clamp high", scaled_from_marks(999, TMUA), 9.0)
check("the ladder omits nothing between 2 and 9", len(grade_ladder(20, 40, TMUA)), 8)

# ── metrics ────────────────────────────────────────────────────────────────
qs = [{"id": i, "n": i, "topic": "Algebra" if i <= 5 else "Geometry",
       "spec_refs": ["MM1.1"], "answer": "C"} for i in range(1, 21)]
# 12 right, 3 wrong, 5 never answered.
resp = ([{"question_id": i, "selected": "C", "flagged": False, "time_sec": 30,
          "change_count": 0} for i in range(1, 13)]
        + [{"question_id": i, "selected": "A", "flagged": True, "time_sec": 200,
            "change_count": 2} for i in range(13, 16)])
m = compute_metrics(resp, qs, 40, TMUA)

check("raw counts only correct answers", m["raw"], 12)
check("unanswered counts the rows that are absent too", m["unanswered"], 5)
check("flagged is counted", m["flagged"], 3)
check("changed answers are summed", m["changed_answers"], 6)
check("scaled matches the curve", m["scaled"], 5.5)
check("marks to 7.0 is the gap to 15", m["marks_to_7"], 3)
check("the next whole grade above 5.5 is 6.0", m["next_whole_grade"], 6.0)
check("marks to the next whole grade", m["marks_to_next"], 1)
check("per-question rows cover the whole paper", len(m["per_question"]), 20)
check("topics are broken out", sorted(t["topic"] for t in m["by_topic"]),
      ["Algebra", "Geometry"])
check("Algebra is 5 for 5", [t for t in m["by_topic"] if t["topic"] == "Algebra"][0],
      {"topic": "Algebra", "correct": 5, "total": 5})
check("the result is labelled an estimate", m["estimate"], True)

# Slow is relative to the student's own pace on this paper, not a fixed number
# of seconds — 200s against a 30s mean is slow; nothing is slow if all equal.
slow = [r["n"] for r in m["per_question"] if r["slow"]]
check("questions well over the mean are flagged slow", slow, [13, 14, 15])
even = compute_metrics(
    [{"question_id": i, "selected": "C", "flagged": False, "time_sec": 60,
      "change_count": 0} for i in range(1, 21)], qs, 40, TMUA)
check("nothing is slow when every question took the same time",
      [r["n"] for r in even["per_question"] if r["slow"]], [])
check("a full-marks paper is 9.0", even["scaled"], 9.0)
check("and has no next grade to reach", even["next_whole_grade"], None)
check("and no marks to 9", even["marks_to_next"], None)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
