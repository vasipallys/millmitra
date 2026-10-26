import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/authService';

const STORAGE_KEY = 'millmitra.comfort';
const ComfortContext = createContext({
  comfort: false,
  setComfort: () => {},
});

function readComfort() {
  try {
    return localStorage.getItem(STORAGE_KEY) === '1';
  } catch {
    return false;
  }
}

export function ComfortProvider({ user = null, children }) {
  const [comfort, setComfortState] = useState(readComfort);

  useEffect(() => {
    const fromUser = user?.preferences?.comfort_mode;
    if (typeof fromUser === 'boolean') {
      setComfortState(fromUser);
      try {
        localStorage.setItem(STORAGE_KEY, fromUser ? '1' : '0');
      } catch {
        // ignore
      }
    }
  }, [user?.preferences?.comfort_mode]);

  useEffect(() => {
    document.documentElement.dataset.comfort = comfort ? '1' : '0';
    document.body.style.fontSize = comfort ? '18px' : '';
  }, [comfort]);

  const setComfort = (next, persist = true) => {
    const value = Boolean(next);
    setComfortState(value);
    try {
      localStorage.setItem(STORAGE_KEY, value ? '1' : '0');
    } catch {
      // ignore
    }
    if (persist) {
      authService.updatePreferences({ comfort_mode: value }).catch(() => {});
    }
  };

  const value = useMemo(() => ({ comfort, setComfort }), [comfort]);
  return <ComfortContext.Provider value={value}>{children}</ComfortContext.Provider>;
}

export function useComfort() {
  return useContext(ComfortContext);
}
