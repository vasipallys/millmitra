import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';
import { ensureSidebarOpen, sidebarItem } from './helpers/ui.js';

test.describe('Sales access', () => {
  test('sales user can open Sales', async ({ page, request }) => {
    await openAs(page, request, 'sales', '/sales');
    await expect(page.getByRole('heading', { name: 'Sales Management' })).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('alert').filter({ hasText: /don't have access/i })).toHaveCount(0);
  });

  test('operator cannot open Sales', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/dashboard');
    await ensureSidebarOpen(page);
    await expect(sidebarItem(page, 'Sales')).toHaveCount(0);

    await page.goto('/sales', { waitUntil: 'domcontentloaded' });
    await expect(page.getByRole('alert')).toContainText(/don't have access|cannot open this page/i);
  });
});
