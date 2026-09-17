"""The official admissions papers a student can work through, and their keys.

Pure functions and loaded data only: no Flask, no database, no request context.
Same rule as prediction.py, prescription.py, revision.py and admissions.py, so
every rule here is testable without a running app.

What this is for. `admissions.py` answers "what is this raw score worth on
today's scale?". This module answers the question before it: "which papers are
there to sit, and did I get question 14 right?". The tests are entirely
multiple choice and every question is worth exactly one mark, so marking a
paper is comparing two lists of letters — which means Telos can do it, and a
student never has to translate their answers into a score by hand.

Three grades of support, and the interface says which rather than pretending
they are the same:

  * ENGAA and NSAA, 2016-2023 — `answer_keys.json`, extracted and verified from
    the awarding body's own published keys. Telos marks these outright.
  * TMUA, SPEC and 2016-2023 — the papers are published, the keys were never
    extracted. A student marks their own and taps through right or wrong.
  * ESAT, 2024 onward — UAT-UK publishes no papers at all, so the only ESAT
    rows are sittings the student did themselves. Self-marked, same as TMUA.

The keys are read from `scripts/admissions/answer_keys.json` rather than copied
here. That file is the output of `scripts/admissions/extract_keys.py`, which
reads the official PDFs, and it is the reason the numbers in it can be trusted:
a second copy in this module would be a hand-typed transcription of exactly the
data the archive records as never safe to hand-type.
"""

from __future__ import annotations

import json
import os

from paper_templates import TEMPLATES

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_PATH = os.path.join(HERE, "scripts", "admissions", "answer_keys.json")

BOARD = "UAT-UK"


def _load_keys():
    """{("ENGAA", "2016"): {"Part A": ["G", "D", ...], ...}}.

    A missing file is not an error. The keys are a tracked artefact, but the
    tracker degrades to self-marking without them, and a deploy that cannot
    find one file should lose auto-marking rather than fail to boot.
    """
    try:
        with open(KEYS_PATH, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, ValueError):
        return {}
    return {(d["test"], d["year"]): d["parts"] for d in raw.values()}


ANSWER_KEYS = _load_keys()


def test_name(subject):
    """"ENGAA (2019-2023)" -> "ENGAA". The catalogue key carries the era."""
    return subject.split(" (")[0].strip()


def slug(subject):
    """"ENGAA (2019-2023)" -> "engaa-2019-2023", for a URL.

    The catalogue key is a storage identity, not a label — it carries spaces
    and brackets, and percent-encoding it into a path would put "%20%28" in
    front of a student on every paper list. The slug is derived rather than
    stored so the two cannot drift; `from_slug` is its only inverse.
    """
    out = []
    for ch in subject.lower():
        out.append(ch if ch.isalnum() else "-")
    return "-".join(part for part in "".join(out).split("-") if part)


def from_slug(value):
    """The catalogue subject a slug names, or None. Never trusts the input."""
    for subject in TEMPLATES.get(BOARD, {}):
        if slug(subject) == value:
            return subject
    return None


def answer_key(subject, year, part):
    """The official answers for one part of one year, or None if never extracted."""
    return ANSWER_KEYS.get((test_name(subject), str(year)), {}).get(part)


# Which tests have published question papers at all, which is a different
# question from whether Telos holds a key for them.
#
#   ENGAA, NSAA  papers and keys both published, and both extracted
#   TMUA         papers published 2016-2023; the keys were never extracted
#   ESAT         UAT-UK publishes nothing — no past paper, no specimen, only
#                subject guides. The ESAT rows exist so a candidate can record
#                a sitting they actually took, and there is no document to
#                offer them. Listing one as "missing" would be waiting for a
#                file that is never coming.
PUBLISHES_PAPERS = {"ENGAA", "NSAA", "TMUA"}

# And which report a 1-9 scaled score rather than a raw mark. TMUA and ESAT are
# scaled against each year's own candidates; ENGAA and NSAA reported the raw
# mark itself, against a published distribution. The difference decides what a
# marked paper is allowed to say it means — telling an ENGAA candidate their
# raw mark "is not a score on the 1-9 scale" describes a scale their test never
# had.
SCALED_1_9 = {"TMUA", "ESAT"}


