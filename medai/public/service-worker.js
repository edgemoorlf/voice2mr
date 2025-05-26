const CACHE_NAME = 'medai-cache-v1';
const urlsToCache = [
  '/', // Root of the application
  '/manifest.json', // Web app manifest
  '/offline.html', // Placeholder for offline fallback page
  // Add your main icons specified in manifest.json, for example:
  // '/icons/icon-192x192.png',
  // '/icons/icon-512x512.png',
  // Add any other critical CSS, JS, or images needed for the initial shell to render offline
  // '/styles/main.css',
  // '/images/logo.png'
];

// Install event:
// - Opens the cache
// - Caches all specified URLs
// - Skips waiting to activate the new service worker immediately
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting()) // Force the waiting service worker to become the active service worker.
  );
});

// Activate event:
// - Claims all clients (open tabs/windows)
// - Cleans up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    self.clients.claim() // Allow an active service worker to set itself as the controller for all clients within its scope.
      .then(() => {
        // Clean up old caches
        return caches.keys().then((cacheNames) => {
          return Promise.all(
            cacheNames.filter((cacheName) => {
              // Delete caches that are not the current one
              return cacheName.startsWith('medai-cache-') && cacheName !== CACHE_NAME;
            }).map((cacheName) => {
              return caches.delete(cacheName);
            })
          );
        });
      })
  );
});

// Fetch event:
// - Implements a "network falling back to cache" strategy for navigation requests
// - Implements a "cache first, falling back to network" strategy for other requests (e.g., static assets)
self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      (async () => {
        try {
          const cache = await caches.open(CACHE_NAME);
          
          // Try network first
          const response = await fetch(event.request).catch(() => null);
          
          // If we got a successful response, cache it and return it
          if (response && response.ok) {
            const responseToCache = response.clone();
            await cache.put(event.request, responseToCache);
            return response;
          }

          // If we get here, either:
          // 1. fetch failed completely (offline) - response is null
          // 2. response was not ok (404, 500, etc)
          // In either case in PWA, we should show offline content
          
          // Try to get the page from cache first
          const cachedResponse = await cache.match(event.request);
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // If not in cache, serve the offline page
          const offlineResponse = await cache.match('/offline.html');
          if (offlineResponse) {
            return new Response(offlineResponse.body, {
              status: 200,
              headers: {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-store'
              }
            });
          }
          
          // Last resort - plain text response
          return new Response('You are offline and the offline page could not be loaded.', {
            status: 503,
            headers: { 'Content-Type': 'text/plain' }
          });
        } catch (error) {
          console.error('SW: Critical error in fetch handler:', error);
          return new Response('Service Worker Error', {
            status: 500,
            headers: { 'Content-Type': 'text/plain' }
          });
        }
      })()
    );
  } else {
    // Cache first, falling back to network for other requests
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          // Cache hit - return response
          if (response) {
            return response;
          }
          // Not in cache - fetch from network
          return fetch(event.request).then(
            (networkResponse) => {
              // If the fetch is successful, clone the response and cache it
              if (networkResponse && networkResponse.ok) {
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME)
                  .then((cache) => {
                    cache.put(event.request, responseToCache);
                  });
              }
              return networkResponse;
            }
          ).catch(() => {
             // If fetch fails (e.g. asset not found on server), you might want to return a fallback for specific asset types
             // For example, a placeholder image:
             // if (event.request.url.match(/\.(jpe?g|png|gif|svg)$/)) {
             //   return caches.match('/images/placeholder.png');
             // }
            return new Response("Network error trying to fetch " + event.request.url, {
                status: 408, // Request Timeout
                headers: { 'Content-Type': 'text/plain' },
            });
          });
        })
    );
  }
});


// Background Sync:
// Listens for 'sync' events, which are typically triggered when the network connection is restored.
// This example assumes you have a 'failed-requests' queue for POST requests that failed due to network issues.
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-failed-requests') {
    event.waitUntil(replayFailedRequests());
  }
});

async function replayFailedRequests() {
  // This is a placeholder. You'll need to implement a way to store and retrieve failed requests.
  // For example, using IndexedDB.
  console.log('Attempting to replay failed requests...');
  // const failedRequests = await getFailedRequestsFromIndexedDB(); // Implement this
  // failedRequests.forEach(requestData => {
  //   fetch(requestData.url, requestData.options)
  //     .then(response => {
  //       if (response.ok) {
  //         removeFailedRequestFromIndexedDB(requestData.id); // Implement this
  //       }
  //     })
  //     .catch(error => console.error('Failed to replay request:', error));
  // });
}

// Periodic Sync (for updating content regularly, e.g., every 24 hours)
// Note: Periodic Background Sync is a newer API and might not be supported in all browsers.
// You need to request permission for it.
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'update-content') {
    event.waitUntil(updateContent());
  }
});

async function updateContent() {
  console.log('Performing periodic content update...');
  // Example: Re-cache key assets or fetch new data
  // const cache = await caches.open(CACHE_NAME);
  // await cache.addAll(['/', '/index.html', '/styles/main.css']); // Re-cache important assets
  // Or fetch new data from an API and store it in IndexedDB
}

// Message event:
// Allows communication between the service worker and clients (pages).
// For example, to trigger an immediate update of the service worker.
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// You might want to create an offline.html page to show when the user is offline and the requested page isn't cached.
// Example: medai/public/offline.html
/*
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Offline</title>
  <style>
    body { font-family: sans-serif; text-align: center; padding-top: 50px; }
    h1 { color: #333; }
  </style>
</head>
<body>
  <h1>You are offline</h1>
  <p>Please check your internet connection.</p>
</body>
</html>
*/

// IMPORTANT: Add URLs of essential static assets generated by Next.js build to urlsToCache.
// These typically include:
// - CSS files for global styles and specific pages
// - JavaScript chunks (_next/static/chunks/...)
// - Web fonts
//
// You can find these in your .next/static directory after a build.
// It's often better to let the service worker cache these dynamically on first fetch
// rather than hardcoding them, as their names can change with each build.
// The current "cache first, falling back to network" strategy for non-navigation requests
// will handle this for assets requested by your pages.
//
// However, for a truly offline-first experience for the main shell of your app,
// you might want to pre-cache the critical Next.js static assets.
// This can be complex due to hashed filenames.
// Tools like `workbox-webpack-plugin` (even without `next-pwa`) can help inject a manifest of these assets.
// Or, you could have a build step that generates a list of these assets and injects them into this SW file.

console.log('Advanced Service Worker Loaded'); 