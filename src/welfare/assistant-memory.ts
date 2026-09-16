import type { AssistantAttribute, Profile } from "@/lib/types";
import type { BenefitCard, MatchResult } from "./api";

/** 後端 /api/assistant 回傳的 learned 項目 */
export interface LearnedAttribute {
  attribute_id: string;
  label: string;
  type: string;
  unit?: string;
  value: AssistantAttribute["value"];
  value_label: string;
  options?: { value: string; label: string }[];
  source: "asked" | "parsed" | "unsure";
  evidence?: string;
}

const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

/**
 * 把助理這一輪確認的資料合併進資料卡。後端每輪都會回傳目前已知的全部對話資料，
 * 所以只有值真的變了（或新出現）的項目才算「新補充」，用來在聊天視窗告訴使用者寫進了什麼。
 */
export function mergeLearned(current: Profile["assistantAttributes"], learned: LearnedAttribute[], now = new Date().toISOString()) {
  const next: Record<string, AssistantAttribute> = { ...(current ?? {}) };
  const changed: AssistantAttribute[] = [];
  for (const item of learned) {
    const previous = next[item.attribute_id];
    if (previous && same(previous.value, item.value)) continue;
    const entry: AssistantAttribute = {
      label: item.label, type: item.type, unit: item.unit || undefined, value: item.value, valueLabel: item.value_label,
      options: item.options?.length ? item.options : undefined, source: item.source, evidence: item.evidence || undefined, updatedAt: now,
    };
    next[item.attribute_id] = entry;
    changed.push(entry);
  }
  return { next, changed };
}

/** 資料卡上修改助理補充的值：換算顯示文字，並標記為使用者自己確認過 */
export function editLearned(entry: AssistantAttribute, raw: string, now = new Date().toISOString()): AssistantAttribute {
  let value: AssistantAttribute["value"] = raw === "" ? null : raw;
  let valueLabel = raw === "" ? "不確定" : raw;
  if (raw !== "" && entry.type === "boolean") { value = raw === "true"; valueLabel = value ? "是" : "否"; }
  if (raw !== "" && entry.type === "number") { value = Number(raw); valueLabel = `${raw}${entry.unit ?? ""}`; }
  if (raw !== "" && (entry.type === "enum" || entry.type === "multi_enum")) {
    const option = entry.options?.find(o => o.value === raw);
    value = entry.type === "multi_enum" ? [raw] : raw;
    valueLabel = option?.label ?? raw;
  }
  return { ...entry, value, valueLabel, source: value === null ? "unsure" : "edited", updatedAt: now };
}

/** 依需求排序：先列使用者在資料卡選的需求領域，再依還缺幾項資料 */
const NEED_DOMAINS: Record<string, string[]> = {
  "就學、學費或獎助學金": ["education", "youth"],
  "求職、失業或職業訓練": ["labor", "youth"],
  "租屋、住宅或居住改善": ["housing"],
  "生活費、育兒或急難救助": ["social_welfare"],
  "醫療、身心障礙或長期照顧": ["health", "disability", "long_term_care"],
};

export function needDomains(profile: Profile | null) {
  const needs = profile?.screening?.needs ?? [];
  return new Set(needs.flatMap(need => NEED_DOMAINS[need] ?? []));
}

export function rankForProfile(cards: BenefitCard[], results: Record<string, MatchResult>, domains: Set<string>) {
  return [...cards].sort((a, b) =>
    Number(!domains.has(a.domain_id)) - Number(!domains.has(b.domain_id))
    || (results[a.id]?.needs.length ?? 0) - (results[b.id]?.needs.length ?? 0)
    || a.title.localeCompare(b.title, "zh-Hant"));
}
