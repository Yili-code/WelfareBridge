import type { Profile } from './types';
import type { MatchResponse } from '@/benefits/types';

const categories: Record<string, string[]> = {
 '就學與學費': ['scholarship', 'student_aid', 'tuition_waiver', 'education_subsidy', 'housing_support', 'emergency_aid_student', 'student_loan', 'study_abroad'],
 '就業與職訓': ['unemployment_benefit', 'training_allowance', 'employment_incentive', 'youth_employment', 'worker_welfare'],
 '住宅與租金': ['rental_subsidy', 'housing_loan_subsidy', 'social_housing'],
};
const domains: Record<string, string[]> = {
 '經濟補助': ['social_welfare'], '育兒與托育': ['social_welfare'], '生活物資': ['social_welfare'],
 '醫療與健保': ['health'], '長照與照顧': ['long_term_care', 'disability'], '身心健康支持': ['health', 'disability'],
};

export function officialRecommendations(result: MatchResponse | null, profile: Profile) {
 const relevant = (item: { category: string; domain: string }) => profile.needs.some(need => categories[need]?.includes(item.category) || domains[need]?.includes(item.domain));
 const related = (result?.matches || []).filter(relevant);
 const removed = new Set((result?.ranking?.removed || []).map(item => item.benefit_id));
 const matches = related.filter(item => !removed.has(item.benefit_id) && !item.is_overview && (item.status === 'high_match' || item.status === 'possible_match'));
 matches.sort((a, b) => Number(b.status === 'high_match') - Number(a.status === 'high_match') || b.eligibility_score - a.eligibility_score);
 return { matches, pending: related.filter(item => item.status === 'insufficient_data').length };
}
