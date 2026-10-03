import { expect } from '@playwright/test';

export function uniqueNote(suffix = '') {
  return `pw-${Date.now()}${suffix ? `-${suffix}` : ''}`;
}

export function drawer(page) {
  return page.locator('.MuiDrawer-paper');
}

export function sidebarItem(page, name) {
  return drawer(page).locator('.MuiListItemButton-root', { hasText: name });
}

export async function ensureSidebarOpen(page) {
  const paper = drawer(page);
  const width = await paper.evaluate((el) => el.getBoundingClientRect().width).catch(() => 0);
  if (width < 80) {
    await page.getByRole('button', { name: 'menu', exact: true }).click();
  }
  await expect(page.getByRole('button', { name: 'Dashboard Overview & Analytics' })).toBeVisible({ timeout: 10_000 });
}

export async function openMuiSelect(page, label) {
  const control = page.getByLabel(label).first();
  await expect(control).toBeVisible({ timeout: 12_000 });
  await control.click();
  const items = page.locator('li.MuiMenuItem-root').filter({ visible: true });
  await expect(items.first()).toBeVisible({ timeout: 10_000 });
  return items;
}

export async function selectOptionByName(page, label, name) {
  const items = await openMuiSelect(page, label);
  await items.filter({ hasText: name }).first().click();
}

export async function selectFirstRealOption(page, label) {
  const options = await openMuiSelect(page, label);
  const count = await options.count();
  expect(count, `${label} dropdown should load options from the API`).toBeGreaterThan(0);
  const first = options.first();
  const text = (await first.innerText()).trim();
  await first.click();
  return { count, text };
}

export async function waitForPageTitle(page, title) {
  await expect(page.getByRole('heading', { name: title }).first()).toBeVisible({ timeout: 20_000 });
}
