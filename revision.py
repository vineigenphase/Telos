"""Spaced repetition — Phase 6.

Pure functions only: no Flask, no database. Everything takes plain data and
returns plain data, so the scheduling can be tested without a request context,
the same way prediction.py and prescription.py are.

SM-2, simplified to the spec's table. A question answered below the redo
threshold joins the queue, and each review moves it:

    Got it   repetitions += 1, interval from the ladder, ease += 0.10
    Partly   interval unchanged,                        ease -= 0.15
    Missed   repetitions = 0, interval back to 1 day,   ease -= 0.20

`ease` is recorded and clamped but does NOT drive the interval — the ladder
does. That is the spec's simplification, not an oversight: real SM-2 multiplies
by ease, which makes intervals unpredictable early on when there is barely any
evidence about the student. The value is kept because it is the obvious input
if scheduling is ever refined, and because a question repeatedly answered
"Partly" visibly drifts toward the floor.

The daily cap is the other thing worth keeping. An uncapped backlog after a week
away is how people quit, so the queue shows at most CAP items and says plainly
how many it is holding back.
"""

from __future__ import annotations

# Days between reviews, by how many times the question has been got right in a
# row. Beyond the end of the ladder the interval stays at the last value —
# something answered correctly six times running does not need a year off.
LADDER = [1, 3, 7, 16, 35]

EASE_START = 2.5
EASE_MIN = 1.3
EASE_MAX = 2.8

EASE_DELTA = {"got": 0.10, "partly": -0.15, "missed": -0.20}

OUTCOMES = ("got", "partly", "missed")

# How many due items a student is shown at once.
DAILY_CAP = 20


def clamp_ease(ease):
    """Keep ease inside its band. Outside it the number stops meaning anything."""
    return max(EASE_MIN, min(EASE_MAX, float(ease)))


def interval_for(repetitions):
    """Days until the next review, for a question got right `repetitions` times.

    Zero repetitions means it has never been got right since it entered the
    queue, so it comes back tomorrow.
    """
    if repetitions <= 0:
        return LADDER[0]
    return LADDER[min(repetitions, len(LADDER)) - 1]


def review(item, outcome):
    """Apply one review to a queue item.

    `item` is a mapping with `ease`, `interval_days` and `repetitions`. Returns
    a new dict of the fields that changed — the caller writes them and sets
    due_at to now + interval_days. Nothing here knows what "now" is, which is
    what makes it testable.
    """
    if outcome not in OUTCOMES:
        raise ValueError("unknown outcome: %r" % (outcome,))

    reps = int(item.get("repetitions") or 0)
    ease = clamp_ease(item.get("ease") or EASE_START)
    interval = int(item.get("interval_days") or LADDER[0])

    if outcome == "got":
        reps += 1
        interval = interval_for(reps)
    elif outcome == "missed":
        reps = 0
        interval = LADDER[0]
    # "partly" leaves both alone: the student half-knows it, so seeing it again
    # on the same rhythm is right. Only the ease moves, which is the record that
    # this one keeps being difficult.

    return {
        "repetitions": reps,
        "interval_days": interval,
        "ease": clamp_ease(ease + EASE_DELTA[outcome]),
    }


def cap_queue(due, priority_of=None, cap=DAILY_CAP):
    """The items to show today, and how many are being held back.

    Returns (shown, total). When more than `cap` are due, the ones shown are the
    highest priority — by the same topic score Phase 4 uses, so the queue and
    the prescriptions agree about what matters rather than offering two
    different answers to "what should I do next".
    """
    total = len(due)
    if total <= cap:
        return list(due), total
    if priority_of is None:
        ordered = list(due)
    else:
        ordered = sorted(due, key=lambda it: -priority_of(it))
    return ordered[:cap], total


def queue_message(shown, total, cap=DAILY_CAP):
    """What to tell the student about the size of the queue."""
    if total == 0:
        return "Nothing due. Log a paper and anything you drop marks on will appear here."
    if total <= cap:
        return "%d due today." % total
    return "%d of %d due — the rest will keep." % (shown, total)
