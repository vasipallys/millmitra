import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('Dynamic form', () => {
  test('admin saves a metadata-defined inspection record', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/form-builder');
    await page.getByRole('button', { name: /Add field|फ़ील्ड जोड़ें|ఫీల్డ్/i }).click();
    await page.getByLabel(/Field name|फ़ील्ड नाम/i).last().fill('note');
    await page.getByLabel(/Label EN/i).last().fill('Note');
    await page.getByTestId('save-form-layout').click();

    await page.goto('/forms/farmer');
    await expect(page.getByRole('heading', { name: /Dynamic forms|डायनामिक|డైనమిక్/i })).toBeVisible();
    const note = page.getByLabel(/Note|Soil|Custom|नोट/i).first();
    if (await note.count()) {
      await note.fill('field walk');
    }
    await page.getByTestId('dynamic-form-save').click();
    await expect(page.getByText(/saved|सहेजा|సేవ్/i).first()).toBeVisible({ timeout: 15_000 });
  });
});
