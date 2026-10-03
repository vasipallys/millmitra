import { useState, useEffect } from 'react';
import { clearDevServiceWorkers, isDevRuntime } from '../utils/pwaRuntime';

let productionSwPromise = null;
const updateListeners = new Set();

function registerProductionServiceWorker() {
  if (isDevRuntime() || !('serviceWorker' in navigator)) {
    return Promise.resolve(null);
  }
  if (!productionSwPromise) {
    productionSwPromise = navigator.serviceWorker.register('/sw.js').then((registration) => {
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (!newWorker) return;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            updateListeners.forEach((notify) => notify());
          }
        });
      });
      return registration;
    });
  }
  return productionSwPromise;
}

/**
 * Progressive Web App helpers: install prompt, offline flag, production SW.
 * Development never registers sw.js — it fights Vite HMR and can 503 SPA routes.
 */
export const usePWA = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstallable, setIsInstallable] = useState(false);
  const [installPrompt, setInstallPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [swRegistration, setSwRegistration] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const handleBeforeInstallPrompt = (event) => {
      if (isDevRuntime()) {
        return;
      }
      event.preventDefault();
      setInstallPrompt(event);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setInstallPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    const notifyUpdate = () => {
      if (!cancelled) setUpdateAvailable(true);
    };
    updateListeners.add(notifyUpdate);

    (async () => {
      if (isDevRuntime()) {
        const shouldReload = await clearDevServiceWorkers();
        if (shouldReload && !cancelled) {
          window.location.reload();
        }
        return;
      }
      try {
        const registration = await registerProductionServiceWorker();
        if (!cancelled) setSwRegistration(registration);
      } catch {
        // Install still works from the manifest; SW is optional for the mill UI.
      }
    })();

    return () => {
      cancelled = true;
      updateListeners.delete(notifyUpdate);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const installPWA = async () => {
    if (!installPrompt) return false;

    try {
      const result = await installPrompt.prompt();
      if (result.outcome === 'accepted') {
        setIsInstalled(true);
        setIsInstallable(false);
        setInstallPrompt(null);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const updateServiceWorker = () => {
    if (swRegistration && swRegistration.waiting) {
      swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      setUpdateAvailable(false);
      window.location.reload();
    }
  };

  const cacheData = async (key, data) => {
    try {
      if ('caches' in window) {
        const cache = await caches.open('smart-mill-data');
        await cache.put(key, new Response(JSON.stringify(data)));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const getCachedData = async (key) => {
    try {
      if ('caches' in window) {
        const cache = await caches.open('smart-mill-data');
        const response = await cache.match(key);
        if (response) {
          return await response.json();
        }
      }
      return null;
    } catch {
      return null;
    }
  };

  const storeOfflineAction = async (action) => {
    try {
      const offlineActions = JSON.parse(localStorage.getItem('offlineActions') || '[]');
      offlineActions.push({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...action,
      });
      localStorage.setItem('offlineActions', JSON.stringify(offlineActions));
      return true;
    } catch {
      return false;
    }
  };

  const getOfflineActions = () => {
    try {
      return JSON.parse(localStorage.getItem('offlineActions') || '[]');
    } catch {
      return [];
    }
  };

  const clearOfflineActions = () => {
    try {
      localStorage.removeItem('offlineActions');
      return true;
    } catch {
      return false;
    }
  };

  const syncOfflineActions = async (syncFunction) => {
    if (!isOnline) return false;

    const actions = getOfflineActions();
    const syncedActions = [];

    for (const action of actions) {
      try {
        await syncFunction(action);
        syncedActions.push(action.id);
      } catch {
        // Leave unsynced actions for the next pass.
      }
    }

    if (syncedActions.length > 0) {
      const remainingActions = actions.filter((action) => !syncedActions.includes(action.id));
      localStorage.setItem('offlineActions', JSON.stringify(remainingActions));
    }

    return syncedActions.length;
  };

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  };

  const showNotification = (title, options = {}) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      return new Notification(title, {
        icon: '/logo192.png',
        badge: '/logo192.png',
        ...options,
      });
    }
    return null;
  };

  return {
    isOnline,
    isInstallable,
    isInstalled,
    updateAvailable,
    installPWA,
    updateServiceWorker,
    cacheData,
    getCachedData,
    storeOfflineAction,
    getOfflineActions,
    clearOfflineActions,
    syncOfflineActions,
    requestNotificationPermission,
    showNotification,
  };
};
