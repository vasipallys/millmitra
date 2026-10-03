import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';
import { selectFirstRealOption, uniqueNote } from './helpers/ui.js';

test.describe('Mill flow', () => {
  test('receive walk-in paddy and continue to the next step', async ({ page, request }) => {
    const location = uniqueNote('godown');
    await openAs(page, request, 'operator', '/mill-flow');
    await expect(page.getByRole('heading', { name: 'Mill flow' }).first()).toBeVisible({ timeout: 20_000 });

    await page.getByRole('button', { name: 'Start from receive paddy' }).click();
    await expect(page.getByText('1. Receive paddy')).toBeVisible();

    const farmer = page.getByLabel('Farmers').first();
    await farmer.click();
    await page.getByRole('option', { name: 'Walk-in / later' }).click();
    await expect(farmer).toContainText(/Walk-in \/ later/i);

    await selectFirstRealOption(page, 'Variety');
    await page.getByLabel('Quantity (kg)').fill('25');
    await page.getByLabel(/Purchase Price/i).fill('22');
    await page.getByLabel('Storage Location').fill(location);

    const save = page.getByRole('button', { name: 'Save paddy and continue' });
    await expect(save).toBeEnabled();
    await Promise.all([
      page.waitForResponse((response) => (
        /\/inventory\//.test(response.url())
        && response.request().method() === 'POST'
      ), { timeout: 20_000 }).catch(() => null),
      save.click(),
    ]);

    const nextStep = page.getByText('2. Start batch');
    const error = page.getByRole('alert').filter({ hasText: /could not save|Fill required|failed/i });
    await expect(nextStep.or(error)).toBeVisible({ timeout: 20_000 });
    await expect(error).toHaveCount(0);
    await expect(nextStep).toBeVisible();
  });
});
