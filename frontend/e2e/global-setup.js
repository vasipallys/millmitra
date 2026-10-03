const UI = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000';
const API = process.env.PLAYWRIGHT_API_URL || 'http://127.0.0.1:5000';

async function assertReachable(url, label) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (response.status >= 400) {
      throw new Error(
        `${label} at ${url} returned HTTP ${response.status}. `
        + 'That port is in use but is not a healthy MillMitra process. '
        + 'Set PLAYWRIGHT_BASE_URL to the Vite URL printed by npm run dev.'
      );
    }
  } catch (error) {
    const reason = error.name === 'AbortError' ? 'timed out after 8s' : (error.message || String(error));
    throw new Error(
      `${label} is not reachable at ${url} (${reason}). `
      + 'Start the existing mill processes, then rerun. '
      + 'UI: cd frontend && npm run dev. '
      + 'API: cd backend && .\\venv\\Scripts\\python.exe app.py. '
      + 'Do not start a second server if 3000 or 5000 is already in use.'
    );
  } finally {
    clearTimeout(timer);
  }
}

export default async function globalSetup() {
  await assertReachable(UI, 'MillMitra UI');
  await assertReachable(`${API}/api/health`, 'MillMitra API');
}
