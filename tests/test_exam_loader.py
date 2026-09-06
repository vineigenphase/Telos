import os
"""Exam Mode paper loader — every rejection rule, shown to fire.

Pure: `validate()` takes the spec table as an argument, so none of this needs a
database. Each check builds a valid paper, breaks exactly one thing, and
asserts the specific complaint appears. A validator that accepts everything
passes a suite that only ever feeds it good input, which is the failure mode
this avoids.
"""
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "content", "exam_papers"))
from loader import validate, spec_group, report  # noqa: E402

fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


def rejects(label, paper, fragment, table=None):
    """The paper must be rejected, AND for the stated reason."""
    errors, _ = validate(paper, table if table is not None else SPEC)
    hit = any(fragment.lower() in e.lower() for e in errors)
    print(f"{'PASS' if hit else 'FAIL'}  rejects {label}" +
          ("" if hit else f"  — no error matched {fragment!r}; got {errors[:3]}"))
    if not hit:
        fails.append(f"rejects {label}")


# The seeded spec table, as migration 041 writes it.
SPEC = {
    **{f"MM{i}": ["P1", "P2", "M2"] for i in range(1, 9)},
    **{f"M{i}": ["P1", "P2", "M1", "M2", "PHY"] for i in range(1, 8)},
    **{f"Arg{i}": ["P2"] for i in range(1, 5)},
    **{f"Prf{i}": ["P2"] for i in range(1, 6)},
    **{f"Err{i}": ["P2"] for i in range(1, 3)},
    **{f"P{i}": ["PHY"] for i in range(1, 8)},
}


def question(n, answer="C", options=None, **over):
    opts = options or {c: f"opt {c} q{n}" for c in "ABCDEF"}
    q = {
        "n": n, "topic": "t", "spec_refs": ["MM1.1"], "difficulty": 3,
        "stem_html": f"<p>q{n}</p>", "diagram_svg": None,
        "options": opts, "answer": answer,
        "solution_html": "<p>s</p>",
        "traps": {c: f"why {c} is wrong" for c in opts if c != answer},
    }
    q.update(over)
    return q


def paper(count=20, family="TMUA", module="P1", **over):
    p = {
        "paper_code": "X-1", "family": family, "module": module, "title": "T",
        "series": "s", "spec_version": "2026-27",
        "duration_sec": 4500 if family == "TMUA" else 2400,
        "questions": [question(i) for i in range(1, count + 1)],
    }
    p.update(over)
    return p


# ── the happy path, first — otherwise every rejection below proves nothing ──
errors, warnings = validate(paper(), SPEC)
check("a well-formed TMUA paper validates", errors, [])
check("and raises no warnings", warnings, [])

esat = paper(count=27, family="ESAT", module="M2")
errors, _ = validate(esat, SPEC)
check("a well-formed 27-question ESAT paper validates", errors, [])

# ── spec section 2's own rejection rules ───────────────────────────────────
rejects("a paper with the wrong question count", paper(count=19), "20 or 27")

p = paper()
p["questions"][3]["answer"] = "Z"
rejects("an answer that is not one of the options", p, "not one of the options")

p = paper()
del p["questions"][5]["traps"]["A"]
rejects("a wrong option with no trap", p, "no trap explaining")

p = paper()
p["questions"][2]["options"]["B"] = p["questions"][2]["options"]["A"]
rejects("two textually identical options", p, "textually identical")

# Whitespace and case must not let a duplicate through.
p = paper()
p["questions"][2]["options"]["B"] = "  " + p["questions"][2]["options"]["A"].upper() + " "
rejects("a duplicate differing only in case and spacing", p, "textually identical")

# ── the cross-module rule, which is the point of the spec table ────────────
#
# MM4 is the sine and cosine rules. ESAT Maths 1 candidates are not expected to
# recall them, so a Maths 1 paper citing MM4.1 must be rejected — this is the
# spec's hard rule made enforceable.
p = paper(count=27, family="ESAT", module="M1")
p["questions"][0]["spec_refs"] = ["MM4.1"]
rejects("sine/cosine (MM4) in ESAT Maths 1", p, "may not draw on")

