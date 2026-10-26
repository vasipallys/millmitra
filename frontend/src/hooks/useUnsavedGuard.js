import { useEffect } from 'react';

export default function useUnsavedGuard(dirty, message) {
  useEffect(() => {
    if (!dirty) return undefined;
    const onBefore = (event) => {
      event.preventDefault();
      event.returnValue = message || '';
    };
    window.addEventListener('beforeunload', onBefore);
    return () => window.removeEventListener('beforeunload', onBefore);
  }, [dirty, message]);
}
