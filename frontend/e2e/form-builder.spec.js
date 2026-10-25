import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('Form builder', () => {
  test('admin can add a field and save the farmer layout', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/form-builder');
    await expect(page.getByRole('heading', { name: /Form builder/i })).toBeVisible();
    await page.getByRole('button', { name: 'Add field' }).click();
    await page.getByLabel('Field name').last().fill('soil_type');
    await page.getByLabel('Label EN').last().fill('Soil type');
    await page.getByTestId('save-form-layout').click();
    await expect(page.getByText('Form layout saved')).toBeVisible({ timeout: 15_000 });
  });
});
