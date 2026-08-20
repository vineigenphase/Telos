"""Generate PWA icon PNGs: a "T" whose crossbar is a row of heatmap cells in
the same red -> teal scale used on the real topic heatmap (.hm-cell.pct-* in
telos.css), sitting on the sidebar's gradient mark. Re-run after any change
to either color scale.

Usage: .venv\\Scripts\\python.exe scripts\\generate_icons.py
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "static", "icons")

ACCENT = (139, 92, 246)       # #8b5cf6 — sidebar mark gradient start
ACCENT_DARK = (109, 40, 217)  # #6d28d9 — sidebar mark gradient end

# .hm-cell.pct-0 .. .pct-90, weakest to strongest, straight from telos.css.
HEATMAP_SCALE = [
    (239, 68, 68),    # pct-0  red
    (249, 115, 22),   # pct-50 orange
    (234, 179, 8),    # pct-60 gold
    (132, 204, 22),   # pct-70 lime
    (34, 197, 94),    # pct-80 green
    (20, 184, 166),   # pct-90 teal
]


def gradient_square(size, radius_ratio):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            r = int(ACCENT[0] + (ACCENT_DARK[0] - ACCENT[0]) * t)
            g = int(ACCENT[1] + (ACCENT_DARK[1] - ACCENT[1]) * t)
            b = int(ACCENT[2] + (ACCENT_DARK[2] - ACCENT[2]) * t)
            img.putpixel((x, y), (r, g, b, 255))
    if radius_ratio <= 0:
        return img
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=255
    )
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def add_sheen(img, size):
    """A faint diagonal highlight, top-left to center, so the mark doesn't
    read as flat — subtle, not a gloss sticker."""
    sheen = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheen)
    d.ellipse([-size * 0.3, -size * 0.5, size * 0.75, size * 0.55],
              fill=(255, 255, 255, 28))
    img.alpha_composite(sheen)


def draw_mosaic_t(img, x0, y0, x1, y1):
    """Draws a T inside the given box: crossbar = 6 heatmap-scale cells
    (weak -> strong, left to right), stem = solid white, rounded only where
    it meets open air so the bar-to-stem joint stays a clean right angle."""
    w = x1 - x0
    h = y1 - y0
    draw = ImageDraw.Draw(img)

    bar_h = h * 0.30
    bar_y0, bar_y1 = y0, y0 + bar_h
    stem_w = w * 0.30
    stem_x0 = x0 + (w - stem_w) / 2
    stem_x1 = stem_x0 + stem_w
    stem_y0, stem_y1 = bar_y1, y1

    # Stem first (bottom corners only, so its top edge is a flat seam
    # against the crossbar rather than a visible rounded notch).
    draw.rounded_rectangle(
        [stem_x0, stem_y0, stem_x1, stem_y1],
        radius=w * 0.05,
        fill=(255, 255, 255, 255),
        corners=(False, False, True, True),
    )

    # Crossbar: N heatmap cells with a hairline gap, background peeking
    # through — reads as a data strip, not just a plain bar.
    n = len(HEATMAP_SCALE)
    gap = w * 0.018
    cell_w = (w - gap * (n - 1)) / n
    radius = min(cell_w, bar_h) * 0.28
    for i, color in enumerate(HEATMAP_SCALE):
        cx0 = x0 + i * (cell_w + gap)
        cx1 = cx0 + cell_w
        draw.rounded_rectangle([cx0, bar_y0, cx1, bar_y1], radius=radius,
                               fill=(*color, 255))


def make_icon(size, radius_ratio, name):
    img = gradient_square(size, radius_ratio)
    m = size * 0.16
    draw_mosaic_t(img, m, m, size - m, size - m)
    add_sheen(img, size)
    img.save(os.path.join(OUT, name))
    print("wrote", name)


def make_maskable(size, name):
    # Full-bleed background (OS applies its own mask), T shrunk into the
    # ~80% safe zone so Android doesn't crop it.
    img = gradient_square(size, 0)
    inset = size * 0.28
    draw_mosaic_t(img, inset, inset, size - inset, size - inset)
    add_sheen(img, size)
    img.save(os.path.join(OUT, name))
    print("wrote", name)


def make_apple_touch(size, name):
    # Apple ignores alpha and applies its own rounding, so ship opaque.
    img = gradient_square(size, 0)
    m = size * 0.18
    draw_mosaic_t(img, m, m, size - m, size - m)
    add_sheen(img, size)
    img.convert("RGB").save(os.path.join(OUT, name))
    print("wrote", name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    make_icon(192, 0.25, "icon-192.png")
    make_icon(512, 0.25, "icon-512.png")
    make_maskable(512, "maskable-512.png")
    make_apple_touch(180, "apple-touch-180.png")
