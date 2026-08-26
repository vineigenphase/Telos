"""Extract AQA AS notional component boundaries for one qualification code.

Separate from aqa_extract.py for the same reason the OCR AS parser is separate:
an AS row carries six numbers (max, then A B C D E) where an A-level row carries
seven (max, then A* A B C D E). One parser reading both would, on a near-miss,
store an A boundary in the A* column — the exact shape of the fault that made
Physics predict U on an 85%.

An AS component row looks like

    7356/1 MATHEMATICS AS PAPER 1 80 60 53 46 39 33

The first component of a subject is sometimes prefixed with the subject code on
the same line, so the pattern anchors on the "code/number" token rather than the
start of the line. The bare subject rows ("7356 MATHEMATICS AS 160 115 ...") are
the qualification award across every paper and are never matched, because they
carry no slash.

Every row is checked against the max mark the paper should have.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pypdf import PdfReader

SP = DOCS
YEARS = ["2022", "2023", "2024", "2025"]


def extract(qual_code, expected_max, years=YEARS):
    """{(component, year): (max, a, b, c, d, e)} — no A*, AS has none."""
    pat = re.compile(
        rf"(?:^|\s){qual_code}/(\w+)\s+.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
    out, problems = {}, []
    for year in years:
        path = os.path.join(SP, f"aqa_as_{year}.pdf")
        if not os.path.exists(path):
            problems.append(f"{year}: no PDF")
            continue
        lines = []
        for pg in PdfReader(path).pages:
            lines += (pg.extract_text() or "").splitlines()

        # Repair rows split mid-code, as the A-level documents also do: a line
        # ending in the qualification code and a slash belongs with the next.
        joined, skip = [], False
        for i, l in enumerate(lines):
            if skip:
                skip = False
                continue
            if l.rstrip().endswith(qual_code + "/") and i + 1 < len(lines):
                joined.append(l.rstrip() + lines[i + 1].lstrip())
                skip = True
            else:
                joined.append(l)
        lines = joined

        # A component can appear twice: where AQA scales a component it prints
        # the raw boundaries and then the scaled ones. A student marks their own
        # paper out of the raw total, so collect every candidate and take the
        # one whose max matches. Taking the last match would silently pick the
        # scaled row and inflate every boundary.
        candidates = {}
        for l in (x.strip() for x in lines):
            m = pat.search(l)
            if m:
                comp = m.group(1)
                candidates.setdefault(comp, []).append(
                    tuple(int(v) for v in m.groups()[1:]))

        found = {}
        for comp, rows in candidates.items():
            want = expected_max.get(comp)
            match = [r for r in rows if want is not None and r[0] == want]
            # Fall back to the first row so a wrong expectation surfaces as a
            # max-mark failure below rather than as a missing component.
            found[comp] = match[0] if match else rows[0]

        for comp, want in expected_max.items():
            got = found.get(comp)
            if got is None:
                problems.append(f"{year}: component {comp} missing")
            elif got[0] != want:
                problems.append(f"{year}: {comp} max {got[0]}, expected {want}")
            elif not (got[1] > got[2] > got[3] > got[4] > got[5] > 0):
                problems.append(f"{year}: {comp} boundaries not descending: {got}")
            else:
                out[(comp, year)] = got
    return out, problems


if __name__ == "__main__":
    for code, exp in (
        ("7356", {"1": 80, "2": 80}),
        ("7366", {"1": 80, "2D": 40, "2M": 40, "2S": 40}),
        ("7407", {"1": 70, "2": 70}),
        ("7404", {"1": 80, "2": 80}),
        ("7401", {"1": 75, "2": 75}),
        ("7036", {"1": 80, "2": 80}),
        ("7135", {"1": 70, "2": 70}),
        ("7651", {"1": 90, "2": 50, "3T": 60}),
        ("7661", {"1": 90, "2": 50, "3T": 60}),
        ("7691", {"1": 90, "2": 50, "3T": 60}),
    ):
        data, probs = extract(code, exp)
        print(f"=== {code}: {len(data)} rows")
        for p in probs:
            print("     -", p)
