"""Pull the numbered topic headings for each Edexcel FM option paper.

The spec is a three-column table, so pypdf emits it a cell at a time: a bare
number, then the topic name (often wrapped over two or three lines), then the
"1.1 ..." sub-items. A heading is therefore the run of text between a bare
number and the first sub-item marker.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

SP = DOCS
text = open(os.path.join(SP, "fm_spec.txt"), encoding="utf-8").read()
lines = [l.rstrip() for l in text.splitlines()]

SECTIONS = [
    ("FP1", "Paper 3A: Further Pure Mathematics 1"),
    ("FP2", "Paper 4A: Further Pure Mathematics 2"),
    ("FS1", "Paper 3B: Further Statistics 1"),
    ("FS2", "Paper 4B: Further Statistics 2"),
    ("FM1", "Paper 3C: Further Mechanics 1"),
    ("FM2", "Paper 4C: Further Mechanics 2"),
    ("D1",  "Paper 3D: Decision Mathematics 1"),
    ("D2",  "Paper 4D: Decision Mathematics 2"),
]

starts = {}
for code, title in SECTIONS:
    for i, l in enumerate(lines):
        if l.strip().startswith(title):
            starts[code] = i
            break

order = sorted(starts.items(), key=lambda kv: kv[1])
bounds = {}
for n, (code, i) in enumerate(order):
    end = order[n + 1][1] if n + 1 < len(order) else len(lines)
    bounds[code] = (i, end)

SUB = re.compile(r"^\s*\d+\.\d+")
NUM = re.compile(r"^\s*(\d{1,2})\s*$")

for code, _t in SECTIONS:
    if code not in bounds:
        print(f"{code}: section not found"); continue
    lo, hi = bounds[code]
    topics, seen = [], set()
    i = lo
    while i < hi:
        m = NUM.match(lines[i])
        if m:
            n = int(m.group(1))
            words, j = [], i + 1
            while j < hi and not SUB.match(lines[j]) and len(words) < 6:
                w = lines[j].strip()
                if not w or NUM.match(lines[j]):
                    break
                words.append(w)
                j += 1
            name = " ".join(words).strip()
            name = re.sub(r"\s+", " ", name)
            if name and 3 <= len(name) <= 46 and n not in seen and not name[0].islower():
                seen.add(n)
                topics.append(name)
            i = j
        else:
            i += 1
    print(f'    "{code}": {topics},')
