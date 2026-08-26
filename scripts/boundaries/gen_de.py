"""Emit migration 010: the official D and E boundaries for every stored row.

Parsed from the same OCR and Pearson PDFs the A*/A/B/C figures came from, and
written by machine rather than transcribed. Every generated UPDATE is checked
against the row it targets: the D/E it sets must sit below that row's C and
stay above zero, so a mis-parse fails here instead of quietly lowering
somebody's predicted grade.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
from pypdf import PdfReader

SP = DOCS
sys.path.insert(0, REPO)

# ── OCR Physics A (H556) ────────────────────────────────────────────────────
OCR_ONE = re.compile(
    r"^H556\s+(0\d)\s+.+?\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
OCR_RAW = re.compile(r"^Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
OCR_COMP = re.compile(r"^(0\d)\s+(\D.*)$")
PAPER = {"01": "Paper 1", "02": "Paper 2", "03": "Paper 3"}

def ocr_block(lines):
    i = next(n for n, l in enumerate(lines) if l.strip() == "A Level Physics A")
    out = []
    for l in lines[i + 1:]:
        s = l.strip()
        if s.startswith(("A Level ", "AS Level ", "AS GCE ")):
            break
        out.append(s)
    return out

de = {}   # (subject, board, paper_code, year) -> (d, e)

for year in ("2018", "2019", "2022", "2023", "2024", "2025"):
    lines = []
    for pg in PdfReader(os.path.join(SP, f"ocr{year}.pdf")).pages:
        lines += (pg.extract_text() or "").splitlines()
    found = {}
    for l in (x.strip() for x in lines):
        m = OCR_ONE.match(l)
        if m:
            code, mx, a_s, a, b, c, d, e = m.groups()
            found[code] = (int(d), int(e))
    if not found:
        blk = ocr_block(lines)
        comps = [OCR_COMP.match(l).group(1) for l in blk if OCR_COMP.match(l)]
        raws = [OCR_RAW.match(l).groups() for l in blk if OCR_RAW.match(l)]
        for code, r in zip(comps, raws):
            found[code] = (int(r[5]), int(r[6]))
    for code, (d, e) in found.items():
        if code in PAPER:
            de[("Physics", "OCR A", PAPER[code], year)] = (d, e)

# ── Pearson Maths / Further Maths ───────────────────────────────────────────
PE_DATA = re.compile(
    r"^(9FM0|9MA0)\s+A Level .*?Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*$")
PE_LABEL = re.compile(r"^(Paper\s+\d[A-D]?)\s*$")
PE_MAP = {("9FM0", "Paper 1"): ("Further Maths", "CP1"),
          ("9FM0", "Paper 2"): ("Further Maths", "CP2"),
          ("9FM0", "Paper 3C"): ("Further Maths", "FM1"),
          ("9FM0", "Paper 3B"): ("Further Maths", "FS1"),
          ("9MA0", "Paper 1"): ("Maths", "Pure 1"),
          ("9MA0", "Paper 2"): ("Maths", "Pure 2"),
          ("9MA0", "Paper 3"): ("Maths", "Stats&Mech")}

for year in ("2022", "2023", "2024", "2025"):
    path = os.path.join(SP, f"pearson{year}.pdf")
    if not os.path.exists(path):
        continue
    lines = []
    for pg in PdfReader(path).pages:
        lines += (pg.extract_text() or "").splitlines()
    for i, l in enumerate(lines):
        m = PE_DATA.match(l.strip())
        if not m or i + 1 >= len(lines):
            continue
        lab = PE_LABEL.match(lines[i + 1].strip())
        if not lab:
            continue
        key = (m.group(1), lab.group(1))
        if key in PE_MAP:
            subject, paper = PE_MAP[key]
            de[(subject, "Edexcel", paper, year)] = (int(m.group(7)), int(m.group(8)))

# ── Check each value against the row it will update ─────────────────────────
os.environ.pop("CANONICAL_HOST", None)
import app as A
with A.get_db() as db:
    stored = {(r["subject"], r["board"], r["paper_code"], r["year"]): r["c_boundary"]
              for r in db.execute("SELECT * FROM grade_boundaries").fetchall()}

updates, skipped, bad = [], [], []
for key in sorted(de):
    d, e = de[key]
    c = stored.get(key)
    if c is None:
        skipped.append(key)                       # no such row (e.g. 2018/2019 Edexcel)
        continue
    if not (c > d > e > 0):
        bad.append((key, c, d, e))
        continue
    subject, board, paper, year = key
    updates.append(
        f"UPDATE grade_boundaries SET d_boundary = {d}, e_boundary = {e}\n"
        f" WHERE subject = '{subject}' AND board = '{board}'"
        f" AND paper_code = '{paper.replace(chr(39), chr(39)*2)}' AND year = '{year}';")

if bad:
    print("REFUSING TO WRITE — D/E do not sit below C:")
    for b in bad:
        print("   ", b)
    raise SystemExit(1)

header = f'''-- 010_de_values.sql
-- The official D and E boundaries, for every row where the board publishes them.
--
-- Generated from the same OCR and Pearson PDFs as the A*/A/B/C figures, by
-- script rather than by hand. Each value was checked against the row it
-- updates: D and E must fall below that row's C boundary and stay above zero.
--
-- {len(updates)} rows updated. {len(skipped)} official rows had no matching row here
-- and were skipped rather than inserted — this migration only fills in grades
-- for boundaries that already exist.
--
-- Rows left with NULL d/e keep the old behaviour: prediction.boundary_ladder
-- infers them from the mean gap, exactly as it did for every row before this.
--
-- Idempotent: re-running sets the same values.

'''
out = os.path.join(MIGRATIONS, "010_de_values.sql")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(header + "\n".join(updates) + "\n")
print(f"wrote {len(updates)} updates; skipped {len(skipped)} unmatched official rows")
for k in skipped[:6]:
    print("   skipped:", k)
