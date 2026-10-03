import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';
import { openMuiSelect } from './helpers/ui.js';

test.describe('Inventory', () => {
  test('Add Stock product type dropdown loads API options', async ({ page, request }) => {
    await openAs(page, request, 'operator', '/inventory');
    await expect(page.getByRole('heading', { name: 'Inventory Management' })).toBeVisible({ timeout: 20_000 });

    await page.getByRole('button', { name: 'Add Stock' }).click();
    await expect(page.getByRole('heading', { name: 'Add new stock' })).toBeVisible();

    const stockOptions = await openMuiSelect(page, 'Stock type');
    const productTypeChoice = page.getByRole('option', { name: /product/i }).first();
    if (await productTypeChoice.count()) {
      await productTypeChoice.click();
    } else {
      await stockOptions.first().click();
    }

    const typeOptions = await openMuiSelect(page, /Product type|Paddy Variety/i);
    await expect(typeOptions.first()).toBeVisible({ timeout: 12_000 });
    expect(await typeOptions.count()).toBeGreaterThan(0);
    await page.keyboard.press('Escape');
  });
});
