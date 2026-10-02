"""The National Mock: the event state machine, as pure functions.

No Flask, no database — the same contract as prediction.py, prescription.py
and admissions.py. Every function that cares about the time takes `now`
explicitly, which is the whole reason this module exists: the event has three
states and two boundaries, and the only honest way to test the boundaries is
to hand the code a time rather than wait for one.

That mattered immediately. The window moved once already, from Sunday 4
October to Friday 2 October, and it may well move again on the day — so
nothing here hardcodes a date. The window arrives as arguments, read from the
mock_events row.
"""

from datetime import datetime, timedelta, timezone
import secrets

# The three states. A visitor is early, sitting, or late, and the page says a
# different thing in each.
BEFORE = "before"
SITTING = "sitting"
AFTER = "after"

# A registration count is published only once it is a reason to join rather
# than a reason not to. "4 registered" is worse than saying nothing, and on a
# launch day the number starts at zero in front of everybody.
COUNT_VISIBLE_FROM = 50

# Source codes: lowercase, short, and drawn from a small alphabet, because
# they end up in a database column, a URL and an admin table. Anything else a
# visitor puts in ?r= is dropped rather than stored.
SOURCE_MAX = 32
_SOURCE_OK = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-_.")

# Referral codes avoid I, O, 0 and 1 — they get read off a phone screen and
# typed by someone else, which is the one job the backfilled hex codes do
# badly.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LEN = 7


def clean_source(raw):
    """A ?r= value as it may be stored, or "" if nothing usable survives.

    Permissive about what it accepts and strict about what it keeps: a link
    shared through three apps picks up punctuation, and losing the attribution
    because someone's client appended a bracket would be worse than storing
    the trimmed stem.
    """
    if not raw:
        return ""
    kept = [c for c in str(raw).strip().lower()[:SOURCE_MAX * 2] if c in _SOURCE_OK]
    return "".join(kept)[:SOURCE_MAX].strip("-_.")


def new_code(exists=None):
    """A fresh referral code. `exists(code)` says whether one is taken.

    Random rather than derived from the user id: a code that is a function of
    a sequence lets anyone walk the user table by guessing.
    """
    for _ in range(12):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LEN))
        if exists is None or not exists(code):
            return code
    # 32^7 is 34 billion; twelve collisions in a row means `exists` is lying,
    # and silently handing back a duplicate would trip the unique constraint
    # at insert time with no clue why.
    raise RuntimeError("could not find a free referral code in 12 tries")


def state(window_start, window_end, now):
    """BEFORE, SITTING or AFTER.

    Boundaries are inclusive at the start and exclusive at the end, so the
    event is open at exactly 10:00:00 and shut at exactly 22:00:00 — the same
    convention the attempt clock already uses, where ends_at having passed
    means the paper is over.
    """
    if now < window_start:
        return BEFORE
    if now < window_end:
        return SITTING
    return AFTER


def countdown(target, now):
    """(days, hours, minutes, seconds) until `target`, never negative.

    Rendered server-side so the page has a real countdown in its first frame
    rather than a row of dashes waiting on JavaScript. The client ticks it
    from there.
    """
    secs = int((target - now).total_seconds())
    if secs < 0:
        secs = 0
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    minutes, secs = divmod(secs, 60)
    return days, hours, minutes, secs


def show_count(registered):
    """Whether to publish the registration figure at all."""
    return registered >= COUNT_VISIBLE_FROM


def percentiles_ok(cohort, min_cohort):
    """Whether a cohort is big enough for a percentile to mean anything.

    A rank among eleven people is noise presented as information, and the one
    number this whole event exists to produce is the one it must not fake. If
    the cohort falls short the result still shows the score, the scaled band
    and the topic breakdown — everything except the comparison.
    """
    return cohort >= max(1, min_cohort)


