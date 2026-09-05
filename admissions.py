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


# ---------------------------------------------------------------------------
# The 1-9 scale, as UAT-UK defines it
# ---------------------------------------------------------------------------
#
# Response data is analysed with the Rasch item-response model, differences in
# difficulty between forms are removed by equating, and the resulting ability
# scale is mapped to 1.0-9.0 by fixing two percentiles of the cohort.
#
# The anchors have been re-set four times, so a scaled score only means
# something alongside the regime it was issued under. Each line is the awarding
# body's own wording:
#
#   TMUA 2016         "approximately 50% ... higher than 5.0", "approximately
#                     10% ... higher than 7.5"
#   TMUA 2017-2023    "approximately one third of candidates will achieve
#                     overall scores higher than 6.5. High scores are capped
#                     at 9.0."
#   ENGAA / NSAA      "typical applicants will score around 4.0. Approximately
#                     10% of applicants will achieve scores higher than 7.0."
#   TMUA/ESAT 2024+   "typical candidates will score around 4.5. Approximately
#                     10% of candidates will achieve scores higher than 7.0."
#
# CURRENT is the 2024+ regime, which is what "on today's scale" means. It is
# corroborated three ways: the Explanation of Results wording above; the
# TMUA 2024-25 Technical Report, which says the median theta "should be fixed
# to a scaled score of 4.5 and the candidate ability corresponding to the 90th
# percentile should be fixed to a scaled score of 7.0"; and the published
# summary statistics, where P50 is 4.5 and P90 is 7.0 in every module of both
# cycles.
#
# NOTE. An earlier draft of this module used 9.0 for the 90th percentile, taken
# from a summary of the public results page. It was wrong, and it would have
# inflated every score this module produced. The percentile tables settle it.
#
# The useful consequence: the reported scale is DEFINED by percentiles, so the
# target end of an equating needs no published conversion table — a percentile
# is all it takes. Which is just as well, because no raw-to-scale table has
# ever been published for TMUA or ESAT, in any year.
#
# And the reason this module exists at all: the awarding body explicitly
# DISCLAIMS cross-year comparison. "This scaling process has been revised for
# 2024/25, and scores should not be compared directly with TMUA scores from
# earlier years", and "as the scaling is calculated independently for each
# admissions cycle, the scaled score summaries cannot be directly compared
# across admissions cycles". So a student cannot read their 2019 result against
# today's scale, and equating is the only honest way to answer the question.
SCALE_REGIMES = {
    "2016":     ((50.0, 5.0), (90.0, 7.5)),
    "2017-2023": ((66.7, 6.5), (90.0, 8.0)),   # one third above 6.5; see below
    "engaa-nsaa": ((50.0, 4.0), (90.0, 7.0)),
    "current":  ((50.0, 4.5), (90.0, 7.0)),
}
# The 2017-2023 TMUA wording gives only ONE anchor — a third above 6.5 — and a
# 9.0 cap. The second point here is an inference, not a published figure, and
# is why nothing in this module converts a 2017-2023 TMUA scaled score without
# being told to. It is recorded so the gap is visible rather than forgotten.
SCALE_ANCHORS = SCALE_REGIMES["current"]
SCALE_MIN, SCALE_MAX = 1.0, 9.0


def scale_from_percentile(pct):
    """A 1-9 reported score for a candidate standing at `pct` in the cohort.

    Interpolating straight down the percentile axis between the two anchors
    would be wrong: the underlying scale is a Rasch ability scale, which is
    roughly linear in z, not in percentile. So the percentile is converted to a
    z-score first and the anchors are applied there, which keeps the spacing
    right away from the middle. Straight-line interpolation on percentiles
    would compress the top end badly, exactly where candidates care.

    Clamped to 1.0-9.0. The scale has a real ceiling and a real floor, and a
    98th-percentile candidate is a 9.0 rather than an 11.
    """
    (p_lo, s_lo), (p_hi, s_hi) = SCALE_ANCHORS
    z_lo = _inv_phi(p_lo / 100.0)
    z_hi = _inv_phi(p_hi / 100.0)

    pct = max(0.01, min(float(pct), 99.99))
    z = _inv_phi(pct / 100.0)

    score = s_lo + (s_hi - s_lo) * ((z - z_lo) / (z_hi - z_lo))
    return round(max(SCALE_MIN, min(score, SCALE_MAX)), 1)


def equate_to_scale(raw, source):
    """A raw mark on an old paper, as a 1-9 score on today's reported scale.

    This is the whole point of the module for a student working through the
    ENGAA/NSAA back-catalogue: raw mark -> standing in that paper's cohort ->
    the reported score that standing is worth.

    A caveat that belongs in the result rather than a footnote, and is returned
    in `caveat` so the interface has to deal with it. The 1-9 anchors are fixed
    to the ESAT/TMUA cohort. ENGAA was sat by Cambridge engineering applicants
    and NSAA by Cambridge natural-scientists — narrower, stronger populations
    than the ESAT cohort, which spans several universities. So the 70th
    percentile of ENGAA 2019 is NOT the same ability as the 70th percentile of
    ESAT today, and the number here reads a little low for that reason. It is
    indicative, and must be shown as indicative.
    """
    if source is None:
        raise MissingDistribution("no distribution for this paper and year")
    pct = percentile_of(raw, source)
    return {
        "raw": float(raw),
        "of": source.max_marks,
        "percentile": round(pct, 1),
        "scale_score": scale_from_percentile(pct),
        "quality": source.quality,
        "paper": f"{source.test} {source.year} {source.part}",
        "source": source.source,
        "caveat": "cohort-relative: the 1-9 anchors are fixed to the ESAT/TMUA "
                  "cohort, which is broader than the one that sat this paper",
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
