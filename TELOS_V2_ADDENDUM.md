# Telos v2 — Addendum: domain, mobile UI, PWA

Slots into `TELOS_V2_SPEC.md`. Read that first — the same working rules apply
(one branch per phase, migrations numbered, feature flags, ask before deleting
user-facing routes).

Domain purchased: **telosapp.co.uk**

New phase order:
`0 → 0.4 → 0.6 → 1 → 2 → 3 → 2.5 → 5 → 4 → 9 → 6 → 7 → 10`

(Phase 8, the weekly parent report, was cut on 2026-08-25. See the spec.)

---

## Phase 0.4 — Point telosapp.co.uk at Railway

Branch: none needed (infrastructure, no code beyond the config commit at the end)

### What you (Claude Code) do

Railway's CLI can add the domain and print the exact DNS records needed:

```bash
railway link          # if not already linked to the web service
railway domain telosapp.co.uk
railway domain www.telosapp.co.uk
```

**Both a CNAME and a TXT record are required.** The CNAME routes traffic; the TXT
verifies ownership, and requests to the domain return 404 until Railway has verified
it. Print both records exactly as the CLI gives them and hand them to me — I'll add
them at the registrar.

**Railway does not publish a static IP, so A records will not work.** Do not suggest
one.

### The apex problem, and what to tell me

`telosapp.co.uk` with no subdomain is an apex domain. Standard DNS says apex records
must be A/AAAA, not CNAME — but Railway needs a CNAME. Railway supports CNAME
flattening and dynamic ALIAS/ANAME records as the workaround, and which one is
available depends entirely on the DNS provider.

So check with me which registrar the domain is at, then:

- **Cloudflare** — flattens CNAMEs at the root automatically. Just add the CNAME.
- **Registrar without flattening/ALIAS** (GoDaddy, Hostinger, most budget hosts) —
  the clean fix is to move nameservers to Cloudflare (free, ~10 minutes plus
  propagation). Recommend this rather than fighting it.
- **Fallback if I don't want to move DNS** — serve from `www.telosapp.co.uk` (a normal
  subdomain CNAME, no flattening needed) and set an HTTP 301 at the apex. Works, but
  the canonical hostname becomes the www one.

Do not put any other record at the same name as a CNAME — a CNAME can't coexist with
other records at that label.

### Code changes once DNS resolves

1. **Canonical host redirect.** Pick one hostname (prefer bare `telosapp.co.uk`) and
   301 everything else to it — the www variant *and* the old
   `web-production-37ddd9.up.railway.app`. Two hostnames serving the same content
   splits SEO and breaks the PWA scope in Phase 2.5.

```python
CANONICAL_HOST = os.environ.get("CANONICAL_HOST")  # "telosapp.co.uk"

@app.before_request
def _canonical_host():
    if not CANONICAL_HOST or app.debug:
        return
    if request.host.split(":")[0] != CANONICAL_HOST:
        return redirect(request.url.replace(request.host, CANONICAL_HOST, 1), 301)
```

2. **Force HTTPS** and set `PREFERRED_URL_SCHEME = "https"`.
3. **Session cookies:** `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`,
   `SESSION_COOKIE_SAMESITE="Lax"`.
4. **Update Stripe** — success/cancel URLs and the webhook endpoint must use the new
   host. A webhook still pointing at the Railway subdomain will keep working, but move
   it so there's one source of truth.
5. **Add `CANONICAL_HOST`** to Railway variables and `.env.example`.
6. **`robots.txt` and `sitemap.xml`** at the new host. Add a `<link rel="canonical">`
   to the base template.

### Acceptance

- `https://telosapp.co.uk` serves the app with a valid certificate
- `www.` and the `.up.railway.app` host both 301 to canonical
- Stripe test checkout completes end to end on the new domain
- Login persists across a redirect (catches a cookie-domain mistake)

**Note for later:** `.com` is not owned. If it's available it's worth ~£9 to hold
defensively, but that's my call, not a blocker.

---

## Phase 0.6 — Mobile-first foundation and the three screens that matter

Branch: `feat/mobile-first`

A-level students are phone-first. If the app is awkward on a phone, no marks get
logged, and with no data every Pro feature in the main spec is worthless. This phase
is therefore a prerequisite for the paid features, not a polish pass afterwards.

**Scope discipline: three screens only** — dashboard, papers list, mark entry. Do not
attempt a full-app redesign. Everything built from Phase 1 onward gets designed at
390px first so it never needs redoing.

### 0.6a — CSS foundation

Refactor the existing stylesheet to genuinely mobile-first: base styles target a
390px phone, media queries *add* at `min-width: 640px` (tablet) and `1024px`
(desktop). No `max-width` queries — those are desktop-first in disguise.

Add to the existing CSS custom properties:

