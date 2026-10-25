import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';
import rtlPlugin from 'stylis-plugin-rtl';

const ltrCache = createCache({ key: 'mui' });
const rtlCache = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

export default function RtlCache({ dir, children }) {
  return (
    <CacheProvider value={dir === 'rtl' ? rtlCache : ltrCache}>
      {children}
    </CacheProvider>
  );
}