# The same reference IS allowed in Maths 2, or the rule would be a blanket ban.
p = paper(count=27, family="ESAT", module="M2")
p["questions"][0]["spec_refs"] = ["MM4.1"]
errors, _ = validate(p, SPEC)
check("but MM4 is fine in ESAT Maths 2", errors, [])

# Logic and proof belong to TMUA Paper 2 alone.
p = paper(module="P1")
p["questions"][0]["spec_refs"] = ["Arg1"]
rejects("logic (Arg) in TMUA Paper 1", p, "may not draw on")

p = paper(module="P2")
p["questions"][0]["spec_refs"] = ["Arg1"]
errors, _ = validate(p, SPEC)
check("but Arg is fine in TMUA Paper 2", errors, [])

p = paper()
p["questions"][0]["spec_refs"] = ["ZZ9.1"]
rejects("a spec_ref not in the table at all", p, "not in the specification table")

p = paper()
p["questions"][0]["spec_refs"] = []
rejects("a question with no spec_refs", p, "no spec_refs")

# ── structural checks ──────────────────────────────────────────────────────
p = paper()
p["questions"][7]["n"] = 99
rejects("question numbers that do not run 1..N", p, "must run 1..")

p = paper()
p["questions"][1]["options"] = {"A": "a", "B": "b", "C": "c", "D": "d"}
p["questions"][1]["answer"] = "A"
p["questions"][1]["traps"] = {"B": "x", "C": "y", "D": "z"}
rejects("fewer than five options", p, "5-8 options")

p = paper()
p["questions"][0]["stem_html"] = "   "
rejects("an empty stem", p, "stem_html is empty")

p = paper()
p["questions"][0]["difficulty"] = 9
rejects("a difficulty outside 1-5", p, "difficulty must be 1-5")

p = paper()
p["questions"][0]["traps"]["C"] = "the correct answer should not have a trap"
rejects("a trap on the correct answer", p, "has a trap explanation")

p = paper()
p["questions"][0]["traps"]["Z"] = "no such option"
rejects("a trap for an option that does not exist", p, "do not exist")

rejects("a missing family", paper(family=None), "family must be")
rejects("an unknown module", paper(module="XX"), "module must be one of")

# ── the two stricter checks are WARNINGS, not rejections ───────────────────
#
# The spec says "20 or 27", so a 27-question TMUA paper satisfies its letter
# while being wrong. That is worth saying out loud and not worth blocking on.
p = paper(count=27, family="TMUA")
errors, warnings = validate(p, SPEC)
check("a 27-question TMUA paper is not rejected", errors, [])
check("but it is warned about",
      any("20 questions" in w for w in warnings), True)

p = paper(duration_sec=60)
errors, warnings = validate(p, SPEC)
check("a wrong duration is not rejected", errors, [])
check("but it is warned about", any("4500s" in w for w in warnings), True)

# ── spec_group parsing ─────────────────────────────────────────────────────
check("MM4.1 belongs to group MM4", spec_group("MM4.1"), "MM4")
check("M5.18 belongs to group M5", spec_group("M5.18"), "M5")
check("Arg1 is its own group", spec_group("Arg1"), "Arg1")
check("a deep sub-point still resolves", spec_group("MM7.2.3"), "MM7")
check("nonsense resolves to nothing", spec_group("not a ref"), None)
check("an empty ref resolves to nothing", spec_group(""), None)

# ── the report carries what the author needs ───────────────────────────────
p = paper()
for i, q in enumerate(p["questions"]):
    q["difficulty"] = 1 + (i % 5)
txt = report(p, *validate(p, SPEC))
check("the report shows the difficulty ramp", "difficulty ramp:" in txt, True)
check("and the spec coverage", "spec coverage:" in txt, True)
check("and says it is loadable", "OK — ready to load" in txt, True)

txt = report(paper(count=19), *validate(paper(count=19), SPEC))
check("a rejected paper says nothing was written",
      "REJECTED — nothing was written" in txt, True)

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
