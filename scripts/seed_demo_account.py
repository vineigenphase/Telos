"""Seed the `telos` demo account — a realistic student, for filming.

Every screen in Telos is empty until somebody has done the work, so recording a
walkthrough needs an account with a term's worth of marks already in it. This
builds one: three A-levels, papers spread over ten weeks, and every paper
marked question by question, because per-question marks are what the heatmap,
the prescriptions and the revision queue all run on. A demo account with only
paper totals would show blank versions of the three screens worth filming.

Deterministic. The random seed is fixed, so re-running produces exactly the
same account — a retake looks identical to the take before it, and a number
quoted in voiceover does not change under you.

Idempotent. It deletes the demo account's own data first, so it can be run
between takes to reset. It touches nothing belonging to any other user.

    railway run .venv\\Scripts\\python.exe scripts\\seed_demo_account.py

The password is generated, printed once, and never written to the repository.
Pass --password to set your own.
"""

from __future__ import annotations

import argparse
import datetime
import os
import random
import secrets
import string
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db  # noqa: E402
from paper_templates import TEMPLATES  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

EMAIL = "fastachievers1@gmail.com"
USERNAME = "telos"

# Fixed so every run is identical. A demo that reshuffles between takes is a
# demo you cannot cut together.
SEED = 20260910

# The three subjects, which are also the three tutored on the landing page.
SUBJECTS = [
    ("Edexcel", "Further Maths", "A-Level"),
    ("Edexcel", "Maths", "A-Level"),
    ("OCR A", "Physics", "A-Level"),
]

# The story the data tells: a strong student who is losing marks in a few
# specific places, improving over the ten weeks. That is what makes the
# prescription and trend screens say something rather than shrug.
#
# These topics stay weak throughout. Real weakness is persistent — a student
# who is bad at complex numbers is bad at them in October and in December — and
# a heatmap where the red moves randomly week to week is a heatmap nobody can
# act on.
WEAK = {
    "Further Maths": ["Further Differential Equations", "Groups", "Polar Coordinates"],
    "Maths": ["Numerical Methods", "Hypothesis Testing", "Moments"],
    "Physics": ["Capacitance", "Nuclear Physics", "Uncertainty & Error Analysis"],
}

# Papers to log per subject, oldest first. Chosen so each subject clears the
# three-paper minimum the prediction engine needs, with enough history for the
# week-on-week deltas to have something to compare.
PLAN = {
    "Further Maths": [("CP1", "2022"), ("CP1", "2023"), ("CP2", "2022"),
                      ("FP1", "2023"), ("CP2", "2023"), ("CP1", "2024"),
                      ("FP1", "2024"), ("CP2", "2024")],
    "Maths": [("Pure 1", "2022"), ("Pure 2", "2022"), ("Stats&Mech", "2022"),
              ("Pure 1", "2023"), ("Pure 2", "2023"), ("Pure 1", "2024")],
    "Physics": [("Paper 1", "2022"), ("Paper 2", "2022"), ("Paper 1", "2023"),
                ("Paper 3", "2023"), ("Paper 2", "2023"), ("Paper 1", "2024")],
}


def password():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(16))


