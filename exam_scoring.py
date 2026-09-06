"""Exam Mode scoring — raw marks to an estimated 1-9 score, and the metrics.

Pure functions: no Flask, no database. Same rule as prediction.py and
revision.py, so the whole scoring model is testable without a request context.

Ported from the reference player's `scaledFrom40` and `minRawFor` rather than
rewritten, as engine spec section 7 asks. That matters more than it looks: the
standalone HTML papers and Telos must give a student the same number for the
same script, and two independent implementations of a piecewise interpolation
will eventually disagree at a boundary and there will be no way to say which is
right.

The estimate is an estimate. UAT-UK equates every sitting with a Rasch model
and anchors the reported scale to that year's own cohort — median at 4.5,
roughly the top tenth above 7.0 — and has never published a raw-to-scale table
for either test in any year. So the anchors here are a modelled guess, they
live in the database rather than in this file so they can be recalibrated
without a deploy, and every score derived from them must be shown as an
estimate. Anything circulating as an official conversion table is somebody's
reconstruction.
"""

from __future__ import annotations

# Fallbacks only. The live values come from exam_scale_anchors; these exist so
# the pure functions can be exercised without a database and so a missing row
# degrades to the spec's published defaults rather than to nothing.
DEFAULT_ANCHORS = {
    "TMUA": [[0, 1.0], [8, 2.0], [14, 3.3], [20, 4.5], [26, 6.0],
             [30, 7.0], [34, 8.0], [38, 8.8], [40, 9.0]],
    "ESAT": [[0, 1.0], [5, 2.0], [9, 3.3], [13, 4.5], [17, 6.0],
             [20, 7.0], [23, 8.0], [26, 8.8], [27, 9.0]],
}

# A question taking more than this multiple of the paper's mean is flagged slow.
SLOW_MULTIPLE = 1.8


def scaled_from_marks(marks, anchors):
    """Interpolate a mark on the family's full basis to a 1-9 score.

    The reference's `scaledFrom40`, kept behaviour-for-behaviour: clamp into the
    anchor range, walk to the first segment whose upper mark is not below the
    input, interpolate linearly within it, round to one decimal place.

    Rounding at the end rather than at each step is deliberate — rounding
    early makes the scale step in visible jumps that do not match the anchors.
    """
    if not anchors:
        raise ValueError("no anchors")
    top_mark = anchors[-1][0]
    marks = max(0.0, min(float(marks), float(top_mark)))
    for i in range(1, len(anchors)):
        m0, s0 = anchors[i - 1]
        m1, s1 = anchors[i]
        if marks <= m1:
            if m1 == m0:                       # a degenerate anchor pair
                return round(float(s1), 1)
            return round(s0 + (s1 - s0) * (marks - m0) / (m1 - m0), 1)
    return round(float(anchors[-1][1]), 1)


def scaled_for_raw(raw, question_count, family_marks, anchors):
    """A raw mark out of `question_count`, as a scaled score.

    The raw mark is put on the family's basis first. A 20-question TMUA paper
    is doubled onto the 40-mark two-paper sitting; a 27-question ESAT module is
    unchanged, because ESAT modules are scored separately as in the real test.
    """
    if question_count <= 0:
        raise ValueError("question_count must be positive")
    return scaled_from_marks(raw * family_marks / question_count, anchors)


def min_raw_for(target, question_count, family_marks, anchors):
    """The lowest raw mark reaching `target`, or None if it is unreachable.

    The reference's `minRawFor`, including its epsilon. Without the tolerance a
    score landing exactly on an anchor can fail its own `>=` through binary
    floating point, and the ladder then shows the rung one mark too high.
    """
    for r in range(0, question_count + 1):
        if scaled_for_raw(r, question_count, family_marks, anchors) >= target - 1e-9:
            return r
    return None


