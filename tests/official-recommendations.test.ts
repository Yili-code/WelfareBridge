import { expect, it } from 'vitest';
import { officialRecommendations, residenceMismatch } from '../src/lib/official-recommendations';
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

it('uses the engine tier when present and lists fully matched benefits before those needing more information', () => {
 const item = (id: string, tier: 'tier1' | 'tier2' | 'hidden', status: string, needs: string[] = []) => ({ benefit_id: id, category: 'scholarship', domain: 'education', status, tier, needs, eligibility_score: .5, is_overview: false }) as MatchItem;
 const result = { matches: [item('needs-two', 'tier2', 'possible_match', ['a', 'b']), item('hidden', 'hidden', 'not_match'), item('ok', 'tier1', 'high_match'), item('needs-one', 'tier2', 'possible_match', ['a'])] } as MatchResponse;
 const selected = officialRecommendations(result, { needs: ['就學與學費'] } as Profile);
 expect(selected.confirmed.map(i => i.benefit_id)).toEqual(['ok']);
 expect(selected.needsInfo.map(i => i.benefit_id)).toEqual(['needs-one', 'needs-two']);
 expect(selected.matches.map(i => i.benefit_id)).not.toContain('hidden');
});

it('puts benefits whose household-registration city does not match the user last, and names the city', () => {
 const item = (id: string, core: MatchItem['core'] = []) => ({ benefit_id: id, category: 'scholarship', domain: 'education', status: 'possible_match', tier: 'tier2', needs: [], core, eligibility_score: .9, is_overview: false }) as unknown as MatchItem;
 const elsewhere = item('other-city', [{ kind: 'residence', status: 'uncertain', state: 'violated', reason: '', needs: [], label: '設籍彰化縣', signals: ['structure'] }]);
 const result = { matches: [elsewhere, item('same-city', [{ kind: 'residence', status: 'confirmed', state: 'satisfied', reason: '', needs: [], label: '設籍基隆市', signals: ['structure', 'title'] }])] } as MatchResponse;
 const selected = officialRecommendations(result, { needs: ['就學與學費'] } as Profile);
 expect(selected.needsInfo.map(i => i.benefit_id)).toEqual(['same-city', 'other-city']);
 expect(residenceMismatch(elsewhere)).toBe('設籍彰化縣');
 expect(residenceMismatch(item('same-city'))).toBe('');
});
