"""Prescription engine — "your next 3 questions".

Pure functions only — no Flask, no database, mirroring prediction.py. Everything
takes plain data and returns plain data, so it unit tests without a request
context.

Phase 3 tells a student *what* their grade is. This tells them what to do about
it on a Tuesday evening. The heatmap already shows which topics are weak; the
missing step is turning that ranking into three specific questions with a reason
attached.

Why a score and not just "worst topic first": the weakest topic is often a rare
one. Being at 30% on a topic worth 3 marks a year matters less than 65% on one
worth 15. The priority score below trades accuracy off against how much the
topic actually costs across a paper, so the recommendation follows marks rather
than embarrassment.

Spec note — the spec calls the question source `bank_questions`; the table is
actually `question_bank`, it is per-user, and it is empty until that user
uploads and tags a paper. So selection falls back to re-doing weak questions
from papers already logged (`question_marks`). The spec's own rule, "preferring
unattempted questions, then ones scored below 60%", already assumes attempt
data, which only the marks table has.

The cutoff itself is a departure from the spec, agreed with the owner: 75%, not
60%. 60% is around a C, so a student sitting on a B was told there was nothing
to work on — which is wrong for the students this is for. 75% is roughly the
A/B border, so the redo list keeps offering work to someone who is already
doing well and wants an A*.
"""

from __future__ import annotations

import math

RECENCY_BOOST = 1.3         # topic last seen in the most recent N papers
RECENCY_WINDOW = 3          # ...where N is this many papers
# The redo cutoff. The spec says 60%; this is deliberately higher — see the
# module docstring. Everything derives from this constant, the user-facing
# message included, so it is the only place to change it.
WEAK_THRESHOLD = 0.75
TOP_TOPICS = 3
DEFAULT_PICKS = 3
MIN_TOPIC_MARKS = 1.0       # ignore topics with almost no marks behind them


# ---------------------------------------------------------------------------
# Topic priority
# ---------------------------------------------------------------------------

def topic_stats(marks, recent_paper_ids=()):
    """Roll per-question marks up into per-topic aggregates.

    `marks`: dicts with topic, obtained, max_marks, paper_id. Rows with no
    topic are skipped — an untagged question can't be prescribed against.

    `recent_paper_ids`: the most recent RECENCY_WINDOW paper ids, used for the
    recency factor. Order doesn't matter, membership does.
    """
    recent = set(recent_paper_ids)
    agg = {}
    for m in marks:
        topic = (m.get("topic") or "").strip()
        if not topic:
            continue
        try:
            got = float(m["obtained"])
            mx = float(m["max_marks"])
        except (TypeError, ValueError, KeyError):
            continue
        if mx <= 0:
            continue
        t = agg.setdefault(topic, {
            "topic": topic, "got": 0.0, "max": 0.0, "n": 0,
            "papers": set(), "recent": False,
        })
        t["got"] += got
        t["max"] += mx
        t["n"] += 1
        pid = m.get("paper_id")
        if pid is not None:
            t["papers"].add(pid)
            if pid in recent:
                t["recent"] = True
    return agg


def priority(marks_lost_ratio, topic_frequency, recency_factor):
    """priority = marks_lost_ratio x log(1 + frequency) x recency_factor

    The log is what stops a topic that appears in every single paper from
    swamping everything else — frequency should tilt the ranking, not decide it.
    """
    return marks_lost_ratio * math.log(1 + topic_frequency) * recency_factor


def rank_topics(marks, recent_paper_ids=(), limit=TOP_TOPICS):
    """Rank topics worst-value-first. Returns a list of dicts, highest priority
    first, each carrying the numbers needed to explain itself later."""
    agg = topic_stats(marks, recent_paper_ids)
    ranked = []
    for t in agg.values():
        if t["max"] < MIN_TOPIC_MARKS:
            continue
        accuracy = t["got"] / t["max"]
        lost_ratio = 1.0 - accuracy
        # Nothing lost means nothing to prescribe. Without this a topic the
        # student has fully mastered still surfaces whenever their question
        # bank happens to hold an unattempted question tagged with it.
        if lost_ratio <= 0:
            continue
        frequency = len(t["papers"]) or 1
        recency = RECENCY_BOOST if t["recent"] else 1.0
        ranked.append({
            "topic": t["topic"],
            "accuracy": accuracy,
            "pct": round(accuracy * 100),
            "marks_lost": round(t["max"] - t["got"], 1),
            "marks_available": round(t["max"], 1),
            "marks_lost_per_paper": round((t["max"] - t["got"]) / frequency, 1),
            "frequency": frequency,
            "questions_seen": t["n"],
            "recency_factor": recency,
            "priority": round(priority(lost_ratio, frequency, recency), 4),
        })

    # Sort by priority, then by marks lost, then topic name so the order is
    # stable across runs — a "today" panel that reshuffles itself on refresh
    # reads as noise.
    ranked.sort(key=lambda t: (-t["priority"], -t["marks_lost"], t["topic"]))
    return ranked[:limit] if limit else ranked


# ---------------------------------------------------------------------------
# The "why" line — not optional
# ---------------------------------------------------------------------------

def why_line(topic):
    """Explain the pick in the student's own numbers.

    An unexplained recommendation gets ignored, so every question carries the
    accuracy that flagged the topic and what it costs per paper.
    """
    per_paper = topic["marks_lost_per_paper"]
    if per_paper >= 0.5:
        cost = f", worth ~{per_paper:g} mark{'s' if per_paper != 1 else ''}/paper"
    else:
        cost = ""
    return f"You're at {topic['pct']}% on {topic['topic']}{cost}."


