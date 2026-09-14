// v2 使用者資料工具：profile 是扁平的 {attributes: {attribute_id: {value, source, evidence, confirmed, confidence}}, need_type, ...}
// 屬性 id 與型別一律以 /api/meta/options 的 catalog（registry.catalog()）為準；這裡不寫死任何屬性清單。

import type { AttributeSource, AttributeValue, FieldSpec, Profile, ProfileChip, QuestionOption } from '../types';
import { NAMESPACE_LABELS } from './labels';
import { formatNumber } from './format';

export function emptyProfile(): Profile {
  return { attributes: {}, need_type: 'unknown', urgency: 'normal', dislikes: [], current_benefits: [], preferences: {}, asked: [], skipped: [] };
}

/** 後端回傳的 profile 可能缺欄位，補齊為完整結構。 */
export function normalizeProfile(input: Partial<Profile> | null | undefined): Profile {
  const base = emptyProfile();
  if (!input) return base;
  return {
    attributes: { ...(input.attributes ?? {}) },
    need_type: input.need_type || 'unknown',
    urgency: input.urgency || 'normal',
    dislikes: [...(input.dislikes ?? [])],
    current_benefits: [...(input.current_benefits ?? [])],
    preferences: { ...(input.preferences ?? {}) },
    asked: [...(input.asked ?? [])],
    skipped: [...(input.skipped ?? [])],
  };
}

export function isEmptyValue(value: unknown): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string' && value.trim() === '') return true;
  if (Array.isArray(value) && value.length === 0) return true;
  if (typeof value === 'number' && Number.isNaN(value)) return true;
  return false;
}

/** 設定單一屬性；空值 → 移除該屬性（後端對未提供的屬性回 unknown，不會判成不符合）。 */
export function setAttribute(profile: Profile, attributeId: string, value: unknown, source: AttributeSource = 'form', extra: Partial<AttributeValue> = {}): Profile {
  const attributes = { ...profile.attributes };
  if (isEmptyValue(value)) {
    delete attributes[attributeId];
  } else {
    attributes[attributeId] = { value, source, evidence: extra.evidence ?? '', confirmed: extra.confirmed ?? true, confidence: extra.confidence ?? 1 };
  }
  return { ...profile, attributes, skipped: profile.skipped.filter((id) => id !== attributeId) };
}

/** 追問的回答：來源 asked、記入 asked 清單。 */
export function applyAnswer(profile: Profile, attributeId: string, value: unknown): Profile {
  const next = setAttribute(profile, attributeId, value, 'asked');
  return { ...next, asked: next.asked.includes(attributeId) ? next.asked : [...next.asked, attributeId] };
}

/** 跳過一題：記入 skipped（後端 planner 不會再問）。 */
export function skipAttribute(profile: Profile, attributeId: string): Profile {
  const attributes = { ...profile.attributes };
  delete attributes[attributeId];
  return { ...profile, attributes, skipped: profile.skipped.includes(attributeId) ? profile.skipped : [...profile.skipped, attributeId] };
}

export function getValue(profile: Profile, attributeId: string): unknown {
  return profile.attributes[attributeId]?.value ?? null;
}

export function attributeLabel(attributeId: string, catalog?: Record<string, FieldSpec> | null): string {
  if (attributeId === 'need_type') return '需求類型';
  return catalog?.[attributeId]?.label ?? attributeId;
}

export function namespaceLabel(namespace: string, namespaces?: Record<string, string> | null): string {
  return namespaces?.[namespace] ?? NAMESPACE_LABELS[namespace] ?? namespace;
}

function optionLabelOf(options: QuestionOption[] | undefined, value: unknown): string {
  const found = options?.find((option) => String(option.value) === String(value));
  return found ? found.label : String(value);
}

/** 屬性值的顯示文字：enum → 選項 label；布林 → 是/否；陣列 → 以「、」串接。 */
export function displayAttributeValue(attributeId: string, value: unknown, catalog?: Record<string, FieldSpec> | null): string {
  if (isEmptyValue(value)) return '—';
  const spec = catalog?.[attributeId];
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (Array.isArray(value)) return value.map((item) => optionLabelOf(spec?.options, item)).join('、');
  if (typeof value === 'number') return spec?.type === 'number' ? formatNumber(value) : String(value);
  if (spec?.options?.length) return optionLabelOf(spec.options, value);
  return String(value);
}

/** 已填寫屬性的摘要（表單送出前預覽用；比對後改用 API 回傳的 profile_chips）。 */
export function profileChips(profile: Profile, catalog?: Record<string, FieldSpec> | null): ProfileChip[] {
  const chips: ProfileChip[] = [];
  for (const [attributeId, item] of Object.entries(profile.attributes)) {
    if (isEmptyValue(item.value)) continue;
    chips.push({ attribute_id: attributeId, label: attributeLabel(attributeId, catalog), value: displayAttributeValue(attributeId, item.value, catalog), source: item.source, evidence: item.evidence ?? '' });
  }
  return chips;
}

export function answeredCount(profile: Profile): number {
  return Object.values(profile.attributes).filter((item) => !isEmptyValue(item.value)).length;
}

/** 表單可顯示的屬性（排除推導屬性），依 namespace 分組並以 ask_priority 排序；domains 有值時只留相關屬性（或 all）。 */
export function groupCatalogByNamespace(catalog: Record<string, FieldSpec> | null | undefined, domains: string[] = []): Array<{ namespace: string; fields: Array<[string, FieldSpec]> }> {
  if (!catalog) return [];
  const wanted = new Set(domains);
  const groups = new Map<string, Array<[string, FieldSpec]>>();
  for (const [id, spec] of Object.entries(catalog)) {
    if (spec.derived) continue;
    if (wanted.size && !spec.domains.includes('all') && !spec.domains.some((domain) => wanted.has(domain))) continue;
    const list = groups.get(spec.namespace) ?? [];
    list.push([id, spec]);
    groups.set(spec.namespace, list);
  }
  const order = Object.keys(NAMESPACE_LABELS);
  return Array.from(groups.entries())
    .sort((a, b) => {
      const ia = order.indexOf(a[0]);
      const ib = order.indexOf(b[0]);
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    })
    .map(([namespace, fields]) => ({ namespace, fields: fields.sort((a, b) => b[1].ask_priority - a[1].ask_priority || a[0].localeCompare(b[0])) }));
}

/** 追問答案值 → catalog 型別（single_choice 的布林選項字串化後轉回布林等）。 */
export function coerceAnswer(spec: FieldSpec | undefined, value: unknown): unknown {
  if (!spec) return value;
  if (spec.type === 'boolean') {
    if (value === 'true') return true;
    if (value === 'false') return false;
    return value;
  }
  if (spec.type === 'number') {
    if (typeof value === 'string' && value.trim() !== '') return Number(value);
    return value;
  }
  return value;
}

/** Demo 範例：只用登錄表裡存在的屬性 id（education.level、education.grade、education.school、education.department、residence.household_city、academic.average_score）。 */
export function demoProfile(): Profile {
  let profile = emptyProfile();
  profile = setAttribute(profile, 'education.level', 'university');
  profile = setAttribute(profile, 'education.grade', 2);
  profile = setAttribute(profile, 'education.school', '國立臺灣海洋大學');
  profile = setAttribute(profile, 'education.department', '資訊工程');
  profile = setAttribute(profile, 'residence.household_city', '基隆市');
  profile = setAttribute(profile, 'academic.average_score', 82);
  profile = setAttribute(profile, 'applicant.is_student', true);
  return { ...profile, need_type: 'cash_now' };
}
