"""Extract Pearson notional component boundaries for one A-level subject.

Three layouts appear across these documents and all three are handled:

  * name, numbers and label on consecutive lines —
        9PH0 A Level Physics Raw 90 69 59 48 38 28 18 0
        Paper 1
  * name and numbers split (2024) —
        A Level Physics
        Raw 90 69 59 48 38 28 18 0
        Paper 1
  * a row whose label is missing entirely (2019 Physics Paper 2, whose label
    line reads "9PE0"). Those are resolved only when exactly one expected paper
    is unaccounted for and exactly one unlabelled row of that paper's max mark
    remains — a deduction, not a guess, and it prints a note when it fires.

Column layouts also vary: most series print A* A B C D E, some print A B C D E
with no A* at component level. A row without one returns None in that position
rather than silently storing A as A*.

Every row is checked against the paper's expected max mark.
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
# 2019 zero-pads to three digits ("Paper 021"), where every other series
# writes "Paper 21". Leading zeros are stripped below, so both give "21".
LABEL = re.compile(r"^Paper\s+(\d{1,3}[A-D]?)\s*$")
RAW7 = re.compile(r"Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")
RAW6 = re.compile(r"Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")

NOTES = []


def _rows_for(lines, title):
    """[(values, label_or_None)] for every Raw row belonging to `title`."""
    out = []
    for i, raw in enumerate(lines):
        s = raw.strip()

        # Fourth layout (2024): a bare "Raw" line with every number on its own
        # line beneath it, then the paper label. Handled first because RAW7 and
        # RAW6 cannot match a line that holds no digits.
        if s == "Raw":
            owner_v = None
            for back in (1, 2, 3):
                if i - back >= 0 and title in lines[i - back].strip():
                    owner_v = True
                    break
            if owner_v:
                nums, k = [], i + 1
                while k < len(lines) and re.fullmatch(r"\d+", lines[k].strip()):
                    nums.append(int(lines[k].strip()))
                    k += 1
                lab_v = LABEL.match(lines[k].strip()) if k < len(lines) else None
                label_v = (lab_v.group(1).lstrip("0") or "0") if lab_v else None
                if len(nums) >= 8:                 # max, A*, A, B, C, D, E, U
                    out.append((tuple(nums[:7]), label_v))
                elif len(nums) == 7:               # no A* at component level
                    out.append(((nums[0], None) + tuple(nums[1:6]), label_v))
            continue

        m7, m6 = RAW7.search(s), RAW6.search(s)
        if not (m7 or m6):
            continue
        # The subject name is either on this line or just above it.
        owner = None
        for back in range(0, 3):
            if i - back < 0:
                break
            probe = lines[i - back].strip()
            if title in probe:
                owner = probe
                break
            if back and re.search(r"A Level |AS ", probe) and title not in probe:
                break          # a different qualification's block
        if owner is None:
            continue
        if m7:
            vals = tuple(int(v) for v in m7.groups())
        else:
            g = tuple(int(v) for v in m6.groups())
            vals = (g[0], None) + g[1:]
        label = None
        for fwd in (1, 2):
            if i + fwd < len(lines):
                lab = LABEL.match(lines[i + fwd].strip())
                if lab:
                    label = lab.group(1).lstrip("0") or "0"
                    break
        out.append((vals, label))
    return out


def extract(subject_name, expected_max, years, code=None, level="A Level"):
    """{(paper, year): (max, a*, a, b, c, d, e)}

    `level` picks which block of the document to read: "A Level" or "AS". The
    AS tables use the same no-A* layout this parser already handles for
    Mathematics at A-level, so nothing else changes — but the title must be
    exact, because "AS Mathematics" and "AS Further Mathematics" are different
    qualifications and one is a substring of the other.
    """
    title = level + " " + subject_name
    out, problems = {}, []
    for year in years:
        path = os.path.join(SP, "pearson%s.pdf" % year)
        if not os.path.exists(path):
            problems.append("%s: no PDF" % year)
            continue
        lines = []
        for pg in PdfReader(path).pages:
            lines += (pg.extract_text() or "").splitlines()

        rows = _rows_for(lines, title)
        found, spare = {}, []
        for vals, label in rows:
            if label and label in expected_max:
                want = expected_max[label]
                if label not in found or vals[0] == want:
                    found[label] = vals
            else:
                spare.append(vals)

        # A single unlabelled row can be placed when exactly one paper is still
        # missing and the row's max mark matches it.
        missing = [p for p in expected_max if p not in found]
        if len(missing) == 1 and len(spare) == 1 and spare[0][0] == expected_max[missing[0]]:
            found[missing[0]] = spare[0]
            NOTES.append("%s %s: Paper %s had no label; placed by max mark (%d)"
                         % (subject_name, year, missing[0], spare[0][0]))

        for paper, want in expected_max.items():
            if paper not in found:
                problems.append("%s: Paper %s missing" % (year, paper))
            elif found[paper][0] != want:
                problems.append("%s: Paper %s max %d, expected %d"
                                % (year, paper, found[paper][0], want))
            else:
                out[(paper, year)] = found[paper]
    return out, problems


if __name__ == "__main__":
    YEARS = ["2019", "2022", "2023", "2024", "2025"]
    for name, exp in (("Physics", {"1": 90, "2": 90, "3": 120}),
                      ("Chemistry", {"1": 90, "2": 90, "3": 120}),
                      ("Biology A (Salters Nuffield)", {"1": 100, "2": 100, "3": 100})):
        data, probs = extract(name, exp, YEARS)
        print("=== %s: %d rows ===" % (name, len(data)))
        print("   PROBLEMS:" if probs else "   all papers parsed for every series")
        for p in probs[:8]:
            print("     -", p)
    for n in NOTES:
        print("NOTE:", n)
