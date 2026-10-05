"""Move a National Mock's window, without a deploy.

    # Show the current window and go no further.
    railway run --service web .venv\\Scripts\\python.exe scripts\\nm_set_window.py

    # Move it. Local UK dates and times; the conversion to UTC is done by
    # Postgres, which is the only thing on this machine with a time-zone
    # database.
    railway run --service web .venv\\Scripts\\python.exe scripts\\nm_set_window.py \\
        --date 2026-10-10 --open 10:00 --close 22:00 --results 2026-10-11T08:00

This exists because the window is a row rather than a constant, and that was
the right call: it has now moved twice. Both the public countdown and the lock
on the papers read it, so they can never disagree, and neither needs a restart
to notice.

Times are entered in **Europe/London** and stored in UTC. That is where an
hour gets lost if anyone does the arithmetic by hand — the launch window sits
inside BST — so the conversion is handed to Postgres and the result is read
back and printed in both zones for checking.

Clearing `results_released_at` is deliberate and automatic: a window that has
moved describes an event that has not happened yet, and leaving the stamp in
place would have the page announcing results for a sitting still in the future.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nationalmock  # noqa: E402
from db import get_db  # noqa: E402


def show(db, slug):
    row = db.execute(
        "SELECT slug, title, min_cohort, "
        "       window_start AT TIME ZONE 'Europe/London' AS opens, "
        "       window_end   AT TIME ZONE 'Europe/London' AS closes, "
        "       results_due_at AT TIME ZONE 'Europe/London' AS results, "
        "       window_start AS opens_utc, window_end AS closes_utc, "
        "       results_released_at, "
        "       (SELECT COUNT(*) FROM mock_event_entries e "
        "         WHERE e.event_id = mock_events.id) AS registered "
        "FROM mock_events WHERE slug=?", (slug,)).fetchone()
    if not row:
        print(f"no event with slug {slug!r}")
        return None
    print(f"{row['title']}  ({row['slug']})")
    print(f"  opens   {nationalmock.fmt_when(row['opens'])}"
          f"   [{row['opens_utc']:%Y-%m-%d %H:%M}Z]")
    print(f"  closes  {nationalmock.fmt_when(row['closes'])}"
          f"   [{row['closes_utc']:%Y-%m-%d %H:%M}Z]")
    print(f"  results {nationalmock.fmt_when(row['results'])}")
    print(f"  released: {row['results_released_at'] or 'not yet'}")
    print(f"  registered: {row['registered']}   threshold: {row['min_cohort']}")
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--event", default=os.environ.get("NM_SLUG", "nm1"))
    ap.add_argument("--date", help="window date, YYYY-MM-DD, UK local")
    ap.add_argument("--open", default="10:00", help="HH:MM UK local")
    ap.add_argument("--close", default="22:00", help="HH:MM UK local")
    ap.add_argument("--results", help="YYYY-MM-DDTHH:MM UK local")
    ap.add_argument("--min-cohort", type=int)
    args = ap.parse_args()

    with get_db() as db:
        print("before:")
        before = show(db, args.event)
        if not before:
            return 1
        if not args.date:
            print()
            print("Nothing changed. Pass --date to move the window.")
            return 0

        if before["registered"]:
            # Not refused — an event does get postponed — but said out loud,
            # because these are people who already chose a time and nothing
            # here tells them it moved. W6's campaign mail is how you would.
            print()
            print(f"NOTE: {before['registered']} person(s) are already "
                  f"registered for the old window. They will not be told.")

        # Postgres does the conversion. A naive local timestamp cast AT TIME
        # ZONE 'Europe/London' is read as a wall-clock time in London and
        # returned as the correct instant, BST or GMT, which is exactly the
        # arithmetic that must not be done by hand.
        db.execute(
            "UPDATE mock_events SET "
            "  window_start = (?::timestamp AT TIME ZONE 'Europe/London'), "
            "  window_end   = (?::timestamp AT TIME ZONE 'Europe/London'), "
            "  results_due_at = COALESCE("
            "      (?::timestamp AT TIME ZONE 'Europe/London'), results_due_at), "
            # A moved window describes an event that has not happened yet.
            "  results_released_at = NULL "
            "WHERE slug=?",
            (f"{args.date} {args.open}", f"{args.date} {args.close}",
             args.results.replace("T", " ") if args.results else None,
             args.event))
        if args.min_cohort is not None:
            db.execute("UPDATE mock_events SET min_cohort=? WHERE slug=?",
                       (args.min_cohort, args.event))

        # Read back rather than trust the write. The whole point of this script
        # is that the hour is easy to get wrong.
        print()
        print("after:")
        after = show(db, args.event)
        if after["closes_utc"] <= after["opens_utc"]:
            raise SystemExit("the window closes before it opens — refusing to "
                             "leave that in place; re-run with sane times")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