def grade_ladder(question_count, family_marks, anchors):
    """[(whole score, lowest raw mark reaching it)] for 2.0 through 9.0.

    Rungs that cannot be reached on this paper are omitted rather than shown
    with a null, because a ladder is a thing a student reads to aim at and a
    rung they cannot stand on is noise.
    """
    out = []
    for g in range(2, 10):
        r = min_raw_for(float(g), question_count, family_marks, anchors)
        if r is not None:
            out.append((float(g), r))
    return out


def compute_metrics(responses, questions, family_marks, anchors):
    """Everything the results page needs, from one attempt.

    `responses`  [{question_id, selected, flagged, time_sec, change_count}]
    `questions`  [{id, n, topic, spec_refs, answer}]

    Returns the metrics dict stored on the attempt. Computed server-side at
    submit and stored, so the results page reads a snapshot rather than
    recomputing against anchors that may since have been recalibrated — a
    student's recorded score must not move under them.
    """
    by_id = {q["id"]: q for q in questions}
    n = len(questions)
    by_q = {r["question_id"]: r for r in responses}

    raw = 0
    per_question = []
    topics = {}
    spec = {}
    unanswered = flagged = changed = 0
    times = []

    for q in sorted(questions, key=lambda q: q["n"]):
        r = by_q.get(q["id"]) or {}
        selected = r.get("selected")
        correct = selected is not None and selected == q["answer"]
        t = int(r.get("time_sec") or 0)

        raw += 1 if correct else 0
        if selected is None:
            unanswered += 1
        if r.get("flagged"):
            flagged += 1
        changed += int(r.get("change_count") or 0)
        times.append(t)

        per_question.append({
            "n": q["n"], "question_id": q["id"], "topic": q.get("topic"),
            "selected": selected, "answer": q["answer"],
            "state": "correct" if correct else ("unanswered" if selected is None else "wrong"),
            "time_sec": t, "flagged": bool(r.get("flagged")),
            "change_count": int(r.get("change_count") or 0),
        })

        bucket = topics.setdefault(q.get("topic") or "Untagged", {"correct": 0, "total": 0})
        bucket["total"] += 1
        bucket["correct"] += 1 if correct else 0

        for ref in (q.get("spec_refs") or []):
            b = spec.setdefault(ref, {"correct": 0, "total": 0})
            b["total"] += 1
            b["correct"] += 1 if correct else 0

    # Slow is relative to this attempt, not to a fixed number of seconds. A
    # question is slow because it cost this student more than their own pace,
    # which is the only comparison available for an unsat paper.
    answered_times = [t for t in times if t > 0]
    mean_time = (sum(answered_times) / len(answered_times)) if answered_times else 0.0
    for row in per_question:
        row["slow"] = bool(mean_time and row["time_sec"] > SLOW_MULTIPLE * mean_time)

    scaled = scaled_for_raw(raw, n, family_marks, anchors)
    ladder = grade_ladder(n, family_marks, anchors)

    next_whole = None if scaled >= 9.0 else float(int(scaled) + 1)
    raw_next = min_raw_for(next_whole, n, family_marks, anchors) if next_whole else None
    raw_seven = min_raw_for(7.0, n, family_marks, anchors)

    return {
        "raw": raw,
        "max": n,
        "scaled": scaled,
        "next_whole_grade": next_whole,
        "raw_needed_for_next": raw_next,
        "marks_to_next": (raw_next - raw) if raw_next is not None else None,
        "raw_needed_for_7": raw_seven,
        "marks_to_7": (raw_seven - raw) if raw_seven is not None else None,
        "grade_ladder": [{"score": g, "raw": r} for g, r in ladder],
        "by_topic": [{"topic": k, **v} for k, v in sorted(topics.items())],
        "by_spec_ref": [{"ref": k, **v} for k, v in sorted(spec.items())],
        "per_question": per_question,
        "unanswered": unanswered,
        "flagged": flagged,
        "changed_answers": changed,
        "time_total_sec": sum(times),
        "time_mean_sec": round(mean_time, 1),
        "estimate": True,
    }
