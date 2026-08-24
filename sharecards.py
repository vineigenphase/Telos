"""Phase 9 — server-rendered share cards.

Marketing, not a feature: these are free, and the point is that a screenshot
of one lands in a feed and sends someone back to telosapp.co.uk.

Design constraints, from the spec:

  * Two sizes — 1080x1920 (story) and 1080x1080 (post).
  * One dominant number, high contrast, legible at thumbnail size. The test is
    to shrink the render to 200px wide and see if the number still reads; that
    test runs in tests/test_share_cards.py rather than being left to eyeballs.
  * The Telos wordmark and a short URL on every card.
  * Never include anything the user hasn't chosen to share.

The last one is a hard rule and shapes the whole module: nothing here takes a
user row. A renderer is handed a plain payload dict of already-public facts,
and there is no code path from a card to an email address or a display name.
Board and subject are on the card because a grade is meaningless without them.

Visual language follows the app's Editorial treatment rather than the original
UI brief — warm neutral ground, brass accent, structure carried by hairline
rules and space rather than by fills, and every figure in Newsreader. Colours
come from telos.css through brand.css_colour, so a palette change reaches the
cards without anyone remembering to come back here.
"""
import os

from PIL import Image, ImageDraw, ImageFont

from brand import FONTS, css_colour, mark_glyph

# ── Sizes ────────────────────────────────────────────────────────────────────

STORY = (1080, 1920)
POST = (1080, 1080)
SIZES = {"story": STORY, "post": POST}

# ── Palette, read from the stylesheet ────────────────────────────────────────

BG = css_colour("bg", (11, 11, 12))
CARD = css_colour("card", (16, 16, 17))
BORDER = css_colour("border", (31, 31, 32))
TEXT = css_colour("text", (242, 241, 238))
MUTED = css_colour("muted", (113, 112, 107))
MUTED_2 = css_colour("muted-2", (138, 137, 133))
ACCENT = css_colour("accent", (201, 162, 39))
ACCENT_2 = css_colour("accent-2", (224, 190, 85))

HEATMAP_SCALE = [
    (90, css_colour("hm-90", (110, 143, 94))),
    (80, css_colour("hm-80", (138, 155, 85))),
    (70, css_colour("hm-70", (169, 147, 47))),
    (60, css_colour("hm-60", (201, 162, 39))),
    (50, css_colour("hm-50", (185, 120, 60))),
    (0, css_colour("hm-0", (168, 82, 70))),
]

SHARE_HOST = "telosapp.co.uk"

# ── Fonts ────────────────────────────────────────────────────────────────────

_FONT_FILES = {
    ("inter", 400): "Inter-Regular.ttf",
    ("inter", 600): "Inter-SemiBold.ttf",
    ("inter", 700): "Inter-Bold.ttf",
    ("serif", 400): "Newsreader-Regular.ttf",
    ("serif", 600): "Newsreader-SemiBold.ttf",
}
_font_cache = {}


def font(family, weight, size):
    key = (family, weight, size)
    if key not in _font_cache:
        path = os.path.join(FONTS, _FONT_FILES[(family, weight)])
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def heat_colour(pct):
    for floor, rgb in HEATMAP_SCALE:
        if pct >= floor:
            return rgb
    return HEATMAP_SCALE[-1][1]


# ── Drawing helpers ──────────────────────────────────────────────────────────

def tracked(d, xy, text, f, fill, tracking, anchor_x="left"):
    """Draw text with letter-spacing, which Pillow has no notion of.

    Used only for the wordmark and the small eyebrow labels. Returns the total
    width so callers can centre or measure.
    """
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x, y = xy
    if anchor_x == "center":
        x -= total / 2
    elif anchor_x == "right":
        x -= total
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + tracking
    return total


def fit_font(d, text, family, weight, target_w, start, floor=24):
    """Largest size at or below `start` whose text fits `target_w`."""
    size = start
    while size > floor and d.textlength(text, font=font(family, weight, size)) > target_w:
        size -= 4
    return font(family, weight, size)


def rule(d, x0, x1, y, colour=BORDER, width=2):
    d.line([(x0, y), (x1, y)], fill=colour, width=width)


# ── Card chrome ──────────────────────────────────────────────────────────────

