import type { ReactNode } from 'react';
import { BENEFIT_STATUS_LABELS, CRAWL_STATUS_LABELS, MATCH_STATUS_META, PROCESSING_STATUS_LABELS, ROLE_LABELS, extractorLabel } from '../utils/labels';

export type Tone = 'gray' | 'slate' | 'blue' | 'green' | 'emerald' | 'amber' | 'red' | 'indigo' | 'purple';

const TONES: Record<Tone, string> = {
  gray: 'bg-gray-100 text-gray-700 ring-gray-200',
  slate: 'bg-slate-100 text-slate-700 ring-slate-200',
  blue: 'bg-blue-50 text-blue-700 ring-blue-200',
  green: 'bg-green-50 text-green-700 ring-green-200',
  emerald: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  amber: 'bg-amber-50 text-amber-800 ring-amber-200',
  red: 'bg-red-50 text-red-700 ring-red-200',
  indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-200',
  purple: 'bg-purple-50 text-purple-700 ring-purple-200',
};

export function Badge({ tone = 'gray', children, title, className = '' }: { tone?: Tone; children: ReactNode; title?: string; className?: string }) {
  return (
    <span title={title} className={`inline-flex items-center gap-1 whitespace-nowrap rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${TONES[tone]} ${className}`}>
      {children}
    </span>
  );
}

/** 補助狀態：active / expired / needs_review / superseded */
export function BenefitStatusBadge({ status, needsReview, reviewReasons }: { status: string; needsReview?: boolean; reviewReasons?: string[] }) {
  if (status === 'expired') return <Badge tone="gray">已截止</Badge>;
  if (status === 'superseded') return <Badge tone="gray">{BENEFIT_STATUS_LABELS.superseded}</Badge>;
  if (needsReview || status === 'needs_review') {
    return (
      <Badge tone="amber" title={reviewReasons?.length ? reviewReasons.join('\n') : '待人工確認'}>
        ⚠ 待人工確認
      </Badge>
    );
  }
  return <Badge tone="green">{BENEFIT_STATUS_LABELS[status] ?? status}</Badge>;
}

/** 爬蟲最近一次執行狀態 */
export function CrawlStatusBadge({ status }: { status: string }) {
  const label = CRAWL_STATUS_LABELS[status] ?? status;
  switch (status) {
    case 'success':
      return <Badge tone="green">✅ {label}</Badge>;
    case 'partial':
      return <Badge tone="amber">⚠ {label}</Badge>;
    case 'failed':
      return <Badge tone="red">❌ {label}</Badge>;
    case 'skipped':
      return <Badge tone="gray">⏭ {label}</Badge>;
    case 'never':
      return <Badge tone="slate">⏳ {label}</Badge>;
    default:
      return <Badge tone="slate">{label}</Badge>;
  }
}

export function MatchStatusBadge({ status }: { status: string }) {
  const meta = MATCH_STATUS_META[status] ?? { label: status, emoji: '' };
  const tone: Tone = status === 'high_match' ? 'emerald' : status === 'possible_match' ? 'amber' : status === 'not_match' ? 'red' : 'slate';
  return (
    <Badge tone={tone}>
      {meta.emoji} {meta.label}
    </Badge>
  );
}

/** 原始文件 processing_status */
export function ProcessingStatusBadge({ status }: { status: string }) {
  const label = PROCESSING_STATUS_LABELS[status] ?? (status || '—');
  const tone: Tone = status === 'extracted' ? 'green' : status === 'error' ? 'red' : status === 'needs_review' ? 'amber' : status === 'filtered_out' ? 'slate' : status === 'provider_data' ? 'indigo' : 'gray';
  return <Badge tone={tone}>{label}</Badge>;
}

/** 規則角色 required / exclusion / bonus */
export function RoleBadge({ role }: { role: string }) {
  const tone: Tone = role === 'bonus' ? 'purple' : role === 'exclusion' ? 'red' : role === 'procedural' ? 'gray' : 'blue';
  return <Badge tone={tone}>{ROLE_LABELS[role] ?? role}</Badge>;
}

export function ExtractorBadge({ extractor }: { extractor: string | undefined | null }) {
  const tone: Tone = extractor === 'llm' || extractor === 'llm_supplement' ? 'purple' : extractor === 'structured_field' ? 'blue' : extractor === 'pattern' ? 'indigo' : 'slate';
  return <Badge tone={tone}>{extractorLabel(extractor)}</Badge>;
}

/** Schema 審核狀態（列表用） */
export function ReviewBadge({ needsReview, reviewReasons }: { needsReview: boolean; reviewReasons: string[] }) {
  if (!needsReview) return <Badge tone="green">✅ 通過檢核</Badge>;
  return (
    <Badge tone="amber" title={reviewReasons.length ? reviewReasons.join('\n') : '需人工確認'}>
      ⚠ 待人工確認
    </Badge>
  );
}

export function VerifiedBadge({ verified, method }: { verified: boolean; method?: string | null }) {
  if (verified) {
    return (
      <span className="inline-flex flex-col leading-tight">
        <Badge tone="green">✅ 已驗證</Badge>
        {method ? <span className="mt-0.5 text-[11px] text-slate-500">{method}</span> : null}
      </span>
    );
  }
  return <Badge tone="amber">⚠ 待確認</Badge>;
}

/** 本地 AI（Ollama）是否在線 */
export function LlmOnlineBadge({ online, model, provider }: { online: boolean; model?: string; provider?: string }) {
  if (!provider || provider === 'none') return <Badge tone="slate">未啟用本地 AI</Badge>;
  return (
    <Badge tone={online ? 'purple' : 'red'} title={provider}>
      {online ? '🟣 本地 AI 在線' : '⚠ 本地 AI 離線'}
      {model ? <span className="mono font-normal">{model}</span> : null}
    </Badge>
  );
}
