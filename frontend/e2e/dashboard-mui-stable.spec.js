import { test, expect } from '@playwright/test';
import { openAs } from './helpers/auth.js';

test.describe('MUI dashboard unchanged by Tailwind coexist', () => {
  test('body is not preflight-reset and MUI heading uses Roboto', async ({ page, request }) => {
    await openAs(page, request, 'admin', '/dashboard');
    const heading = page.getByRole('heading', { name: /Smart Dashboard|डैशबोर्ड|డాష్/i }).first();
    await expect(heading).toBeVisible();
    const metrics = await heading.evaluate((node) => {
      const styles = getComputedStyle(node);
      const body = getComputedStyle(document.body);
      return {
        font: styles.fontFamily,
        bodyMargin: body.margin,
        dir: document.documentElement.dir,
      };
    });
    expect(metrics.font.toLowerCase()).toContain('roboto');
    expect(metrics.bodyMargin === '0px' || Number.parseFloat(metrics.bodyMargin) === 0).toBeTruthy();
  });
});
