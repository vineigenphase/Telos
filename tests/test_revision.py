import os
"""Spaced repetition scheduling (pure).

The scheduling is where this feature is either useful or quietly annoying, and
none of it needs a database — so it is tested here as plain data in, plain data
out, the same way the prediction and prescription engines are.

The properties that matter to a student: getting something right pushes it
further away, missing it brings it back tomorrow and wipes the streak, and a
week off does not return a wall of four hundred questions.
"""
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from revision import (  # noqa: E402
    DAILY_CAP, EASE_MAX, EASE_MIN, EASE_START, LADDER, cap_queue, clamp_ease,
    interval_for, queue_message, review,
)

FAILS = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        FAILS.append(label)


def close(label, got, want, tol=0.001):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want ~{want!r})"))
    if not ok:
        FAILS.append(label)


def item(reps=0, ease=EASE_START, interval=1):
    return {"repetitions": reps, "ease": ease, "interval_days": interval}


# ── the ladder ──────────────────────────────────────────────────────────────
check("a question never got right comes back tomorrow", interval_for(0), 1)
check("the ladder runs 1, 3, 7, 16, 35",
      [interval_for(n) for n in (1, 2, 3, 4, 5)], LADDER)
check("...and stops climbing at the end rather than disappearing for a year",
      interval_for(50), LADDER[-1])

# ── one review at a time ────────────────────────────────────────────────────
got = review(item(), "got")
check("getting it right counts a repetition", got["repetitions"], 1)
check("...and schedules it a day out", got["interval_days"], 1)
close("...and nudges the ease up", got["ease"], 2.6)

second = review(item(reps=1, ease=2.6, interval=1), "got")
check("a second success moves it to three days", second["interval_days"], 3)
check("...and counts again", second["repetitions"], 2)

partly = review(item(reps=3, ease=2.5, interval=7), "partly")
check("a half-remembered question keeps its place in the rhythm",
      partly["interval_days"], 7)
check("...and its streak", partly["repetitions"], 3)
close("...but records that it was hard", partly["ease"], 2.35)

missed = review(item(reps=4, ease=2.5, interval=16), "missed")
check("missing it brings it back tomorrow", missed["interval_days"], 1)
check("...and wipes the streak", missed["repetitions"], 0)
close("...and drops the ease furthest", missed["ease"], 2.30)

# ── ease stays inside its band ──────────────────────────────────────────────
check("ease is clamped at the top", clamp_ease(9.0), EASE_MAX)
check("...and at the bottom", clamp_ease(0.1), EASE_MIN)
hard = item(ease=EASE_MIN)
for _ in range(5):
    hard = {**hard, **review(hard, "missed")}
check("a question missed over and over cannot fall through the floor",
      hard["ease"] >= EASE_MIN, True)
easy = item(ease=EASE_MAX)
for _ in range(5):
    easy = {**easy, **review(easy, "got")}
check("...nor one always got right float away", easy["ease"] <= EASE_MAX, True)

# A streak survives being extended well past the ladder.
long_run = item()
for _ in range(8):
    long_run = {**long_run, **review(long_run, "got")}
check("eight correct reviews leave it on the longest interval",
      long_run["interval_days"], LADDER[-1])

try:
    review(item(), "nailed it")
    check("an unknown outcome is refused", "no error", "ValueError")
except ValueError:
    check("an unknown outcome is refused", "ValueError", "ValueError")

# A row straight from the database, with None where a default belongs.
raw = review({"repetitions": None, "ease": None, "interval_days": None}, "got")
check("a row with empty columns still schedules", raw["interval_days"], 1)
close("...from the starting ease", raw["ease"], EASE_START + 0.10)

# ── the daily cap ───────────────────────────────────────────────────────────
few = [{"id": i} for i in range(5)]
shown, total = cap_queue(few)
check("a short queue is shown whole", (len(shown), total), (5, 5))

many = [{"id": i} for i in range(47)]
shown, total = cap_queue(many)
check("a long queue is capped", len(shown), DAILY_CAP)
check("...but still counts what it is holding", total, 47)

# With a priority function the cap keeps the ones worth doing, so the queue and
# the Phase 4 prescriptions do not disagree about what matters.
scored = [{"id": i, "score": i} for i in range(47)]
shown, _ = cap_queue(scored, priority_of=lambda it: it["score"])
check("the cap keeps the highest priority items",
      [it["id"] for it in shown[:3]], [46, 45, 44])
check("...and drops the lowest", min(it["id"] for it in shown), 27)

check("an empty queue says what to do about it",
      "Log a paper" in queue_message(0, 0), True)
check("a queue inside the cap says how many", queue_message(5, 5), "5 due today.")
check("a capped queue says the rest will keep",
      queue_message(20, 47), "20 of 47 due — the rest will keep.")

print()
print("ALL PASS" if not FAILS else f"FAILURES ({len(FAILS)}): {FAILS}")
sys.exit(1 if FAILS else 0)
