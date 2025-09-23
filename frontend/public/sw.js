// Smart Rice Mill ERP - Service Worker
// Provides offline functionality and caching

const CACHE_NAME = 'smart-mill-v2.0.0';
const OFFLINE_URL = '/offline.html';

// Resources to cache for offline use
const STATIC_CACHE_URLS = [
  '/',
  '/manifest.json'
  // Note: In development mode, static files are served by webpack dev server
  // In production, add: '/static/css/main.css', '/static/js/main.js'
];

// API endpoints to cache
const API_CACHE_URLS = [
  '/api/dashboard/overview',
  '/api/dashboard/widgets',
  '/api/farmers',
  '/api/inventory/stock',
  '/api/production/batches'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async (cache) => {
        console.log('Service Worker: Caching static files');
        
        // Cache files individually to avoid failures from missing files
        const cachePromises = STATIC_CACHE_URLS.map(async (url) => {
          try {
            // First check if the resource exists
            const response = await fetch(url);
            if (response.ok) {
              await cache.add(url);
              console.log('Cached:', url);
            } else {
              console.warn('Resource not found, skipping cache:', url);
            }
          } catch (error) {
            console.warn('Failed to cache:', url, error);
          }
        });
        
        await Promise.allSettled(cachePromises);
        return cache;
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle requests with cache-first strategy
self.addEventListener('fetch', (event) => {
  try {
    const { request } = event;
    const url = new URL(request.url);

    // Skip requests to non-existent ports or invalid origins
    if (url.origin.includes('localhost:3001') ||
        url.origin.includes('127.0.0.1:3001') ||
        (!url.origin.includes(location.origin) &&
         !url.origin.includes('localhost:5000') &&
         !url.origin.includes('127.0.0.1:5000'))) {
      return;
    }

    // Handle navigation requests
    if (request.mode === 'navigate') {
      event.respondWith(
        fetch(request)
          .catch(() => {
            // For SPA routes like /settings, /dashboard, etc., return the index.html
            // This allows React Router to handle the routing
            return caches.match('/').then(response => {
              if (response) {
                return response;
              }
              // Fallback offline page if index.html is not cached
              return new Response(`
                <!DOCTYPE html>
                <html>
                <head><title>Offline</title></head>
                <body>
                  <h1>You are offline</h1>
                  <p>Please check your internet connection.</p>
                </body>
                </html>
              `, {
                headers: { 'Content-Type': 'text/html' }
              });
            });
          })
      );
      return;
    }

    // Handle API requests with network-first strategy (only GET requests)
    if (url.pathname.startsWith('/api/')) {
      if (request.method === 'GET') {
        event.respondWith(
          networkFirstStrategy(request)
        );
      } else {
        // For non-GET requests, just fetch without caching
        event.respondWith(
          fetch(request).catch(error => {
            console.error('Failed to fetch API request:', error);
            return new Response(JSON.stringify({
              error: 'Network error',
              message: 'Unable to complete request'
            }), {
              status: 503,
              headers: { 'Content-Type': 'application/json' }
            });
          })
        );
      }
      return;
    }

    // Handle static assets with cache-first strategy
    event.respondWith(
      cacheFirstStrategy(request)
    );
  } catch (error) {
    console.error('Service Worker fetch error:', error);
    // Return a fallback response for any unhandled errors
    event.respondWith(
      new Response('Service Worker Error', {
        status: 500,
        statusText: 'Internal Service Worker Error'
      })
    );
  }
});

// Network-first strategy for API calls
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);

    // Only cache GET requests with successful responses
    if (networkResponse && networkResponse.ok && request.method === 'GET') {
      try {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, networkResponse.clone());
      } catch (cacheError) {
        console.warn('Failed to cache response:', cacheError);
      }
    }

    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', request.url);
    
    try {
      const cachedResponse = await caches.match(request);
      if (cachedResponse) {
        return cachedResponse;
      }
    } catch (cacheError) {
      console.warn('Cache lookup failed:', cacheError);
    }
    
    // Return offline response for failed API calls
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'This data is not available offline',
        offline: true
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  try {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
  } catch (cacheError) {
    console.warn('Cache lookup failed:', cacheError);
  }
  
  try {
    const networkResponse = await fetch(request);

    // Only cache GET requests with successful responses
    if (networkResponse && networkResponse.ok && request.method === 'GET') {
      try {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, networkResponse.clone());
      } catch (cacheError) {
        console.warn('Failed to cache response:', cacheError);
      }
    }

    return networkResponse;
  } catch (error) {
    console.error('Failed to fetch:', request.url, error);

    // For API requests, return a proper JSON error response
    if (request.url.includes('/api/')) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Service temporarily unavailable',
        offline: true
      }), {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }

    // For other requests, return a fallback response
    return new Response('Resource not available offline', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'text/plain'
      }
    });
  }
}

// Background sync for offline data
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(syncOfflineData());
  }
});

// Sync offline data when connection is restored
async function syncOfflineData() {
  try {
    // Get offline data from IndexedDB
    const offlineData = await getOfflineData();
    
    // Sync each piece of offline data
    for (const data of offlineData) {
      try {
        await fetch(data.url, {
          method: data.method,
          headers: data.headers,
          body: data.body
        });
        
        // Remove synced data from offline storage
        await removeOfflineData(data.id);
        
        console.log('Synced offline data:', data.id);
      } catch (error) {
        console.error('Failed to sync data:', data.id, error);
      }
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Placeholder functions for offline data management
async function getOfflineData() {
  // Implementation would use IndexedDB to store offline data
  return [];
}

async function removeOfflineData(id) {
  // Implementation would remove data from IndexedDB
  console.log('Removing offline data:', id);
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New update available',
    icon: '/logo192.png',
    badge: '/logo192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/logo192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/logo192.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Smart Mill ERP', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('Service Worker: Loaded successfully');
