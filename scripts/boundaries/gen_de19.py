"""Migration 011: official D and E for the June 2019 Edexcel rows.

2019's table is laid out differently from later years — the header reads
"Max Mark A B C D E U", with no A* column at component level, and the paper
labels are zero-padded ("Paper 01"). Getting that wrong would shift a column,
which is the exact fault this whole exercise started from.

So the generator does not trust its own parsing: for each row it also reads the
official A, B and C, and refuses to write D/E unless those three already equal
what is stored. If the mapping were off by one, A/B/C would disagree and
nothing would be written.
"""

import sys, os  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import DOCS, MIGRATIONS, REPO, require_docs  # noqa: E402
import os, re, sys
from pypdf import PdfReader

SP = DOCS
sys.path.insert(0, REPO)

# The code prefix is present for Further Maths and absent for Maths in this
# document, so it is optional and the subject name carries the identity.
DATA = re.compile(r"^(?:9FM0\s+)?A Level (Further Mathematics|Mathematics)\s+Raw\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+0\s*$")
LABEL = re.compile(r"^Paper\s+(\d{1,2}[A-D]?)\s*$")
MAP = {("Further Mathematics", "01"): ("Further Maths", "CP1"),
       ("Further Mathematics", "02"): ("Further Maths", "CP2"),
       ("Further Mathematics", "3C"): ("Further Maths", "FM1"),
       ("Further Mathematics", "3B"): ("Further Maths", "FS1"),
       ("Mathematics", "01"): ("Maths", "Pure 1"),
       ("Mathematics", "02"): ("Maths", "Pure 2"),
       ("Mathematics", "03"): ("Maths", "Stats&Mech")}

lines = []
for pg in PdfReader(os.path.join(SP, "pearson2019.pdf")).pages:
    lines += (pg.extract_text() or "").splitlines()

official = {}
for i, l in enumerate(lines):
    m = DATA.match(l.strip())
    if not m or i + 1 >= len(lines):
        continue
    lab = LABEL.match(lines[i + 1].strip())
    if not lab:
        continue
    key = (m.group(1), lab.group(1))
    if key in MAP:
        # Columns are A B C D E — there is no A* at component level in 2019.
        _mx, a, b, c, d, e = (int(x) for x in m.groups()[1:])
        official[MAP[key]] = (a, b, c, d, e)

os.environ.pop("CANONICAL_HOST", None)
import app as A
with A.get_db() as db:
    stored = {(r["subject"], r["paper_code"]):
              (r["a_boundary"], r["b_boundary"], r["c_boundary"], r["d_boundary"])
              for r in db.execute("SELECT * FROM grade_boundaries "
                                  "WHERE board='Edexcel' AND year='2019'").fetchall()}

updates, refused = [], []
for key, (a, b, c, d, e) in sorted(official.items()):
    st = stored.get(key)
    if st is None:
        refused.append((key, "no stored row"))
        continue
    if (st[0], st[1], st[2]) != (a, b, c):
        refused.append((key, f"A/B/C differ: stored {st[:3]} vs official {(a, b, c)}"))
        continue
    if not (c > d > e > 0):
        refused.append((key, f"D/E not below C: {(c, d, e)}"))
        continue
    subject, paper = key
    updates.append(f"UPDATE grade_boundaries SET d_boundary = {d}, e_boundary = {e}\n"
                   f" WHERE subject = '{subject}' AND board = 'Edexcel'"
                   f" AND paper_code = '{paper}' AND year = '2019';")

for r in refused:
    print("  refused:", r)
if not updates:
    print("nothing to write"); raise SystemExit(1)

header = f'''-- 011_de_values_2019.sql
-- Official D and E for the June 2019 Edexcel rows.
--
-- Split from 010 because 2019's table is laid out differently: the header is
-- "Max Mark A B C D E U" with no A* column at component level, and the paper
-- labels are zero-padded. The A* figures already stored for 2019 did not come
-- from this document — Pearson does not publish one at component level for that
-- series — and are left untouched.
--
-- Every value here was checked by re-reading the official A, B and C for the
-- same row and requiring them to equal what is already stored, so a column
-- shift in the parsing would have written nothing at all.
--
-- {len(updates)} rows. Idempotent.

'''
out = os.path.join(MIGRATIONS, "011_de_values_2019.sql")
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(header + "\n".join(updates) + "\n")
print(f"wrote {len(updates)} updates, refused {len(refused)}")
