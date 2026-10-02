"""The release: ranking a cohort, and refusing to rank one that is too small.

This suite exists because the first National Mock drew nobody. The release
script ran clean against production and had nothing to rank, which proves only
that it does not crash on an empty table — so the ranking path, the ties, the
suppression threshold and the idempotency all have to be proved against a
cohort built here.

It builds its own event (`nm-w4-test`), its own paper, and twenty-four users
with deliberate ties, two opt-outs, one empty attempt and one re-sit. It never
touches `nm1`: that row is the live event, and a suite that mutated it would be
repeating exactly the mistake found in test_exam_attempts yesterday, where a
fixture reached for a real content row and silently re-priced the launch paper.

Everything is removed in the finally block, including the event rows, which
`purge_user` cannot reach because mock_event_paper_stats has no user_id.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

os.environ.pop("CANONICAL_HOST", None)

import nationalmock as NM  # noqa: E402
from db import get_db  # noqa: E402
from _fixtures import purge_user  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import national_mock_release as REL  # noqa: E402

SLUG = "nm-w4-test"
CODE = "TEST-W4"
EMAILS = [f"w4-{i:02d}@telos.test" for i in range(24)]
fails = []


def check(label, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + label + f": {got!r}"
          + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


# The cohort. Index -> raw mark, chosen so the interesting cases all appear:
#
#   three tied on 19   -> all rank 1, next distinct score is rank 4
#   two tied on 17     -> rank 4
#   a long middle      -> ordinary ranks
#   two tied on 3      -> joint last
#
# Twenty-two of the twenty-four opt in, which clears a threshold of 20 by two.
# The two who opt out must not appear in anybody's denominator.
MARKS = [19, 19, 19, 17, 17, 16, 15, 14, 14, 13, 12, 11,
         10, 9, 8, 7, 6, 5, 4, 4, 3, 3, 18, 2]
OPTED_OUT = {22, 23}          # the 18 and the 2 — both outside the cohort
EMPTY_FIRST = 5               # this user's first attempt has no answers
RESAT = 6                     # this user sits it twice; the first must count

event_id = paper_id = None
user_ids = {}

try:
    with get_db() as db:
        # ── the event ───────────────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        # Already closed, so the release script's "window still open" guard is
        # satisfied without --force. The guard itself is tested separately.
        w_start = now - timedelta(hours=14)
        w_end = now - timedelta(hours=2)
        db.execute("DELETE FROM mock_events WHERE slug=?", (SLUG,))
        event_id = db.execute(
            "INSERT INTO mock_events (slug, title, window_start, window_end, "
            "  paper_codes, min_cohort, results_due_at) "
            "VALUES (?,?,?,?,?,?,?) RETURNING id",
            (SLUG, "W4 Test Mock", w_start, w_end, [CODE], 20,
             now + timedelta(hours=6))).fetchone()["id"]

        # ── the paper ───────────────────────────────────────────────────────
        db.execute("DELETE FROM exam_papers WHERE paper_code=?", (CODE,))
        paper_id = db.execute(
            "INSERT INTO exam_papers (paper_code, family, module, title, "
            "  duration_sec, question_count, is_published, family_marks, "
            "  price_pence) "
            "VALUES (?,'TMUA','P1','W4 test paper',4500,20,TRUE,40,0) "
            "RETURNING id", (CODE,)).fetchone()["id"]
        qids = []
        for n in range(1, 21):
            qids.append(db.execute(
                "INSERT INTO exam_questions (paper_id, n, topic, spec_refs, "
                "  stem_html, options, answer, traps) "
                "VALUES (?,?,?,?,?,?,?,?) RETURNING id",
                (paper_id, n, "T", ["MM1.1"], f"<p>q{n}</p>",
                 json.dumps({c: c for c in "ABCDEF"}), "C",
                 json.dumps({c: "x" for c in "ABDEF"}))).fetchone()["id"])

        # ── the sitters ─────────────────────────────────────────────────────
        def attempt(uid, raw, started, answers=True):
            aid = db.execute(
                "INSERT INTO exam_attempts (user_id, paper_id, started_at, "
                "  ends_at, submitted_at, status, raw, scaled) "
                "VALUES (?,?,?,?,?, 'submitted', ?, ?) RETURNING id",
                (uid, paper_id, started, started + timedelta(minutes=75),
                 started + timedelta(minutes=70), raw,
                 round(1 + 8 * raw / 20.0, 1))).fetchone()["id"]
            if answers:
                db.execute(
                    "INSERT INTO exam_responses (attempt_id, question_id, "
                    "  selected, time_sec) VALUES (?,?,?,?)",
                    (aid, qids[0], "C", 90))
            return aid

        for i, mark in enumerate(MARKS):
            purge_user(db, EMAILS[i])
            uid = db.execute(
                "INSERT INTO users (email, username, password_hash) "
                "VALUES (?,?,?) RETURNING id",
                (EMAILS[i], f"w4-{i:02d}", "x")).fetchone()["id"]
            user_ids[i] = uid
            db.execute(
                "INSERT INTO mock_event_entries (event_id, user_id, source, "
                "  percentile_optin) VALUES (?,?,?,?)",
                (event_id, uid, "tt", i not in OPTED_OUT))

            base = w_start + timedelta(hours=1, minutes=i)
            if i == EMPTY_FIRST:
                # Opened and submitted with nothing on it, then sat it
                # properly. The empty one must be skipped in favour of the
                # real one rather than becoming this student's result.
                attempt(uid, 0, base, answers=False)
                attempt(uid, mark, base + timedelta(minutes=10))
            elif i == RESAT:
                # Sat it twice, better the second time. The FIRST must count —
                # best-of would rank the people who sat it twice above the
                # people who sat it once.
                attempt(uid, mark, base)
                attempt(uid, 20, base + timedelta(hours=2))
            else:
                attempt(uid, mark, base)

    # ── the release ─────────────────────────────────────────────────────────
    rc = REL.release(SLUG, apply=False, force=False)
    check("a dry run succeeds", rc, 0)
    with get_db() as db:
        n = db.execute("SELECT COUNT(*) AS n FROM mock_event_results "
                       "WHERE event_id=?", (event_id,)).fetchone()["n"]
    check("and writes nothing at all", n, 0)

    rc = REL.release(SLUG, apply=True, force=False)
    check("publishing succeeds", rc, 0)

    with get_db() as db:
        rows = {r["user_id"]: r for r in db.execute(
            "SELECT * FROM mock_event_results WHERE event_id=?",
            (event_id,)).fetchall()}
        stats = db.execute(
            "SELECT * FROM mock_event_paper_stats WHERE event_id=?",
            (event_id,)).fetchone()
        ev = db.execute("SELECT results_released_at FROM mock_events WHERE id=?",
                        (event_id,)).fetchone()

    check("every sitter got a result row", len(rows), 24)
    check("the event is stamped as released",
          ev["results_released_at"] is not None, True)

    # ── the cohort, and who is in it ────────────────────────────────────────
    check("the cohort counts only those who opted in", stats["cohort"], 22)
    check("but everyone who sat it is a sitter", stats["sitters"], 24)
    check("so percentiles were published", bool(stats["published"]), True)

    out = rows[user_ids[22]]
    check("an opt-out is recorded as outside the cohort",
          bool(out["in_cohort"]), False)
    check("with no rank", out["rank"], None)
    check("and no percentile", out["percentile"], None)
    # The 18 belongs to an opt-out. If it had leaked into the cohort it would
    # have pushed the three 19s down and changed every rank below it.
    check("but their mark is still theirs", out["raw"], 18)

    # ── ranks and ties ──────────────────────────────────────────────────────
    top = [rows[user_ids[i]] for i in (0, 1, 2)]
    check("three tied at the top all rank first",
          sorted(r["rank"] for r in top), [1, 1, 1])
    check("and share one percentile",
          len({r["percentile"] for r in top}), 1)
    # 19 of 22 scored strictly lower than 19 (the two 17s, and everyone below).
    check("which is the share who scored lower",
          top[0]["percentile"], int(round(100.0 * 19 / 22)))

    pair = [rows[user_ids[i]] for i in (3, 4)]
    check("the next distinct score skips the ranks used up",
          sorted(r["rank"] for r in pair), [4, 4])

    bottom = [rows[user_ids[i]] for i in (20, 21)]
    check("joint last share the last rank",
          sorted(r["rank"] for r in bottom), [21, 21])
    check("and the lowest score beats nobody", bottom[0]["percentile"], 0)

    check("the cohort size travels with the rank",
          rows[user_ids[0]]["cohort_size"], 22)

    # ── which sitting counted ───────────────────────────────────────────────
    check("an empty attempt is skipped for the real one that follows",
          rows[user_ids[EMPTY_FIRST]]["raw"], MARKS[EMPTY_FIRST])
    # The first sitting, not the better second one. This is the rule the whole
    # cohort claim rests on.
    check("a re-sit does not replace the first sitting",
          rows[user_ids[RESAT]]["raw"], MARKS[RESAT])

    # ── the spread ──────────────────────────────────────────────────────────
    check("the maximum is across all sitters", stats["raw_max"], 19)
    check("and the minimum too", stats["raw_min"], 2)
    check("the median is the middle of the sitters",
          float(stats["raw_median"]), NM.median(MARKS))

    # ── idempotency ─────────────────────────────────────────────────────────
    rc = REL.release(SLUG, apply=True, force=False)
    check("re-releasing without --force is refused", rc, 1)

    rc = REL.release(SLUG, apply=True, force=True)
    check("but --force recomputes", rc, 0)
    with get_db() as db:
        n = db.execute("SELECT COUNT(*) AS n FROM mock_event_results "
                       "WHERE event_id=?", (event_id,)).fetchone()["n"]
        again = db.execute(
            "SELECT rank, percentile FROM mock_event_results "
            "WHERE event_id=? AND user_id=?",
            (event_id, user_ids[0])).fetchone()
    check("without duplicating a single row", n, 24)
    check("and the ranks are unchanged", (again["rank"], again["percentile"]),
          (1, int(round(100.0 * 19 / 22))))

    # ── suppression ─────────────────────────────────────────────────────────
    # The same data, judged against a threshold the cohort cannot meet. This is
    # the branch that mattered for nm1 and the one the empty production run
    # could not exercise.
    with get_db() as db:
        db.execute("UPDATE mock_events SET min_cohort=25 WHERE id=?", (event_id,))
    REL.release(SLUG, apply=True, force=True)
    with get_db() as db:
        stats = db.execute(
            "SELECT * FROM mock_event_paper_stats WHERE event_id=?",
            (event_id,)).fetchone()
        r = db.execute("SELECT * FROM mock_event_results "
                       "WHERE event_id=? AND user_id=?",
                       (event_id, user_ids[0])).fetchone()
    check("below the threshold the paper publishes nothing",
          bool(stats["published"]), False)
    check("so the top scorer has no rank", r["rank"], None)
    check("and no percentile", r["percentile"], None)
    # The point of suppressing a rank rather than a result.
    check("but their mark survives", r["raw"], 19)
    check("and so does their band", r["scaled"] is not None, True)
    check("and the cohort is still counted honestly", stats["cohort"], 22)

    # ── the guard on an open window ─────────────────────────────────────────
    with get_db() as db:
        db.execute("UPDATE mock_events SET min_cohort=20, "
                   "  window_end = NOW() + INTERVAL '3 hours', "
                   "  results_released_at = NULL WHERE id=?", (event_id,))
    rc = REL.release(SLUG, apply=True, force=False)
    check("releasing while the window is open is refused", rc, 1)
    with get_db() as db:
        ev = db.execute("SELECT results_released_at FROM mock_events "
                        "WHERE id=?", (event_id,)).fetchone()
    check("and the event is left unstamped",
          ev["results_released_at"] is None, True)

finally:
    with get_db() as db:
        if event_id:
            db.execute("DELETE FROM mock_event_results WHERE event_id=?",
                       (event_id,))
            db.execute("DELETE FROM mock_event_paper_stats WHERE event_id=?",
                       (event_id,))
            db.execute("DELETE FROM mock_event_entries WHERE event_id=?",
                       (event_id,))
        for email in EMAILS:
            purge_user(db, email)
        if paper_id:
            db.execute("DELETE FROM exam_responses WHERE attempt_id IN "
                       "(SELECT id FROM exam_attempts WHERE paper_id=?)",
                       (paper_id,))
            db.execute("DELETE FROM exam_attempts WHERE paper_id=?", (paper_id,))
            db.execute("DELETE FROM exam_questions WHERE paper_id=?", (paper_id,))
            db.execute("DELETE FROM exam_papers WHERE id=?", (paper_id,))
        if event_id:
            db.execute("DELETE FROM mock_events WHERE id=?", (event_id,))
    print("cleaned up")

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