class Canvas:
    """A card in progress: the ground, the frame, and the shared chrome."""

    def __init__(self, size_name):
        self.size_name = size_name
        self.w, self.h = SIZES[size_name]
        self.pad = 92
        self.figure_box = None
        self.img = Image.new("RGB", (self.w, self.h), BG)
        self.d = ImageDraw.Draw(self.img)
        self._frame()

    def _frame(self):
        # A single hairline inset, the same device the app uses to bound a
        # panel. No fill step between it and the ground — in this treatment
        # structure is rules and space, not stacked surfaces.
        m = 40
        self.d.rectangle([m, m, self.w - m - 1, self.h - m - 1],
                         outline=BORDER, width=2)

    def wordmark(self, y):
        """Mark plus TELOS, top-left. On every card, per the spec."""
        g = 54
        glyph = mark_glyph(g, ACCENT)
        self.img.paste(glyph, (self.pad, y), glyph)
        f = font("inter", 600, 34)
        tracked(self.d, (self.pad + g + 24, y + 10), "TELOS", f, TEXT, 6.5)
        return y + g

    def footer(self):
        """Short URL, bottom-centre. This is the whole call to action."""
        y = self.h - self.pad - 46
        f = font("inter", 400, 30)
        tracked(self.d, (self.w / 2, y), SHARE_HOST, f, MUTED, 4.0,
                anchor_x="center")

    def eyebrow(self, y, text):
        f = font("inter", 600, 27)
        tracked(self.d, (self.pad, y), text.upper(), f, MUTED, 3.4)
        return y + 34

    def figure(self, y, text, max_size, max_ink_h):
        """The one dominant number. Serif, near-white, as large as it fits.

        Fitted to a box in both directions, not to a point size. "A*", "127"
        and "A–A*" differ wildly in width, and the ink height of a given size
        differs again between digits and capitals — so a fixed size either
        overflows the long strings or wastes the short ones. Earlier this
        budgeted on point size alone and the square cards drew their content
        straight through the footer.
        """
        avail_w = self.w - 2 * self.pad
        size = max_size
        while size > 40:
            f = font("serif", 600, size)
            box = self.d.textbbox((0, 0), text, font=f)
            if (box[2] - box[0]) <= avail_w and (box[3] - box[1]) <= max_ink_h:
                break
            size -= 4
        f = font("serif", 600, size)
        box = self.d.textbbox((0, 0), text, font=f)
        self.d.text((self.pad - box[0], y - box[1]), text, font=f, fill=TEXT)
        # Recorded so the thumbnail-legibility test can measure the real ink
        # rather than assume where the figure landed.
        self.figure_box = (self.pad, y, self.pad + box[2] - box[0],
                           y + box[3] - box[1])
        return y + (box[3] - box[1])

    def body(self, y, lines, colour=MUTED_2, size=32, leading=46):
        f = font("inter", 400, size)
        for line in lines:
            self.d.text((self.pad, y), line, font=f, fill=colour)
            y += leading
        return y

    @property
    def content_bottom(self):
        """The floor. Below this is the footer's air, and then the footer."""
        return self.h - self.pad - 46 - 44

    def save(self, fh):
        self.img.save(fh, format="PNG", optimize=True)
        return self.img


# ── Layout constants per size ────────────────────────────────────────────────
#
# The story format has roughly twice the vertical room, and the temptation is
# to scale everything up to fill it. That is wrong for a feed: the figure is
# sized to be read at thumbnail scale in both, and the story simply gets more
# air around it.
#
# figure_max is a ceiling, not a target. Every renderer works out what the
# fixed blocks below the figure need, hands the figure the remainder, and lets
# it shrink. Nothing here may overrun Canvas.content_bottom.

LAYOUT = {
    "story": {"content_top": 620, "figure_max": 430, "grid_rows": 4},
    "post":  {"content_top": 300, "figure_max": 330, "grid_rows": 2},
}

GAP_AFTER_EYEBROW = 18
GAP_AFTER_FIGURE = 58
H_HEADING = 66
H_RULE = 40
LEADING = 46
FIGURE_MIN = 150


def _shell(size_name):
    c = Canvas(size_name)
    c.wordmark(c.pad)
    c.footer()
    return c, LAYOUT[size_name]


def marks_line(marks_to_next, next_grade):
    """"6 marks from an A*" — the single most shareable sentence Telos makes.

    Separated from the renderer because the only thing likely to be wrong here
    is the article, and checking that through a PNG would be absurd.
    """
    if marks_to_next is None or not next_grade:
        return None
    article = "an" if next_grade[0].upper() in "AEIOU" else "a"
    if marks_to_next == 0:
        # Reachable: prediction clamps marks_to_next at zero, so a student
        # sitting exactly on the boundary would otherwise read
        # "0 marks from an A*".
        return f"On the {next_grade} boundary"
    noun = "mark" if marks_to_next == 1 else "marks"
    return f"{marks_to_next} {noun} from {article} {next_grade}"


def _heading(c, y, text):
    c.d.text((c.pad, y), text, font=font("inter", 600, 38), fill=TEXT)
    return y + H_HEADING


# ── Card: predicted grade ────────────────────────────────────────────────────

