"""Unit tests for the predicted grade engine.

Pure functions, no database, no Flask — runnable with `python tests/test_prediction.py`.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prediction import (  # noqa: E402
    MissingBoundaries, attempt_grade_score, confidence_level, infer_de,
    marks_for_score, predict, recency_weighted, score_to_grade,
    select_boundaries,
)

FAILS = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        FAILS.append(label)


def close(label, got, want, tol=0.01):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want ~{want!r})"))
    if not ok:
        FAILS.append(label)


# A hard year and an easy year for the same paper. This contrast is the whole
# point of the engine.
HARD = {"board": "Edexcel", "subject": "Further Maths", "paper_code": "CP1",
        "year": "2019", "a_star": 60, "a_boundary": 52, "b_boundary": 44, "c_boundary": 36}
EASY = {"board": "Edexcel", "subject": "Further Maths", "paper_code": "CP1",
        "year": "2023", "a_star": 68, "a_boundary": 61, "b_boundary": 54, "c_boundary": 47}
OTHER = {"board": "Edexcel", "subject": "Further Maths", "paper_code": "CP2",
         "year": "2019", "a_star": 62, "a_boundary": 54, "b_boundary": 46, "c_boundary": 38}
ROWS = [HARD, EASY, OTHER]


# ── boundary handling ───────────────────────────────────────────────────────
d, e = infer_de(60, 52, 44, 36)
close("D inferred from observed spacing", d, 28)
close("E inferred from observed spacing", e, 20)

bs, src = select_boundaries(ROWS, "Edexcel", "Further Maths", "CP1", "2019")
check("exact boundary match", src, "exact")
check("exact match returns that year", bs["a_star"], 60)

bs, src = select_boundaries(ROWS, "Edexcel", "Further Maths", "CP1", "2021")
check("missing year falls back to same paper", src, "median of same paper, other years")
close("fallback uses the median A*", float(bs["a_star"]), 64)   # median(60, 68)

try:
    select_boundaries(ROWS, "OCR A", "Physics", "Paper 1", "2020")
    check("unknown subject raises", False, True)
except MissingBoundaries:
    check("unknown subject raises rather than inventing boundaries", True, True)


# ── one attempt -> grade score ──────────────────────────────────────────────
close("exact A boundary is exactly 5.0", attempt_grade_score(52, HARD, 75), 5.0)
close("exact A* boundary is exactly 6.0", attempt_grade_score(60, HARD, 75), 6.0)
close("exact C boundary is exactly 3.0", attempt_grade_score(36, HARD, 75), 3.0)
close("midway A->A* is 5.5", attempt_grade_score(56, HARD, 75), 5.5)

full = attempt_grade_score(75, HARD, 75)
close("full marks caps at 6.5", full, 6.5)
check("above A* never exceeds the cap", attempt_grade_score(75, HARD, 75) <= 6.5, True)

below_e = attempt_grade_score(10, HARD, 75)
check("below E scales down toward 0", 0 < below_e < 1, True)
close("zero marks is 0.0", attempt_grade_score(0, HARD, 75), 0.0)

# THE point of the whole engine: same raw mark, different difficulty
hard_score = attempt_grade_score(55, HARD, 75)
easy_score = attempt_grade_score(55, EASY, 75)
check("same marks on a harder paper scores higher", hard_score > easy_score, True)
check("55 on the hard year is an A", score_to_grade(hard_score), "A")
check("55 on the easy year is a B", score_to_grade(easy_score), "B")

# inverse
close("marks_for_score inverts attempt_grade_score",
      marks_for_score(attempt_grade_score(47, HARD, 75), HARD, 75), 47, tol=0.2)


# ── aggregation ─────────────────────────────────────────────────────────────
mean, weights = recency_weighted([5.0, 4.0, 3.0])
check("most recent paper carries the most weight", weights[0] > weights[1] > weights[2], True)
check("recency weighting pulls toward the newest score", mean > 4.0, True)

check("confidence: 10+ papers, tight spread", confidence_level(12, 0.1), "high")
check("confidence: 5-9 papers", confidence_level(6, 0.1), "medium")
check("confidence: 3-4 papers", confidence_level(3, 0.1), "low")
check("wide error downgrades a high sample", confidence_level(12, 0.9), "medium")


# ── predict() ───────────────────────────────────────────────────────────────
def attempt(year, score, code="CP1"):
    return {"board": "Edexcel", "subject": "Further Maths", "paper_code": code,
            "year": year, "score": score, "max_marks": 75}


one = predict([attempt("2019", 55)], ROWS)
check("a single paper refuses to predict", one["ready"], False)
check("single paper says how many more are needed", one["needed"], 2)
check("refusal carries a usable message", "2 more paper" in one["message"], True)

two = predict([attempt("2019", 55), attempt("2023", 55)], ROWS)
check("two papers still refuses", two["ready"], False)

three = predict([attempt("2019", 55), attempt("2023", 55), attempt("2019", 50, "CP2")], ROWS)
check("three papers predicts", three["ready"], True)
check("three papers is low confidence", three["confidence"], "low")
check("low confidence is shown as a range", three["range_label"] is not None, True)
check("low confidence is flagged provisional", three["provisional"], True)
check("prediction names the next grade", three["next_grade"] is not None, True)
check("prediction says how many marks away", isinstance(three["marks_to_next"], int), True)
check("marks to next is never negative", three["marks_to_next"] >= 0, True)

# improving trend must move the number: same scores, opposite order
improving = predict([attempt("2023", 65), attempt("2023", 55), attempt("2023", 45)], ROWS)
declining = predict([attempt("2023", 45), attempt("2023", 55), attempt("2023", 65)], ROWS)
check("recency weighting distinguishes improving from declining",
      improving["grade_score"] > declining["grade_score"], True)

# missing boundaries: the attempt is skipped and reported, never guessed
mixed = predict([attempt("2019", 55), attempt("2023", 55),
                 {"board": "OCR A", "subject": "Physics", "paper_code": "Paper 1",
                  "year": "2020", "score": 60, "max_marks": 100},
                 attempt("2019", 50, "CP2")], ROWS)
check("attempt with no boundaries is skipped", len(mixed["skipped"]), 1)
check("skip reason is recorded", mixed["skipped"][0]["reason"], "no boundaries available")
check("remaining attempts still predict", mixed["ready"], True)

unscored = predict([attempt("2019", None), attempt("2023", 55),
                    attempt("2019", 50, "CP2"), attempt("2023", 60)], ROWS)
check("paper with no score is skipped", unscored["skipped"][0]["reason"], "no score recorded")
check("sample size counts only scored papers", unscored["sample_size"], 3)

strong = predict([attempt("2019", 62), attempt("2019", 61), attempt("2019", 60),
                  attempt("2019", 63), attempt("2019", 61)], ROWS)
check("consistent A* work predicts A*", strong["predicted_grade"], "A*")
check("a top prediction has no next grade to chase", strong["next_grade"], None)
check("tight consistent spread is at least medium", strong["confidence"] in ("medium", "high"), True)

print()
print("ALL PASS" if not FAILS else f"FAILURES ({len(FAILS)}): {FAILS}")
sys.exit(1 if FAILS else 0)
