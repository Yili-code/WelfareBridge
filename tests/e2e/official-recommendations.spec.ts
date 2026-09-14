import { test, expect } from '@playwright/test';

test('dashboard does not recommend unrelated or insufficient-data benefits', async ({ page }) => {
 await page.route('**/api/matching', route => route.fulfill({ json: { matches: [
  { benefit_id: 'rent', title: '無關租屋方案', category: 'rental_subsidy', domain: 'housing', status: 'high_match', eligibility_score: 1, explanation: [] },
  { benefit_id: 'unknown', title: '未知資格獎學金', category: 'scholarship', domain: 'education', status: 'insufficient_data', eligibility_score: .5, explanation: [] },
  { benefit_id: 'aid', title: '相關學費補助', category: 'student_aid', domain: 'education', status: 'possible_match', eligibility_score: .6, explanation: ['學生身分符合'] }
 ], ranking: { removed: [] } } }));
 await page.goto('/');
 await page.evaluate(() => localStorage.setItem('wf.profiles', JSON.stringify([{ id: 'one', nickname: '測試', age: 22, identities: [], needs: ['就學與學費'], region: '', economy: '不確定' }])));
 await page.goto('/dashboard');
 const section = page.getByRole('region', { name: '官方補助媒合' });
 await expect(section.getByText('相關學費補助', { exact: true })).toBeVisible();
 await expect(section.getByText('無關租屋方案')).toHaveCount(0);
 await expect(section.getByText('未知資格獎學金')).toHaveCount(0);
 await expect(section.getByText(/另有 1 筆相關補助缺少判斷資料/)).toBeVisible();
});
