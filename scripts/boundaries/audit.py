"""What years does every offered paper actually have boundaries for?"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, sys, collections
sys.path.insert(0, REPO); os.chdir(REPO)
sys.stdout.reconfigure(encoding="utf-8")
from db import get_db
from paper_templates import TEMPLATES, qualification_level

TARGET = ["2019", "2022", "2023", "2024", "2025"]   # 2020/2021: no exam series

with get_db() as db:
    rows = db.execute("SELECT board, subject, paper_code, year FROM grade_boundaries").fetchall()
have = collections.defaultdict(set)
for r in rows:
    have[(r["board"], r["subject"], r["paper_code"])].add(str(r["year"]))

by_qual = collections.defaultdict(lambda: collections.Counter())
papers = collections.defaultdict(int)
for board, subjects in TEMPLATES.items():
    for subject, cfg in subjects.items():
        lvl = qualification_level(board, subject)
        for p in cfg["papers"]:
            papers[(board, subject, lvl)] += 1
            got = have[(board, subject, p["code"])]
            for y in TARGET:
                by_qual[(lvl, board, subject)][y] += 1 if y in got else 0

print("%-16s %-8s %-20s %s" % ("LEVEL", "BOARD", "SUBJECT", "  ".join(TARGET)))
missing_total = complete = 0
for (lvl, board, subject), c in sorted(by_qual.items()):
    n = papers[(board, subject, lvl)]
    cells = []
    full = True
    for y in TARGET:
        if c[y] == n:
            cells.append("  ok ")
        else:
            cells.append("%2d/%-2d" % (c[y], n))
            full = False
            missing_total += n - c[y]
    if full:
        complete += 1
    else:
        print("%-16s %-8s %-20s %s" % (lvl, board, subject, " ".join(cells)))
print()
print("qualifications fully covered 2019+2022-2025: %d of %d" % (complete, len(by_qual)))
print("missing (paper, year) pairs: %d" % missing_total)