# ── Rendering UK local times ──────────────────────────────────────────────────
#
# Every timestamp is stored in UTC, and every one of them is read by a student
# in Europe/London. The conversion is done by Postgres — `window_start AT TIME
# ZONE 'Europe/London'` — rather than by zoneinfo here, for one blunt reason:
# Windows ships no IANA time-zone database, so ZoneInfo("Europe/London") raises
# on the development machine unless the `tzdata` package is installed, and
# requirements.txt is deliberately held at seven dependencies. Postgres already
# has the database. These functions therefore take an ALREADY-LOCAL naive
# datetime and only format it.
#
# The launch window sits inside BST, so an hour's error here would print the
# wrong unlock time on the page the entire event points at.

def fmt_time(local):
    """10:00."""
    return local.strftime("%H:%M") if local else ""


def fmt_date(local):
    """Friday 2 October. The day number is interpolated rather than taken from
    strftime, because the no-pad flag for it differs between platforms: %-d on
    Linux, %#d on Windows, and whichever one is wrong raises or prints the
    literal."""
    return (f"{local.strftime('%A')} {local.day} {local.strftime('%B')}"
            if local else "")


def fmt_when(local):
    """10:00 on Friday 2 October."""
    return f"{fmt_time(local)} on {fmt_date(local)}" if local else ""


# ── Ranking a cohort ─────────────────────────────────────────────────────────
#
# The one number this event exists to produce, so the rules are written down
# here rather than embedded in a SQL window function where nobody will find
# them.
#
# Ranked on RAW marks, not the scaled band. Everyone in a cohort sat the same
# paper, so raw is directly comparable and is the finer measure: the 1-9 scale
# is deliberately coarse and would tie half the cohort together.
#
# Ties genuinely tie. There is no secondary sort on time taken or on submission
# order — two people who scored 14 out of 20 did equally well, and inventing a
# separator to break that would be inventing a result.

def cohort_ranks(entries):
    """{key: (rank, percentile)} for [(key, raw_score), ...].

    `rank` is competition ranking: the best score is 1, equal scores share a
    rank, and the next distinct score skips the ones used up. So three people
    tied at the top are all 1st and the next is 4th — which is what "joint
    first" means everywhere else.

    `percentile` is the percentage of the cohort who scored STRICTLY LOWER,
    rounded to a whole number. Tied students get the same figure, and the
    bottom scorer gets 0 rather than a flattering fraction of one. Stated to
    the student as "you scored higher than N% of the cohort", which is the only
    phrasing that means exactly this and cannot be read as a grade.

    Whole numbers because a percentile of 87.3 in a cohort of twenty-three is
    three digits of precision over an interval of four points. The rounding is
    the honest part.
    """
    rows = list(entries)
    n = len(rows)
    if not n:
        return {}
    scores = sorted((s for _k, s in rows), reverse=True)
    # One pass per distinct score rather than per student: a cohort of a few
    # hundred is nothing, but the shape matters if this is ever run on a year's
    # worth of events at once.
    higher, lower = {}, {}
    for i, s in enumerate(scores):
        if s not in higher:
            higher[s] = i                       # how many scored strictly more
    for i, s in enumerate(reversed(scores)):
        if s not in lower:
            lower[s] = i                        # how many scored strictly less
    return {k: (higher[s] + 1, int(round(100.0 * lower[s] / n)))
            for k, s in rows}


def median(values):
    """The middle value, or the mean of the two middle ones. None if empty."""
    vals = sorted(values)
    n = len(vals)
    if not n:
        return None
    mid = n // 2
    return float(vals[mid]) if n % 2 else (vals[mid - 1] + vals[mid]) / 2.0


def above_median(rank, cohort):
    """Whether a rank sits in the better half.

    The share card uses this: a card saying "47th of 50" is a thing a student
    posts once and then regrets, and a product that hands them the means to do
    it has done them no favours. Their own results page still shows the true
    figure — this governs what gets a one-tap share button, not what they are
    told.
    """
    if not cohort or not rank:
        return False
    return rank <= (cohort + 1) // 2
