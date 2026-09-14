import type { Profile } from "./types";

/** Map confirmed facts only. Combined questionnaire answers stay unknown. */
export function toBenefitProfile(profile: Profile) {
 const attributes: Record<string, unknown> = {};
 if (profile.age != null) attributes["applicant.age"] = profile.age;
 // Legacy region fields did not distinguish registration from residence.
 if (profile.screening?.residence && profile.region) attributes["residence.household_city"] = profile.region;
 if (profile.currentRegion) attributes["residence.current_city"] = profile.currentRegion;
 if (profile.economy === "低收入戶") attributes["identity.low_income"] = true;
 if (profile.economy === "中低收入戶") attributes["identity.middle_low_income"] = true;
 // Age brackets, grouped degrees, and applicant-or-family disability are ambiguous.
 return { attributes, need_type: "unknown", dislikes: [], current_benefits: [], asked: [], skipped: [] };
}
