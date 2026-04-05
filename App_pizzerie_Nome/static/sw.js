const CACHE_NAME = "ecomora-cache-v1";
const urlsToCache = [
  "/",
  "/ordina",
  "/prenota",
  "/menu-view",
  "/static/logo.png",
  "/static/icon-192.png",
  "/static/icon-512.png",
  "/static/manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});