// MillMitra production service worker. Not registered during `npm run dev`.
const CACHE_NAME = 'millmitra-v3.0.0';
const OFFLINE_URL = '/offline.html';

const STATIC_CACHE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  OFFLINE_URL,
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async (cache) => {
        await Promise.allSettled(
          STATIC_CACHE_URLS.map(async (url) => {
            try {
              const response = await fetch(url, { cache: 'no-store' });
              if (isCacheableResponse(response)) {
                await cache.put(url, response.clone());
              }
            } catch {
              // Skip missing files during install.
            }
          })
        );
        return self.skipWaiting();
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  if (shouldBypass(request)) {
    return;
  }

  if (isSpaNavigation(request)) {
    event.respondWith(handleSpaNavigation(request));
    return;
  }

  try {
    const url = new URL(request.url);

    if (url.pathname.startsWith('/api/')) {
      if (request.method === 'GET') {
        event.respondWith(networkFirstStrategy(request));
      }
      return;
    }

    event.respondWith(cacheFirstStrategy(request));
  } catch {
    event.respondWith(fetch(request));
  }
});

function shouldBypass(request) {
  if (request.method !== 'GET') {
    return true;
  }

  let url;
  try {
    url = new URL(request.url);
  } catch {
    return true;
  }

  if (url.protocol === 'ws:' || url.protocol === 'wss:') {
    return true;
  }

  const upgrade = request.headers.get('Upgrade');
  if (upgrade && upgrade.toLowerCase() === 'websocket') {
    return true;
  }

  if (url.origin !== self.location.origin) {
    return true;
  }

  const path = url.pathname;
  if (
    path.startsWith('/@') ||
    path.startsWith('/src/') ||
    path.startsWith('/node_modules/') ||
    path.includes('@vite') ||
    path.includes('@react-refresh') ||
    path.includes('.hot-update') ||
    path === '/sw.js'
  ) {
    return true;
  }

  // Vite HMR handshake: ws://host/?token=...
  if (path === '/' && url.searchParams.has('token')) {
    return true;
  }

  return false;
}

function isSpaNavigation(request) {
  if (request.mode === 'navigate' || request.destination === 'document') {
    return true;
  }
  try {
    const url = new URL(request.url);
    if (url.origin !== self.location.origin) {
      return false;
    }
    const last = url.pathname.split('/').pop();
    return Boolean(last) && !last.includes('.');
  } catch {
    return false;
  }
}

function isCacheableResponse(response) {
  return Boolean(
    response
    && response.ok
    && response.status === 200
    && response.type !== 'opaque'
    && response.type !== 'opaqueredirect'
  );
}

async function handleSpaNavigation(request) {
  try {
    const networkResponse = await fetch(request, { cache: 'no-store' });
    if (isCacheableResponse(networkResponse)) {
      return networkResponse;
    }
    if (networkResponse && networkResponse.status < 500) {
      return networkResponse;
    }
    const index = await fetch('/', { cache: 'no-store' });
    if (index.ok) {
      return index;
    }
    return networkResponse;
  } catch {
    const cached = await caches.match('/')
      || await caches.match('/index.html')
      || await caches.match(OFFLINE_URL);
    if (cached) {
      return cached;
    }
    return new Response(
      '<!DOCTYPE html><html><head><meta charset="utf-8"><title>MillMitra</title></head><body><p>MillMitra cannot reach the server. Start the mill API and refresh.</p></body></html>',
      { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    );
  }
}

async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (isCacheableResponse(networkResponse) && request.method === 'GET') {
      try {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, networkResponse.clone());
      } catch {
        // Cache write is optional.
      }
    }
    return networkResponse;
  } catch {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: 'This data is not available offline',
        offline: true,
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

async function cacheFirstStrategy(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
  } catch {
    // Fall through to network.
  }

  try {
    const networkResponse = await fetch(request);
    if (isCacheableResponse(networkResponse) && request.method === 'GET') {
      try {
        const cache = await caches.open(CACHE_NAME);
        await cache.put(request, networkResponse.clone());
      } catch {
        // Cache write is optional.
      }
    }
    return networkResponse;
  } catch {
    if (isSpaNavigation(request)) {
      return handleSpaNavigation(request);
    }
    return Response.error();
  }
}

self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(syncOfflineData());
  }
});

async function syncOfflineData() {
  return undefined;
}

self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New mill update',
    icon: '/logo192.png',
    badge: '/logo192.png',
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
    },
  };

  event.waitUntil(
    self.registration.showNotification('MillMitra', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow('/'));
});
