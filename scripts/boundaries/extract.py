"""Pull A Level Physics A (H556) boundaries out of OCR's official PDFs.

Two layouts appear across the years. 2018/2019/2022/2025 put a component on one
line ("H556 01 Modelling physics Raw 100 83 72 60 49 38 27 0"); 2023/2024 split
the code, the name and the numbers onto separate lines and rely on order. Both
are handled, and every row is checked against the max mark the component is
supposed to have, so a mis-parse shows up as a failure rather than as a
plausible-looking wrong number.

Prints only. These numbers drive every Physics prediction, so a human reads
them before anything is written.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os
import re

from pypdf import PdfReader

SP = DOCS
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]

# The component max marks, from the specification. Used as a parse check.
EXPECTED_MAX = {"01": 100, "02": 100, "03": 70}

ONE_LINE = re.compile(
    r"^H556\s+(0\d)\s+(.+?)\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
RAW = re.compile(r"^Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
COMP = re.compile(r"^(0\d)\s+(\D.*)$")
OVERALL = re.compile(r"(?:^|\s)Overall\s+(270)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")

results, problems = {}, []


def physics_a_block(lines):
    """Lines under the 'A Level Physics A' heading, up to the next heading."""
    try:
        i = next(n for n, l in enumerate(lines) if l.strip() == "A Level Physics A")
    except StopIteration:
        return None
    out = []
    for l in lines[i + 1:]:
        s = l.strip()
        if s.startswith("A Level ") or s.startswith("AS Level ") or s.startswith("AS GCE "):
            break
        out.append(s)
    return out


for year in YEARS:
    path = os.path.join(SP, f"ocr{year}.pdf")
    lines = []
    for pg in PdfReader(path).pages:
        lines += (pg.extract_text() or "").splitlines()

    found = {}

    # Layout A: one line per component, anywhere in the document.
    for l in (x.strip() for x in lines):
        m = ONE_LINE.match(l)
        if m:
            code, name, mx, a_star, a, b, c, d, e = m.groups()
            found[code] = (name, int(mx), *(int(v) for v in (a_star, a, b, c, d, e)))

    # Layout B: split lines within the Physics A block, matched by order.
    if not found:
        blk = physics_a_block(lines) or []
        comps = [COMP.match(l).groups() for l in blk if COMP.match(l)]
        raws = [RAW.match(l).groups() for l in blk if RAW.match(l)]
        for (code, name), r in zip(comps, raws):
            found[code] = (name, *(int(v) for v in r))

    blk = physics_a_block(lines) or lines
    ov = next((OVERALL.search(l) for l in blk if OVERALL.search(l)), None)

    for code in ("01", "02", "03"):
        if code not in found:
            problems.append(f"{year}: component {code} not found")
        elif found[code][1] != EXPECTED_MAX[code]:
            problems.append(f"{year}: component {code} max {found[code][1]}, expected {EXPECTED_MAX[code]}")

    results[year] = {"components": found, "overall": ov.groups() if ov else None}

print(f"{'YEAR':<6}{'COMP':<5}{'NAME':<22}{'MAX':>5}{'A*':>6}{'A':>5}{'B':>5}{'C':>5}{'D':>5}{'E':>5}")
for year in YEARS:
    for code in ("01", "02", "03"):
        v = results[year]["components"].get(code)
        if not v:
            continue
        name, mx, a_star, a, b, c, d, e = v
        print(f"{year:<6}{code:<5}{name[:20]:<22}{mx:>5}{a_star:>6}{a:>5}{b:>5}{c:>5}{d:>5}{e:>5}")
    ov = results[year]["overall"]
    if ov:
        mx, a_star, a, b, c, d, e = (int(x) for x in ov)
        print(f"{year:<6}{'--':<5}{'OVERALL':<22}{mx:>5}{a_star:>6}{a:>5}{b:>5}{c:>5}{d:>5}{e:>5}")
    print()

print("PARSE PROBLEMS:" if problems else "All components parsed and max marks check out.")
for p in problems:
    print("  -", p)
