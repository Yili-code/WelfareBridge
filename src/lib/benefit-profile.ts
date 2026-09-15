import type { Profile } from "./types";
import { QUESTIONS } from "./questionnaire";

/** Map confirmed facts and retain grouped education as possible values. */
export function toBenefitProfile(profile: Profile) {
 const attributes: Record<string, unknown> = {};
 if (profile.age != null) attributes["applicant.age"] = profile.age;
 // Legacy region fields did not distinguish registration from residence.
 if (profile.screening?.residence && profile.region) attributes["residence.household_city"] = profile.region;
 if (profile.currentRegion) attributes["residence.current_city"] = profile.currentRegion;
 if (profile.economy === "低收入戶") attributes["identity.low_income"] = true;
 if (profile.economy === "中低收入戶") attributes["identity.middle_low_income"] = true;
 const economy = profile.screening?.economy?.[0];
 if (economy === QUESTIONS[4].options[2] || economy === QUESTIONS[4].options[3]) {
  attributes["identity.low_income"] = false;
  attributes["identity.middle_low_income"] = false;
 }
 const education = profile.screening?.education?.[0];
 if (education && QUESTIONS[3].options.includes(education)) {
  attributes["applicant.is_student"] = education !== QUESTIONS[3].options[0];
 }
 // Preserve the possible levels without inventing an exact degree.
 const levels: Record<string, string[]> = {
  '國小或國中': ['elementary', 'junior_high'],
  '高中職或五專前三年': ['senior_high', 'vocational_high', 'junior_college'],
  '大學、二專或五專後兩年': ['university', 'junior_college'],
  '碩士班或博士班': ['master', 'doctoral'],
 };
 const needs = profile.screening?.needs ?? profile.needs;
 const domains: Record<string, string[]> = {
  '就學、學費或獎助學金': ['education'], '就學與學費': ['education'],
  '求職、失業或職業訓練': ['labor'], '就業與職訓': ['labor'],
  '租屋、住宅或居住改善': ['housing'], '住宅與租金': ['housing'],
  '生活費、育兒或急難救助': ['social_welfare'], '經濟補助': ['social_welfare'],
  '育兒與托育': ['social_welfare'], '生活物資': ['social_welfare'],
  '醫療、身心障礙或長期照顧': ['health', 'disability', 'long_term_care'],
  '醫療與健保': ['health'], '長照與照顧': ['long_term_care', 'disability'], '身心健康支持': ['health', 'disability'],
 };
 return { attributes, need_type: "unknown", dislikes: [], current_benefits: [], asked: [], skipped: [],
  preferences: { enum_candidates: education && levels[education] ? { 'education.level': levels[education] } : {} },
  _domains: [...new Set(needs.flatMap(need => domains[need] || []))] };
}