```css
:root {
  --tap-min: 44px;              /* minimum touch target */
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-top: env(safe-area-inset-top, 0px);
  --nav-height: calc(56px + var(--safe-bottom));
}
```

Base template `<head>`:

```html
<meta name="viewport"
      content="width=device-width, initial-scale=1, viewport-fit=cover">
```

`viewport-fit=cover` is required for `env(safe-area-inset-*)` to return real values.

**Non-negotiable rules:**

| Rule | Why |
|---|---|
| All interactive elements ≥ 44×44px | Anything smaller is a mis-tap |
| All `<input>`/`<select>` font-size ≥ 16px | iOS Safari silently zooms the page on focus below 16px |
| No hover-only affordances | Touch has no hover — tooltips must become tap-to-reveal |
| Bottom nav padded by `--safe-bottom` | Otherwise the iPhone home indicator sits on top of it |
| `touch-action: manipulation` on buttons | Removes the 300ms tap delay |
| No horizontal page scroll at 320px | Test at iPhone SE width, not just 390 |

### 0.6b — Navigation

Current nav is 7 main items plus 4 account items. That does not survive a phone.

**Mobile (< 640px):** fixed bottom tab bar, exactly 5 items —
**Today · Papers · Heatmap · Revise · More**. "More" is a sheet containing Question
Bank, Stats, Pro Zone, Mocks, Subscription, and the admin links (admin only).

**Tablet/desktop (≥ 640px):** keep the existing top nav.

Render both from one `NAV_ITEMS` structure in config with a `primary` boolean, so the
two layouts can't drift.

Active tab needs a clear state — icon fill plus label colour, not colour alone.

### 0.6c — Mark entry (the most important screen in the product)

**Target: a full 8-question paper logged in under 60 seconds, thumb only, one hand.**

Route: `/papers/<id>/enter`

Do not shrink the desktop table. Build a dedicated flow:

- **One question per screen.** Question number and max marks large at the top.
- **Custom numeric keypad**, not the native keyboard. Use a grid of buttons plus a
  hidden input with `inputmode="numeric"`. The native iOS keyboard covers half the
  screen and animates in and out on every field.
- **Auto-advance** once the entered value can't be extended (e.g. max is 8 and they
  tap 8; max is 12 and they tap 1 then 2).
- **Swipe left/right** to move between questions; progress dots at the top, tappable.
- **Running total** and, once Phase 3 lands, a live predicted-grade preview at the top.
  That preview is the single best conversion surface in the app — a free user watching
  it update is the moment to show what Pro adds.
- **Save per question, not per paper** (`POST /papers/<id>/questions/<n>`, debounced
  ~400ms). A student who loses 8 questions to a dropped connection does not come back.
  Keep an optimistic local state and a small "saving/saved" indicator.
- **Undo** on the last entry.
- **Skip** — partial papers must be allowed. Don't require every question.

Accessibility: keypad buttons need `aria-label`s, and the flow must work with an
external keyboard on iPad (number keys, arrows, Enter).

### 0.6d — Heatmap on mobile

A 7-year × 8-question grid does not fit on 390px, and shrinking it makes it
illegible. Don't try.

- **< 640px:** pivot to a per-topic list — topic name, horizontal accuracy bar,
  marks lost, sorted worst-first. Tap a topic for the per-question detail.
- **≥ 640px:** keep the full grid.

Same underlying data, two renderers. On the grid, make the first column sticky and
allow horizontal scroll for the in-between widths.

### 0.6e — iPad

iPad is where students actually revise, so treat it as a first-class layout rather
than a stretched phone:

- Two-column at ≥ 1024px: heatmap or list on the left, detail on the right
- Mark entry keeps the keypad but sits in a centred column, max-width ~480px
- Support both orientations; test landscape, which is how a keyboard case is used

### Acceptance

Test at 320, 390, 768, 1024 and 1440px. At every width: no horizontal scroll, no
overlapping elements, every tap target ≥ 44px, no input under 16px. Then time
yourself logging an 8-question paper on a phone-sized viewport — if it's over 60
seconds, the flow isn't done.

---

## Phase 2.5 — Progressive Web App

Branch: `feat/pwa`

