import type { Profile } from "./types";
import { QUESTIONS } from "./questionnaire";

/** Map confirmed facts only. Combined questionnaire answers stay unknown. */
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
 // Age brackets, grouped degrees, and applicant-or-family disability are ambiguous.
 return { attributes, need_type: "unknown", dislikes: [], current_benefits: [], asked: [], skipped: [] };
}
