/** True for `npm run dev`. Production builds register the service worker. */
export const isDevRuntime = () => import.meta.env.DEV;

/**
 * Drop leftover production SWs/caches on localhost so Vite HMR and SPA
 * routes are not intercepted. Returns true if the page should reload once.
 */
export async function clearDevServiceWorkers() {
  if (!isDevRuntime() || !('serviceWorker' in navigator)) {
    return false;
  }

  const registrations = await navigator.serviceWorker.getRegistrations();
  const hadController = Boolean(navigator.serviceWorker.controller);
  if (registrations.length) {
    await Promise.all(registrations.map((registration) => registration.unregister()));
  }

  if ('caches' in window) {
    const keys = await caches.keys();
    await Promise.all(
      keys
        .filter((key) => /smart-mill|millmitra|workbox/i.test(key))
        .map((key) => caches.delete(key))
    );
  }

  if ((registrations.length || hadController) && !sessionStorage.getItem('mm-sw-dev-cleared')) {
    sessionStorage.setItem('mm-sw-dev-cleared', '1');
    return true;
  }
  return false;
}
