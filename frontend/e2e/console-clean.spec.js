import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';
import { attachConsoleGuard } from './helpers/console.js';

const ROUTES = [
  '/customers',
  '/farmers',
  '/users',
  '/forms/inspection',
  '/dashboard-builder',
];

test.describe('App console stays clean', () => {
  for (const path of ROUTES) {
    test(`${path} has no app console errors`, async ({ page, request }) => {
      const guard = attachConsoleGuard(page);
      await openAs(page, request, 'admin', path);
      await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 15000 });
      await page.waitForTimeout(1200);
      guard.assertClean();
    });
  }
});
