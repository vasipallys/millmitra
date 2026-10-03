export const API = process.env.PLAYWRIGHT_API_URL || 'http://127.0.0.1:5000';

export const USERS = {
  admin: { username: 'admin', password: 'admin123' },
  manager: { username: 'manager', password: 'manager123' },
  operator: { username: 'operator', password: 'operator123' },
  quality: { username: 'quality', password: 'quality123' },
  sales: { username: 'sales', password: 'sales123' },
  accountant: { username: 'accountant', password: 'accountant123' },
};

export async function apiLogin(request, username, password) {
  const response = await request.post(`${API}/api/auth/login`, {
    data: { username, password, method: 'password' },
    timeout: 15_000,
  });
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`API login failed for ${username}: HTTP ${response.status()} ${body.slice(0, 180)}`);
  }
  return response.json();
}

export async function openAs(page, request, role, path = '/dashboard') {
  const account = USERS[role] || role;
  const username = account.username || role;
  const password = account.password;
  const data = await apiLogin(request, username, password);
  await page.addInitScript(({ token, user, sessionToken }) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    if (sessionToken) {
      localStorage.setItem('sessionToken', sessionToken);
    }
    localStorage.setItem('millmitra.language', 'en');
  }, {
    token: data.access_token,
    user: data.user,
    sessionToken: data.session_token || '',
  });
  await page.goto(path, { waitUntil: 'domcontentloaded' });
  await page.getByRole('heading', { name: /Opening MillMitra/i }).waitFor({ state: 'hidden', timeout: 20_000 }).catch(() => {});
}

export async function loginViaForm(page, username, password) {
  await page.addInitScript(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionToken');
    localStorage.setItem('millmitra.language', 'en');
  });
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await page.locator('input[autocomplete="username"]').fill(username);
  await page.locator('input[autocomplete="current-password"]').fill(password);
  await page.getByRole('button', { name: 'Login', exact: true }).click();
}

export async function expectSignedIn(page) {
  await page.getByRole('button', { name: 'Account menu' }).waitFor({ timeout: 20_000 });
}

export async function logoutFromApp(page) {
  await page.getByRole('button', { name: 'Account menu' }).click();
  await page.getByRole('menuitem', { name: 'Logout' }).click();
  await page.getByRole('heading', { name: 'Sign in to MillMitra' }).waitFor({ timeout: 15_000 });
  await page.getByRole('button', { name: 'Login', exact: true }).waitFor({ timeout: 10_000 });
}
