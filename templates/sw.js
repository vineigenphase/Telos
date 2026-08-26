// Telos service worker. Kept deliberately simple — see TELOS_V2_ADDENDUM.md
// Phase 2.5b for the rules this follows.
//
// CACHE_VERSION is injected server-side from the deployed git commit, so a
// new deploy always gets a fresh cache name and stale assets get evicted on
// activate. Never bump this by hand.
const CACHE_VERSION = "{{ cache_version }}";
const CACHE_NAME = "telos-" + CACHE_VERSION;

// /logout is a GET that redirects to the login page. Caching it would store
// that redirect as the answer, and the stale-while-slow path below could then
// hand back the login page without the server ever ending the session.
const NEVER_CACHE_PREFIXES = ["/admin", "/subscription", "/stripe", "/logout"];

// How long a navigation waits for the network before falling back to the copy
// we already have. This is the fix for the cold open: Railway may be starting a
// container and Neon may be waking from scale-to-zero, and until now a slow
// backend produced the same blank screen as a broken one — a good cached page
// sat unused because the old code only reached for it when fetch REJECTED.
// Standalone PWAs make it worse: iOS holds the manifest's background_color over
// the whole wait, so "slow" reads as "black screen for ages".
const NAV_NETWORK_TIMEOUT = 2500;

const PRECACHE_URLS = [
  "/offline",
  "/static/css/telos.css",
  "/static/js/telos.js",
  "/static/manifest.webmanifest",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
];

function neverCache(url) {
  return NEVER_CACHE_PREFIXES.some(p => url.pathname.startsWith(p));
}

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(
        names.filter(n => n.startsWith("telos-") && n !== CACHE_NAME)
             .map(n => caches.delete(n))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const req = event.request;
  const url = new URL(req.url);

  // Cross-origin (Stripe.js, fonts CDNs, etc.) and any non-GET request
  // (mark-entry saves, forms, webhooks) always go straight to the network.
  // The page's own retry/queue logic owns failure handling for those.
  if (url.origin !== self.location.origin || req.method !== "GET") return;
  if (neverCache(url)) return;

  // HTML navigations: network-first, but only for as long as the network is
  // actually being quick about it. See navigate() below.
  if (req.mode === "navigate") {
    event.respondWith(navigate(req));
    return;
  }

  // Static assets: cache-first, populate on miss.
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(req).then(cached => cached || fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
        return res;
      }))
    );
  }
});

// A navigation, in three cases.
//
//   nothing cached  -> wait for the network however long it takes, then the
//                      offline shell. A blank wait beats a wrong page.
//   cached, network wins the race -> fresh page, cache updated.
//   cached, network too slow or failed -> the cached page, now, while the
//                      request continues in the background and refreshes the
//                      cache for next time.
//
// The third case is the whole point. A study tracker showing last-known state
// for one navigation is worth far more than a correct page nobody waited for.
async function navigate(req) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(req);

  // Kept alive past the race so the cache still refreshes when the slow
  // response finally lands. Its rejection is handled here, not left dangling.
  const network = fetch(req)
    .then(res => {
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    })
    .catch(() => null);

  if (!cached) {
    return (await network) || (await cache.match("/offline")) || Response.error();
  }

  const raced = await Promise.race([
    network,
    new Promise(resolve => setTimeout(() => resolve(null), NAV_NETWORK_TIMEOUT)),
  ]);
  return raced || cached;
}

// Signing out must not leave the previous account's pages on the device, where
// the stale-while-slow path could serve them back to whoever opens the app
// next. The page asks for this before it navigates away.
self.addEventListener("message", event => {
  if (!event.data || event.data.type !== "telos-signout") return;
  event.waitUntil(
    caches.keys().then(names => Promise.all(
      names.filter(n => n.startsWith("telos-")).map(n => caches.delete(n))
    ))
  );
});