def has_published_paper(subject):
    """Is there an official document for this test, whoever holds it?"""
    return test_name(subject) in PUBLISHES_PAPERS


def reports_scaled_score(subject):
    """Does this test report 1.0-9.0, or a raw mark?"""
    return test_name(subject) in SCALED_1_9


# Tests whose parts are published as separate documents. ENGAA and NSAA print
# every part inside one Section 1 paper, so both rows of a year point at the
# same PDF; TMUA publishes Paper 1 and Paper 2 as two files, so each row has
# its own. Getting this wrong does not fail loudly — it offers a student the
# wrong half of the sitting — so it is stated per test rather than inferred.
PER_PART_PDFS = {"TMUA"}


def pdf_stem(subject, year, part=None):
    """The filename stem one row's PDF is stored under, or None if unpublished.

    `part` is required for a test in PER_PART_PDFS and ignored otherwise.
    "Paper 1" becomes P1; the suffix is built from the part's own digits so a
    third paper would need no change here.
    """
    if not has_published_paper(subject):
        return None
    test = test_name(subject)
    if test not in PER_PART_PDFS:
        return f"{test}_{year}_S1"
    digits = "".join(ch for ch in (part or "") if ch.isdigit())
    if not digits:
        return None
    return f"{test}_{year}_P{digits}"


def official_papers(subject):
    """Every (year, part) a student could log for one admissions qualification.

    Ordered newest year first, because a candidate sitting this autumn works
    backwards from the most recent paper — it is the closest thing published to
    the one they will actually face.
    """
    entry = TEMPLATES.get(BOARD, {}).get(subject)
    if not entry:
        return []

    out = []
    for year in sorted(entry.get("years", []), reverse=True):
        for paper in entry["papers"]:
            key = answer_key(subject, year, paper["code"])
            out.append({
                "subject": subject,
                "test": test_name(subject),
                "year": year,
                "part": paper["code"],
                "name": paper["name"],
                "optional": bool(paper.get("optional")),
                # The key is authoritative about length where there is one. The
                # catalogue's max_marks is the fallback, and the two were
                # checked against each other across all 16 keys.
                "max_marks": len(key) if key else paper["max_marks"],
                "auto_marked": key is not None,
                "published": has_published_paper(subject),
                "scaled": reports_scaled_score(subject),
                # Whether this row's document is its own or shared with the
                # other parts of the same sitting — the interface puts the
                # download in a different place for each.
                "own_pdf": test_name(subject) in PER_PART_PDFS,
                "pdf_stem": pdf_stem(subject, year, paper["code"]),
            })
    return out


def all_official_papers():
    """Every admissions paper in the catalogue, grouped by qualification."""
    return {subject: official_papers(subject)
            for subject in TEMPLATES.get(BOARD, {})}


def options_for(key):
    """The letters that actually appear as answers in one key, sorted.

    Read from the key rather than assumed to be A-E. ENGAA Part A runs to H,
    and a keypad offering five options on a paper with eight would make three
    correct answers unreachable — a fault that looks like the student being
    wrong.
    """
    if not key:
        return list("ABCDEFGH")
    return sorted(set(key))


def mark(given, key):
    """Compare a student's answers against the official key.

    `given` is a list positional with `key`, with None for anything left blank.
    Returns one dict per question, which is what the entry screen renders and
    what the database rows are written from.

    A blank is not a wrong answer for review purposes, but it does score zero,
    which is how these tests work: there is no negative marking on any of them,
    so the only cost of a guess is that it might be wrong.
    """
    out = []
    for i, correct in enumerate(key):
        chose = (given[i] if i < len(given) else None) or None
        out.append({
            "n": i + 1,
            "given": chose,
            "correct": correct,
            "is_correct": chose == correct,
            "answered": chose is not None,
        })
    return out


def score(marked):
    """(raw, out_of) from the output of mark()."""
    return sum(1 for q in marked if q["is_correct"]), len(marked)
