// Telos service worker. Kept deliberately simple — see TELOS_V2_ADDENDUM.md
// Phase 2.5b for the rules this follows.
//
// CACHE_VERSION is injected server-side from the deployed git commit, so a
// new deploy always gets a fresh cache name and stale assets get evicted on
// activate. Never bump this by hand.
const CACHE_VERSION = "{{ cache_version }}";
const CACHE_NAME = "telos-" + CACHE_VERSION;

const NEVER_CACHE_PREFIXES = ["/admin", "/subscription", "/stripe"];

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

  // HTML navigations: network-first, cache the good response, fall back to
  // the last cached copy of this exact page, then to the offline shell.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
          return res;
        })
        .catch(() =>
          caches.match(req).then(cached => cached || caches.match("/offline"))
        )
    );
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
