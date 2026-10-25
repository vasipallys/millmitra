import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { LOCALES, localeDir, translations } from './translations';

const STORAGE_KEY = 'millmitra.language';

const I18nContext = createContext({
  locale: 'en',
  dir: 'ltr',
  setLocale: () => {},
  t: (key) => key,
  roleLabel: (role) => role || '',
  statusLabel: (status) => status || '',
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

  const dir = localeDir(locale);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = dir;
    document.body.dir = dir;
  }, [locale, dir]);

  const value = useMemo(() => ({
    locale,
    dir,
    setLocale,
    locales: LOCALES,
    t: (key, vars) => {
      let text = translations[locale]?.[key] || translations.en[key] || key;
      if (vars && typeof text === 'string') {
        Object.keys(vars).forEach((name) => {
          text = text.replace(new RegExp(`\\{${name}\\}`, 'g'), String(vars[name]));
        });
      }
      return text;
    },
    roleLabel: (role) => {
      if (!role) return translations[locale]?.role || translations.en.role;
      const key = role === 'quality' ? 'role_quality_control' : `role_${role}`;
      return translations[locale]?.[key] || translations.en[key] || role;
    },
    statusLabel: (status) => {
      if (!status) return '';
      const key = `status_${String(status).toLowerCase()}`;
      return translations[locale]?.[key] || translations.en[key] || String(status).replace(/_/g, ' ');
    },
  }), [locale, dir]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}
