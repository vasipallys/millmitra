import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';
import { ensureSidebarOpen, sidebarItem } from './helpers/ui.js';

test.describe('Role access', () => {
  test('operator sidebar hides Finance and Users; /finance is denied', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/dashboard');
    await ensureSidebarOpen(page);
    await expect(sidebarItem(page, 'Farmers')).toBeVisible();
    await expect(sidebarItem(page, 'Finance')).toHaveCount(0);
    await expect(sidebarItem(page, 'Users')).toHaveCount(0);
    await expect(sidebarItem(page, 'Dropdown lists')).toHaveCount(0);

    await page.goto('/finance', { waitUntil: 'domcontentloaded' });
    await expect(page.getByRole('alert')).toContainText(/don't have access|cannot open this page/i);
  });

  test('admin sees Users and Dropdown lists', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/dashboard');
    await ensureSidebarOpen(page);
    await expect(sidebarItem(page, 'Users')).toBeVisible();
    await expect(sidebarItem(page, 'Dropdown lists')).toBeVisible();
  });
});
