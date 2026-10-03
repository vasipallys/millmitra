import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('Notifications', () => {
  test('bell opens without throwing', async ({ page, request }) => {
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(String(error)));

    await openAs(page, request, 'operator', '/dashboard');
    await page.getByRole('button', { name: 'Notifications' }).click();

    const panel = page.getByRole('menu').or(page.getByText(/notification/i).first());
    await expect(panel.first()).toBeVisible({ timeout: 10_000 });
    expect(pageErrors, pageErrors.join('\n')).toEqual([]);
  });
});
