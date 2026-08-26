"""Unit tests for the prescription engine — "your next 3 questions".

Pure functions, no database, no Flask — runnable with
`python tests/test_prescription.py`.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prescription import (  # noqa: E402
    RECENCY_BOOST, WEAK_THRESHOLD, prescribe, priority, rank_topics,
    topic_stats, why_line,
)

# Marks that sit exactly on the redo cutoff, out of ten. Written in terms of
# WEAK_THRESHOLD rather than as a number, because a fixture that hardcodes the
# old cutoff turns into a silent behaviour change the day the cutoff moves —
# which is exactly what happened when it went from 60% to 75%.
AT_LINE = WEAK_THRESHOLD * 10

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


def mark(topic, got, mx, paper_id=1, q_num="1", year="2023", code="CP1"):
    return {"topic": topic, "obtained": got, "max_marks": mx, "paper_id": paper_id,
            "q_num": q_num, "year": year, "paper_code": code,
            "board": "Edexcel", "subject": "Further Maths"}


# ── topic aggregation ───────────────────────────────────────────────────────

agg = topic_stats([
    mark("Complex Numbers", 2, 10, paper_id=1, q_num="1"),
    mark("Complex Numbers", 3, 10, paper_id=2, q_num="4"),
    mark("Matrices", 9, 10, paper_id=1, q_num="2"),
    mark("", 5, 10, paper_id=1, q_num="3"),          # untagged -> skipped
    mark(None, 5, 10, paper_id=1, q_num="9"),        # untagged -> skipped
])
check("untagged questions are skipped", sorted(agg.keys()), ["Complex Numbers", "Matrices"])
check("marks summed across papers", agg["Complex Numbers"]["got"], 5.0)
check("frequency counts distinct papers", len(agg["Complex Numbers"]["papers"]), 2)

# A zero-max question can't be scored against and must not divide by zero.
check("zero-max rows ignored", "Nothing" in topic_stats([mark("Nothing", 0, 0)]), False)


# ── the priority formula ────────────────────────────────────────────────────

close("priority = lost x log(1+freq) x recency",
      priority(0.5, 3, 1.0), 0.5 * math.log(4))
check("recency boost multiplies", priority(0.5, 3, RECENCY_BOOST) > priority(0.5, 3, 1.0), True)

# The headline claim of the design: a frequent mid-weak topic outranks a rare
# catastrophic one. Being at 30% on something worth 3 marks a year matters less
# than 65% on something worth 15.
rare_disaster = priority(0.70, 1, 1.0)      # 30% accuracy, seen in 1 paper
common_weak = priority(0.35, 8, 1.0)        # 65% accuracy, seen in 8 papers
check("frequent weak topic outranks rare disaster", common_weak > rare_disaster, True)


# ── ranking ─────────────────────────────────────────────────────────────────

MARKS = []
# Complex Numbers: bad and everywhere -> should rank first
for i in range(1, 5):
    MARKS.append(mark("Complex Numbers", 3, 10, paper_id=i, q_num="1"))
# Matrices: strong, everywhere -> should not be prescribed
for i in range(1, 5):
    MARKS.append(mark("Matrices", 9, 10, paper_id=i, q_num="2"))
# Proof: bad but seen once
MARKS.append(mark("Proof", 1, 10, paper_id=1, q_num="3"))
# Vectors: middling, twice
MARKS.append(mark("Vectors", 5, 10, paper_id=1, q_num="4"))
MARKS.append(mark("Vectors", 5, 10, paper_id=2, q_num="4"))

ranked = rank_topics(MARKS, recent_paper_ids=[])
check("returns at most 3 topics", len(ranked), 3)
check("weakest frequent topic ranks first", ranked[0]["topic"], "Complex Numbers")
check("strong topic is not prescribed", "Matrices" in [t["topic"] for t in ranked], False)
check("accuracy reported as a percent", ranked[0]["pct"], 30)
check("frequency is distinct papers", ranked[0]["frequency"], 4)
close("marks lost per paper", ranked[0]["marks_lost_per_paper"], 7.0)

# Recency: the same topic scores higher when it appeared in a recent paper.
cold = rank_topics(MARKS, recent_paper_ids=[])[0]["priority"]
warm = rank_topics(MARKS, recent_paper_ids=[1, 2, 3])[0]["priority"]
check("recent topics are boosted", warm > cold, True)
close("boost is exactly the recency factor", warm, cold * RECENCY_BOOST, tol=0.001)

# Ranking must be stable — a Today panel that reshuffles on refresh reads as noise.
check("ranking is stable across runs",
      [t["topic"] for t in rank_topics(MARKS)] == [t["topic"] for t in rank_topics(MARKS)], True)


# ── the "why" line ──────────────────────────────────────────────────────────

why = why_line(ranked[0])
check("why names the topic", "Complex Numbers" in why, True)
check("why gives the accuracy", "30%" in why, True)
check("why gives the per-paper cost", "7 marks/paper" in why, True)


# ── selection ───────────────────────────────────────────────────────────────

# No bank at all: everything must come from redoing weak logged questions.
res = prescribe(MARKS, bank=[], recent_paper_ids=[1])
check("prescribes with an empty bank", res["ready"], True)
check("returns three picks", len(res["picks"]), 3)
check("all picks are redos when the bank is empty",
      {p["kind"] for p in res["picks"]}, {"redo"})
check("every pick carries a why", all(p["why"] for p in res["picks"]), True)
check("picks spread across topics",
      len({p["topic"] for p in res["picks"]}), 3)
check("redo picks name the source paper", res["picks"][0]["source"], "2023 CP1 Q1")

# A ranked topic with nothing prescribable is skipped, not padded out — the
# remaining slots go to topics that do have a question behind them.
mixed = [
    mark("Complex Numbers", 2, 10, paper_id=1, q_num="1"),
    mark("Complex Numbers", 2, 10, paper_id=2, q_num="1"),
    mark("Proof", 1, 10, paper_id=1, q_num="3"),
    # Exactly at the cutoff, derived so this fixture does not silently become
    # a weak question the next time the threshold moves.
    mark("Vectors", AT_LINE, 10, paper_id=1, q_num="4"),
    mark("Vectors", AT_LINE, 10, paper_id=2, q_num="4"),
]
res_mixed = prescribe(mixed, bank=[])
check("a topic with no weak question contributes no pick",
      "Vectors" in {p["topic"] for p in res_mixed["picks"]}, False)
check("...and the slot goes to a topic that has one",
      len(res_mixed["picks"]), 3)

# A question already above the threshold is not worth redoing.
# 90%: comfortably above the cutoff, but not perfect — a topic with nothing
# at all to gain ranks out entirely, which would test something else.
strong = [mark("Vectors", 9, 10, paper_id=1, q_num="4")]
res_strong = prescribe(strong, bank=[])
check("nothing prescribed when every question is strong", res_strong["ready"], False)
check("...and it says why", res_strong["reason"], "no_questions")
check("...but the topic ranking still comes back", len(res_strong["topics"]) > 0, True)

# Exactly at the threshold is not weak — the cutoff is inclusive.
at_line = [mark("Vectors", AT_LINE, 10, paper_id=1, q_num="4")]
check(f"{int(WEAK_THRESHOLD*100)}% exactly is not prescribed as a redo",
      prescribe(at_line, bank=[])["ready"], False)

# With a bank, unattempted questions win over redos.
BANK = [
    {"id": 101, "q_num": "7", "topics": ["Complex Numbers"], "max_marks": 12,
     "upload_id": 5, "year": "2021", "paper_code": "CP1"},
    {"id": 102, "q_num": "8", "topics": ["Complex Numbers"], "max_marks": 4,
     "upload_id": 5, "year": "2021", "paper_code": "CP1"},
]
res_bank = prescribe(MARKS, bank=BANK, recent_paper_ids=[1])
check("bank question is preferred over a redo", res_bank["picks"][0]["kind"], "new")
check("biggest bank question first", res_bank["picks"][0]["q_num"], "7")
check("bank pick names its source", res_bank["picks"][0]["source"], "2021 CP1 Q7")
check("topics without bank cover still fall back to redo",
      "redo" in {p["kind"] for p in res_bank["picks"]}, True)

# Topic matching is case- and whitespace-insensitive; tags are typed by hand.
sloppy = [{"id": 201, "q_num": "3", "topics": ["  complex NUMBERS "], "max_marks": 9,
           "upload_id": 5, "year": "2021", "paper_code": "CP2"}]
check("bank topic match ignores case and padding",
      prescribe(MARKS, bank=sloppy)["picks"][0]["kind"], "new")

# A bank question for a paper/question the user already logged is not "new".
already = [{"id": 301, "q_num": "1", "topics": ["Complex Numbers"], "max_marks": 10,
            "upload_id": 5, "year": "2023", "paper_code": "CP1"}]
check("already-attempted bank questions are not offered as new",
      prescribe(MARKS, bank=already)["picks"][0]["kind"], "redo")

# No usable data at all.
empty = prescribe([], bank=[])
check("no topics is a stated state, not a crash", empty["ready"], False)
check("...with a reason", empty["reason"], "no_topics")
check("...and a message for the panel", bool(empty["message"]), True)

# The engine must never hand back more than asked for.
check("limit is respected", len(prescribe(MARKS, bank=BANK, limit=2)["picks"]), 2)
check("a single pick is possible", len(prescribe(MARKS, bank=BANK, limit=1)["picks"]), 1)


print()
print("ALL PASS" if not FAILS else f"FAILURES ({len(FAILS)}): {FAILS}")
sys.exit(1 if FAILS else 0)
