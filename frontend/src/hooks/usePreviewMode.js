import { useCallback, useState } from 'react';

const storageKey = (pageKey) => `millmitra.previewMode.${pageKey}`;

export function usePreviewMode(pageKey) {
  const [mode, setModeState] = useState(() => {
    try {
      const stored = sessionStorage.getItem(storageKey(pageKey));
      return stored === 'sample' ? 'sample' : 'actual';
    } catch {
      return 'actual';
    }
  });

  const setMode = useCallback((next) => {
    const value = next === 'sample' ? 'sample' : 'actual';
    setModeState(value);
    try {
      sessionStorage.setItem(storageKey(pageKey), value);
    } catch {
      // sessionStorage may be unavailable
    }
  }, [pageKey]);

  return {
    mode,
    setMode,
    isSample: mode === 'sample',
    isActual: mode === 'actual',
  };
}
