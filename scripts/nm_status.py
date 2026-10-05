"""Where the National Mock stands, right now.

Read-only. Run it as often as you like during the window:

    railway run --service web .venv\\Scripts\\python.exe scripts\\nm_status.py

It answers the questions the day actually turns on:

  * how many people the links brought, and from where — the figure that says
    whether anything was posted at all, and which post worked;
  * how many of those visits became accounts;
  * how many registered for the event, and through which link;
  * how many are sitting or have sat each paper;
  * which papers are above the cohort threshold and will therefore get a
    percentile, and which will not.

Visits come before registrations deliberately. After the first event every
figure below registrations was zero, and the only one that explained why was
the visit count: nothing had been posted. A dashboard that starts at
"registrations: 0" invites you to fix the signup flow.

That last one matters more than the headline count. The public page hides the
registration figure below 50, and the threshold that decides whether the event
produces its one real output is per paper, not overall — so a healthy-looking
total can still mean five papers that each publish nothing.

Nothing here writes. The one number it must never quietly round is the cohort
size: if a paper is at 19 against a threshold of 20, that is the whole story of
the day and it is said plainly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nationalmock  # noqa: E402
from db import get_db  # noqa: E402

SLUG = os.environ.get("NM_SLUG", "nm1")


def main():
    with get_db() as db:
        event = db.execute(
            "SELECT id, title, min_cohort, paper_codes, "
            "       window_start AT TIME ZONE 'Europe/London' AS opens, "
            "       window_end   AT TIME ZONE 'Europe/London' AS closes, "
            "       results_due_at AT TIME ZONE 'Europe/London' AS results, "
            "       results_released_at, "
            "       NOW() < window_start AS before, "
            "       NOW() >= window_end  AS after "
            "FROM mock_events WHERE slug=?", (SLUG,)).fetchone()
        if not event:
            print(f"no event with slug {SLUG!r}")
            return 1

        phase = ("BEFORE" if event["before"]
                 else "AFTER" if event["after"] else "OPEN")
        print(f"{event['title']}  [{phase}]")
        print(f"  opens   {nationalmock.fmt_when(event['opens'])}")
        print(f"  closes  {nationalmock.fmt_when(event['closes'])}")
        print(f"  results {nationalmock.fmt_when(event['results'])}"
              + ("  (released)" if event["results_released_at"] else ""))
        print(f"  cohort threshold: {event['min_cohort']} per paper")
        print()

        total = db.execute(
            "SELECT COUNT(*) AS n, "
            "       COUNT(*) FILTER (WHERE percentile_optin) AS opted "
            "FROM mock_event_entries WHERE event_id=?", (event["id"],)).fetchone()
        print(f"registered: {total['n']}   "
              f"opted into the cohort comparison: {total['opted']}")
        # Said out loud rather than left to be worked out: the public page is
        # silent about the count below this, and "why does it not show the
        # number" is the first thing anyone asks.
        if not nationalmock.show_count(total["n"]):
            print(f"  (the public page shows no count until "
                  f"{nationalmock.COUNT_VISIBLE_FROM})")
        print()

        # Traffic first, registrations second, because they answer different
        # questions and the first one is the one that is usually wrong. A post
        # that sends nobody and a post that sends people who do not sign up
        # need opposite responses, and a registration count alone cannot tell
        # them apart.
        print("visits, by where the link was posted")
        rows = db.execute(
            "SELECT COALESCE(detail, '(none)') AS src, COUNT(*) AS n, "
            "       MAX(created_at) AS last "
            "FROM analytics_events WHERE event='landed' "
            "GROUP BY 1 ORDER BY n DESC, 1").fetchall()
        if not rows:
            print("  no tagged visits ever — nothing has been posted, or the "
                  "links were posted without their ?r= code")
        for r in rows:
            print(f"  {r['src']:<16} {r['n']:>4}   last {r['last']:%Y-%m-%d %H:%M}")
        print()

        print("accounts created, by first touch")
        rows = db.execute(
            "SELECT COALESCE(signup_source, '(direct)') AS src, COUNT(*) AS n "
            "FROM users GROUP BY 1 ORDER BY n DESC, 1").fetchall()
        for r in rows:
            print(f"  {r['src']:<16} {r['n']:>4}")
        print()

        print("event registrations, by where they came from")
        rows = db.execute(
            "SELECT COALESCE(source, '(direct)') AS source, COUNT(*) AS n "
            "FROM mock_event_entries WHERE event_id=? "
            "GROUP BY 1 ORDER BY n DESC, 1", (event["id"],)).fetchall()
        if not rows:
            print("  nobody yet")
        for r in rows:
            print(f"  {r['source']:<16} {r['n']:>4}")
        print()

        print("per paper")
        # Attempts are counted against the event's own papers, and only ones
        # started inside the window — an admin's pre-flight check the night
        # before is not a sitting, and must not inflate a cohort it would then
        # also push over the threshold.
        rows = db.execute(
            "SELECT p.paper_code, p.title, "
            "       COUNT(*) FILTER (WHERE a.status='live')      AS live, "
            "       COUNT(*) FILTER (WHERE a.status<>'live')     AS done, "
            "       COUNT(DISTINCT a.user_id) FILTER ("
            "           WHERE a.status<>'live' AND e.percentile_optin) AS cohort "
            "FROM exam_papers p "
            "LEFT JOIN exam_attempts a "
            "       ON a.paper_id = p.id "
            "      AND a.started_at >= (SELECT window_start FROM mock_events WHERE id=?) "
            "      AND a.started_at <  (SELECT window_end   FROM mock_events WHERE id=?) "
            "LEFT JOIN mock_event_entries e "
            "       ON e.user_id = a.user_id AND e.event_id = ? "
            "WHERE p.paper_code = ANY(?) "
            "GROUP BY p.paper_code, p.title "
            "ORDER BY p.paper_code",
            (event["id"], event["id"], event["id"],
             list(event["paper_codes"]))).fetchall()

        print(f"  {'paper':<14} {'live':>5} {'done':>5} {'cohort':>7}  percentile")
        for r in rows:
            ok = nationalmock.percentiles_ok(r["cohort"], event["min_cohort"])
            verdict = "yes" if ok else f"NO (needs {event['min_cohort'] - r['cohort']} more)"
            print(f"  {r['paper_code']:<14} {r['live']:>5} {r['done']:>5} "
                  f"{r['cohort']:>7}  {verdict}")

        short = [r["paper_code"] for r in rows
                 if not nationalmock.percentiles_ok(r["cohort"],
                                                    event["min_cohort"])]
        print()
        if short:
            print(f"{len(short)} of {len(rows)} papers would publish no "
                  f"percentile: {', '.join(short)}")
            print("See runbook.md, 'If the cohort is short'. Do not lower the "
                  "threshold to make a number appear.")
        else:
            print("every paper is above the threshold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
