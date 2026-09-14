import { test, expect } from '@playwright/test';
import { QUESTIONS, profileTags } from '../../src/lib/questionnaire';

test('edit preserves identity, refreshes matching, persists and cancels safely', async ({ page }) => {
  const screening = Object.fromEntries(QUESTIONS.map(q => [q.key, [q.options[0]]]));
  const profile = { id: 'edit-test', createdAt: '2026-01-01', nickname: '測試對象', relation: 'self', age: 17, region: '臺北市', currentRegion: '臺北市', screening, ...profileTags(screening) };
  const requests: string[] = [];
  await page.route('**/api/matching', async route => {
    requests.push(route.request().postData() || '');
    await route.fulfill({ json: { matches: [] } });
  });
  await page.goto('/');
  await page.evaluate(p => {
    localStorage.setItem('wf.profiles', JSON.stringify([p]));
    localStorage.setItem('wf.activeProfile', p.id);
  }, profile);
  await page.goto('/dashboard');
  await expect.poll(() => requests.length).toBeGreaterThan(0);
  const before = requests.length;
  await page.getByRole('button', { name: '編輯身分', exact: true }).click();
  await page.getByLabel('修改項目').selectOption('1');
  await expect(page.getByRole('spinbutton')).toHaveValue('17');
  await page.getByRole('spinbutton').fill('22');
  await expect(page.getByRole('button', { name: '儲存修改' })).toBeDisabled();
  await page.getByRole('button', { name: '18～未滿 25 歲', exact: true }).click();
  await page.getByRole('spinbutton').fill('22');
  await page.getByRole('button', { name: '儲存修改' }).click();
  await expect.poll(() => requests.length).toBeGreaterThan(before);
  expect(requests.at(-1)).toContain('22');
  await page.reload();
  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('wf.profiles')!));
  expect(stored).toHaveLength(1);
  expect(stored[0]).toMatchObject({ id: profile.id, createdAt: profile.createdAt, age: 22 });
  await page.getByRole('button', { name: '編輯身分', exact: true }).click();
  await page.getByLabel('修改項目').selectOption('1');
  await expect(page.getByRole('spinbutton')).toHaveValue('22');
  await page.getByRole('spinbutton').fill('23');
  await page.getByRole('button', { name: '取消編輯', exact: true }).click();
  expect(await page.evaluate(() => JSON.parse(localStorage.getItem('wf.profiles')!)[0].age)).toBe(22);
});