# ---------------------------------------------------------------------------
# Question selection
# ---------------------------------------------------------------------------

def _bank_candidates(bank, topic_name, attempted_keys):
    """Unattempted bank questions for a topic, best first.

    `bank`: dicts with id, q_num, topics (already parsed to a list), plus
    whatever source labelling the caller wants to carry through.
    """
    out = []
    wanted = topic_name.strip().lower()
    for q in bank:
        topics = [str(t).strip().lower() for t in (q.get("topics") or [])]
        if wanted not in topics:
            continue
        key = (str(q.get("paper_code") or ""), str(q.get("q_num") or ""))
        if key in attempted_keys:
            continue
        out.append(q)
    # More marks first — a 12-mark question teaches more than a 2-mark one.
    out.sort(key=lambda q: (-(float(q.get("max_marks") or 0)), str(q.get("q_num"))))
    return out


def _redo_candidates(marks, topic_name):
    """Already-attempted questions on this topic scored below the threshold,
    worst first. These are the fallback when the bank has nothing."""
    wanted = topic_name.strip().lower()
    out = []
    for m in marks:
        if (m.get("topic") or "").strip().lower() != wanted:
            continue
        try:
            got = float(m["obtained"])
            mx = float(m["max_marks"])
        except (TypeError, ValueError, KeyError):
            continue
        if mx <= 0:
            continue
        ratio = got / mx
        if ratio >= WEAK_THRESHOLD:
            continue
        out.append({**m, "ratio": ratio, "pct": round(ratio * 100)})
    # Worst ratio first, then biggest question — most recoverable marks first.
    out.sort(key=lambda m: (m["ratio"], -float(m["max_marks"])))
    return out


def prescribe(marks, bank=(), recent_paper_ids=(), limit=DEFAULT_PICKS):
    """Top-level: turn a user's marks and question bank into next actions.

    `marks`: per-question rows (topic, obtained, max_marks, paper_id, q_num,
    paper_code, year, board, subject).
    `bank`: their tagged question bank, `topics` already parsed to a list.

    Returns a dict. Never a bare list — the caller needs the topic ranking too,
    and needs to know *why* it got nothing back when it gets nothing back.
    """
    topics = rank_topics(marks, recent_paper_ids, limit=TOP_TOPICS)
    if not topics:
        return {
            "ready": False,
            "reason": "no_topics",
            "topics": [],
            "picks": [],
            "message": "Tag a few questions with topics and Telos will tell you "
                       "what to work on next.",
        }

    attempted_keys = {
        (str(m.get("paper_code") or ""), str(m.get("q_num") or ""))
        for m in marks
    }

    picks = []
    used_bank, used_redo = set(), set()

    # One pass per topic before any second pick, so three picks cover three
    # topics rather than three questions on the same one. A student who only
    # ever revises their single worst topic still fails the other two.
    for _ in range(limit):
        progressed = False
        for topic in topics:
            if len(picks) >= limit:
                break
            pick = None

            for q in _bank_candidates(bank, topic["topic"], attempted_keys):
                if q["id"] in used_bank:
                    continue
                used_bank.add(q["id"])
                pick = {
                    "kind": "new",
                    "topic": topic["topic"],
                    "q_num": q.get("q_num"),
                    "max_marks": q.get("max_marks"),
                    "source": _source_label(q),
                    "bank_id": q["id"],
                    "upload_id": q.get("upload_id"),
                    "why": why_line(topic),
                    "action": "Try it",
                }
                break

            if pick is None:
                for m in _redo_candidates(marks, topic["topic"]):
                    key = (m.get("paper_id"), str(m.get("q_num")))
                    if key in used_redo:
                        continue
                    used_redo.add(key)
                    pick = {
                        "kind": "redo",
                        "topic": topic["topic"],
                        "q_num": m.get("q_num"),
                        "max_marks": m.get("max_marks"),
                        "source": _source_label(m),
                        "paper_id": m.get("paper_id"),
                        "scored": f"{_g(m['obtained'])}/{_g(m['max_marks'])}",
                        "pct": m["pct"],
                        "why": why_line(topic),
                        "action": "Redo it",
                    }
                    break

            if pick:
                picks.append(pick)
                progressed = True
        if not progressed:
            break

    if not picks:
        return {
            "ready": False,
            "reason": "no_questions",
            "topics": topics,
            "picks": [],
            "message": "Nothing to prescribe yet — you're above "
                       f"{int(WEAK_THRESHOLD * 100)}% on every question you've logged. "
                       "Upload and tag a paper to get new questions.",
        }

    return {"ready": True, "topics": topics, "picks": picks[:limit]}


def _source_label(row):
    """'2019 Paper 1 Q4' — enough to actually find the question."""
    bits = [str(row.get("year") or "").strip(), str(row.get("paper_code") or "").strip()]
    label = " ".join(b for b in bits if b)
    q = str(row.get("q_num") or "").strip()
    if q:
        label = f"{label} Q{q}" if label else f"Q{q}"
    return label or "your question bank"


def _g(v):
    """Trim trailing .0 — marks are shown as 7/8, never 7.0/8.0."""
    f = float(v)
    return int(f) if f == int(f) else round(f, 1)
