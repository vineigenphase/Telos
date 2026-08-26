"""Extract OCR A Level Further Mathematics A (H245) component boundaries.

H245 is keyed by component code (Y540-Y545) rather than by a single
qualification code, so it needs its own reader. Two layouts appear: most years
put a component on one line, while 2023 is column-major — six component labels
and six option-combination labels, then every max mark, every A*, every A, and
so on down the columns. Only the first six rows are components; the rest are
overall figures for each pair of options, which are not what a student logs.

Every row must come out at 75 marks, which is what proves a column-major table
has not been read as rows.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
from pypdf import PdfReader

SP = DOCS
# H245 was first assessed in 2019 — reformed Further Maths was first taught in
# 2017 — so there is deliberately no 2018.
YEARS = ["2019", "2022", "2023", "2024", "2025"]
HEADING = "A Level Further Mathematics A (H245)"
COMPONENT_MAX = 75

ONE_LINE = re.compile(
    r"^(Y54\d)\s+01\s+(.+?)\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
NUM = re.compile(r"^\d+$")


def extract():
    data, problems = {}, []
    for year in YEARS:
        lines = []
        for pg in PdfReader(os.path.join(SP, f"ocr{year}.pdf")).pages:
            lines += (pg.extract_text() or "").splitlines()

        found = {}
        for l in (x.strip() for x in lines):
            m = ONE_LINE.match(l)
            if m:
                code, _name, mx, a_s, a, b, c, d, e = m.groups()
                found[code] = tuple(int(v) for v in (mx, a_s, a, b, c, d, e))

        if not found:
            try:
                i = next(n for n, l in enumerate(lines) if l.strip() == HEADING)
            except StopIteration:
                problems.append(f"{year}: heading not found"); continue
            blk = []
            for l in lines[i + 1:]:
                s = l.strip()
                if s.startswith(("A Level ", "AS Level ", "AS GCE ")):
                    break
                blk.append(s)

            codes = [l for l in blk if re.fullmatch(r"Y54\d", l)]
            n_rows = sum(1 for l in blk if l in ("Raw", "Overall"))
            nums = []
            for l in blk:
                if NUM.match(l):
                    nums.append(int(l))
                elif nums:
                    break
            if codes and n_rows and len(nums) >= n_rows * 7:
                cols = [nums[k * n_rows:(k + 1) * n_rows] for k in range(7)]
                for idx, code in enumerate(codes):
                    found[code] = tuple(col[idx] for col in cols)

        for code in ("Y540", "Y541", "Y542", "Y543", "Y544", "Y545"):
            if code not in found:
                problems.append(f"{year}: {code} missing")
            elif found[code][0] != COMPONENT_MAX:
                problems.append(f"{year}: {code} max {found[code][0]}, expected {COMPONENT_MAX}")
            else:
                data[(code, year)] = found[code]
    return data, problems


if __name__ == "__main__":
    data, probs = extract()
    print(f"{'COMP':<7}{'YEAR':<6}{'MAX':>5}{'A*':>6}{'A':>5}{'B':>5}{'C':>5}{'D':>5}{'E':>5}")
    for key in sorted(data, key=lambda k: (k[0], k[1])):
        mx, a_s, a, b, c, d, e = data[key]
        print(f"{key[0]:<7}{key[1]:<6}{mx:>5}{a_s:>6}{a:>5}{b:>5}{c:>5}{d:>5}{e:>5}")
    print()
    print("PROBLEMS:" if probs else "all six components parsed for every series, max marks check out")
    for p in probs:
        print("  -", p)
