const CACHE_VERSION = "emax-shell-v4"
const OFFLINE_URL = "/offline"

const APP_SHELL = [
    "/offline",
    "/captura",

    "/static/css/pwa/captura.css",

    "/static/js/offline/bootstrap.js",
    "/static/js/offline/db.js",
    "/static/js/offline/sync.js",

    "/static/js/pwa/captura.js",
]


self.addEventListener("install", event => {
    event.waitUntil(
        caches
            .open(CACHE_VERSION)
            .then(cache => cache.addAll(APP_SHELL))
            .then(() => self.skipWaiting())
    )
})


self.addEventListener("activate", event => {
    event.waitUntil(
        caches
            .keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(name => {
                            return (
                                name.startsWith("emax-")
                                && name !== CACHE_VERSION
                            )
                        })
                        .map(name => caches.delete(name))
                )
            })
            .then(() => self.clients.claim())
    )
})


self.addEventListener("fetch", event => {
    const request = event.request

    if (request.method !== "GET") {
        return
    }

    const url = new URL(request.url)

    if (url.origin !== self.location.origin) {
        return
    }

    // Las peticiones API nunca se obtienen de caché.
    if (url.pathname.startsWith("/api/")) {
        return
    }

    // Navegación: servidor primero, fallback offline.
    if (request.mode === "navigate") {
        event.respondWith(
            fetch(request).catch(async () => {
                return (
                    await caches.match(request)
                    ?? await caches.match(OFFLINE_URL)
                )
            })
        )

        return
    }

    // Recursos estáticos: red primero, caché como respaldo.
    if (url.pathname.startsWith("/static/")) {
        event.respondWith(
            fetch(request)
                .then(async response => {
                    if (response.ok) {
                        const cache =
                            await caches.open(CACHE_VERSION)

                        await cache.put(
                            request,
                            response.clone()
                        )
                    }

                    return response
                })
                .catch(() => caches.match(request))
        )
    }
})