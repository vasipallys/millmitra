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

  test('Urdu sets RTL and mirrors the sidebar', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/dashboard');
    await ensureSidebarOpen(page);
    await selectOptionByName(page, 'Language', /اردو|Urdu/i);
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    const sidebarBox = await page.locator('nav, aside, [data-testid="sidebar"]').first().boundingBox();
    const navBox = await page.getByRole('banner').first().boundingBox().catch(() => null);
    expect(sidebarBox).toBeTruthy();
    if (sidebarBox) {
      expect(sidebarBox.x).toBeGreaterThan(200);
    }
    if (navBox) {
      expect(navBox.x).toBeGreaterThanOrEqual(0);
    }
    await page.getByLabel(/Language|زبان/).first().click();
    await page.getByRole('option', { name: 'English' }).click();
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  });
});
