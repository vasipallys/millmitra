/** Axios / SSE base. In Vite dev, same-origin `/api` uses the proxy and skips CORS preflight. */
export function apiBaseUrl() {
  const fromEnv = import.meta.env.VITE_API_URL;
  if (import.meta.env.DEV) {
    if (!fromEnv || /localhost|127\.0\.0\.1/.test(String(fromEnv))) {
      return '/api';
    }
  }
  if (fromEnv) return String(fromEnv).replace(/\/$/, '');
  return 'http://localhost:5000/api';
}
