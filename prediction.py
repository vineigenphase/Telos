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

Not every qualification reaches the top of that scale. An AS-level is graded
A-E with no A*, so its ladder ends at 5 and a perfect AS script scores 5.5, not
6.5. The ladder's top is read from the ladder itself rather than assumed, which
is what keeps an AS student from being predicted a grade that cannot appear on
their certificate. A boundary set says which it is by whether a_star is there.
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
    """Infer D and E by extending the observed spacing downward.

    a_star may be None, for a qualification that has no A* — the spacing is
    then taken from the gaps that do exist. Passing a real A* gives exactly the
    result it always did.

    Only used for boundary sets that carry no published D/E — rows typed in
    through the admin screen, and medians assembled across years. Where the
    board publishes D and E, boundary_ladder reads them instead; see migrations
    009-011, which added the columns and filled them from OCR's and Pearson's
    own documents.

    The approximation extends the mean gap between the boundaries that ARE
    known: for Edexcel Pure 1 2025 (88/74/61/48) the gaps are 14/13/13, giving
    D=35 and E=22, which is close to how real boundaries fall. Close, but a
    guess — which is why real values win wherever they exist.
    """
    gaps = [a - b, b - c]
    if a_star is not None:
        gaps.insert(0, a_star - a)
    step = sum(gaps) / len(gaps)
    d = c - step
    e = d - step
    return max(d, 0.0), max(e, 0.0)


def boundary_ladder(bs):
    """[(grade_point, marks), ...] ascending, from E up to the top grade.

    `bs` is a mapping with a_star / a_boundary / b_boundary / c_boundary, and
    optionally d_boundary / e_boundary. Published D and E are used when present
    and inferred otherwise — a set may legitimately have neither, since medians
    across years and hand-entered rows carry only the four.

    a_star of None means the qualification has no A* (an AS-level), and the
    ladder ends at A. Callers must read the top from ladder[-1] rather than
    assuming 6; see attempt_grade_score and marks_for_score.
    """
    a_star = bs["a_star"]
    a_star = float(a_star) if a_star is not None else None
    a = float(bs["a_boundary"])
    b = float(bs["b_boundary"])
    c = float(bs["c_boundary"])

    d = bs.get("d_boundary") if hasattr(bs, "get") else None
    e = bs.get("e_boundary") if hasattr(bs, "get") else None
    if d is None or e is None:
        d, e = infer_de(a_star, a, b, c)
    else:
        d, e = float(d), float(e)

    ladder = [(1, e), (2, d), (3, c), (4, b), (5, a)]
    if a_star is not None:
        ladder.append((6, a_star))
    return ladder


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
    """Median of each boundary across rows.

    D and E are only carried through when EVERY row in the set has them. A
    median mixing published values with absent ones would be neither, and a
    ladder built half from real boundaries and half from inferred ones is worse
    than one built consistently either way. A* is treated the same way, for the
    same reason: a set is either a qualification with an A* or one without, and
    a median over the rows that happen to have one would invent a top grade for
    a qualification that has none.
    """
    stars = [r["a_star"] for r in rows]
    out = {
        "a_star":      (median(float(v) for v in stars)
                        if all(v is not None for v in stars) else None),
        "a_boundary":  median(float(r["a_boundary"]) for r in rows),
        "b_boundary":  median(float(r["b_boundary"]) for r in rows),
        "c_boundary":  median(float(r["c_boundary"]) for r in rows),
    }

    def col(name):
        vals = []
        for r in rows:
            try:
                v = r[name]
            except (KeyError, IndexError, TypeError):
                return None
            if v is None:
                return None
            vals.append(float(v))
        return median(vals) if vals else None

    d, e = col("d_boundary"), col("e_boundary")
    if d is not None and e is not None:
        out["d_boundary"], out["e_boundary"] = d, e
    return out


# ---------------------------------------------------------------------------
# One attempt -> a position on the grade scale
# ---------------------------------------------------------------------------

def attempt_grade_score(marks, bs, max_marks):
    """Convert raw marks into a continuous grade score.

    Between two boundaries, interpolate linearly. Above the top grade, add a
    small bonus scaled by the marks left to full — otherwise a 100% script and
    a bare top grade look identical. The top is whatever the ladder ends on:
    6.5 for an A-level, 5.5 for an AS. Below E, scale linearly down to 0 at
    zero marks.
    """
    marks = float(marks)
    ladder = boundary_ladder(bs)
    top_point, top_marks = ladder[-1]
    e_marks = ladder[0][1]

    if marks >= top_marks:
        headroom = max(float(max_marks) - top_marks, 1.0)
        over = min(marks - top_marks, headroom)
        return top_point + A_STAR_BONUS_CAP * (over / headroom)

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
    top_point, top_marks = ladder[-1]
    if score >= top_point:
        headroom = max(float(max_marks) - top_marks, 1.0)
        return top_marks + (min(score - top_point, A_STAR_BONUS_CAP)
                            / A_STAR_BONUS_CAP) * headroom
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
        # The ceiling is the qualification's own top grade, not always A*.
        # Telling an AS student they are four marks off an A* would name a
        # grade their certificate cannot carry.
        top_point = boundary_ladder(ref)[-1][0]
        target_point = min(top_point, int(math.floor(mean)) + 1)
        if mean < top_point:
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