Do this **after** Phase 0.6 (there's no point installing a bad mobile UI) and after
the canonical domain exists (scope is host-bound).

Deliberately not a native app: it's one codebase, ships without review, and keeps
Stripe at ~7% instead of Apple's 15–30%. Revisit native around £2–3k MRR.

### 2.5a — Manifest

`static/manifest.webmanifest`:

```json
{
  "name": "Telos — Past Paper Tracker",
  "short_name": "Telos",
  "description": "Track past papers, find your weak topics, predict your grade.",
  "start_url": "/?source=pwa",
  "scope": "/",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#0d0f14",
  "theme_color": "#0d0f14",
  "icons": [
    { "src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/static/icons/maskable-512.png", "sizes": "512x512",
      "type": "image/png", "purpose": "maskable" }
  ],
  "shortcuts": [
    { "name": "Log a paper", "url": "/papers/new" },
    { "name": "Revise", "url": "/revise" }
  ]
}
```

Match `background_color` and `theme_color` to the existing dark theme's actual
values — read them from the CSS variables rather than copying mine.

Head tags (iOS ignores manifest icons for the home screen, so the Apple tag is
required, not optional):

```html
<link rel="manifest" href="/static/manifest.webmanifest">
<meta name="theme-color" content="#0d0f14">
<link rel="apple-touch-icon" sizes="180x180" href="/static/icons/apple-touch-180.png">
<meta name="apple-mobile-web-app-title" content="Telos">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

Generate icons from one source SVG with Pillow. Maskable needs ~20% safe padding or
Android will crop the logo.

### 2.5b — Service worker

`static/sw.js`, registered from the base template. Keep it simple; a clever service
worker is a debugging nightmare.

- **Static assets** (CSS, JS, icons, fonts): cache-first, versioned cache name
- **HTML navigations:** network-first, falling back to a cached `/offline` page
- **Never cache** anything under `/admin`, `/subscription`, `/stripe`, or any POST
- Bump `CACHE_VERSION` on deploy — derive it from the git SHA at build time, not by
  hand, or you will ship a stale app to installed users and not understand why
- `skipWaiting` + `clients.claim`, and show a small "update available, tap to
  refresh" toast rather than reloading under the user

Also set `Cache-Control: no-store` on authenticated HTML responses server-side. A
student's marks must never be served from cache to a different session on a shared
iPad.

### 2.5c — Install prompt

Two different paths, and iOS is the awkward one:

- **Android/Chrome:** capture `beforeinstallprompt`, stash the event, show a custom
  "Add Telos to your home screen" banner, call `prompt()` on tap.
- **iOS Safari:** there is no programmatic install. Detect iOS + Safari + not already
  standalone (`navigator.standalone === false`), and show a small illustrated sheet:
  Share button → Add to Home Screen. Most 16–18 year olds do not know this exists, so
  the illustration matters more than the copy.

Rules: show it at most once per 14 days, never on a user's first session, dismissible
and remembered (localStorage), and never on desktop.

Good trigger: right after they log their third paper — they've seen the value and
Phase 3 has just unlocked their predicted grade.

### 2.5d — Offline behaviour

Minimum viable, don't over-engineer:

- Cached shell and an `/offline` page that explains what's happening
- Read-only access to the last-viewed dashboard if cached
- Mark entry: if a save fails, queue it in IndexedDB and retry on reconnect. Show a
  clear "not saved yet" state — never a false "saved".

Do not attempt full offline write sync. Not worth the complexity at this stage.

### 2.5e — Web push (defer to a sub-phase, ship the rest first)

Works on iOS 16.4+ **only after the user installs to the home screen**, so it depends
on 2.5c landing first.

- VAPID keys, `pywebpush` server-side, subscriptions in a `push_subscriptions` table
- Ask permission on a user action, never on page load — an unprompted permission
  dialog gets denied permanently and you don't get a second chance
- Use it for: revision due reminders, streak nudges, exam countdown milestones
- Frequency cap: one per day maximum, respect a quiet-hours window (nothing between
  22:00 and 07:00), one-tap opt-out in settings
- These go to teenagers during exam season. Notifications should be useful and calm,
  never pressuring or guilt-based ("you haven't revised in 3 days" is the wrong tone —
  "3 questions due when you're ready" is the right one)

### Acceptance

- Lighthouse PWA audit passes on the deployed domain
- Installs to home screen on a real iPhone and a real iPad, opens without browser
  chrome, correct icon and splash colour
- Works offline to the extent above; no white screen
- A deploy reaches an already-installed user within one refresh
- No authenticated page is ever served from a stale cache

---

## Cross-cutting

**Test on real devices, not just DevTools.** Safari on iOS behaves differently from
emulated Safari in Chrome, particularly around input focus, `100vh`, and safe areas.
Use `100dvh`, not `100vh` — `100vh` on iOS includes the area behind the browser bar
and will cut off your bottom nav.

**Don't regress desktop.** The admin screens are used on a laptop; mobile-first must
not make them worse.

**Performance budget:** dashboard interactive in under 2.5s on a simulated 4G
connection and mid-tier Android. Students are on school wifi.

---

## Kickoff

```bash
git checkout -b feat/mobile-first
```

Start with Phase 0.4 — run the Railway CLI commands and give me the exact CNAME and
TXT records to add, plus a question about which registrar holds the DNS so we can
settle the apex approach. Then stop and wait; the rest of 0.4 needs those records
live.
