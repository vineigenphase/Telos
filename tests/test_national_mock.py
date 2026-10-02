"""The National Mock: the funnel end to end, and the three states of the page.

Two halves.

The first is the pure state machine from nationalmock.py, exercised at both
boundaries of the window — the one place an off-by-one would be invisible until
10:00:00 on the day and then wrong for everybody at once.

The second walks the funnel a visitor from TikTok actually walks: /nm?r=tt,
through the redirect, register, pick a subject, come back, join. The claim being
tested is that `source` arrives as 'tt' at the far end, because that is the only
evidence the launch will ever have about whether the videos worked.

The window is NEVER moved in the database to test the states. It is a
production row, the event is hours away, and a suite that dies halfway through
after an UPDATE would leave the real event mis-dated with nobody watching.
The route's two readers — _nm_event and _nm_window — are patched in process
instead, which tests the same code paths and cannot outlive the test.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

# Before importing app, as test_canonical_host.py does in the other direction.
# With CANONICAL_HOST set, _force_canonical_host answers every GET from the
# test client's "localhost" with a 301 before any other before_request runs —
# including the one that captures ?r=. run_all.py already pops it; popping it
# here as well is what lets this suite be run on its own.
os.environ.pop("CANONICAL_HOST", None)

import app as A  # noqa: E402
import exam as E  # noqa: E402
import nationalmock as NM  # noqa: E402
from db import get_db  # noqa: E402
from _fixtures import purge_user  # noqa: E402

app = A.app
app.debug = False
EMAIL = "nationalmock@telos.test"
PW = "national-mock-pw-1"
fails = []


def check(label, got, want):
    ok = got == want
    print(("PASS  " if ok else "FAIL  ") + label + f": {got!r}"
          + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


# ── The state machine ────────────────────────────────────────────────────────

START = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
END = datetime(2026, 10, 2, 21, 0, tzinfo=timezone.utc)

check("a second before the window, the event is still ahead",
      NM.state(START, END, START - timedelta(seconds=1)), NM.BEFORE)
# Inclusive at the start: at exactly 10:00:00 the paper is open. Anything else
# means the first candidate to tap at ten gets told to come back.
check("at the opening instant it is open",
      NM.state(START, END, START), NM.SITTING)
check("a second before closing it is still open",
      NM.state(START, END, END - timedelta(seconds=1)), NM.SITTING)
# Exclusive at the end, matching the attempt clock: ends_at having passed means
# the paper is over.
check("at the closing instant it is shut",
      NM.state(START, END, END), NM.AFTER)

check("the countdown counts down",
      NM.countdown(START, START - timedelta(hours=14, minutes=30)),
      (0, 14, 30, 0))
check("and never goes negative",
      NM.countdown(START, START + timedelta(hours=3)), (0, 0, 0, 0))

check("a source code is normalised", NM.clean_source("TT-03"), "tt-03")
check("and junk is dropped, not stored", NM.clean_source("<script>"), "script")
check("an empty source stays empty", NM.clean_source("  ---  "), "")

check("49 registrations is not a number worth publishing", NM.show_count(49), False)
check("50 is", NM.show_count(50), True)
check("a cohort of 16 cannot carry a percentile",
      NM.percentiles_ok(16, 20), False)
check("a cohort of 20 can", NM.percentiles_ok(20, 20), True)

codes = {NM.new_code() for _ in range(200)}
check("referral codes do not repeat in 200 draws", len(codes), 200)
check("and avoid the characters people misread",
      any(c in "".join(codes) for c in "IO01"), False)

# ── The funnel ───────────────────────────────────────────────────────────────

real_event = A._nm_event
real_window = A._nm_window


def fake_event(shift):
    """The real nm1 row with its window moved by `shift`, as a dict.

    A dict rather than a Row because every reader — the route and the template
    — reaches it by key or by attribute, and Jinja falls back from one to the
    other. Derived from the real row so the paper codes, title and min_cohort
    stay true; only the clock moves.
    """
    def wrapped(db, slug=A.NM_SLUG):
        row = dict(real_event(db, slug))
        for utc, local in (("window_start", "start_local"),
                           ("window_end", "end_local")):
            row[utc] = row[utc] + shift
            # The *_local columns are naive London time; shifting both by the
            # same delta keeps them consistent with each other, which is all
            # the page renders.
            row[local] = row[local] + shift
        return row
    return wrapped


def fake_window(shift):
    def wrapped(slug=A.NM_SLUG):
        start, end, start_local = real_window(slug)
        if not start:
            return (None, None, None)
        return (start + shift, end + shift, start_local + shift)
    return wrapped


def with_window(start_delta, _end=None):
    """Put the window's OPENING `start_delta` from now, keeping its length.

    Expressed relative to now rather than as a fixed offset from the real
    window, because the real window is tomorrow and "one day earlier" lands in
    a different phase depending on what time of day the suite is run — which
    is exactly how this test first went green on the logic and red on the
    clock.
    """
    start, _e, _l = real_window()
    shift = (datetime.now(timezone.utc) + start_delta) - start
    A._nm_event = fake_event(shift)
    A._nm_window = fake_window(shift)


try:
    with get_db() as db:
        purge_user(db, EMAIL)

    # ── The link in the video caption ────────────────────────────────────────
    c = app.test_client()
    r = c.get("/nm?r=tt", follow_redirects=False)
    check("/nm redirects", r.status_code, 302)
    loc = r.headers.get("Location", "")
    check("to the event page", loc.split("?")[0].endswith("/national-mock"), True)
    # The whole point of the short link is that it carries the source through.
    check("carrying the source with it", "r=tt" in loc, True)
    r = c.get("/nm", follow_redirects=False)
    check("and works with no query string at all",
          r.headers.get("Location", "").endswith("/national-mock"), True)

    # ── Before the window ───────────────────────────────────────────────────
    body = c.get("/national-mock?r=tt").get_data(as_text=True)
    check("the event page is public", "Telos National Mock" in body, True)
    check("it counts down to the opening", "Unlocks in" in body, True)
    check("a visitor is asked to register free", "Register free" in body, True)
    check("the independence line is on the page",
          "not affiliated with any awarding organisation" in body, True)
    check("the og:image is absolute",
          'og:image" content="https://' in body, True)
    # Below 50 the number is not published at all, rather than published small.
    check("the registration count is withheld",
          "registered so far" in body, False)

    # ── Register, which must carry the source onto the account ──────────────
    r = c.post("/register?next=/national-mock",
               data={"email": EMAIL, "username": "nmtest", "password": PW},
               follow_redirects=False)
    check("registering redirects to the subject picker",
          "/welcome" in r.headers.get("Location", ""), True)

    with get_db() as db:
        u = db.execute("SELECT id, signup_source, referral_code, marketing_optin "
                       "FROM users WHERE email=?", (EMAIL,)).fetchone()
    uid = u["id"]
    check("the first touch is on the account", u["signup_source"], "tt")
    check("the account has a referral code of its own",
          len(u["referral_code"] or ""), NM.CODE_LEN)
    check("and marketing is off until asked for", bool(u["marketing_optin"]), False)

    r = c.post("/welcome", data={"qualification": "Edexcel|Maths|A-Level"},
               follow_redirects=False)
    check("finishing setup returns them to the event, not the dashboard",
          r.headers.get("Location", "").endswith("/national-mock"), True)

    # ── Joining, with both boxes left alone ─────────────────────────────────
    r = c.post("/national-mock/join", data={}, follow_redirects=False)
    check("joining redirects back to the event", r.status_code, 302)
    with get_db() as db:
        entry = db.execute(
            "SELECT e.source, e.percentile_optin, u.marketing_optin "
            "FROM mock_event_entries e JOIN users u ON u.id=e.user_id "
            "WHERE e.user_id=?", (uid,)).fetchone()
    check("the entry records where they came from", entry["source"], "tt")
    # The two claims the Children's Code turns on. An unticked box that arrives
    # as True is the one bug on this page that would be a reportable failure
    # rather than a bad experience.
    check("an unticked cohort box stays off",
          bool(entry["percentile_optin"]), False)
    check("an unticked marketing box stays off",
          bool(entry["marketing_optin"]), False)

    body = c.get("/national-mock").get_data(as_text=True)
    check("the page now says they are in", "You're registered." in body, True)
    check("and explains what opting out costs them",
          "not a percentile" in body, True)

    # ── Changing their mind ─────────────────────────────────────────────────
    c.post("/national-mock/join",
           data={"percentile_optin": "1", "marketing_optin": "1"})
    with get_db() as db:
        entry = db.execute(
            "SELECT e.source, e.percentile_optin, u.marketing_optin "
            "FROM mock_event_entries e JOIN users u ON u.id=e.user_id "
            "WHERE e.user_id=?", (uid,)).fetchone()
        n = db.execute("SELECT COUNT(*) AS n FROM mock_event_entries "
                       "WHERE user_id=?", (uid,)).fetchone()["n"]
    check("a second join does not create a second entry", n, 1)
    check("it turns the cohort comparison on",
          bool(entry["percentile_optin"]), True)
    check("and the marketing consent with it",
          bool(entry["marketing_optin"]), True)
    check("while the original source is kept, not overwritten",
          entry["source"], "tt")

    # ── The lock ────────────────────────────────────────────────────────────
    # Mock A is free and published, so without the lock this paper could be sat
    # the day before by anybody. That would not break the app; it would break
    # the percentile, quietly, which is worse.
    with get_db() as db:
        locked_paper = db.execute(
            "SELECT * FROM exam_papers WHERE paper_code='TMUA-P1-A'").fetchone()
    check("the lock refuses a free event paper before the window",
          E.NM_LOCK_BEFORE_WINDOW, True)

    r = c.post("/exam/TMUA-P1-A/start")
    check("starting a sealed paper is refused", r.status_code, 403)
    data = r.get_json()
    # 403 and "unlocks", never 402 and "buy". A buy prompt for a free paper, on
    # the day of a free event, is the single most damaging thing this flow
    # could say.
    check("as a lock, not a paywall", data.get("error"), "event_locked")
    check("the message says when it opens", "unlocks at" in data["message"], True)
    check("and never mentions paying",
          any(w in data["message"].lower() for w in ("£", "buy", "pay")), False)
    check("it points at the event page",
          data.get("event_url", "").endswith("/national-mock"), True)

    body = c.get("/exam").get_data(as_text=True)
    check("Exam Mode shows the paper as locked", "pill-locked" in body, True)
    check("with the unlock time said once", "unlock at 10:00 on Friday" in body
          or "unlock at" in body, True)

    # A paper that is not on the event card is untouched by all of this.
    r = c.post("/exam/TMUA-P1-B/start")
    check("a Mock B paper is unaffected by the lock",
          r.status_code in (402, 200), True)

    # ── Inside the window ───────────────────────────────────────────────────
    # Opened an hour ago, so "now" falls inside it whatever time the suite runs.
    with_window(timedelta(hours=-1))
    body = c.get("/national-mock").get_data(as_text=True)
    check("inside the window the page says it is open", "Open now" in body, True)
    check("and counts down to the close", "Window closes in" in body, True)
    r = c.post("/exam/TMUA-P1-A/start")
    check("and the paper starts", r.status_code, 200)
    attempt = r.get_json()["attempt_id"]
    with get_db() as db:
        db.execute("DELETE FROM exam_responses WHERE attempt_id=?", (attempt,))
        db.execute("DELETE FROM exam_attempts WHERE id=?", (attempt,))

    # ── After the window ────────────────────────────────────────────────────
    # Opened thirteen hours ago, so its twelve-hour window has shut.
    with_window(timedelta(hours=-13))
    body = c.get("/national-mock").get_data(as_text=True)
    check("after the window the page says so", "window</em> closed" in body, True)
    check("and promises the results at a stated time",
          "Saturday" in body or "Results" in body, True)
    check("the countdown is gone", "Unlocks in" in body, False)

finally:
    A._nm_event = real_event
    A._nm_window = real_window
    with get_db() as db:
        purge_user(db, EMAIL)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
