import { test, expect } from '@playwright/test';
import { loginViaForm, expectSignedIn } from './helpers/auth.js';

test.describe('Login', () => {
  test('admin password succeeds and lands on the mill', async ({ page }) => {
    await loginViaForm(page, 'admin', 'admin123');
    await expectSignedIn(page);
    await expect(page).not.toHaveURL(/\/login$/);
    await expect(
      page.getByText(/Next step|Register farmer|Add stock|Open Mill flow/i).first()
    ).toBeVisible({ timeout: 20_000 });
  });

  test('wrong password shows not recognized', async ({ page }) => {
    await loginViaForm(page, 'admin', 'wrong-password-pw');
    await expect(page.getByRole('alert')).toContainText(/not recognized/i, { timeout: 15_000 });
    await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
  });
});
