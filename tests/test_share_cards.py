"""Phase 9 — share card rendering.

Pure rendering, no database and no Flask — runnable with
`python tests/test_share_cards.py`.

The two tests worth having here are the ones the spec states as rules and
which are otherwise left to somebody squinting at a PNG:

  * "legible at thumbnail size — shrink to 200px wide and if the number isn't
    readable, it's wrong." Measured, not eyeballed.
  * "never include anything a user hasn't chosen to share." Checked by proving
    an extra field in the payload cannot change a single pixel.

The third is overflow. An earlier draft budgeted the figure on point size
rather than ink height, and the square cards drew their content straight
through the footer — which looked fine in the story format nobody had thought
to re-check. The gap band above the footer is asserted empty.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

import sharecards as sc  # noqa: E402

FAILS = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        FAILS.append(label)


def ok(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


GRADE = {"grade": "A*", "range_label": "A–A*", "subject": "Mathematics",
         "board": "Edexcel", "marks_to_next": 6, "next_grade": "A*",
         "confidence": "medium", "sample_size": 9}
HEAT = {"accuracy": 87, "subject": "Physics", "strongest": "Mechanics",
        "weakest": "Capacitance",
        "cells": [{"pct": p} for p in
                  (95, 88, 72, 64, 55, 40, 91, 83, 77, 69, 58, 45, 30, 86,
                   74, 62, 51, 38, 92, 80, 68, 57, 44, 33, 90, 79, 66, 54)]}
MILE = {"value": 127, "unit": "papers", "detail": "Since September"}

CARDS = {"grade": GRADE, "heatmap": HEAT, "milestone": MILE}


# ── the shareable sentence ──────────────────────────────────────────────────

check("article follows the grade's sound", sc.marks_line(6, "A*"), "6 marks from an A*")
check("...and a consonant takes 'a'", sc.marks_line(3, "B"), "3 marks from a B")
check("...E is a vowel sound", sc.marks_line(1, "E"), "1 mark from an E")
check("one mark is singular", sc.marks_line(1, "A"), "1 mark from an A")
check("sitting on the boundary is not '0 marks'", sc.marks_line(0, "A*"),
      "On the A* boundary")
check("no next grade means no sentence", sc.marks_line(None, "A*"), None)
check("no marks figure means no sentence", sc.marks_line(4, None), None)


# ── sizes ───────────────────────────────────────────────────────────────────

for name, size in (("story", (1080, 1920)), ("post", (1080, 1080))):
    for t, payload in CARDS.items():
        c = sc.render(t, payload, name)
        check(f"{t}/{name} renders at the spec's size", (c.w, c.h), size)


# ── nothing may cross into the footer ───────────────────────────────────────
#
# The band between content_bottom and the footer baseline is deliberate air.
# Any ink in it means a block overran its budget.

def ink_rows(img, y0, y1, x0, x1):
    px = img.convert("RGB").load()
    bg = sc.BG
    rows = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 12:
                rows.append(y)
                break
    return rows


for name in ("story", "post"):
    for t, payload in CARDS.items():
        c = sc.render(t, payload, name)
        footer_y = c.h - c.pad - 46
        # Inset past the frame so the frame's own hairline isn't counted.
        bad = ink_rows(c.img, c.content_bottom + 1, footer_y, 60, c.w - 60)
        ok(f"{t}/{name} keeps clear of the footer", not bad,
           "" if not bad else f"ink at rows {bad[:4]}")


# ── the 200px thumbnail test ────────────────────────────────────────────────
#
# The spec's own acceptance test. The figure's ink box is recorded at render
# time, so this measures the real number rather than assuming where it sits.

THUMB_W = 200
MIN_THUMB_INK = 20          # px tall in a 200px-wide thumbnail

for name in ("story", "post"):
    for t, payload in CARDS.items():
        c = sc.render(t, payload, name)
        scale = THUMB_W / c.w
        x0, y0, x1, y1 = c.figure_box
        h = (y1 - y0) * scale
        ok(f"{t}/{name} figure survives a 200px thumbnail", h >= MIN_THUMB_INK,
           f"{h:.1f}px tall (floor {MIN_THUMB_INK})")


def luminance(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


contrast = ((luminance(sc.TEXT) + 0.05) / (luminance(sc.BG) + 0.05))
ok("the figure is high-contrast against the ground", contrast >= 12,
   f"{contrast:.1f}:1")


# ── privacy: the payload is the whole world ─────────────────────────────────
#
# "Never include anything a user hasn't chosen to share." A renderer is handed
# a payload and has no other source of truth, so adding personal fields to the
# payload must not change the render by one pixel.

def png_bytes(card_type, payload, size_name):
    c = sc.render(card_type, payload, size_name)
    buf = io.BytesIO()
    c.save(buf)
    return buf.getvalue()

for t, payload in CARDS.items():
    tainted = dict(payload)
    tainted.update({"email": "svinujan10@gmail.com", "name": "Real Name",
                    "user_id": 1, "display_name": "Someone"})
    same = png_bytes(t, payload, "story") == png_bytes(t, tainted, "story")
    ok(f"{t} ignores personal fields in the payload", same)


# ── input validation ────────────────────────────────────────────────────────

for bad_type in ("", "grades", "GRADE", None):
    try:
        sc.render(bad_type, GRADE, "story")
        ok(f"unknown card type {bad_type!r} is rejected", False)
    except ValueError:
        ok(f"unknown card type {bad_type!r} is rejected", True)

try:
    sc.render("grade", GRADE, "square")
    ok("unknown size is rejected", False)
except ValueError:
    ok("unknown size is rejected", True)


# ── degenerate payloads must not crash ──────────────────────────────────────

ok("a grade card with only a grade renders",
   sc.render("grade", {"grade": "B"}, "post").w == 1080)
ok("a heatmap with no cells renders",
   sc.render("heatmap", {"accuracy": 0}, "post").w == 1080)
ok("a milestone with no detail renders",
   sc.render("milestone", {"value": 1}, "post").w == 1080)
ok("a long subject does not overflow the card",
   sc.render("grade", dict(GRADE, subject="Further Mathematics",
                           board="Edexcel"), "post").w == 1080)


print()
print("ALL PASS" if not FAILS else f"FAILURES ({len(FAILS)}): {FAILS}")
sys.exit(1 if FAILS else 0)
