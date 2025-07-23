import { useState, useEffect } from 'react';

/**
 * Custom hook for Progressive Web App functionality
 * Handles installation prompts, offline status, and service worker updates
 */
export const usePWA = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstallable, setIsInstallable] = useState(false);
  const [installPrompt, setInstallPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [swRegistration, setSwRegistration] = useState(null);

  useEffect(() => {
    // Register service worker
    registerServiceWorker();

    // Listen for online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setInstallPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Check if app is already installed
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setInstallPrompt(null);
    };

    window.addEventListener('appinstalled', handleAppInstalled);

    // Check if running in standalone mode (installed)
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Register service worker
  const registerServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        setSwRegistration(registration);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              setUpdateAvailable(true);
            }
          });
        });

        console.log('Service Worker registered successfully');
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  };

  // Install PWA
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
    } catch (error) {
      console.error('PWA installation failed:', error);
      return false;
    }
  };

  // Update service worker
  const updateServiceWorker = () => {
    if (swRegistration && swRegistration.waiting) {
      swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      setUpdateAvailable(false);
      window.location.reload();
    }
  };

  // Cache data for offline use
  const cacheData = async (key, data) => {
    try {
      if ('caches' in window) {
        const cache = await caches.open('smart-mill-data');
        const response = new Response(JSON.stringify(data));
        await cache.put(key, response);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to cache data:', error);
      return false;
    }
  };

  // Get cached data
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
    } catch (error) {
      console.error('Failed to get cached data:', error);
      return null;
    }
  };

  // Store offline action
  const storeOfflineAction = async (action) => {
    try {
      const offlineActions = JSON.parse(localStorage.getItem('offlineActions') || '[]');
      offlineActions.push({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...action
      });
      localStorage.setItem('offlineActions', JSON.stringify(offlineActions));
      return true;
    } catch (error) {
      console.error('Failed to store offline action:', error);
      return false;
    }
  };

  // Get offline actions
  const getOfflineActions = () => {
    try {
      return JSON.parse(localStorage.getItem('offlineActions') || '[]');
    } catch (error) {
      console.error('Failed to get offline actions:', error);
      return [];
    }
  };

  // Clear offline actions
  const clearOfflineActions = () => {
    try {
      localStorage.removeItem('offlineActions');
      return true;
    } catch (error) {
      console.error('Failed to clear offline actions:', error);
      return false;
    }
  };

  // Sync offline actions when online
  const syncOfflineActions = async (syncFunction) => {
    if (!isOnline) return false;

    const actions = getOfflineActions();
    const syncedActions = [];

    for (const action of actions) {
      try {
        await syncFunction(action);
        syncedActions.push(action.id);
      } catch (error) {
        console.error('Failed to sync action:', action.id, error);
      }
    }

    // Remove synced actions
    if (syncedActions.length > 0) {
      const remainingActions = actions.filter(action => !syncedActions.includes(action.id));
      localStorage.setItem('offlineActions', JSON.stringify(remainingActions));
    }

    return syncedActions.length;
  };

  // Request notification permission
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  };

  // Show notification
  const showNotification = (title, options = {}) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      return new Notification(title, {
        icon: '/logo192.png',
        badge: '/logo192.png',
        ...options
      });
    }
    return null;
  };

  return {
    // Status
    isOnline,
    isInstallable,
    isInstalled,
    updateAvailable,
    
    // Actions
    installPWA,
    updateServiceWorker,
    
    // Data management
    cacheData,
    getCachedData,
    storeOfflineAction,
    getOfflineActions,
    clearOfflineActions,
    syncOfflineActions,
    
    // Notifications
    requestNotificationPermission,
    showNotification
  };
};
