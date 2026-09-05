"""Admissions-test scoring — putting a raw score from any year on today's scale.

Pure functions only: no Flask, no database, no I/O. Same rule as prediction.py,
prescription.py and revision.py, so every rule here is testable without a
request context.

The problem this solves. A student works through ENGAA 2019 and gets 14 out of
20 on Part A. That number means nothing on its own: the 2019 cohort, the 2019
paper and today's ESAT are three different things, and the tests have got
harder. What the student wants is "and that would be roughly what on this
year's scale?".

The method is **equipercentile equating**, which is the standard way to put two
tests on one scale:

    raw score  ->  percentile in ITS OWN cohort  ->  score at that percentile
                                                     in the TARGET cohort

Difficulty is handled automatically, because a percentile is a statement about
where you stand among people, not about how hard the paper was. A 14/20 that
put you in the top quarter in 2019 comes out as whatever the top quarter is
worth today, whether that is a higher or a lower raw mark.

Two grades of source data, and the difference is reported rather than hidden:

  * a published percentile or cumulative-frequency table -> "exact"
  * a published mean and standard deviation only        -> "estimated", via a
    normal approximation. Cruder, defensible, and labelled so the interface can
    say so.

And where a year has neither, `MissingDistribution` is raised and the caller
declines to convert. This is deliberately the same posture as
prediction.MissingBoundaries: an admissions score nobody published is not a
number to invent, because a fabricated conversion silently mis-scores every
student who ever uses that paper.

One caveat this module cannot resolve on its own. If a test's 1-9 scale is
norm-referenced to each year's cohort, then scaled scores are ALREADY
comparable across years and equating them is a no-op — the work is only in
raw -> scaled. If it is not norm-referenced, cross-year equating is doing real
work. `Distribution.norm_referenced` records which, per test, from whatever the
awarding body actually says.
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field


class MissingDistribution(Exception):
    """No published data for this test, year and part. Never guessed around."""


@dataclass(frozen=True)
class Distribution:
    """What was published about one paper-part's cohort in one year.

    Exactly one of `percentiles` or (`mean`, `sd`) must be usable. `source` is
    where the numbers came from, carried so the interface can cite it and so a
    figure can be traced back to a document rather than trusted.
    """

    test: str
    year: str
    part: str
    max_marks: int
    source: str
    # {raw_score: percentage of candidates scoring AT OR BELOW that raw score}
    percentiles: dict = field(default_factory=dict)
    mean: float | None = None
    sd: float | None = None
    norm_referenced: bool | None = None

    @property
    def quality(self):
        if self.percentiles:
            return "exact"
        if self.mean is not None and self.sd:
            return "estimated"
        return None

    def __post_init__(self):
        if self.quality is None:
            raise ValueError(
                f"{self.test} {self.year} {self.part}: a Distribution needs either "
                f"a percentile table or a mean and a non-zero sd")


# ---------------------------------------------------------------------------
# Normal approximation, used only when a mean and sd are all that exist
# ---------------------------------------------------------------------------

def _phi(z):
    """Standard normal CDF, via the error function.

    math.erf is in the standard library and accurate enough here; a candidate's
    percentile does not need more precision than the published mean carries.
    """
    import math
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _inv_phi(p):
    """Inverse standard normal CDF — Acklam's rational approximation.

    Accurate to about 1.15e-9, which is far beyond what the inputs justify, but
    it is short and has no dependency. Bisection would also work and be slower
    for no benefit.
    """
    import math
    if not 0.0 < p < 1.0:
        raise ValueError("p must be strictly between 0 and 1")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    lo, hi = 0.02425, 1 - 0.02425
    if p < lo:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > hi:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


# ---------------------------------------------------------------------------
# raw <-> percentile
# ---------------------------------------------------------------------------

def percentile_of(raw, dist):
    """Where `raw` stands in `dist`'s cohort, as a percentage 0-100.

    From a published table this is a lookup with linear interpolation between
    the two nearest published marks — a table rarely lists every mark, and a
    step function would make one extra mark worth several percentiles at some
    points and none at others.

    From a mean and sd it is the normal CDF, which assumes the cohort is
    roughly normal. That assumption is why this path is labelled "estimated".
    """
    if raw is None:
        raise ValueError("raw score is required")
    raw = max(0, min(float(raw), float(dist.max_marks)))

    if dist.percentiles:
        marks = sorted(dist.percentiles)
        if raw <= marks[0]:
            return float(dist.percentiles[marks[0]])
        if raw >= marks[-1]:
            return float(dist.percentiles[marks[-1]])
        i = bisect_left(marks, raw)
        if marks[i] == raw:
            return float(dist.percentiles[raw])
        lo_m, hi_m = marks[i - 1], marks[i]
        lo_p, hi_p = dist.percentiles[lo_m], dist.percentiles[hi_m]
        span = hi_m - lo_m
        return float(lo_p + (hi_p - lo_p) * ((raw - lo_m) / span))

    z = (raw - dist.mean) / dist.sd
    return _phi(z) * 100.0


def raw_at_percentile(pct, dist):
    """The raw mark standing at `pct` in `dist`'s cohort. The inverse."""
    pct = max(0.0, min(float(pct), 100.0))

    if dist.percentiles:
        pairs = sorted((p, m) for m, p in dist.percentiles.items())
        ps = [p for p, _ in pairs]
        if pct <= ps[0]:
            return float(pairs[0][1])
        if pct >= ps[-1]:
            return float(pairs[-1][1])
        i = bisect_left(ps, pct)
        if ps[i] == pct:
            return float(pairs[i][1])
        (lo_p, lo_m), (hi_p, hi_m) = pairs[i - 1], pairs[i]
        span = hi_p - lo_p
        return float(lo_m + (hi_m - lo_m) * ((pct - lo_p) / span))

    # Clamped away from the exact ends, where the inverse normal runs off.
    p = max(1e-6, min(pct / 100.0, 1 - 1e-6))
    return max(0.0, min(dist.mean + _inv_phi(p) * dist.sd, float(dist.max_marks)))


