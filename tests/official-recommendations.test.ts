import { expect, it } from 'vitest';
import { officialRecommendations } from '../src/lib/official-recommendations';
import type { MatchItem, MatchResponse } from '../src/benefits/types';
import type { Profile } from '../src/lib/types';

it('keeps education needs relevant and excludes unknown-only and removed candidates', () => {
 const item = (id: string, category: string, status: string, score: number) => ({ benefit_id: id, category, domain: category === 'rental_subsidy' ? 'housing' : 'education', status, eligibility_score: score }) as MatchItem;
 const result = { matches: [item('rent', 'rental_subsidy', 'high_match', 1), item('unknown', 'scholarship', 'insufficient_data', .5), item('possible', 'scholarship', 'possible_match', .99), item('high', 'tuition_waiver', 'high_match', .85), item('expired', 'scholarship', 'high_match', 1)], ranking: { removed: [{ benefit_id: 'expired' }] } } as MatchResponse;
 const selected = officialRecommendations(result, { needs: ['就學與學費'] } as Profile);
 expect(selected.matches.map(item => item.benefit_id)).toEqual(['high', 'possible']);
 expect(selected.pending).toBe(1);
 expect(officialRecommendations(result, { needs: [] } as unknown as Profile).matches).toEqual([]);
});

it('does not recommend child education programs as current tuition aid for adults', () => {
 const matches = ['公立及非營利幼兒園幼兒就學補助', '衛生福利部辦理兒童及少年未來教育與發展帳戶', '大專學生助學金'].map((title, i) => ({ title, benefit_id: String(i), category: 'education_subsidy', domain: 'education', status: 'high_match', eligibility_score: 1 })) as MatchItem[];
 const result = { matches } as MatchResponse;
 expect(officialRecommendations(result, { age: 20, needs: ['就學與學費'] } as Profile).matches.map(item => item.title)).toEqual(['大專學生助學金']);
 expect(officialRecommendations(result, { age: 5, relation: 'child', needs: ['就學與學費'] } as Profile).matches).toHaveLength(3);
 expect(officialRecommendations(result, { age: null, needs: ['就學與學費'] } as Profile).matches).toHaveLength(3);
});
