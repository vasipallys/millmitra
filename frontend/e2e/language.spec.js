import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';
import { ensureSidebarOpen, selectOptionByName, sidebarItem } from './helpers/ui.js';

test.describe('Language', () => {
  test('Telugu changes a sidebar label, then English restores it', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/dashboard');
    await ensureSidebarOpen(page);
    await expect(sidebarItem(page, 'Farmers')).toBeVisible();

    await selectOptionByName(page, 'Language', 'తెలుగు');
    await expect(sidebarItem(page, 'రైతులు')).toBeVisible({ timeout: 10_000 });

    await page.getByLabel(/Language|భాష/).first().click();
    await page.getByRole('option', { name: 'English' }).click();
    await expect(sidebarItem(page, 'Farmers')).toBeVisible({ timeout: 10_000 });
  });
});
