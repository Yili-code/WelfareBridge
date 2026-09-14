import type { Profile, Resource } from './types';
import { AGE_RANGES, QUESTIONS } from './questionnaire';

/** 初篩保留資訊不足的候選；不等同正式資格審核。 */
export function matchReason(resource: Resource, profile: Profile): string | null {
 const pending: string[] = [];
 const local = resource.regions.length > 0 && !resource.regions.includes('全國');
 if (local && !resource.regions.includes(profile.region)) {
   if (!profile.screening) return null;
   // 資源尚未區分戶籍地與居住地要求，不能直接排除。
   pending.push('戶籍／居住地條件待確認');
 }
 const index = QUESTIONS[1].options.indexOf(profile.screening?.age?.[0] || '');
 const range = profile.age != null ? [profile.age, profile.age] : AGE_RANGES[index];
 if (range) {
   if (resource.minAge != null && range[1] < resource.minAge) return null;
   if (resource.maxAge != null && range[0] > resource.maxAge) return null;
   if ((resource.minAge != null && range[0] < resource.minAge) || (resource.maxAge != null && range[1] > resource.maxAge)) pending.push('實際年齡待確認');
 } else if (resource.minAge != null || resource.maxAge != null) pending.push('年齡待補充');
 const identityHits = resource.identities.filter(i => profile.identities.includes(i));
 const needHits = resource.needs.filter(n => profile.needs.includes(n));
 if (resource.identities.length && !identityHits.length) {
   if (profile.screening) pending.push('身分資格待確認');
   else if (!needHits.length) return null;
 }
 if (!profile.screening && resource.needs.length && !needHits.length && !identityHits.length) return null;
 const parts = [...identityHits, ...needHits.map(n => `需求：${n}`)];
 if (local && resource.regions.includes(profile.region)) parts.unshift(profile.region);
 if (profile.screening) return `「${profile.nickname}」的初篩候選${parts.length ? `：${parts.join('・')}` : ''}；${pending.length ? pending.join('、') + '；' : ''}仍需核對補助完整資格與併領限制`;
 return parts.length ? `符合「${profile.nickname}」的 ${parts.join('・')}` : `符合「${profile.nickname}」的條件`;
}

export function matchResources(resources: Resource[], profile: Profile) {
 return resources.map(resource => ({ resource, reason: matchReason(resource, profile) }))
  .filter((x): x is { resource: Resource; reason: string } => x.reason !== null)
  .sort((a, b) => b.resource.needs.filter(n => profile.needs.includes(n)).length - a.resource.needs.filter(n => profile.needs.includes(n)).length);
}
