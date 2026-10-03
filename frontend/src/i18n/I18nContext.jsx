import { createContext, useContext, useMemo, useState } from 'react';
import { LOCALES, translations } from './translations';

const STORAGE_KEY = 'millmitra.language';

const I18nContext = createContext({
  locale: 'en',
  setLocale: () => {},
  t: (key) => key,
  locales: LOCALES,
});

function readLocale() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && translations[stored]) return stored;
  } catch {
    // ignore
  }
  return 'en';
}

export function I18nProvider({ children }) {
  const [locale, setLocaleState] = useState(readLocale);

  const setLocale = (next) => {
    const code = translations[next] ? next : 'en';
    setLocaleState(code);
    try {
      localStorage.setItem(STORAGE_KEY, code);
    } catch {
      // ignore
    }
  };

  const value = useMemo(() => ({
    locale,
    setLocale,
    locales: LOCALES,
    t: (key) => translations[locale]?.[key] || translations.en[key] || key,
  }), [locale]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}
