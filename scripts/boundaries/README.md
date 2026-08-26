# Boundary loaders

Every row in `grade_boundaries` was produced by a script in this directory
reading an awarding body's own document. None of it was typed by hand, and that
is deliberate: eighteen rows of six numbers entered by hand is exactly how the
OCR Physics data came to be shifted a column, which made the app predict U on
papers scoring 81–90%.

## The method

Each board gets the same treatment, and the order matters:

1. Download the board's own document.
2. Write or extend a parser for that board's layout.
3. **Check every component against its own expected max mark.** This has caught
   a genuine fault on every board it has been pointed at. It is not ceremony.
4. Generate the migration SQL *by script*, never by hand.
5. Cross-check against a second source where one exists.
6. Author topics from the specification.
7. Run the suites, then deploy.

A generator refuses to write anything if a single row fails its checks. A
mis-parse produces nothing rather than something plausible.

## Running one

The documents are not in this repository — about 60MB of PDFs and spreadsheets
that belong to the boards. Download what a script needs into `documents/`
(gitignored), or point `TELOS_BOUNDARY_DOCS` at wherever you already have them:

```
set TELOS_BOUNDARY_DOCS=C:\somewhere\else
.venv\Scripts\python.exe scripts\boundaries\gen_sqa_higher.py
```

A generator writes a migration into `migrations/` and prints what it skipped.
It never touches the database — applying the migration is a separate step:

```
railway run .venv\Scripts\python.exe migrations\run_migrations.py
```

`audit.py` is the one to run first if you are wondering what is missing. It
reports, per qualification, which of 2019 and 2022–2025 are fully covered.

**Note:** a migration already applied is skipped by filename, so regenerating
one that has shipped will not re-run it. Add a new migration instead.

### Dependencies

`pypdf`, `cryptography` and `openpyxl` are needed to read the documents and are
deliberately **not** in `requirements.txt` — the app never parses a PDF. Install
them when you need them and uninstall afterwards:

```
.venv\Scripts\python.exe -m pip install pypdf cryptography openpyxl
...
.venv\Scripts\python.exe -m pip uninstall -y pypdf cryptography openpyxl
```

`cryptography` is not optional for AQA's 2018 and 2019 AS documents: those are
encrypted where the later ones are not, and `pypdf` fails on them with an opaque
traceback rather than saying so.

## Where the documents come from

Filenames are what the scripts expect.

### AQA

| File | Source |
|---|---|
| `aqa_subj_YYYY.pdf` | A-level boundaries, [grade boundaries archive](https://www.aqa.org.uk/exams-administration/results-days/grade-boundaries/archive) |
| `aqa_as_2018.pdf` | `https://filestore.aqa.org.uk/over/stat_pdf/AQA-AS-RL-GDE-BDY-JUN-2018.PDF` |
| `aqa_as_2019.pdf` | `https://filestore.aqa.org.uk/over/stat_pdf/AQA-AS-RL-GDE-BDY-JUN-2019.PDF` |
| `aqa_as_2022.pdf` … `aqa_as_2024.pdf` | `https://filestore.aqa.org.uk/over/stat_pdf/AQA-AS-GDE-BDY-JUN-YYYY.PDF` |
| `aqa_as_2025.pdf` | A hashed `/files/…` URL — AQA moved off the predictable naming. Find it on the archive page. |
| `aqa_*_spec.pdf` | Subject specifications, for topic lists |

**AQA's A-level documents contain no AS tables at all.** They are separate
files. Assuming otherwise produces nothing, silently.

### OCR

| File | Source |
|---|---|
| `ocrYYYY.pdf` | A-level, and from 2022 the AS tables are a section of the same file |
| `ocr_as2019.pdf` | `https://www.ocr.org.uk/Images/552364-reformed-as-level-grade-boundaries-june-2019.pdf` |
| `ocr_*_spec.pdf` | Subject specifications |

In 2019 OCR published AS boundaries as their own document ("Reformed AS
Levels"), which has no AS section heading because the whole file is AS.
`ocr_as_extract.py` recognises that by content — AS headings and no A-level ones
— rather than by title.

### Pearson / Edexcel

| File | Source |
|---|---|
| `pearsonYYYY.pdf` | One document per series, carrying A-level and AS sections |
| `edx_*_spec.pdf` | Subject specifications |

### SQA

| File | Source |
|---|---|
| `sqa_2025.xlsx` | [Grade boundaries](https://www.sqa.org.uk/sqa/105159.html) — one file carries 2019 and 2022–2025 |
| `sqacomp_2022.xlsx` | `https://www.sqa.org.uk/sqa/files_ccc/component-marks-data-tables-2022.xlsx` |
| `sqacomp_2023.xlsx` | `https://www.sqa.org.uk/sqa/files_ccc/component-marks-datatables-2023.xlsx` |
| `sqacomp_2024.xlsx` | `https://www.sqa.org.uk/sqa/files_ccc/component-marks-tables-2024.xlsx` |
| `sqacomp_2025.xlsx` | `https://www.sqa.org.uk/sqa/files_ccc/assessment-marks-tables-2025.xlsx` |
| `ahspec_*.pdf` | Advanced Higher course specifications |

Note the four different filename conventions for what is the same publication.

## What each board does differently

Written down because every one of these cost real time to discover.

- **OCR** uses three table layouts, including a column-major one in 2023 where
  the numbers run down the columns rather than across the rows.
- **Pearson** uses four, including one number per line (2024), and one row whose
  paper label is missing entirely (Physics 2019 Paper 2, whose label reads
  `9PE0`). It also zero-pads paper labels to three digits in 2019 (`Paper 021`)
  where every other series writes `Paper 21`.
- **AQA** scales its language components and prints both the raw and the scaled
  row. Taking the last match doubles every boundary. It also breaks a row
  mid-code (German 2023 splits `7662/3T` across two lines).
- **AS tables carry six numbers where A-level tables carry seven.** Each board's
  AS rows are parsed by their own reader rather than a widened one: a parser
  reading both would, on a near miss, store an A boundary in the A\* column.
- **SQA** publishes boundaries for the whole course only and never per
  component, which is why its rows are the only derived ones in the table — see
  `derived_from_course` and migrations 037–039. It also renames its own
  components between years (`Assignment: Writing` vs `Assignment - Writing`;
  a comma replaced by a double space in 2023), and its component-marks
  spreadsheet has four different layouts across four years.

## Cancelled series

There are no 2020 or 2021 boundaries for any board, and there never will be.
Both series were cancelled; grades came from centre and teacher assessment and
nothing was published. `tests/test_boundaries.py` fails if such a row reappears.
