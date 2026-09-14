import { test, expect } from '@playwright/test';

test('admin diagnosis shows submitted facts and rejected benefit evidence', async ({ page }) => {
 await page.route('**/api/matching/diagnose', async route => {
  expect(route.request().postDataJSON().profile.attributes['applicant.age']).toBe(22);
  await route.fulfill({ json: { total: 1, returned: 1, truncated: false, profile_used: { attributes: { 'applicant.age': 22 } }, profile_notes: [], items: [{ benefit_id: 'old', title: '高齡補助', status: 'not_match', source_url: '', retrieval_exclusions: [], explanation: ['年齡未達 65 歲'], ranking_stage: 'not_ranked', ranking_reasons: [], rule_count: 1, matched_conditions: [], missing_conditions: [], complex_conditions: [], bonus_conditions: [], failed_conditions: [{ rule_id: 'r', group_id: 'age', attribute_id: 'applicant.age', operator: '>=', value: 65, user_value: 22, reason: '未達門檻', excerpt: '申請人須年滿65歲', confidence: 1, inferred: false, status: 'not_match' }] }] } });
 });
 await page.goto('/');
 await page.evaluate(() => localStorage.setItem('wf.profiles', JSON.stringify([{ id: 'one', nickname: '測試', age: 22, identities: [], needs: [], region: '', economy: '不確定' }])));
 await page.goto('/admin');
 await page.getByRole('button', { name: '媒合診斷', exact: true }).click();
 await page.getByRole('button', { name: '開始診斷' }).click();
 await page.getByText('高齡補助 · 條件不符', { exact: true }).click();
 await expect(page.getByText('申請人須年滿65歲', { exact: true })).toBeVisible();
 await expect(page.getByRole('cell', { name: '22', exact: true })).toBeVisible();
});