def question_shape(rng, max_marks):
    """Split a paper into questions that look like a real paper.

    Real papers open with short questions and end with long ones, so a flat
    split of equal marks would look wrong to anyone who has sat one — and the
    per-question screen is the thing being filmed.
    """
    qs, remaining, n = [], max_marks, 1
    while remaining > 0:
        if remaining <= 14:
            qs.append(remaining)
            break
        # Early questions short, later ones longer.
        lo, hi = (2, 6) if n <= 3 else (4, 10) if n <= 7 else (6, 14)
        m = min(rng.randint(lo, hi), remaining - 2)
        qs.append(m)
        remaining -= m
        n += 1
    return qs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--password", help="set a specific password instead of generating one")
    ap.add_argument("--keep", action="store_true",
                    help="keep the existing password if the account already exists")
    args = ap.parse_args(argv)

    rng = random.Random(SEED)
    today = datetime.date.today()
    pw = args.password or password()

    with get_db() as db:
        existing = db.execute("SELECT id FROM users WHERE email=?", (EMAIL,)).fetchone()

        if existing:
            uid = existing["id"]
            # Wipe only this account's own data, so the script can be run
            # between takes. Nothing here reaches another user's rows.
            db.execute("DELETE FROM question_marks WHERE paper_id IN "
                       "(SELECT id FROM papers WHERE user_id=?)", (uid,))
            db.execute("DELETE FROM papers WHERE user_id=?", (uid,))
            db.execute("DELETE FROM grade_predictions WHERE user_id=?", (uid,))
            db.execute("DELETE FROM grade_prediction_history WHERE user_id=?", (uid,))
            db.execute("DELETE FROM revision_queue WHERE user_id=?", (uid,))
            db.execute("DELETE FROM user_subjects WHERE user_id=?", (uid,))
            db.execute("DELETE FROM user_papers WHERE user_id=?", (uid,))
            if not args.keep:
                db.execute("UPDATE users SET password_hash=? WHERE id=?",
                           (generate_password_hash(pw), uid))
            print(f"reset the existing demo account (user {uid})")
        else:
            uid = db.execute(
                "INSERT INTO users (email, username, password_hash, plan, grandfathered) "
                "VALUES (?,?,?,'pro',TRUE) RETURNING id",
                (EMAIL, USERNAME, generate_password_hash(pw))).fetchone()["id"]
            print(f"created the demo account (user {uid})")

        # Pro without Stripe. grandfathered is the existing mechanism for an
        # account that should have everything without a subscription, and it
        # keeps the demo out of the billing data entirely.
        db.execute("UPDATE users SET grandfathered=TRUE, plan='pro', "
                   "username=?, exam_date=? WHERE id=?",
                   (USERNAME, today + datetime.timedelta(days=68), uid))

        for board, subject, level in SUBJECTS:
            db.execute("INSERT INTO user_subjects (user_id, board, subject, level) "
                       "VALUES (?,?,?,?) ON CONFLICT DO NOTHING",
                       (uid, board, subject, level))

        total_papers = total_qs = 0

        for board, subject, _level in SUBJECTS:
            cfg = TEMPLATES[board][subject]
            by_code = {p["code"]: p for p in cfg["papers"]}
            weak = set(WEAK[subject])
            plan = PLAN[subject]

            for i, (code, year) in enumerate(plan):
                paper = by_code[code]
                max_marks = paper["max_marks"]
                topics = cfg.get("topics", {}).get(code) or ["General"]

                # Oldest paper ten weeks ago, most recent three days ago, so
                # the trend windows have both halves and the dashboard's
                # "this week" figures are not empty.
                days_ago = int(70 - (i / max(1, len(plan) - 1)) * 67)
                sat = today - datetime.timedelta(days=days_ago)

                # Improving across the run: about 68% early, about 88% late.
                # Strong enough to be predicted an A/A*, with room to show
                # marks-to-next-grade rather than a ceiling.
                base = 0.68 + 0.20 * (i / max(1, len(plan) - 1))

                shape = question_shape(rng, max_marks)
                marks, score = [], 0
                for qi, q_max in enumerate(shape):
                    topic = topics[qi % len(topics)]
                    # A weak topic costs marks consistently. This is what makes
                    # the heatmap and the "your next 3 questions" screen show
                    # something a viewer can follow.
                    rate = base - 0.30 if topic in weak else base + 0.04
                    rate = max(0.15, min(rate + rng.uniform(-0.10, 0.10), 1.0))
                    got = max(0, min(round(q_max * rate), q_max))
                    marks.append((str(qi + 1), got, q_max, topic))
                    score += got

                pid = db.execute(
                    "INSERT INTO papers (user_id, subject, board, paper_code, year, "
                    "  series, score, max_marks, date_completed, time_taken, "
                    "  weak_topics, notes) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?) RETURNING id",
                    (uid, subject, board, code, year, "June", score, max_marks,
                     sat.isoformat(), rng.randint(78, 122),
                     ", ".join(sorted(t for _, g, m, t in marks if g < m * 0.6)),
                     "")).fetchone()["id"]

                for q_num, got, q_max, topic in marks:
                    # created_at is set to the sitting date, not now, or every
                    # mark would land in this week's trend window and the
                    # dashboard would show ten weeks of work as one day of it.
                    db.execute(
                        "INSERT INTO question_marks (paper_id, q_num, obtained, "
                        "  max_marks, topic, created_at) VALUES (?,?,?,?,?,?)",
                        (pid, q_num, got, q_max, topic,
                         datetime.datetime.combine(sat, datetime.time(18, 30))))
                total_qs += len(marks)
                total_papers += 1

            print(f"  {subject:<14} {len(plan)} papers")

    # Predictions are cached, not computed on read, so they have to be built
    # after the marks exist or the dashboard shows nothing until the next save.
    import app as A
    A.recompute_predictions(uid)

    with get_db() as db:
        preds = db.execute(
            "SELECT subject, predicted_grade, confidence FROM grade_predictions "
            "WHERE user_id=? ORDER BY subject", (uid,)).fetchall()

    print(f"\n{total_papers} papers, {total_qs} question marks")
    for p in preds:
        print(f"  predicted {p['subject']:<14} {p['predicted_grade']}"
              f"  ({p['confidence']} confidence)")

    print("\n" + "=" * 60)
    print(f"  email     {EMAIL}")
    print(f"  username  {USERNAME}")
    if args.keep and existing:
        print("  password  unchanged")
    else:
        print(f"  password  {pw}")
        print("\n  Not written to the repository. Save it somewhere.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
