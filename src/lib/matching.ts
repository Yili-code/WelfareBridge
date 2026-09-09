import type { Profile, Resource } from "./types";

/**
 * 比對資源與 profile。
 * 回傳 null 代表不符合；回傳字串則是「為什麼推薦給你」的說明，
 * 直接顯示在通知裡，讓使用者知道系統是根據哪些條件配對的。
 */
export function matchReason(resource: Resource, profile: Profile): string | null {
  const regionOk =
    resource.regions.length === 0 ||
    resource.regions.includes("全國") ||
    resource.regions.includes(profile.region);
  if (!regionOk) return null;

  if (resource.minAge != null && profile.age < resource.minAge) return null;
  if (resource.maxAge != null && profile.age > resource.maxAge) return null;

  const identityHits = resource.identities.filter((i) =>
    profile.identities.includes(i),
  );
  const needHits = resource.needs.filter((n) => profile.needs.includes(n));

  // 有指定身分／需求時，至少要命中一項才推薦
  const hasFilters = resource.identities.length > 0 || resource.needs.length > 0;
  if (hasFilters && identityHits.length === 0 && needHits.length === 0) {
    return null;
  }

  const parts: string[] = [];
  if (resource.regions.includes(profile.region)) parts.push(profile.region);
  if (identityHits.length) parts.push(identityHits.join("、"));
  if (needHits.length) parts.push(`需求：${needHits.join("、")}`);
  if (resource.minAge != null || resource.maxAge != null) {
    parts.push(`${profile.age} 歲符合年齡條件`);
  }

  return parts.length
    ? `符合「${profile.nickname}」的 ${parts.join("・")}`
    : `符合「${profile.nickname}」的條件`;
}

/** 列出符合某個 profile 的所有資源 */
export function matchResources(resources: Resource[], profile: Profile) {
  return resources
    .map((r) => ({ resource: r, reason: matchReason(r, profile) }))
    .filter((x): x is { resource: Resource; reason: string } => x.reason !== null);
}
