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
  preferences: { enum_candidates: education && levels[education] ? { 'education.level': levels[education] } : {} } as Record<string, unknown>,
  _domains: [...new Set(needs.flatMap(need => domains[need] || []))] };
}

const AGE_BRACKETS: [number, number | null][] = [[0, 17], [18, 24], [25, 29], [30, 64], [65, null]];
const EMPLOYMENT: (string | null)[] = ["employed", "self_employed", "unemployed", null, null, "student"];
const HOUSING: (string | null)[] = ["rent", "dorm", "own", "family", null];

/**
 * Profile for the eligibility engine (dashboard, My Benefits, diagnostics).
 * The assistant keeps using toBenefitProfile so the chat-to-schema flow is unchanged.
 * Adds only what the questionnaire answers state: age bracket as a range, explicit economic hardship,
 * work and housing status, care needs, and "not ticked" for certificate-based identities a person always knows
 * (indigenous status, disability certificate, single-parent / special-circumstances family).
 */
export function toMatchingProfile(profile: Profile) {
 const base = toBenefitProfile(profile);
 const attributes = { ...base.attributes };
 const preferences = { ...base.preferences };
 const screening = profile.screening ?? {};
 const pick = (key: string) => QUESTIONS.find(q => q.key === key)!;
 const chosen = (key: string) => (screening[key] ?? []).map(option => pick(key).options.indexOf(option)).filter(index => index >= 0);
 const [age] = chosen("age");
 if (profile.age == null && age != null) preferences.number_ranges = { "applicant.age": AGE_BRACKETS[age] };
 const [economy] = chosen("economy");
 if (economy === 2) attributes["identity.economic_hardship"] = true;
 if (economy === 3) attributes["identity.economic_hardship"] = false;
 const identity = chosen("identity");
 if (identity.length) {
  if (identity.includes(0)) attributes["identity.indigenous"] = true;
  else attributes["identity.indigenous"] = false;
  if (!identity.includes(1)) { attributes["disability.has_certificate"] = false; attributes["disability.family_member_has_certificate"] = false; }
  if (!identity.includes(2)) { attributes["identity.single_parent"] = false; attributes["identity.special_circumstances"] = false; }
 }
 const employment = chosen("employment").map(index => EMPLOYMENT[index]).filter(Boolean);
 if (employment.length === 1) attributes["employment.status"] = employment[0];
 const [housing] = chosen("housing");
 if (housing != null && HOUSING[housing]) attributes["housing.tenure"] = HOUSING[housing];
 const support = chosen("support");
 if (support.includes(1)) attributes["care.needs_care"] = true;
 if (support.includes(2)) attributes["care.is_primary_caregiver"] = true;
 return { ...base, attributes, preferences };
}
