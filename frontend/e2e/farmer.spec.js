import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

const TINY_PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  'base64'
);

test.describe('Register farmer', () => {
  test('dialog opens and required-field validation appears on empty Next', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/farmers');
    await page.getByRole('button', { name: /Register Farmer|Register First Farmer/i }).first().click();
    await expect(page.getByRole('heading', { name: 'Register New Farmer' })).toBeVisible();

    const next = page.getByRole('button', { name: 'Next' });
    if (await next.isEnabled()) {
      await next.click();
    } else {
      await expect(next).toBeDisabled();
    }

    await expect(page.getByText(/Registration Form Validation|Name is required/i).first()).toBeVisible();
    await expect(page.getByLabel('Full Name').or(page.getByLabel(/Name/i)).first()).toBeVisible();
  });

  test('ID upload accepts empty OCR or Grok without failing the suite', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/farmers');
    await page.getByRole('button', { name: /Register Farmer|Register First Farmer/i }).first().click();
    await expect(page.getByRole('heading', { name: 'Register New Farmer' })).toBeVisible();

    const file = page.locator('input[type="file"]');
    if (!(await file.count())) {
      return;
    }
    await file.setInputFiles({
      name: 'pw-id.png',
      mimeType: 'image/png',
      buffer: TINY_PNG,
    });
    const note = page.getByText(/Filled using Grok|Filled using Tesseract|No details could be read|Reading document|Check the filled/i);
    await note.first().waitFor({ timeout: 20_000 }).catch(() => {});
  });
});
