import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('Dashboard', () => {
  test('shows a next action for mill work', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/dashboard');
    await expect(page.getByText('Next step', { exact: true })).toBeVisible({ timeout: 20_000 });
    await expect(
      page.getByRole('button', { name: /Register farmer|Add stock|Open Mill flow/i })
    ).toBeVisible();
  });
});
