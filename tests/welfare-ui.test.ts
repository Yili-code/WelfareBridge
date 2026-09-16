import { describe, expect, it } from "vitest";
import { toMatchingProfile } from "../src/lib/benefit-profile";
import type { Profile } from "../src/lib/types";
import type { BenefitCard, MatchResult } from "../src/welfare/api";
import { editLearned, mergeLearned, type LearnedAttribute } from "../src/welfare/assistant-memory";
import { emptyFilters, facetCounts, searchCards } from "../src/welfare/search";

const card = (id: string, extra: Partial<BenefitCard> = {}): BenefitCard => ({
  id, title: `補助${id}`, domain_id: "housing", domain: "住宅", service_type: "租金補貼", audiences: ["一般民眾"], region: "全國", agency: "內政部", points: [], price: null, updated: "", ...extra,
});
const result = (status: MatchResult["status"], needs: string[] = []): MatchResult => ({ status, reasons: [], needs });

describe("查詢補助：篩選、搜尋與排序", () => {
  const cards = [
    card("a", { title: "臺北市租金補貼", region: "臺北市", audiences: ["租屋族"] }),
    card("b", { title: "高雄市急難救助", region: "高雄市", domain_id: "social_welfare", domain: "社會福利", service_type: "急難救助" }),
    card("c", { title: "全國學產基金", audiences: ["學生", "低收／中低收"], domain_id: "education", domain: "教育", service_type: "助學金", updated: "2026-09-01" }),
  ];

  it("counts facets and filters by any selected value", () => {
    expect(facetCounts(cards, "region")).toEqual([["全國", 1], ["臺北市", 1], ["高雄市", 1]].sort((x, y) => (x[0] as string).localeCompare(y[0] as string, "zh-Hant")));
    const filters = emptyFilters();
    filters.audiences.add("學生");
    expect(searchCards(cards, { query: "", filters, onlyMatch: false, sort: "title" }).map(c => c.id)).toEqual(["c"]);
  });

  it("matches every keyword and treats 台 and 臺 the same", () => {
    expect(searchCards(cards, { query: "台北 租金", filters: emptyFilters(), onlyMatch: false, sort: "title" }).map(c => c.id)).toEqual(["a"]);
  });

  it("puts likely matches first and hides unlikely ones only when asked", () => {
    const results = { a: result("maybe", ["就業狀態", "年齡"]), b: result("no"), c: result("yes") };
    expect(searchCards(cards, { query: "", filters: emptyFilters(), onlyMatch: false, sort: "match", results }).map(c => c.id)).toEqual(["c", "a", "b"]);
    expect(searchCards(cards, { query: "", filters: emptyFilters(), onlyMatch: true, sort: "match", results }).map(c => c.id)).toEqual(["c", "a"]);
  });
});

describe("小幫手補充的資料寫回資料卡", () => {
  const learned = (value: LearnedAttribute["value"], value_label: string): LearnedAttribute => ({ attribute_id: "employment.status", label: "就業狀態", type: "enum", value, value_label, options: [{ value: "unemployed", label: "失業中" }, { value: "employed", label: "受僱" }], source: "asked" });

  it("reports only values that are new or changed", () => {
    const first = mergeLearned(undefined, [learned("unemployed", "失業中")], "2026-09-17T00:00:00Z");
    expect(first.changed.map(c => c.valueLabel)).toEqual(["失業中"]);
    const again = mergeLearned(first.next, [learned("unemployed", "失業中")]);
    expect(again.changed).toEqual([]);
    expect(mergeLearned(first.next, [learned("employed", "受僱")]).changed.map(c => c.valueLabel)).toEqual(["受僱"]);
  });

  it("uses the assistant's answers ahead of what the questionnaire implies, keeping unconfirmed readings unconfirmed", () => {
    const { next } = mergeLearned(undefined, [learned("employed", "受僱"), { attribute_id: "family.children_count", label: "子女人數", type: "number", value: 2, value_label: "2人", source: "parsed", evidence: "我有兩個小孩" }]);
    const profile = { id: "p", nickname: "我", relation: "self", region: "臺北市", age: 40, identities: [], economy: "", needs: [], createdAt: "",
      screening: { employment: ["待業中，正在找工作"] }, assistantAttributes: next } as Profile;
    const attributes = toMatchingProfile(profile).attributes as Record<string, unknown>;
    expect(attributes["employment.status"]).toEqual({ value: "employed", source: "asked", confirmed: true, evidence: "" });
    expect(attributes["family.children_count"]).toEqual({ value: 2, source: "parsed", confirmed: false, evidence: "我有兩個小孩" });
  });

  it("editing on the data card marks the value as confirmed by the user", () => {
    const { next } = mergeLearned(undefined, [learned("unemployed", "失業中")]);
    const edited = editLearned(next["employment.status"], "employed");
    expect(edited).toMatchObject({ value: "employed", valueLabel: "受僱", source: "edited" });
    expect(editLearned(next["employment.status"], "")).toMatchObject({ value: null, valueLabel: "不確定", source: "unsure" });
  });
});
