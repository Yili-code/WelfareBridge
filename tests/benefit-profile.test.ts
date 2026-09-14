import { describe, expect, it } from "vitest";
import { toBenefitProfile } from "../src/lib/benefit-profile";
import type { Profile } from "../src/lib/types";
const base: Profile = { id: "one", nickname: "測試", relation: "self", region: "臺北市", age: null, economy: "不確定", identities: [], needs: [], createdAt: "" };
describe("welfare questionnaire to eligibility engine", () => {
 it("does not invent exact age, personal disability, degree, or registered city from ambiguous or legacy input", () => {
  const result = toBenefitProfile({ ...base, screening: { age: ["18～未滿 25 歲"], identity: ["本人或家庭成員持有身心障礙證明"], education: ["碩士班或博士班"] } });
  expect(result.attributes).toEqual({});
 });
 it("keeps registered and current cities distinct and sends confirmed age and income status", () => {
  const result = toBenefitProfile({ ...base, age: 22, currentRegion: "臺南市", economy: "低收入戶", screening: { residence: ["戶籍與居住地在不同縣市"] } });
  expect(result.attributes).toMatchObject({ "applicant.age": 22, "residence.household_city": "臺北市", "residence.current_city": "臺南市", "identity.low_income": true });
 });
});
