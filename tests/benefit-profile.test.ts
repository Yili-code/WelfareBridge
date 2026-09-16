import { describe, expect, it } from "vitest";
import { toBenefitProfile, toMatchingProfile } from "../src/lib/benefit-profile";
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
 it("matching profile turns the age bracket into a range instead of an exact age", () => {
  const result = toMatchingProfile({ ...base, screening: { age: ["65 歲以上"] } });
  expect(result.attributes).not.toHaveProperty("applicant.age");
  expect(result.preferences.number_ranges).toEqual({ "applicant.age": [65, null] });
  expect(toMatchingProfile({ ...base, age: 70, screening: { age: ["65 歲以上"] } }).preferences).not.toHaveProperty("number_ranges");
 });
 it("matching profile records certificate identities that were not ticked, but not ambiguous ones", () => {
  const result = toMatchingProfile({ ...base, screening: { identity: ["本人或家庭成員持有身心障礙證明"], economy: ["沒有上述資格，但家庭經濟困難"] } });
  expect(result.attributes).toMatchObject({ "identity.indigenous": false, "identity.single_parent": false, "identity.special_circumstances": false, "identity.economic_hardship": true });
  expect(result.attributes).not.toHaveProperty("disability.has_certificate");
  expect(toMatchingProfile({ ...base, screening: {} }).attributes).not.toHaveProperty("identity.indigenous");
 });
 it("matching profile maps single clear work and housing answers and care needs", () => {
  const result = toMatchingProfile({ ...base, screening: { employment: ["待業中，正在找工作"], housing: ["租屋，包含整戶或分租"], support: ["本人因照顧家人而減少工作或無法工作"] } });
  expect(result.attributes).toMatchObject({ "employment.status": "unemployed", "housing.tenure": "rent", "care.is_primary_caregiver": true });
  expect(toMatchingProfile({ ...base, screening: { employment: ["受僱工作中，包含兼職", "學生"] } }).attributes).not.toHaveProperty("employment.status");
 });
 it("assistant profile stays unchanged so the chat-to-schema flow is not affected", () => {
  const profile = { ...base, screening: { identity: ["以上皆無／不確定"], housing: ["租屋，包含整戶或分租"] } };
  expect(toBenefitProfile(profile).attributes).toEqual({});
 });
});
