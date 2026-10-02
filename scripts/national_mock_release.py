"""Mark the National Mock cohort and publish the percentiles.

    # Look at what WOULD be published. Writes nothing. This is the default.
    railway run --service web .venv\\Scripts\\python.exe scripts\\national_mock_release.py

    # Actually publish.
    railway run --service web .venv\\Scripts\\python.exe scripts\\national_mock_release.py --publish

    # Recompute after an already-published release (a late attempt finalised,
    # or min_cohort changed).
    railway run --service web .venv\\Scripts\\python.exe scripts\\national_mock_release.py --publish --force

**Dry run is the default.** Publishing is the irreversible-feeling half of this
event — a student who is told they came 14th of 31 remembers that number — so
the script shows the whole table first and only writes when asked twice.

## The rules, stated because they are decisions and not derivations

**Which sitting counts: the FIRST completed attempt started inside the window,
that has at least one answer recorded.**

Not the best of several. The papers are locked until the window opens, so
everybody's first attempt is a genuine cold sitting, and that is the only thing
the cohort claim rests on. Taking the best of several would quietly rank the
people who sat it twice above the people who sat it once, which is not a
measure of anything. The "at least one answer" clause exists so that an
accidental open-and-submit does not become somebody's event result — a real
zero is kept, an empty attempt is skipped in favour of the next one.

**Ranked on raw marks, not the scaled band.** Everyone in a cohort sat the same
paper, so raw is directly comparable and far finer: the 1-9 scale would tie
most of the cohort together.

**Below min_cohort, a paper publishes no percentile at all.** The mark, the
band and the topic breakdown all still stand; only the position is withheld.
A rank among eleven people is noise presented as information, and the first
event's credibility is the whole asset.

**Only opted-in sitters form the cohort.** Someone who left the box unticked
still gets a result row — their mark is theirs — with a NULL rank, and they are
not counted in anyone else's denominator either.

**Stragglers are finalised, not ignored.** An attempt started at 21:55 runs on
its own clock past the window's end, and a student who closed the tab without
submitting would otherwise get nothing. Any overdue live attempt on an event
paper is marked through the same code path a real submit uses.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nationalmock  # noqa: E402
from db import get_db  # noqa: E402


def finalise_stragglers(db, event, apply):
    """Mark any overdue live attempt on an event paper. Returns how many.

    Uses exam._finalise, the same function a real submit goes through, rather
    than a hand-written UPDATE here. Two code paths that both mark a paper is
    how two students sitting the same paper end up scored differently.
    """
    import exam

    rows = db.execute(
        "SELECT a.id FROM exam_attempts a JOIN exam_papers p ON p.id=a.paper_id "
        "WHERE a.status='live' AND a.ends_at < NOW() "
        "  AND p.paper_code = ANY(?) "
        "  AND a.started_at >= ? AND a.started_at < ?",
        (list(event["paper_codes"]), event["window_start"],
         event["window_end"])).fetchall()
    if not apply:
        return len(rows)
    done = 0
    for r in rows:
        attempt = db.execute(
            "SELECT a.*, p.paper_code, p.family, p.module, p.family_marks "
            "FROM exam_attempts a JOIN exam_papers p ON p.id=a.paper_id "
            "WHERE a.id=?", (r["id"],)).fetchone()
        exam._finalise(db, attempt, expired=True)
        done += 1
    return done


def sittings(db, event, paper_id):
    """The one attempt per user that counts, for one paper.

    The window filter is on started_at: a paper begun at 21:55 and submitted at
    23:20 was begun inside the window, which is what the rules promised. The
    clock was always going to run past the close for anyone starting late.
    """
    rows = db.execute(
        "SELECT a.id AS attempt_id, a.user_id, a.raw, a.scaled, a.started_at, "
        "       COALESCE(e.percentile_optin, FALSE) AS opted, "
        "       (SELECT COUNT(*) FROM exam_responses r "
        "         WHERE r.attempt_id = a.id) AS answers "
        "FROM exam_attempts a "
        "LEFT JOIN mock_event_entries e "
        "       ON e.user_id = a.user_id AND e.event_id = ? "
        "WHERE a.paper_id = ? AND a.status <> 'live' AND a.raw IS NOT NULL "
        "  AND a.started_at >= ? AND a.started_at < ? "
        # Oldest first, so the first row per user is the first sitting.
        "ORDER BY a.user_id, a.started_at, a.id",
        (event["id"], paper_id, event["window_start"],
         event["window_end"])).fetchall()

    counted, skipped_empty = {}, 0
    for r in rows:
        if r["user_id"] in counted:
            continue
        if not r["answers"]:
            # An accidental open-and-submit. Skipped so the NEXT attempt by
            # this user can count — hence no entry in `counted` yet.
            skipped_empty += 1
            continue
        counted[r["user_id"]] = r
    return list(counted.values()), skipped_empty


def release(slug, apply, force):
    with get_db() as db:
        event = db.execute(
            "SELECT *, window_end AT TIME ZONE 'Europe/London' AS end_local "
            "FROM mock_events WHERE slug=?", (slug,)).fetchone()
        if not event:
            print(f"no event with slug {slug!r}")
            return 1

        if event["results_released_at"] and not force:
            print(f"{slug} was already released at {event['results_released_at']}.")
            print("Pass --force to recompute. Ranks already told to students "
                  "may change, so say so if they do.")
            return 1

        from datetime import datetime, timezone
        if datetime.now(timezone.utc) < event["window_end"] and not force:
            print(f"the window is still open — it closes "
                  f"{nationalmock.fmt_when(event['end_local'])}.")
            print("Releasing now would rank a cohort that is still growing. "
                  "Pass --force only if you have decided to close early.")
            return 1

        straggler_count = finalise_stragglers(db, event, apply)
        if straggler_count:
            print(f"{'finalised' if apply else 'would finalise'} "
                  f"{straggler_count} attempt(s) left live past their clock")
            print()

        papers = db.execute(
            "SELECT id, paper_code, title, question_count FROM exam_papers "
            "WHERE paper_code = ANY(?) ORDER BY paper_code",
            (list(event["paper_codes"]),)).fetchall()

        min_cohort = event["min_cohort"]
        print(f"{event['title']} — {'PUBLISHING' if apply else 'DRY RUN'}")
        print(f"threshold: {min_cohort} opted-in sitters per paper")
        print()

        total_rows, published_papers = 0, 0
        for paper in papers:
            counted, skipped = sittings(db, event, paper["id"])
            cohort = [r for r in counted if r["opted"]]
            publish = nationalmock.percentiles_ok(len(cohort), min_cohort)
            ranks = (nationalmock.cohort_ranks(
                        [(r["user_id"], r["raw"]) for r in cohort])
                     if publish else {})

            raws = [r["raw"] for r in counted]
            print(f"{paper['paper_code']}  ({paper['title']})")
            print(f"  sat: {len(counted)}   in cohort: {len(cohort)}   "
                  f"percentiles: {'YES' if publish else 'no'}"
                  + ("" if publish else
                     f" (needs {min_cohort - len(cohort)} more)"))
            if skipped:
                print(f"  skipped {skipped} empty attempt(s) before a real one")
            if raws:
                print(f"  raw out of {paper['question_count']}: "
                      f"min {min(raws)}, median {nationalmock.median(raws)}, "
                      f"max {max(raws)}, mean "
                      f"{sum(raws) / len(raws):.2f}")
            if publish:
                published_papers += 1
                top = sorted(cohort, key=lambda r: -r["raw"])[:3]
                print("  top of the cohort: "
                      + ", ".join(f"{r['raw']} (rank {ranks[r['user_id']][0]})"
                                  for r in top))

            if apply:
                for r in counted:
                    rank, pct = ranks.get(r["user_id"], (None, None))
                    db.execute(
                        "INSERT INTO mock_event_results "
                        "  (event_id, paper_id, user_id, attempt_id, raw, "
                        "   scaled, rank, percentile, cohort_size, in_cohort) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?) "
                        "ON CONFLICT (event_id, paper_id, user_id) DO UPDATE SET "
                        "  attempt_id=EXCLUDED.attempt_id, raw=EXCLUDED.raw, "
                        "  scaled=EXCLUDED.scaled, rank=EXCLUDED.rank, "
                        "  percentile=EXCLUDED.percentile, "
                        "  cohort_size=EXCLUDED.cohort_size, "
                        "  in_cohort=EXCLUDED.in_cohort, computed_at=NOW()",
                        (event["id"], paper["id"], r["user_id"],
                         r["attempt_id"], r["raw"], r["scaled"], rank, pct,
                         len(cohort), bool(r["opted"])))
                    total_rows += 1
                db.execute(
                    "INSERT INTO mock_event_paper_stats "
                    "  (event_id, paper_id, sitters, cohort, published, "
                    "   raw_max, raw_min, raw_mean, raw_median) "
                    "VALUES (?,?,?,?,?,?,?,?,?) "
                    "ON CONFLICT (event_id, paper_id) DO UPDATE SET "
                    "  sitters=EXCLUDED.sitters, cohort=EXCLUDED.cohort, "
                    "  published=EXCLUDED.published, raw_max=EXCLUDED.raw_max, "
                    "  raw_min=EXCLUDED.raw_min, raw_mean=EXCLUDED.raw_mean, "
                    "  raw_median=EXCLUDED.raw_median, computed_at=NOW()",
                    (event["id"], paper["id"], len(counted), len(cohort),
                     publish, max(raws) if raws else None,
                     min(raws) if raws else None,
                     (sum(raws) / len(raws)) if raws else None,
                     nationalmock.median(raws)))
            print()

        if apply:
            # Stamped last, and only once every paper is written, so the page
            # never says "your result is ready" over a half-filled table.
            db.execute("UPDATE mock_events SET results_released_at=NOW() "
                       "WHERE id=?", (event["id"],))
            print(f"published: {total_rows} result row(s) across "
                  f"{len(papers)} paper(s); {published_papers} with "
                  f"percentiles. results_released_at stamped.")
        else:
            print(f"dry run — nothing written. {published_papers} of "
                  f"{len(papers)} paper(s) would publish percentiles.")
            print("Re-run with --publish when the numbers look right.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--event", default=os.environ.get("NM_SLUG", "nm1"))
    ap.add_argument("--publish", action="store_true",
                    help="actually write. Without this, nothing is written.")
    ap.add_argument("--force", action="store_true",
                    help="recompute an already-released event, or release "
                         "before the window has closed.")
    args = ap.parse_args()
    return release(args.event, args.publish, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
