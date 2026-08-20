"""Generate PWA icon PNGs from the same gradient mark used by .sidebar-logo
.logo-mark in telos.css (linear-gradient(135deg, #8b5cf6, #6d28d9), a bold
white "T"). Re-run this after any change to that gradient or wordmark.

Usage: .venv\\Scripts\\python.exe scripts\\generate_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "static", "icons")

ACCENT = (139, 92, 246)   # #8b5cf6
ACCENT_DARK = (109, 40, 217)  # #6d28d9
FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"


def gradient_square(size, radius_ratio):
    """135deg linear gradient, top-left (light) to bottom-right (dark), with
    rounded corners. radius_ratio matches the CSS mark's 8px/32px = 0.25."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            r = int(ACCENT[0] + (ACCENT_DARK[0] - ACCENT[0]) * t)
            g = int(ACCENT[1] + (ACCENT_DARK[1] - ACCENT[1]) * t)
            b = int(ACCENT[2] + (ACCENT_DARK[2] - ACCENT[2]) * t)
            img.putpixel((x, y), (r, g, b, 255))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=255
    )
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def draw_t(img, size, scale=0.55):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, int(size * scale))
    bbox = draw.textbbox((0, 0), "T", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
              "T", font=font, fill=(255, 255, 255, 255))
    return img


def make_icon(size, radius_ratio, name, letter_scale=0.55):
    img = gradient_square(size, radius_ratio)
    draw_t(img, size, letter_scale)
    img.save(os.path.join(OUT, name))
    print("wrote", name)


def make_maskable(size, name):
    # Maskable: full-bleed square background (no rounding — the OS masks it),
    # logo shrunk to fit the ~80% safe zone so Android doesn't crop it.
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg = gradient_square(size, 0)  # radius 0 = plain square, full bleed
    img.paste(bg, (0, 0), bg)
    draw_t(img, size, scale=0.42)  # smaller so the T sits inside the safe zone
    img.save(os.path.join(OUT, name))
    print("wrote", name)


def make_apple_touch(size, name):
    # Apple ignores alpha and adds its own corner rounding, so ship an opaque
    # full-bleed square.
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg = gradient_square(size, 0)
    img.paste(bg, (0, 0), bg)
    draw_t(img, size, scale=0.5)
    img.convert("RGB").save(os.path.join(OUT, name))
    print("wrote", name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    make_icon(192, 0.25, "icon-192.png")
    make_icon(512, 0.25, "icon-512.png")
    make_maskable(512, "maskable-512.png")
    make_apple_touch(180, "apple-touch-180.png")
