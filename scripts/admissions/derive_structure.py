"""Derive each ENGAA/NSAA paper's real structure from the paper itself.

The format changed mid-run and the secondary sources disagree about when and
how, so nothing here is typed from a summary. Every number this prints comes
out of the official question paper.

Two things are read per paper:

  * the instruction block on the front cover, which states the parts and how
    many questions each carries;
  * the actual question numbering through the body, which is the check on the
    cover. A cover that says 20 and a body that numbers to 26 means the cover
    was misread, and the body wins.

Run with the PDFs in scripts/admissions/documents/ (gitignored, ~19MB):

    .venv\\Scripts\\python.exe scripts\\admissions\\derive_structure.py
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.environ.get("TELOS_ADMISSIONS_DOCS", os.path.join(HERE, "documents"))


def text_of(path):
    from pypdf import PdfReader
    pages = []
    for p in PdfReader(path).pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception as e:                      # a page that will not render
            pages.append("")
            print(f"    ! page failed: {e}", file=sys.stderr)
    return pages


# "Part A" / "Section 1" style headings, and any sentence stating a count.
COUNT = re.compile(
    r"(\d{1,2})\s+(?:multiple[- ]choice\s+)?questions?", re.I)
PART = re.compile(r"\bPart\s+([A-D])\b", re.I)
SECTION = re.compile(r"\bSection\s+([12])\b", re.I)
# A question number at the start of a line: "12" or "12." possibly indented.
QNUM = re.compile(r"^\s*(\d{1,2})[.)]?\s", re.M)


def numbering(pages):
    """The highest question number reached, and whether it restarts.

    A restart means the paper numbers each part from 1, which tells us the
    parts are separate mark pools rather than one continuous run.
    """
    seen, restarts, last = [], 0, 0
    for text in pages:
        for m in QNUM.finditer(text):
            n = int(m.group(1))
            if n > 30:                              # not a question number
                continue
            if n == 1 and last > 3:
                restarts += 1
            if n == last + 1 or (n == 1 and last > 3):
                seen.append(n)
                last = n
    return (max(seen) if seen else 0), restarts, len(seen)


def main():
    if not os.path.isdir(DOCS):
        print(f"no documents directory at {DOCS}", file=sys.stderr)
        return 1
    files = sorted(f for f in os.listdir(DOCS) if f.lower().endswith(".pdf"))
    if not files:
        print(f"no PDFs in {DOCS}", file=sys.stderr)
        return 1

    for f in files:
        path = os.path.join(DOCS, f)
        pages = text_of(path)
        cover = "\n".join(pages[:2])
        body = pages

        parts = sorted(set(m.group(1).upper() for m in PART.finditer(cover)))
        sections = sorted(set(m.group(1) for m in SECTION.finditer(cover)))
        counts = [int(m.group(1)) for m in COUNT.finditer(cover)
                  if 5 <= int(m.group(1)) <= 60]
        top, restarts, run = numbering(body)

        print(f"\n=== {f}  ({len(pages)} pages)")
        print(f"    cover mentions : parts {parts or '—'}  sections {sections or '—'}")
        print(f"    counts on cover: {counts or '—'}")
        print(f"    body numbering : reaches {top}, {restarts} restart(s), {run} in sequence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
