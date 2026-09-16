import type { Profile } from './types';
import type { MatchItem, MatchResponse } from '@/benefits/types';

const categories: Record<string, string[]> = {
 '就學與學費': ['scholarship', 'student_aid', 'tuition_waiver', 'education_subsidy', 'housing_support', 'emergency_aid_student', 'student_loan', 'study_abroad'],
 '就業與職訓': ['unemployment_benefit', 'training_allowance', 'employment_incentive', 'youth_employment', 'worker_welfare'],
 '住宅與租金': ['rental_subsidy', 'housing_loan_subsidy', 'social_housing'],
};
const domains: Record<string, string[]> = {
 '經濟補助': ['social_welfare'], '育兒與托育': ['social_welfare'], '生活物資': ['social_welfare'],
 '醫療與健保': ['health'], '長照與照顧': ['long_term_care', 'disability'], '身心健康支持': ['health', 'disability'],
};

/** tier1 ✅ 符合｜tier2 🟡 可能符合・需補充資料｜hidden；舊資料（沒有資格骨幹）由 status 推得 */
export function tierOf(item: Pick<MatchItem, 'tier' | 'status' | 'is_overview'>) {
 if (item.tier) return item.tier;
 if (item.is_overview) return 'hidden';
 return item.status === 'high_match' ? 'tier1' : item.status === 'possible_match' ? 'tier2' : 'hidden';
}

/** 戶籍縣市和使用者不同（未確認，所以沒有被隱藏）時，回傳該補助寫的戶籍條件，例如「設籍彰化縣」。 */
export function residenceMismatch(item: Pick<MatchItem, 'core'>) {
 return (item.core || []).find(facet => facet.kind === 'residence' && facet.state === 'violated')?.label || '';
}

export function officialRecommendations(result: MatchResponse | null, profile: Profile) {
 const adult = profile.age != null && profile.age >= 18;
 // A child's education savings account is not an adult's current tuition aid.
 // This is a homepage relevance filter, not a legal eligibility decision.
 const childEducation = /幼兒園.*(?:就學|學費|收費)|(?:兒童(?:及|與)少年|兒少).*教育.*(?:帳戶|賬戶)/;
 const relevant = (item: { title?: string; category: string; domain: string }) =>
  !(adult && childEducation.test(item.title || '')) &&
  profile.needs.some(need => categories[need]?.includes(item.category) || domains[need]?.includes(item.domain));
 const related = (result?.matches || []).filter(relevant);
 const removed = new Set((result?.ranking?.removed || []).map(item => item.benefit_id));
 const shown = related.filter(item => !removed.has(item.benefit_id) && tierOf(item) !== 'hidden');
 // 別縣市的補助（戶籍條件未確認才沒被隱藏）排在同層最後，避免首頁前幾筆都是其他縣市的方案
 shown.sort((a, b) => Number(tierOf(a) === 'tier2') - Number(tierOf(b) === 'tier2') || Number(!!residenceMismatch(a)) - Number(!!residenceMismatch(b))
  || (a.needs?.length ?? 0) - (b.needs?.length ?? 0) || b.eligibility_score - a.eligibility_score);
 const confirmed = shown.filter(item => tierOf(item) === 'tier1');
 const needsInfo = shown.filter(item => tierOf(item) === 'tier2');
 return { matches: shown, confirmed, needsInfo, pending: related.filter(item => item.status === 'insufficient_data' && tierOf(item) === 'hidden').length };
}
