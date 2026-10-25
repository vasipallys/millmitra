import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('IIoT manual entry', () => {
  test('admin can submit a manual reading', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/iiot');
    await expect(page.getByRole('heading', { name: /IIoT/i })).toBeVisible();
    await page.getByLabel('Value').fill('14.2');
    await page.getByLabel('Reason').fill('lab check');
    await page.getByTestId('iiot-manual-submit').click();
    await expect(page.getByText('manual').first()).toBeVisible({ timeout: 15_000 });
  });
});
