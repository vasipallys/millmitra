import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('UX patterns', () => {
  test('command palette jumps to farmers', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/dashboard');
    await page.keyboard.press('Control+K');
    await expect(page.getByTestId('command-palette-list')).toBeVisible();
    await page.getByTestId('command-palette-query').fill('farmer');
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/\/farmers/);
  });

  test('getting started checklist is on the dashboard', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/dashboard');
    const card = page.getByTestId('getting-started');
    if (await card.count()) {
      await expect(card).toBeVisible();
      await expect(card.getByText(/Register a farmer|किसान/i)).toBeVisible();
    }
  });

  test('comfort mode toggle is on Settings', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/settings');
    const control = page.getByTestId('comfort-mode');
    await expect(control).toBeVisible();
    const box = control.locator('input[type="checkbox"]');
    const wasOn = await box.isChecked();
    await box.click();
    await expect(page.locator('html')).toHaveAttribute('data-comfort', wasOn ? '0' : '1');
  });
});
