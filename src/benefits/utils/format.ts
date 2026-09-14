import type { Amount, ApplicationPeriod, MatchStatus } from '../types';
import { PERIOD_LABELS, UNIT_LABELS } from './labels';

const numberFormatter = new Intl.NumberFormat('zh-TW');

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return numberFormatter.format(value);
}

function unitLabel(unit?: string): string {
  if (!unit || unit.toUpperCase() === 'TWD' || unit === '元' || unit === 'NTD') return '元';
  return unit;
}

function hasNumber(value: unknown): value is number {
  return typeof value === 'number' && !Number.isNaN(value);
}

/** 金額：fixed → 20,000 元；range/tiered → 1,500～5,000 元；unknown → —；有 period 時附註（每學期）。 */
export function formatAmount(amount: Amount | null | undefined, { withPeriod = true }: { withPeriod?: boolean } = {}): string {
  if (!amount) return '—';
  const unit = unitLabel(amount.unit);
  let text = '';
  const hasValue = hasNumber(amount.value);
  const hasMin = hasNumber(amount.min);
  const hasMax = hasNumber(amount.max);
  if (amount.type === 'fixed' && hasValue) {
    text = `${formatNumber(amount.value)} ${unit}`;
  } else if (hasMin && hasMax) {
    text = amount.min === amount.max ? `${formatNumber(amount.min)} ${unit}` : `${formatNumber(amount.min)}～${formatNumber(amount.max)} ${unit}`;
  } else if (hasMax) {
    text = `最高 ${formatNumber(amount.max)} ${unit}`;
  } else if (hasMin) {
    text = `${formatNumber(amount.min)} ${unit}起`;
  } else if (hasValue) {
    text = `${formatNumber(amount.value)} ${unit}`;
  } else {
    return '—';
  }
  if (withPeriod && amount.period && amount.period !== 'unknown') {
    const label = PERIOD_LABELS[amount.period] ?? amount.period;
    if (label) text += `（${label}）`;
  }
  return text;
}

/** 年化金額（後端 amount_annualized；只在 period 可推算時才有值） */
export function formatAnnualized(value: number | null | undefined): string {
  if (!hasNumber(value)) return '原文未載明';
  return `${formatNumber(value)} 元／年`;
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString('zh-TW', { hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  return value;
}

function todayIso(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

export function isExpired(period: ApplicationPeriod | null | undefined): boolean {
  const end = period?.end_date;
  if (!end || !/^\d{4}-\d{2}-\d{2}/.test(end)) return false;
  if (period?.rolling) return false;
  return end.slice(0, 10) < todayIso();
}

/** 距截止日天數（負數＝已過；沒有 end_date → null） */
export function daysLeft(period: ApplicationPeriod | null | undefined): number | null {
  const end = period?.end_date;
  if (!end || !/^\d{4}-\d{2}-\d{2}/.test(end)) return null;
  const endDate = new Date(`${end.slice(0, 10)}T00:00:00`);
  const today = new Date(`${todayIso()}T00:00:00`);
  if (Number.isNaN(endDate.getTime())) return null;
  return Math.round((endDate.getTime() - today.getTime()) / 86400000);
}

/** 申請期間：日期區間；rolling → 隨到隨辦；by_school_deadline → 依各校公告 */
export function formatPeriod(period: ApplicationPeriod | null | undefined): string {
  if (!period) return '原文未載明';
  const { start_date: start, end_date: end, description, rolling, by_school_deadline: bySchool } = period;
  const parts: string[] = [];
  if (start && end) parts.push(`${start} ～ ${end}`);
  else if (end) parts.push(`至 ${end}`);
  else if (start) parts.push(`${start} 起`);
  if (rolling) parts.push('隨到隨辦');
  if (bySchool) parts.push('依各校公告截止日');
  if (parts.length) return parts.join('・');
  return description || '原文未載明';
}

/** 列表用的截止日短字串 */
export function formatDeadline(period: ApplicationPeriod | null | undefined): string {
  if (!period) return '—';
  if (period.end_date) return period.end_date;
  if (period.rolling) return '隨到隨辦';
  if (period.by_school_deadline) return '依各校公告';
  return '—';
}

export function percent(score: number | null | undefined): string {
  if (!hasNumber(score)) return '—';
  return `${Math.round(score * 100)}%`;
}

export function scoreLabel(score: number, status: MatchStatus): string {
  // 文字以後端判定的狀態為準（分數只是輔助），避免「可能符合」的卡片出現「高度符合」字樣
  if (status === 'not_match') return '目前不符合';
  if (status === 'insufficient_data') return '資料不足';
  if (status === 'high_match') return '高度符合';
  return score >= 0.5 ? '可能符合' : '符合度較低';
}

export function formatConfidence(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  if (value > 1) return `${Math.round(value)}%`;
  return `${Math.round(value * 100)}%`;
}

/** 單位標籤；年齡類屬性的 years 顯示為「歲」，其餘為「年」。 */
export function formatUnit(unit: string | null | undefined, attributeId?: string): string {
  if (!unit) return '';
  if (unit === 'years' && attributeId && /\.age$|_age$/.test(attributeId)) return '歲';
  return UNIT_LABELS[unit] ?? unit;
}

/** 規則值顯示：陣列以「、」串接、布林轉是/否、其餘轉字串。 */
export function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (Array.isArray(value)) return value.length ? value.map((v) => displayValue(v)).join('、') : '—';
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (typeof value === 'number') return formatNumber(value);
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export function truncate(text: string | null | undefined, max = 80): string {
  if (!text) return '';
  return text.length > max ? `${text.slice(0, max)}…` : text;
}