def render_grade(payload, size_name="story"):
    """Predicted grade, and the marks to the next boundary.

    payload: grade, range_label, subject, board, marks_to_next, next_grade,
             confidence, sample_size
    """
    c, L = _shell(size_name)

    subject = payload.get("subject") or ""
    board = payload.get("board") or ""
    heading = " · ".join([p for p in (subject, board) if p])

    lines = []
    mtn, nxt = payload.get("marks_to_next"), payload.get("next_grade")
    sentence = marks_line(mtn, nxt)
    if sentence:
        lines.append(sentence)
    n = payload.get("sample_size")
    if n:
        lines.append(f"From {n} paper{'s' if n != 1 else ''} logged")
    conf = payload.get("confidence")
    if conf:
        lines.append(f"{conf.capitalize()} confidence")

    y = L["content_top"]
    below = (GAP_AFTER_FIGURE + (H_HEADING if heading else 0) + H_RULE + 40
             + LEADING * len(lines))
    y = c.eyebrow(y, "Predicted grade") + GAP_AFTER_EYEBROW
    ink = max(FIGURE_MIN, c.content_bottom - y - below)

    y = c.figure(y, payload.get("range_label") or payload["grade"],
                 L["figure_max"], ink) + GAP_AFTER_FIGURE
    if heading:
        y = _heading(c, y, heading)
    rule(c.d, c.pad, c.w - c.pad, y)
    c.body(y + H_RULE, lines, leading=LEADING)
    return c


# ── Card: heatmap snapshot ───────────────────────────────────────────────────

def render_heatmap(payload, size_name="story"):
    """Overall accuracy as the figure, with the topic grid beneath it.

    payload: accuracy, subject, cells [{topic, pct}], strongest, weakest
    """
    c, L = _shell(size_name)

    subject = payload.get("subject")
    lines = []
    if payload.get("strongest"):
        lines.append(f"Strongest: {payload['strongest']}")
    if payload.get("weakest"):
        lines.append(f"Weakest: {payload['weakest']}")

    cells = payload.get("cells") or []
    cols, gap = 8, 10
    cw = (c.w - 2 * c.pad - gap * (cols - 1)) / cols

    y = L["content_top"]
    y = c.eyebrow(y, "Accuracy") + GAP_AFTER_EYEBROW

    # Two blocks can flex here — how many grid rows, and whether strongest and
    # weakest get a line each or share one — so this walks a preference ladder
    # and takes the first arrangement that still leaves the figure readable at
    # thumbnail size. Dropping the grid is the last resort rather than the
    # first, because a heatmap card without the grid is just a number, and the
    # grid is the only thing that says which card this is.
    short = []
    if payload.get("strongest") and payload.get("weakest"):
        short = [f"{payload['strongest']} strongest · {payload['weakest']} weakest"]

    def below_for(rows, n_lines):
        grid = (rows * (cw + gap) + 26) if rows else 0
        return (GAP_AFTER_FIGURE + (H_HEADING if subject else 0) + H_RULE + 44
                + grid + LEADING * n_lines)

    max_rows = min(L["grid_rows"], -(-len(cells) // cols)) if cells else 0
    ladder = []
    for r in range(max_rows, 0, -1):
        ladder.append((r, lines))
        if short:
            ladder.append((r, short))
    ladder.append((0, lines))

    rows, lines = next(
        ((r, ln) for r, ln in ladder
         if c.content_bottom - y - below_for(r, len(ln)) >= FIGURE_MIN),
        (0, lines))

    ink = max(FIGURE_MIN, c.content_bottom - y - below_for(rows, len(lines)))
    y = c.figure(y, f"{int(round(payload['accuracy']))}%",
                 L["figure_max"], ink) + GAP_AFTER_FIGURE
    if subject:
        y = _heading(c, y, subject)
    rule(c.d, c.pad, c.w - c.pad, y)
    y += 44

    for i, cell in enumerate(cells[: cols * rows]):
        r, col = divmod(i, cols)
        x0 = c.pad + col * (cw + gap)
        y0 = y + r * (cw + gap)
        c.d.rounded_rectangle([x0, y0, x0 + cw, y0 + cw], radius=6,
                              fill=heat_colour(cell.get("pct", 0)))
    if rows:
        y += rows * (cw + gap) + 26

    c.body(y, lines, leading=LEADING)
    return c


# ── Card: milestone ──────────────────────────────────────────────────────────

def render_milestone(payload, size_name="story"):
    """Papers completed, or a streak.

    payload: value, unit ('papers' | 'days'), detail
    """
    c, L = _shell(size_name)

    unit = payload.get("unit", "papers")
    lines = [payload["detail"]] if payload.get("detail") else []

    y = L["content_top"]
    y = c.eyebrow(y, "Papers completed" if unit == "papers" else "Day streak")
    y += GAP_AFTER_EYEBROW
    below = GAP_AFTER_FIGURE + H_HEADING + H_RULE + 40 + LEADING * len(lines)
    ink = max(FIGURE_MIN, c.content_bottom - y - below)

    y = c.figure(y, str(payload["value"]), L["figure_max"], ink) + GAP_AFTER_FIGURE
    y = _heading(c, y, "past papers logged" if unit == "papers" else "days in a row")
    rule(c.d, c.pad, c.w - c.pad, y)
    c.body(y + H_RULE, lines, leading=LEADING)
    return c


RENDERERS = {
    "grade": render_grade,
    "heatmap": render_heatmap,
    "milestone": render_milestone,
}


def render(card_type, payload, size_name="story"):
    if card_type not in RENDERERS:
        raise ValueError(f"unknown card type: {card_type}")
    if size_name not in SIZES:
        raise ValueError(f"unknown size: {size_name}")
    return RENDERERS[card_type](payload, size_name)
