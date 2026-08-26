"""Extract AQA notional component boundaries for one qualification code.

AQA prints both the subject award (out of 300) and the notional component
boundaries (out of the paper's own mark) in the same document. Only the
component rows are wanted: a student logs one paper at a time.

A component row looks like

    7357/2 MATHEMATICS ADV PAPER 2 100 80 62 50 38 27 16

i.e. code, title, max mark, then A* A B C D E. The first component of a subject
is sometimes prefixed with the subject code on the same line, so the pattern is
anchored on the "code/number" token rather than the start of the line.

Every row is checked against the max mark the paper should have.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
from pypdf import PdfReader

SP = DOCS


def extract(qual_code, expected_max, years):
    """{(component, year): (max, a*, a, b, c, d, e)}"""
    pat = re.compile(
        rf"(?:^|\s){qual_code}/(\w+)\s+.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
    out, problems = {}, []
    for year in years:
        path = os.path.join(SP, f"aqa_subj_{year}.pdf")
        if not os.path.exists(path):
            problems.append(f"{year}: no PDF"); continue
        lines = []
        for pg in PdfReader(path).pages:
            lines += (pg.extract_text() or "").splitlines()

        # Repair rows split mid-code. German 2023 breaks "7662/3T ..." across
        # two lines, leaving "7662/" alone and the rest orphaned — so only the
        # scaled duplicate matched and the raw row vanished. Rejoin any line
        # that ends with the qualification code and a slash.
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

        # A component can appear twice. Where AQA scales a component it prints
        # the raw boundaries and then the scaled ones — French Paper 1 is both
        # "100 91 82 70..." and "200 182 164 140...". A student marks their own
        # paper out of the raw total, so every candidate row is collected and
        # the one whose max matches the expected max is chosen. Taking the last
        # match would silently pick the scaled row and double every boundary.
        candidates = {}
        for l in (x.strip() for x in lines):
            m = pat.search(l)
            if m:
                comp = m.group(1)
                vals = tuple(int(v) for v in m.groups()[1:])
                candidates.setdefault(comp, []).append(vals)

        found = {}
        for comp, rows in candidates.items():
            want = expected_max.get(comp)
            match = [r for r in rows if want is not None and r[0] == want]
            # Fall back to the first row so a wrong expectation still surfaces
            # as a max-mark failure below rather than as a missing component.
            found[comp] = match[0] if match else rows[0]

        for comp, want in expected_max.items():
            if comp not in found:
                problems.append(f"{year}: component {comp} missing")
            elif found[comp][0] != want:
                problems.append(f"{year}: {comp} max {found[comp][0]}, expected {want}")
            else:
                out[(comp, year)] = found[comp]
    return out, problems


if __name__ == "__main__":
    YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]
    data, probs = extract("7357", {"1": 100, "2": 100, "3": 100}, YEARS)
    print(f"{'PAPER':<7}{'YEAR':<6}{'MAX':>5}{'A*':>6}{'A':>5}{'B':>5}{'C':>5}{'D':>5}{'E':>5}")
    for key in sorted(data, key=lambda k: (k[0], k[1])):
        mx, a_s, a, b, c, d, e = data[key]
        print(f"{key[0]:<7}{key[1]:<6}{mx:>5}{a_s:>6}{a:>5}{b:>5}{c:>5}{d:>5}{e:>5}")
    print()
    print("PROBLEMS:" if probs else "all three papers parsed for every series, max marks check out")
    for p in probs:
        print("  -", p)
