"""Extract component boundaries for an OCR qualification across all series.

OCR uses two layouts. 2018/2019/2022/2025 put a component on one line
("H240 01 Pure Mathematics Raw 100 84 69 ... 0"); 2023/2024 split the code, the
name and the numbers onto separate lines under the qualification heading and
rely on order. Both are handled, and every row is checked against the max mark
the component should have, so a mis-parse fails loudly instead of producing a
plausible wrong number.

Reports only; writing is a separate step.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
from pypdf import PdfReader

SP = DOCS
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]


def extract(qual_code, heading, expected_max):
    """{(component, year): (max, a*, a, b, c, d, e)} for one qualification."""
    one_line = re.compile(
        rf"^{qual_code}\s+(0\d)\s+(.+?)\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        rf"\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
    raw = re.compile(r"^Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
    comp = re.compile(r"^(0\d)\s+(\D.*)$")

    out, problems = {}, []
    for year in YEARS:
        path = os.path.join(SP, f"ocr{year}.pdf")
        if not os.path.exists(path):
            problems.append(f"{year}: no PDF"); continue
        lines = []
        for pg in PdfReader(path).pages:
            lines += (pg.extract_text() or "").splitlines()

        found = {}
        for l in (x.strip() for x in lines):
            m = one_line.match(l)
            if m:
                code, _name, mx, a_s, a, b, c, d, e = m.groups()
                found[code] = tuple(int(v) for v in (mx, a_s, a, b, c, d, e))

        if not found:
            # Split layout: take the block under the qualification heading.
            try:
                i = next(n for n, l in enumerate(lines) if l.strip() == heading)
            except StopIteration:
                problems.append(f"{year}: heading {heading!r} not found"); continue
            blk = []
            for l in lines[i + 1:]:
                s = l.strip()
                if s.startswith(("A Level ", "AS Level ", "AS GCE ")):
                    break
                blk.append(s)
            comps = [comp.match(l).group(1) for l in blk if comp.match(l)]
            raws = [raw.match(l).groups() for l in blk if raw.match(l)]
            if raws:
                # Row-major: "Raw 100 74 65 54 43 32 22" per component.
                for code, r in zip(comps, raws):
                    found[code] = tuple(int(v) for v in r)
            else:
                # Column-major: bare "Raw"/"Overall" labels, then every number
                # for one column before the next — all the max marks, then all
                # the A*s, and so on. The row count comes from the labels, and
                # the max-mark check below is what proves the mapping is right.
                n_rows = sum(1 for l in blk if l in ("Raw", "Overall"))
                nums = []
                for l in blk:
                    if re.fullmatch(r"\d+", l):
                        nums.append(int(l))
                    elif nums and not re.fullmatch(r"\d+", l):
                        break            # numbers are contiguous; stop at the first non-number after them
                if n_rows and len(nums) >= n_rows * 7:
                    cols = [nums[k * n_rows:(k + 1) * n_rows] for k in range(7)]
                    for idx, code in enumerate(comps):
                        if idx < n_rows:
                            found[code] = tuple(col[idx] for col in cols)

        for code, want in expected_max.items():
            if code not in found:
                problems.append(f"{year}: component {code} missing")
            elif found[code][0] != want:
                problems.append(f"{year}: {code} max {found[code][0]}, expected {want}")
            else:
                out[(code, year)] = found[code]
    return out, problems


if __name__ == "__main__":
    data, probs = extract("H240", "A Level Mathematics A",
                          {"01": 100, "02": 100, "03": 100})
    print(f"{'COMP':<6}{'YEAR':<6}{'MAX':>5}{'A*':>6}{'A':>5}{'B':>5}{'C':>5}{'D':>5}{'E':>5}")
    for (code, year) in sorted(data, key=lambda k: (k[0], k[1])):
        mx, a_s, a, b, c, d, e = data[(code, year)]
        print(f"{code:<6}{year:<6}{mx:>5}{a_s:>6}{a:>5}{b:>5}{c:>5}{d:>5}{e:>5}")
    print()
    print("PROBLEMS:" if probs else "all components parsed, max marks check out")
    for p in probs:
        print("  -", p)
