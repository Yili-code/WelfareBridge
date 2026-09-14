import { test, expect } from '@playwright/test';

test('assistant sends conversation context and retries without duplicating user replies', async ({ page }) => {
  const bodies: { messages: { role: string; content: string }[] }[] = [];
  await page.route('**/api/matching', route => route.fulfill({ json: { matches: [] } }));
  await page.route('**/api/assistant', async route => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 2) return route.fulfill({ status: 503, json: { detail: '模型暫時離線' } });
    await route.fulfill({ json: { reply: bodies.length === 1 ? '目前最需要哪方面協助？' : '每月房租大約多少？', quickReplies: [], llm_used: true } });
  });
  await page.goto('/');
  await page.evaluate(() => {
    localStorage.setItem('wf.profiles', JSON.stringify([{ id: 'a', nickname: '測試', relation: 'self', region: '臺北市', age: 22, identities: [], needs: [], economy: '不確定', createdAt: '' }]));
    localStorage.setItem('wf.activeProfile', 'a');
  });
  await page.goto('/dashboard');
  await page.getByRole('button', { name: '不知道怎麼找？問問助理' }).click();
  await expect(page.getByText('目前最需要哪方面協助？', { exact: true })).toBeVisible();
  await page.getByPlaceholder('也可以直接打字說明…').fill('我失業了，付不起房租');
  await page.getByRole('button', { name: '送出', exact: true }).click();
  await expect(page.getByRole('alert').filter({ hasText: '模型暫時離線' })).toBeVisible();
  await page.getByRole('button', { name: '重試', exact: true }).click();
  await expect(page.getByText('每月房租大約多少？', { exact: true })).toBeVisible();
  expect(bodies[2]).toEqual(bodies[1]);
  expect(bodies[2].messages).toEqual([{ role: 'assistant', content: '目前最需要哪方面協助？' }, { role: 'user', content: '我失業了，付不起房租' }]);
  await expect(page.getByText('我失業了，付不起房租', { exact: true })).toHaveCount(1);
});
