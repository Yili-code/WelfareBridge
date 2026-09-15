import { test, expect } from '@playwright/test';

test('assistant sends conversation context and retries without duplicating user replies', async ({ page }) => {
  const bodies: { messages: { role: string; content: string }[] }[] = [];
  await page.route('**/api/matching', route => route.fulfill({ json: { matches: [] } }));
  await page.route('**/api/assistant', async route => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 2) return route.fulfill({ status: 503, json: { detail: '模型暫時離線' } });
    await route.fulfill({ json: { reply: bodies.length === 1 ? '目前最需要哪方面協助？' : '每月房租大約多少？', quickReplies: [], llm_used: true, turn_count: bodies.length === 1 ? 0 : 1, candidate_count: 17, guidance_profile: { attributes: { 'applicant.age': 22 } }, search: bodies.length === 1 ? null : { queries: ['租金補助'], searched_count: 1, candidate_count: 1, truncated: false, items: [{ id: 'rent-1', title: '測試租金補助', status: 'possible_match', source_name: '測試機關', source_url: 'https://example.gov.tw/rent', missing_conditions: ['家庭收入'] }] } } });
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
  await expect(page.getByText(/已回答 1 \/ 9 輪/)).toBeVisible();
  await expect(page.getByText('查看 Schema 與目前資料', { exact: true })).toHaveCount(0);
  await expect(page.getByText('API JSON Schema', { exact: true })).toHaveCount(0);
  const results = page.getByRole('region', { name: '補助搜尋結果' });
  await expect(results.getByRole('link', { name: '測試租金補助' })).toHaveAttribute('href', '/data-center/rent-1');
  await expect(results.getByRole('link', { name: '查看來源' })).toHaveAttribute('href', 'https://example.gov.tw/rent');
  await expect(results.getByText('待確認：家庭收入')).toBeVisible();
});
