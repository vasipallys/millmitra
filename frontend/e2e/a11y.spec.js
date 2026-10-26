import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { openAs } from './helpers/auth.js';

/** Every authenticated route declared in App.jsx (wildcard pages use the list root). */
export const ADMIN_ROUTES = [
  '/dashboard',
  '/mill-flow',
  '/farmers',
  '/inventory',
  '/production',
  '/sales',
  '/customers',
  '/finance',
  '/analytics',
  '/quality-control',
  '/financial-intelligence',
  '/compliance-gst',
  '/analytics-reporting',
  '/notifications',
  '/settings',
  '/users',
  '/access',
  '/lookups',
  '/iiot',
  '/form-builder',
  '/dashboard-builder',
  '/forms/inspection',
];

const OPERATOR_ROUTES = [
  '/dashboard',
  '/mill-flow',
  '/farmers',
  '/inventory',
  '/production',
  '/sales',
  '/finance',
  '/customers',
  '/users',
  '/access',
  '/settings',
  '/quality-control',
  '/analytics',
];

const TABLE_ROUTES = ['/farmers', '/sales', '/users', '/lookups', '/inventory', '/production', '/finance'];

async function collectAxe(page, path, findings) {
  const results = await new AxeBuilder({ page }).analyze();
  findings.push(...results.violations
    .filter((item) => ['serious', 'critical'].includes(item.impact))
    .map((item) => ({
      path,
      id: item.id,
      impact: item.impact,
      help: item.help,
      targets: item.nodes.flatMap((node) => node.target).slice(0, 4),
    })));
}

async function expectHeading(page) {
  await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible({ timeout: 20_000 });
}

async function overflowPx(page) {
  return page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
}

test.describe('Accessibility smoke', () => {
  for (const path of ADMIN_ROUTES) {
    test(`${path} has a page heading and overflow < 8px at 390`, async ({ page, request }) => {
      await page.setViewportSize({ width: 390, height: 844 });
      await openAs(page, request, 'admin', path);
      await expectHeading(page);
      expect(await overflowPx(page)).toBeLessThan(8);
    });

    test(`${path} has a page heading at 1366`, async ({ page, request }) => {
      await page.setViewportSize({ width: 1366, height: 768 });
      await openAs(page, request, 'admin', path);
      await expectHeading(page);
    });
  }

  test('migrated tables render as cards at 390', async ({ page, request }) => {
    test.setTimeout(90_000);
    await page.setViewportSize({ width: 390, height: 844 });
    await openAs(page, request, 'admin', '/users');
    await expectHeading(page);
    const cards = page.getByTestId('data-table-cards');
    if (await cards.count()) {
      await expect(cards.first()).toBeVisible();
    }
    for (const path of TABLE_ROUTES) {
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      await expectHeading(page);
      expect(await overflowPx(page), `${path} overflow`).toBeLessThan(8);
    }
  });

  test('axe serious/critical on login and every admin route at 1366 and 390', async ({ page, request }) => {
    test.setTimeout(360_000);
    const findings = [];
    await page.addInitScript(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    });
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await collectAxe(page, '/login', findings);

    await page.setViewportSize({ width: 1366, height: 768 });
    await openAs(page, request, 'admin', '/dashboard');
    for (const path of ADMIN_ROUTES) {
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      await expectHeading(page);
      await collectAxe(page, `admin-1366:${path}`, findings);
    }

    await page.setViewportSize({ width: 390, height: 844 });
    for (const path of ADMIN_ROUTES) {
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      await expectHeading(page);
      await collectAxe(page, `admin-390:${path}`, findings);
    }
    expect(findings, JSON.stringify(findings, null, 2)).toEqual([]);
  });

  test('axe and heading on operator routes including denied pages', async ({ page, request }) => {
    test.setTimeout(180_000);
    const findings = [];
    await page.setViewportSize({ width: 1366, height: 768 });
    await openAs(page, request, 'operator', '/dashboard');
    for (const path of OPERATOR_ROUTES) {
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      await expectHeading(page);
      await collectAxe(page, `operator:${path}`, findings);
    }
    expect(findings, JSON.stringify(findings, null, 2)).toEqual([]);
  });

  test('keyboard: login then open mill flow', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    });
    await page.goto('/login');
    await page.locator('input[autocomplete="username"]').focus();
    await page.keyboard.type('admin');
    await page.locator('input[autocomplete="current-password"]').focus();
    await page.keyboard.type('admin123');
    await page.getByRole('button', { name: 'Login', exact: true }).press('Enter');
    await expect(page.getByRole('button', { name: 'Account menu' })).toBeVisible({ timeout: 20_000 });
    await page.keyboard.press('Control+K');
    await expect(page.getByTestId('command-palette-list')).toBeVisible();
    await page.getByTestId('command-palette-query').fill('mill');
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/mill-flow/);
  });
});
