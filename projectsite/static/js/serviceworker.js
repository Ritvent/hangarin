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
    e.respondWith(
        caches.match(e.request).then(function(response) {
            // return cache hit or do normal fetch
            return response || fetch(e.request);
        }).catch(function() {
            // optional: fallback logic if offline and not cached
        })
    );
});
