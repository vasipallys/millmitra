import { test, expect } from '@playwright/test';
import { loginViaForm, expectSignedIn, logoutFromApp } from './helpers/auth.js';

test.describe('Logout', () => {
  test('logout returns to the login screen', async ({ page }) => {
    await loginViaForm(page, 'operator', 'operator123');
    await expectSignedIn(page);
    await logoutFromApp(page);
    await expect(page.getByText('Sign in to MillMitra')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Login', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Account menu' })).toHaveCount(0);
  });
});