# ---------------------------------------------------------------------------
# equating
# ---------------------------------------------------------------------------

def equate(raw, source, target):
    """Put `raw` from the `source` cohort onto the `target` cohort's scale.

    Returns a dict carrying the working, not just the answer, because a student
    being told "your 2019 mark is a 6.4 today" deserves to see that it rests on
    standing in the 72nd percentile, and how good the underlying data is.

    `quality` is the WEAKER of the two distributions: equating through an
    estimated distribution gives an estimated answer however good the other end
    is, and reporting the better of the two would overstate it.
    """
    if source is None or target is None:
        raise MissingDistribution("both a source and a target distribution are required")

    pct = percentile_of(raw, source)
    equivalent = raw_at_percentile(pct, target)
    quality = "estimated" if "estimated" in (source.quality, target.quality) else "exact"

    return {
        "raw": float(raw),
        "of": source.max_marks,
        "percentile": round(pct, 1),
        "equivalent_raw": round(equivalent, 1),
        "equivalent_of": target.max_marks,
        "quality": quality,
        "from": f"{source.test} {source.year} {source.part}",
        "to": f"{target.test} {target.year} {target.part}",
        "sources": [source.source, target.source],
    }


def scale_score(raw, dist, table):
    """Convert a raw mark to a 1-9 scaled score using a published table.

    `table` is {raw_mark: scaled_score} as the awarding body published it for
    that sitting. Interpolated between published marks, and never extrapolated
    beyond the ends of the table — a scale that stops at 9.0 stops at 9.0.

    This is deliberately separate from equating. A conversion table is a
    published fact about one sitting; equating is an inference across two.
    Keeping them apart means the interface can say which it is showing.
    """
    if not table:
        raise MissingDistribution(
            f"no published raw-to-scale table for {dist.test} {dist.year} {dist.part}")
    marks = sorted(table)
    raw = max(0.0, min(float(raw), float(dist.max_marks)))
    if raw <= marks[0]:
        return float(table[marks[0]])
    if raw >= marks[-1]:
        return float(table[marks[-1]])
    i = bisect_left(marks, raw)
    if marks[i] == raw:
        return float(table[raw])
    lo, hi = marks[i - 1], marks[i]
    return float(table[lo] + (table[hi] - table[lo]) * ((raw - lo) / (hi - lo)))
