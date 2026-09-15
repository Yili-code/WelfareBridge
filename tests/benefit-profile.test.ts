import { describe, expect, it } from "vitest";
import { toBenefitProfile } from "../src/lib/benefit-profile";
import type { Profile } from "../src/lib/types";
const base: Profile = { id: "one", nickname: "測試", relation: "self", region: "臺北市", age: null, economy: "不確定", identities: [], needs: [], createdAt: "" };
describe("welfare questionnaire to eligibility engine", () => {
 it("carries chosen needs and grouped education without guessing a degree", () => {
  const result = toBenefitProfile({ ...base, age: 20, screening: { needs: ['就學、學費或獎助學金', '租屋、住宅或居住改善', '求職、失業或職業訓練'], education: ['大學、二專或五專後兩年'] } });
  expect(result._domains).toEqual(['education', 'housing', 'labor']);
  expect(result.preferences.enum_candidates).toEqual({ 'education.level': ['university', 'junior_college'] });
  expect(result.attributes).not.toHaveProperty('education.level');
 });
 it("does not invent exact age, personal disability, degree, or registered city from ambiguous or legacy input", () => {
  const result = toBenefitProfile({ ...base, screening: { age: ["18～未滿 25 歲"], identity: ["本人或家庭成員持有身心障礙證明"], education: ["碩士班或博士班"] } });
  expect(result.attributes).toEqual({ "applicant.is_student": true });
 });
 it("keeps registered and current cities distinct and sends confirmed age and income status", () => {
  const result = toBenefitProfile({ ...base, age: 22, currentRegion: "臺南市", economy: "低收入戶", screening: { residence: ["戶籍與居住地在不同縣市"] } });
  expect(result.attributes).toMatchObject({ "applicant.age": 22, "residence.household_city": "臺北市", "residence.current_city": "臺南市", "identity.low_income": true });
 });
 it("sends explicit negative answers so ineligible benefits can be rejected", () => {
  const result = toBenefitProfile({ ...base, screening: { education: ["目前未在學"], economy: ["沒有上述資格，但家庭經濟困難"] } });
  expect(result.attributes).toMatchObject({ "applicant.is_student": false, "identity.low_income": false, "identity.middle_low_income": false });
 });
 it("keeps uncertain financial status unknown instead of treating it as no", () => {
  const result = toBenefitProfile({ ...base, screening: { economy: ["不清楚家庭經濟資料或認定狀態"] } });
  expect(result.attributes).not.toHaveProperty("identity.low_income");
  expect(result.attributes).not.toHaveProperty("identity.middle_low_income");
 });
});
