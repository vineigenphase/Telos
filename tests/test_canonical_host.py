"""Phase 0.4 checks: canonical redirect, cookie flags, robots/sitemap."""
import os, sys

os.environ["CANONICAL_HOST"] = "telosapp.co.uk"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as A  # noqa: E402

app = A.app
app.debug = False
c = app.test_client()
fails = []


def check(label, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f"  (want {want!r})"))
    if not ok:
        fails.append(label)


# 1. www -> apex, https, 301
r = c.get("/login", base_url="https://www.telosapp.co.uk")
check("www GET /login status", r.status_code, 301)
check("www GET /login location", r.headers.get("Location"), "https://telosapp.co.uk/login")

# 2. old railway host -> apex, query string preserved
r = c.get("/subscription?from=pro-zone", base_url="https://web-production-37ddd9.up.railway.app")
check("railway host location", r.headers.get("Location"),
      "https://telosapp.co.uk/subscription?from=pro-zone")

# 3. http on the canonical host -> https
r = c.get("/login", base_url="http://telosapp.co.uk")
check("http -> https status", r.status_code, 301)
check("http -> https location", r.headers.get("Location"), "https://telosapp.co.uk/login")

# 4. already canonical + https -> served, not redirected
r = c.get("/login", base_url="https://telosapp.co.uk")
check("canonical GET /login status", r.status_code, 200)
check("canonical page has rel=canonical",
      b'<link rel="canonical" href="https://telosapp.co.uk/login">' in r.data, True)

# 5. POST is never 301'd (would drop the body — breaks the Stripe webhook)
r = c.post("/subscription/webhook", data=b"{}", base_url="https://www.telosapp.co.uk")
check("POST webhook not redirected", r.status_code != 301, True)
check("POST webhook rejects bad signature", r.status_code, 400)

# 6. robots + sitemap, absolute canonical URLs
r = c.get("/robots.txt", base_url="https://telosapp.co.uk")
check("robots status", r.status_code, 200)
check("robots sitemap line",
      b"Sitemap: https://telosapp.co.uk/sitemap.xml" in r.data, True)
r = c.get("/sitemap.xml", base_url="https://telosapp.co.uk")
check("sitemap status", r.status_code, 200)
check("sitemap has canonical loc",
      b"<loc>https://telosapp.co.uk/subscription</loc>" in r.data, True)
check("sitemap lists no private page", b"/admin" in r.data, False)

# 7. cookie flags
check("SESSION_COOKIE_SECURE", app.config["SESSION_COOKIE_SECURE"], True)
check("SESSION_COOKIE_HTTPONLY", app.config["SESSION_COOKIE_HTTPONLY"], True)
check("SESSION_COOKIE_SAMESITE", app.config["SESSION_COOKIE_SAMESITE"], "Lax")
check("PREFERRED_URL_SCHEME", app.config["PREFERRED_URL_SCHEME"], "https")

# 8. login still sets a session cookie across the https canonical host
r = c.post("/login", data={"email": "nobody@example.com", "password": "wrong"},
           base_url="https://telosapp.co.uk", follow_redirects=False)
check("login POST reachable (not 301)", r.status_code != 301, True)

print()
print("ALL PASS" if not fails else f"FAILURES: {fails}")
sys.exit(1 if fails else 0)
