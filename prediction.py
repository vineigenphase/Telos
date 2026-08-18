"""Predicted grade engine.

Pure functions only — no Flask, no database. Everything here takes plain data
and returns plain data, so it can be unit tested without a request context.

Why not percentages: 62% on a hard 2019 paper and 62% on an easy 2023 paper
are not the same performance. Every attempt is converted to a position on a
continuous grade scale using that paper's real boundaries, which normalises
difficulty automatically.

Scale: A*=6, A=5, B=4, C=3, D=2, E=1, U=0, with fractional positions between
boundaries. A grade score of 4.6 means "comfortably into B, most of the way to
an A".
"""

from __future__ import annotations

import math
from statistics import median

GRADE_POINTS = {"A*": 6, "A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "U": 0}
POINT_TO_GRADE = {v: k for k, v in GRADE_POINTS.items()}

RECENCY_DECAY = 0.85        # weight of each older paper, i = 0 is most recent
MIN_PAPERS = 3              # below this we refuse to predict at all
A_STAR_BONUS_CAP = 0.5      # a perfect script tops out at 6.5, not infinity


# ---------------------------------------------------------------------------
# Boundaries
# ---------------------------------------------------------------------------

class MissingBoundaries(Exception):
    """Raised when no usable boundary set exists. Never guessed around."""


def infer_de(a_star, a, b, c):
    """Infer D and E boundaries by extending the observed spacing downward.

    The grade_boundaries table stores A*/A/B/C only, but the scale needs D and
    E to place a weaker script. Rather than invent numbers, this extends the
    mean gap between the boundaries that ARE known — for Edexcel Pure 1 2025
    (88/74/61/48) the gaps are 14/13/13, giving D=35 and E=22, which is close
    to how real boundaries fall.

    This is an approximation and it is confined to this one function: if real
    D/E data is ever added to the table, delete this and read the columns.
    """
    gaps = [a_star - a, a - b, b - c]
    step = sum(gaps) / len(gaps)
    d = c - step
    e = d - step
    return max(d, 0.0), max(e, 0.0)


def boundary_ladder(bs):
    """[(grade_point, marks), ...] ascending, from E up to A*.

    `bs` is a mapping with a_star / a_boundary / b_boundary / c_boundary.
    """
    a_star = float(bs["a_star"])
    a = float(bs["a_boundary"])
    b = float(bs["b_boundary"])
    c = float(bs["c_boundary"])
    d, e = infer_de(a_star, a, b, c)
    return [(1, e), (2, d), (3, c), (4, b), (5, a), (6, a_star)]


def select_boundaries(rows, board, subject, paper_code, year):
    """Pick a boundary set, with the fallback chain from the spec.

    exact (board, subject, paper, year)
      -> same paper, other years (median of each boundary)
      -> same subject, same year (median)
      -> MissingBoundaries, and the caller skips the attempt.

    Returns (boundary_dict, source_label).
    """
    def match(**kw):
        out = []
        for r in rows:
            if all(str(r[k]) == str(v) for k, v in kw.items()):
                out.append(r)
        return out

    exact = match(board=board, subject=subject, paper_code=paper_code, year=year)
    if exact:
        return exact[0], "exact"

    same_paper = match(board=board, subject=subject, paper_code=paper_code)
    if same_paper:
        return _median_set(same_paper), "median of same paper, other years"

    same_subject = match(board=board, subject=subject, year=year)
    if same_subject:
        return _median_set(same_subject), "median of same subject, same year"

    raise MissingBoundaries(f"no boundaries for {board} {subject} {paper_code} {year}")


def _median_set(rows):
    return {
        "a_star":      median(float(r["a_star"]) for r in rows),
        "a_boundary":  median(float(r["a_boundary"]) for r in rows),
        "b_boundary":  median(float(r["b_boundary"]) for r in rows),
        "c_boundary":  median(float(r["c_boundary"]) for r in rows),
    }


# ---------------------------------------------------------------------------
# One attempt -> a position on the grade scale
# ---------------------------------------------------------------------------

def attempt_grade_score(marks, bs, max_marks):
    """Convert raw marks into a continuous grade score.

    Between two boundaries, interpolate linearly. Above A*, add a small bonus
    scaled by the marks left to full, capped at 6.5 — otherwise a 100% script
    and a bare A* look identical. Below E, scale linearly down to 0 at zero
    marks.
    """
    marks = float(marks)
    ladder = boundary_ladder(bs)
    a_star_marks = ladder[-1][1]
    e_marks = ladder[0][1]

    if marks >= a_star_marks:
        headroom = max(float(max_marks) - a_star_marks, 1.0)
        over = min(marks - a_star_marks, headroom)
        return 6.0 + A_STAR_BONUS_CAP * (over / headroom)

    if marks < e_marks:
        return max(0.0, marks / e_marks) if e_marks > 0 else 0.0

    for (lo_pt, lo_marks), (hi_pt, hi_marks) in zip(ladder, ladder[1:]):
        if lo_marks <= marks < hi_marks:
            span = hi_marks - lo_marks
            if span <= 0:
                return float(lo_pt)
            return lo_pt + (marks - lo_marks) / span
    return float(ladder[-1][0])


def score_to_grade(score):
    """Floor a grade score back to a letter."""
    if score >= 6:
        return "A*"
    return POINT_TO_GRADE[max(0, min(6, int(math.floor(score))))]


def marks_for_score(score, bs, max_marks):
    """Inverse of attempt_grade_score: what raw mark does this score represent?"""
    ladder = boundary_ladder(bs)
    if score >= 6:
        a_star_marks = ladder[-1][1]
        headroom = max(float(max_marks) - a_star_marks, 1.0)
        return a_star_marks + (min(score - 6.0, A_STAR_BONUS_CAP) / A_STAR_BONUS_CAP) * headroom
    if score < 1:
        return score * ladder[0][1]
    for (lo_pt, lo_marks), (hi_pt, hi_marks) in zip(ladder, ladder[1:]):
        if lo_pt <= score < hi_pt:
            return lo_marks + (score - lo_pt) * (hi_marks - lo_marks)
    return ladder[-1][1]


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def recency_weighted(scores):
    """scores ordered most-recent-first. Returns (weighted_mean, weights)."""
    weights = [RECENCY_DECAY ** i for i in range(len(scores))]
    total_w = sum(weights)
    if total_w == 0:
        return 0.0, weights
    return sum(w * s for w, s in zip(weights, scores)) / total_w, weights


def weighted_standard_error(scores, weights, mean):
    """Weighted SE of the mean. 0 for a single paper (no spread to measure)."""
    n = len(scores)
    if n < 2:
        return 0.0
    total_w = sum(weights)
    var = sum(w * (s - mean) ** 2 for w, s in zip(weights, scores)) / total_w
    return math.sqrt(var) / math.sqrt(n)


def confidence_level(sample_size, se):
    """Sample size sets the base level; a wide error interval knocks it down.

    'Spans more than one grade' is read as the +/-1 SE interval being wider
    than a whole grade, i.e. 2*se > 1.0.
    """
    if sample_size >= 10:
        level = "high"
    elif sample_size >= 5:
        level = "medium"
    else:
        level = "low"

    if 2 * se > 1.0:
        level = {"high": "medium", "medium": "low", "low": "low"}[level]
    return level


# ---------------------------------------------------------------------------
# Top level
# ---------------------------------------------------------------------------

def predict(attempts, boundary_rows, reference_year=None):
    """Predict a grade for one (board, subject).

    `attempts`: dicts with board, subject, paper_code, year, score, max_marks,
    ordered MOST RECENT FIRST (taken_at DESC).

    Returns a dict, or a "not enough data" result — never a bare number. The
    caller is expected to render the prediction together with the action; a
    prediction with no next step is just anxiety.
    """
    scored, skipped = [], []
    for a in attempts:
        if a.get("score") is None or not a.get("max_marks"):
            skipped.append({**a, "reason": "no score recorded"})
            continue
        try:
            bs, source = select_boundaries(
                boundary_rows, a["board"], a["subject"], a["paper_code"], a["year"])
        except MissingBoundaries:
            skipped.append({**a, "reason": "no boundaries available"})
            continue
        scored.append({
            "attempt": a,
            "score": attempt_grade_score(a["score"], bs, a["max_marks"]),
            "boundary_source": source,
        })

    n = len(scored)
    if n < MIN_PAPERS:
        return {
            "ready": False,
            "sample_size": n,
            "needed": MIN_PAPERS - n,
            "skipped": skipped,
            "message": f"Log {MIN_PAPERS - n} more paper"
                       f"{'s' if MIN_PAPERS - n != 1 else ''} to unlock your predicted grade.",
        }

    scores = [s["score"] for s in scored]
    mean, weights = recency_weighted(scores)
    se = weighted_standard_error(scores, weights, mean)
    conf = confidence_level(n, se)
    grade = score_to_grade(mean)

    # Marks to the next grade, measured against the most recent boundaries
    # available for this subject — the best available guess at the next real
    # exam's boundaries.
    ref_rows = [r for r in boundary_rows
                if str(r["board"]) == str(attempts[0]["board"])
                and str(r["subject"]) == str(attempts[0]["subject"])]
    next_grade = marks_to_next = None
    if ref_rows:
        if reference_year is None:
            reference_year = max(str(r["year"]) for r in ref_rows if str(r["year"]).isdigit())
        year_rows = [r for r in ref_rows if str(r["year"]) == str(reference_year)] or ref_rows
        ref = _median_set(year_rows)
        ref_max = float(attempts[0].get("max_marks") or 100)
        current_marks = marks_for_score(mean, ref, ref_max)
        target_point = min(6, int(math.floor(mean)) + 1)
        if mean < 6:
            next_grade = POINT_TO_GRADE[target_point]
            target_marks = marks_for_score(float(target_point), ref, ref_max)
            marks_to_next = max(0, math.ceil(target_marks - current_marks))

    # Low confidence is shown as a range rather than a false-precision number.
    range_label = None
    if conf == "low":
        lo = score_to_grade(max(0.0, mean - 1))
        range_label = f"{lo}–{grade}" if lo != grade else grade

    return {
        "ready": True,
        "grade_score": round(mean, 3),
        "predicted_grade": grade,
        "range_label": range_label,
        "next_grade": next_grade,
        "marks_to_next": marks_to_next,
        "confidence": conf,
        "standard_error": round(se, 3),
        "sample_size": n,
        "skipped": skipped,
        "provisional": conf == "low",
    }
