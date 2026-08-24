import os
"""Phase 2.5 checks: manifest, service worker, offline shell, install-prompt
wiring, and the no-store guarantee on authenticated HTML."""
import json, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402

app = A.app
app.debug = False
app.config["WTF_CSRF_ENABLED"] = False
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


anon = app.test_client()
c = app.test_client()
with c.session_transaction() as s:      # log in as the founder account, read-only
    s["_user_id"] = "1"
    s["_fresh"] = True

# ── manifest ─────────────────────────────────────────────────────────────────
r = anon.get("/static/manifest.webmanifest")
check("manifest 200", r.status_code, 200)
manifest = json.loads(r.data)
check("manifest name", manifest["name"], "Telos — Past Paper Tracker")
check("manifest scope is site-wide", manifest["scope"], "/")
check("manifest has a maskable icon",
      any(i.get("purpose") == "maskable" for i in manifest["icons"]), True)
# Read --bg out of the stylesheet rather than restating it here. The splash
# screen and the page background have to agree, and hardcoding the hex in two
# places means a palette change silently breaks that agreement.
_css = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "static", "css", "telos.css")
with open(_css, encoding="utf-8") as _fh:
    _bg = re.search(r"--bg:\s*(#[0-9A-Fa-f]{3,8})", _fh.read()).group(1)
check("manifest theme matches --bg",
      manifest["theme_color"].lower(), _bg.lower())
check("manifest background matches --bg",
      manifest["background_color"].lower(), _bg.lower())

# ── service worker ───────────────────────────────────────────────────────────
r = anon.get("/sw.js")
check("sw.js 200", r.status_code, 200)
check("sw.js served as JS", r.mimetype, "application/javascript")
check("sw.js not cached by the browser", r.headers.get("Cache-Control"), "no-cache")
sw = r.data.decode()
check("cache name is versioned (not a literal placeholder)",
      "{{ cache_version }}" in sw, False)
for prefix in ("/admin", "/subscription", "/stripe"):
    check(f"sw.js never-caches {prefix}", f'"{prefix}"' in sw, True)
check("sw.js precaches the offline shell", '"/offline"' in sw, True)
check("sw.js skips waiting", "skipWaiting()" in sw, True)
check("sw.js claims clients", "clients.claim()" in sw, True)

# Two different deploys must not collide on the same cache name.
old_version = A.SW_CACHE_VERSION
A.SW_CACHE_VERSION = "deadbeef0000"
r2 = anon.get("/sw.js")
check("cache name changes with the deployed commit",
      "deadbeef0000" in r2.data.decode(), True)
A.SW_CACHE_VERSION = old_version

# ── offline shell ────────────────────────────────────────────────────────────
r = anon.get("/offline")
check("offline page 200 without login", r.status_code, 200)
check("offline page mentions being offline", "offline" in r.data.decode().lower(), True)

# ── manifest/meta wired into the pages people actually land on ──────────────
for path, needs_login in [("/login", False), ("/register", False)]:
    r = anon.get(path)
    html = r.data.decode()
    check(f"{path} links the manifest", 'rel="manifest"' in html, True)
    check(f"{path} has an apple-touch-icon", "apple-touch-icon" in html, True)

r = c.get("/")
html = r.data.decode()
check("dashboard links the manifest", 'rel="manifest"' in html, True)
check("dashboard carries the install-prompt paper count", 'data-papers-count="' in html, True)

# ── no-store on authenticated HTML, but not on public/static responses ──────
check("authenticated page is never cached", r.headers.get("Cache-Control"), "no-store")
r = anon.get("/login")
check("anonymous page is not forced no-store", r.headers.get("Cache-Control") == "no-store", False)
r = anon.get("/static/manifest.webmanifest")
check("manifest itself is not forced no-store", r.headers.get("Cache-Control") == "no-store", False)


# ── the mark agrees across every surface that draws it ───────────────────────
#
# The T exists twice: brand.py draws it for the PWA icons and the Phase 9 share
# cards, and the `logo` macro in _icons.html draws it for the web. Two
# definitions is the floor — the web needs real markup, not a PNG — but until
# now nothing checked they still agreed, and brand.py's own docstring said so.
# A silent drift here means the icon on a home screen stops matching the logo
# in the sidebar, which nobody would notice for months.
import brand  # noqa: E402

_macro = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "templates", "_icons.html"), encoding="utf-8").read()

_path = re.search(r'<path d="(M4 6[^"]*)"', _macro)
check("the web logo still declares a path", bool(_path), True)
if _path:
    # Rebuild the point list from the SVG path and compare it to the geometry
    # brand.py renders from. The path is a moveto followed by H/V commands, so
    # walking it with a pen position reproduces the corner list exactly.
    d = _path.group(1)
    m = re.match(r"M\s*([\d.]+)\s+([\d.]+)", d)
    x, y = float(m.group(1)), float(m.group(2))
    pts = [(x, y)]
    for cmd, val in re.findall(r"([HV])\s*([\d.]+)", d):
        if cmd == "H":
            x = float(val)
        else:
            y = float(val)
        pts.append((x, y))
    check("the web logo's geometry matches brand.T_POINTS",
          pts, [(float(a), float(b)) for a, b in brand.T_POINTS])

_shear = re.search(r"skewX\((-?[\d.]+)\)", _macro)
check("the web logo's shear matches brand.SHEAR_DEG",
      float(_shear.group(1)) if _shear else None, -brand.SHEAR_DEG)

_sw = re.search(r'stroke-width="([\d.]+)"', _macro)
check("the web logo's stroke width matches brand.STROKE_W",
      float(_sw.group(1)) if _sw else None, float(brand.STROKE_W))

print()
print("ALL PASS" if not fails else f"FAILURES ({len(fails)}): {fails}")
sys.exit(1 if fails else 0)
