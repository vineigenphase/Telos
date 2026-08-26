"""Extract OCR AS component boundaries.

Separate from ocr_extract.py on purpose. An AS table has six grade columns
(a b c d e u) where an A-level table has seven (a* a b c d e u), and a parser
that tried to read both would, on a bad match, silently store an A boundary in
the A* column — which is exactly the fault that made Physics predict U.

The AS tables live in their own section of the same document, under a heading
that begins "AS qualification and notional component raw mark grade
boundaries". Everything before that heading is A-level and is skipped, so a
component code that appears at both levels cannot be read from the wrong one.

Both OCR layouts are handled: one line per component, and the 2023 split layout
where codes, names and numbers sit in separate runs under the heading.

Every row is checked against the max mark the component should have.
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
YEARS = ["2018", "2019", "2022", "2023", "2024", "2025"]

# 2025 says "AS Level qualification...", every other year says "AS qualification...".
AS_SECTION = re.compile(
    r"AS (?:Level )?qualification and notional component raw mark grade boundaries")
# A heading ends the block belonging to the previous qualification.
HEADING = re.compile(r"^(A Level|AS Level|AS GCE|A Level GCE)\b")


def _as_lines(path):
    """Every line of AS content in the document, or [] if it has none.

    Two shapes. From 2022 OCR publishes one document per series with an
    A-level part and an AS part, and only the lines after the AS heading count.
    In 2019 the AS boundaries were their own document ("Reformed AS Levels"),
    which has no such heading because the whole file is AS.

    An AS-only file is recognised by what it contains rather than by its title:
    AS qualification headings and no A-level ones. That way a combined document
    whose heading wording changes again cannot be mistaken for an AS-only one
    and have its A-level half read as AS.
    """
    lines = []
    for pg in PdfReader(path).pages:
        lines += (pg.extract_text() or "").splitlines()

    start = next((i for i, l in enumerate(lines) if AS_SECTION.search(l)), None)
    if start is not None:
        return lines[start:]

    has_as = any(l.strip().startswith(("AS GCE", "AS Level")) for l in lines)
    has_a_level = any(l.strip().startswith(("A Level GCE", "A Level ")) for l in lines)
    return lines if (has_as and not has_a_level) else []


def extract(heading, expected_max, years=YEARS):
    """{(component, year): (max, a, b, c, d, e)} for one AS qualification.

    `expected_max` maps component code (the "01" part, or the full subject code
    for a qualification whose components have distinct codes) to its max mark.
    """
    codes = "|".join(re.escape(k.split()[0]) for k in expected_max)
    one_line = re.compile(
        rf"^({codes})\s+(0\d)\s+(.+?)\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        rf"\s+(\d+)\s+(\d+)\s+\d+\s*$")
    raw = re.compile(r"^Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")

    out, problems = {}, []
    for year in years:
        # A dedicated AS document for the series wins over the combined one.
        path = next((p for p in (os.path.join(SP, f"ocr_as{year}.pdf"),
                                 os.path.join(SP, f"ocr{year}.pdf"))
                     if os.path.exists(p)), None)
        if path is None:
            problems.append(f"{year}: no PDF")
            continue
        lines = _as_lines(path)
        if not lines:
            problems.append(f"{year}: document has no AS section")
            continue

        # The block belonging to this qualification, heading to next heading.
        i = next((n for n, l in enumerate(lines) if l.strip().startswith(heading)), None)
        if i is None:
            problems.append(f"{year}: heading {heading!r} not found")
            continue
        blk = []
        for l in lines[i + 1:]:
            s = l.strip()
            if HEADING.match(s):
                break
            blk.append(s)

        found = {}
        for s in blk:
            m = one_line.match(s)
            if m:
                qual, part, _name, mx, a, b, c, d, e = m.groups()
                key = qual if qual in expected_max else f"{qual} {part}"
                found[key] = tuple(int(v) for v in (mx, a, b, c, d, e))

        if not found:
            # 2023 is column-major: a run of bare codes, then the component
            # names, then one label per row ("Raw", or "Overall" for the
            # qualification total), then the numbers grouped BY COLUMN — every
            # row's max mark, then every row's a, and so on.
            #
            # Rows are matched to codes by position, which is only safe because
            # each is then checked against its own expected max mark. The
            # "Overall" rows are dropped here rather than filtered later: an
            # Overall row is the qualification total across every component,
            # and storing one as if it were a paper is the exact fault that
            # made Physics predict U on an 85%.
            order  = [x for x in blk if re.fullmatch(codes, x)]
            parts  = [m.group(1) for m in (re.match(r"^(0\d)\s+\D", x) for x in blk) if m]
            labels = [x for x in blk if x in ("Raw", "Overall")]
            nums   = [int(x) for x in blk if re.fullmatch(r"\d+", x)]

            n = len(labels)
            if n and len(nums) >= 7 * n:
                for r, label in enumerate(labels):
                    if label != "Raw" or r >= len(order):
                        continue
                    vals = tuple(nums[k * n + r] for k in range(6))   # max,a,b,c,d,e
                    part = parts[r] if r < len(parts) else None
                    key = f"{order[r]} {part}" if part else order[r]
                    found[key] = vals
                    found.setdefault(order[r], vals)

        for comp, want in expected_max.items():
            key = comp.split()[0] if comp.split()[0] in found else comp
            got = found.get(comp) or found.get(key)
            if got is None:
                problems.append(f"{year}: {comp} missing")
            elif got[0] != want:
                problems.append(f"{year}: {comp} max {got[0]}, expected {want}")
            elif not (got[1] > got[2] > got[3] > got[4] > got[5] > 0):
                problems.append(f"{year}: {comp} boundaries not descending: {got}")
            else:
                out[(comp, year)] = got
    return out, problems


if __name__ == "__main__":
    for heading, exp in (
        ("AS GCE Mathematics A", {"H230 01": 75, "H230 02": 75}),
        ("AS GCE Further Mathematics A", {"Y531": 60, "Y532": 60, "Y533": 60,
                                          "Y534": 60, "Y535": 60}),
        ("AS GCE Physics A", {"H156 01": 70, "H156 02": 70}),
        ("AS GCE Chemistry A", {"H032 01": 70, "H032 02": 70}),
        ("AS GCE Biology A", {"H020 01": 70, "H020 02": 70}),
    ):
        data, probs = extract(heading, exp)
        print(f"=== {heading}: {len(data)} rows")
        for p in probs:
            print("     -", p)
