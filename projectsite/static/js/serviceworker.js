self.addEventListener('install', function(e) {
    e.waitUntil(
        caches.open('projectsite-cache-v2').then(function(cache) {
            return cache.addAll([
                '/static/css/style.css',
                // you can add other static files here later
            ]);
        })
    );
});

self.addEventListener('fetch', function(e) {
    e.respondWith((async function(){
        // Try cache first
        const cached = await caches.match(e.request);
        if (cached) return cached;

        // Not in cache -> try network, but handle network failures gracefully
        try {
            const netResp = await fetch(e.request);
            return netResp;
        } catch (err) {
            // Network failed (offline or other error). Try a sensible fallback.
            // Prefer a cached navigation/root or a small offline Response.
            const fallback = await caches.match('/static/css/style.css');
            if (fallback) return fallback;
            return new Response('Service Unavailable', { status: 503, statusText: 'Service Unavailable' });
        }
    })());
});
