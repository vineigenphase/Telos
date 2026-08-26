"""Migration 013: official D and E for the Edexcel Further Maths option papers.

Migration 010 mapped only the four papers the app offered at the time. Now that
all ten are selectable, the other six need their published D/E too.

Same safety rule as 011: each row's official A, B and C are re-read and must
equal what is already stored before D/E are written, so a mis-parse produces
nothing rather than a plausible wrong number.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
from pypdf import PdfReader

SP = DOCS
sys.path.insert(0, REPO)

MAP = {"3A": "FP1", "3B": "FS1", "3C": "FM1", "3D": "D1",
       "4A": "FP2", "4B": "FS2", "4C": "FM2", "4D": "D2",
       "1": "CP1", "01": "CP1", "2": "CP2", "02": "CP2"}

SEVEN = re.compile(r"Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")
SIX = re.compile(r"Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")
LABEL = re.compile(r"^Paper\s+(\d{1,2}[A-D]?)\s*$")

official = {}
for year in ("2019", "2022", "2023", "2024", "2025"):
    path = os.path.join(SP, f"pearson{year}.pdf")
    if not os.path.exists(path):
        continue
    lines = []
    for pg in PdfReader(path).pages:
        lines += (pg.extract_text() or "").splitlines()
    for i, l in enumerate(lines):
        s = l.strip()
        if "Further Mathematics" not in s or i + 1 >= len(lines):
            continue
        lab = LABEL.match(lines[i + 1].strip())
        if not lab or lab.group(1) not in MAP:
            continue
        m7, m6 = SEVEN.search(s), SIX.search(s)
        if m7:
            _mx, _a_s, a, b, c, d, e = (int(x) for x in m7.groups())
        elif m6:
            _mx, a, b, c, d, e = (int(x) for x in m6.groups())
        else:
            continue
        official[(MAP[lab.group(1)], year)] = (a, b, c, d, e)

os.environ.pop("CANONICAL_HOST", None)
import app as A
with A.get_db() as db:
    stored = {(r["paper_code"], r["year"]):
              (r["a_boundary"], r["b_boundary"], r["c_boundary"], r["d_boundary"])
              for r in db.execute("SELECT * FROM grade_boundaries WHERE board='Edexcel' "
                                  "AND subject='Further Maths'").fetchall()}

updates, refused, already = [], [], 0
for (paper, year), (a, b, c, d, e) in sorted(official.items()):
    st = stored.get((paper, year))
    if st is None:
        refused.append((paper, year, "no stored row")); continue
    if st[3] is not None:
        already += 1; continue                       # 010/011 already filled it
    if (st[0], st[1], st[2]) != (a, b, c):
        refused.append((paper, year, f"A/B/C differ: {st[:3]} vs {(a, b, c)}")); continue
    if not (c > d > e > 0):
        refused.append((paper, year, f"D/E not below C: {(c, d, e)}")); continue
    updates.append(f"UPDATE grade_boundaries SET d_boundary = {d}, e_boundary = {e}\n"
                   f" WHERE subject = 'Further Maths' AND board = 'Edexcel'"
                   f" AND paper_code = '{paper}' AND year = '{year}';")

for r in refused:
    print("  refused:", r)
print(f"already filled by earlier migrations: {already}")
if not updates:
    print("nothing new to write"); raise SystemExit(0)

header = f'''-- 013_de_option_papers.sql
-- Official D and E for the Edexcel Further Maths option papers.
--
-- Migration 010 filled only the four papers the catalogue offered at the time.
-- All ten are selectable now, so the remaining six get their published values.
--
-- Each row's official A, B and C were re-read and had to match what is already
-- stored before D/E were written; a mis-parse writes nothing.
--
-- {len(updates)} rows. Idempotent.

'''
out = os.path.join(MIGRATIONS, "013_de_option_papers.sql")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(header + "\n".join(updates) + "\n")
print(f"wrote {len(updates)} updates, refused {len(refused)}")
