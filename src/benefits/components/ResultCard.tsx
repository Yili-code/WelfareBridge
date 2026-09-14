import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api, errorMessage } from '../services/api';
import type { Labels } from '../hooks/useApi';
import type { FeedbackEvent, FieldSpec, MatchItem, RankedItem } from '../types';
import { daysLeft, formatAmount, formatAnnualized, formatPeriod, isExpired, percent, scoreLabel } from '../utils/format';
import { EFFORT_LABELS, FUNNEL_STAGE_LABELS } from '../utils/labels';
import { attributeLabel } from '../utils/profile';
import { Badge, MatchStatusBadge } from './Badge';
import { ConditionList } from './ConditionList';
import { QuestionInput, type QuestionLike } from './QuestionInput';

export type CardItem = MatchItem & Partial<Pick<RankedItem, 'why' | 'cautions' | 'suitability' | 'in_bundle' | 'funnel_stage'>>;

interface Props {
  item: CardItem;
  catalog: Record<string, FieldSpec> | null;
  cities: string[];
  labels: Labels;
  profileId?: string | null;
  onSupplement?: (attributeId: string, value: unknown) => void;
  busy?: boolean;
  /** 只顯示標題、金額、期限與理由（推薦卡用） */
  compact?: boolean;
}

const NOT_INTERESTED_REASONS = [
  { value: 'amount_too_low', label: '金額太少' },
  { value: 'not_eligible', label: '我其實不符合' },
  { value: 'already_applied', label: '已經申請過' },
  { value: 'too_much_effort', label: '準備太麻煩' },
  { value: 'not_needed', label: '不需要' },
  { value: 'other', label: '其他' },
];

function explanationClass(line: string): string {
  if (line.startsWith('✓')) return 'text-emerald-700';
  if (line.startsWith('✗')) return 'text-red-700';
  if (line.startsWith('？')) return 'text-amber-700';
  if (line.startsWith('★')) return 'text-purple-700';
  if (line.startsWith('△')) return 'text-slate-600';
  return 'text-slate-700';
}

function scoreClass(status: MatchItem['status']): string {
  switch (status) {
    case 'high_match':
      return 'border-emerald-200 bg-emerald-50 text-emerald-700';
    case 'possible_match':
      return 'border-amber-200 bg-amber-50 text-amber-700';
    case 'not_match':
      return 'border-red-200 bg-red-50 text-red-700';
    default:
      return 'border-slate-200 bg-slate-50 text-slate-600';
  }
}

export function DeadlineText({ item }: { item: CardItem }) {
  const period = item.benefit?.application_period;
  const days = item.suitability?.days_left ?? daysLeft(period);
  const expired = item.benefit_status === 'expired' || isExpired(period);
  return (
    <span title={period?.description || undefined} className={expired ? 'text-slate-400 line-through' : ''}>
      📅 {formatPeriod(period)}
      {days !== null && days !== undefined && !expired ? <span className={`ml-1 text-xs ${days <= 7 ? 'text-red-600' : 'text-slate-500'}`}>（剩 {days} 天）</span> : null}
    </span>
  );
}

export function ResultCard({ item, catalog, cities, labels, profileId, onSupplement, busy = false, compact = false }: Props) {
  const [openAttribute, setOpenAttribute] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<FeedbackEvent | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [showReason, setShowReason] = useState(false);
  const [reason, setReason] = useState(NOT_INTERESTED_REASONS[0].value);
  const [sending, setSending] = useState(false);

  const meta = item.benefit ?? {};
  const application = meta.application ?? {};
  const missingAttributes = item.missing_attributes.length ? item.missing_attributes : Array.from(new Set(item.missing_conditions.map((condition) => condition.attribute_id)));
  const expired = item.benefit_status === 'expired' || isExpired(meta.application_period);
  const suitability = item.suitability;

  const questionFor = (attributeId: string): QuestionLike => {
    const spec = catalog?.[attributeId];
    if (spec) return { attribute_id: attributeId, question: spec.question || `請提供：${spec.label}`, type: spec.type, options: spec.options, help: spec.help, sensitivity: spec.sensitivity };
    return { attribute_id: attributeId, question: `請提供：${attributeLabel(attributeId, catalog)}`, type: 'text', options: [] };
  };

  const send = async (event: FeedbackEvent, extra: { reason?: string } = {}) => {
    setSending(true);
    setFeedbackError(null);
    try {
      await api.sendFeedback({ benefit_id: item.benefit_id, profile_id: profileId ?? null, event, reason: extra.reason ?? null });
      if (event !== 'clicked_source') setFeedback(event);
      setShowReason(false);
    } catch (err) {
      setFeedbackError(errorMessage(err));
    } finally {
      setSending(false);
    }
  };

  const header = (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0 flex-1">
        <h3 className="text-base font-semibold leading-snug text-slate-900">
          <Link to={`/data-center/${item.benefit_id}`} className="hover:text-indigo-700 hover:underline">
            {item.title}
          </Link>
        </h3>
        <div className="mt-1 flex flex-wrap items-center gap-1.5 text-sm text-slate-600">
          <span>{item.provider || '（原文未載明機關）'}</span>
          <Badge tone="slate">{labels.of('provider_type', item.provider_type)}</Badge>
          {item.domain ? <Badge tone="indigo">{labels.of('domain', item.domain)}</Badge> : null}
          {item.category ? <Badge tone="blue">{item.category_label || labels.of('category', item.category)}</Badge> : null}
          {meta.benefit_form ? <Badge tone="emerald">{labels.of('benefit_form', meta.benefit_form)}</Badge> : null}
          <MatchStatusBadge status={item.status} />
          {item.in_bundle ? <Badge tone="purple">組合建議</Badge> : null}
          {item.needs_review ? <Badge tone="amber">⚠ 資料待人工確認</Badge> : null}
          {item.is_overview ? <Badge tone="amber">彙整頁</Badge> : null}
          {expired ? <Badge tone="gray">已截止</Badge> : null}
          {item.funnel_stage && item.funnel_stage !== 'eligible' ? <Badge tone="gray">{FUNNEL_STAGE_LABELS[item.funnel_stage] ?? item.funnel_stage}</Badge> : null}
        </div>
        <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-700">
          <span title={meta.amount?.description || undefined}>
            💰 {formatAmount(meta.amount)}
            {typeof meta.amount_annualized === 'number' ? <span className="ml-1 text-xs text-slate-500">（年化 {formatAnnualized(meta.amount_annualized)}）</span> : null}
          </span>
          <DeadlineText item={item} />
          {meta.award_basis ? <span>🏷 {labels.of('award_basis', meta.award_basis)}</span> : null}
        </div>
      </div>
      <div className={`flex min-w-[6.5rem] flex-col items-center rounded-lg border px-3 py-2 ${scoreClass(item.status)}`}>
        <span className="text-2xl font-bold leading-none">{percent(item.eligibility_score)}</span>
        <span className="mt-1 text-xs font-medium">{scoreLabel(item.eligibility_score, item.status)}</span>
        {typeof suitability?.total === 'number' ? (
          <span className="mt-1 text-[11px] text-slate-500" title="適合度 = 期望價值 × 時效 × (1 − 準備成本) × 偏好">
            適合度 {suitability.total.toFixed(2)}
          </span>
        ) : null}
      </div>
    </div>
  );

  const whyBlock =
    item.why?.length || item.cautions?.length ? (
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {item.why?.length ? (
          <div className="rounded-lg bg-emerald-50/70 p-3 text-sm">
            <div className="text-xs font-semibold text-emerald-800">推薦理由</div>
            <ul className="mt-1 space-y-0.5 text-emerald-900">
              {item.why.map((line, index) => (
                <li key={index}>・{line}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {item.cautions?.length ? (
          <div className="rounded-lg bg-amber-50/70 p-3 text-sm">
            <div className="text-xs font-semibold text-amber-800">注意</div>
            <ul className="mt-1 space-y-0.5 text-amber-900">
              {item.cautions.map((line, index) => (
                <li key={index}>・{line}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    ) : null;

  if (compact) {
    return (
      <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        {header}
        {whyBlock}
        <div className="mt-3 text-xs text-slate-500">
          <Link to={`/data-center/${item.benefit_id}`} className="hover:text-indigo-700 hover:underline">
            查看原始公告與解析證據 →
          </Link>
        </div>
      </article>
    );
  }

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      {header}
      {whyBlock}

      {item.explanation.length ? (
        <div className="mt-4 rounded-lg bg-slate-50 p-3">
          <div className="text-sm font-semibold text-slate-800">逐條比對結果</div>
          <ul className="mt-1 space-y-0.5 text-sm">
            {item.explanation.map((line, index) => (
              <li key={index} className={explanationClass(line)}>
                {line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="mt-4 space-y-4">
        <ConditionList title="你符合的條件" icon="✅" tone="emerald" items={item.matched_conditions} catalog={catalog} showUserValue />

        {missingAttributes.length ? (
          <div>
            <h4 className="text-sm font-semibold text-amber-800">
              ⚠ 你尚未提供的資訊 <span className="font-normal text-slate-400">({missingAttributes.length})</span>
            </h4>
            <div className="mt-1 flex flex-wrap gap-2">
              {missingAttributes.map((attributeId) => (
                <button
                  key={attributeId}
                  type="button"
                  disabled={busy || !onSupplement}
                  onClick={() => setOpenAttribute((current) => (current === attributeId ? null : attributeId))}
                  className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs transition-colors ${
                    openAttribute === attributeId ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-amber-200 bg-amber-50 text-amber-800 hover:border-indigo-400 hover:bg-indigo-50'
                  } disabled:cursor-default disabled:opacity-70`}
                  title={onSupplement ? '補充這項資料後會自動重新比對' : undefined}
                >
                  {attributeLabel(attributeId, catalog)}
                  {onSupplement ? <span className="text-[10px] text-indigo-600">補充資料</span> : null}
                </button>
              ))}
            </div>
            {openAttribute && onSupplement ? (
              <div className="mt-2 rounded-lg border border-indigo-200 bg-indigo-50/50 p-3">
                <QuestionInput
                  key={openAttribute}
                  question={questionFor(openAttribute)}
                  cities={cities}
                  busy={busy}
                  compact
                  onAnswer={(value) => {
                    onSupplement(openAttribute, value);
                    setOpenAttribute(null);
                  }}
                  onSkip={() => setOpenAttribute(null)}
                />
              </div>
            ) : null}
            {item.missing_conditions.length ? (
              <details className="mt-1 text-xs text-slate-500">
                <summary className="cursor-pointer select-none">查看需要這些資料的條件（{item.missing_conditions.length}）</summary>
                <ul className="mt-1 list-inside list-disc space-y-0.5">
                  {item.missing_conditions.map((condition, index) => (
                    <li key={`${condition.rule_id || condition.attribute_id}-${index}`}>
                      {condition.human_readable || attributeLabel(condition.attribute_id, catalog)}
                      {condition.inferred ? <span className="text-purple-700">（依機關推定）</span> : null}
                    </li>
                  ))}
                </ul>
              </details>
            ) : null}
          </div>
        ) : null}

        <ConditionList title="可能不符合的條件" icon="✗" tone="red" items={item.failed_conditions} catalog={catalog} showUserValue />
        <ConditionList title="需進一步確認" icon="△" tone="slate" items={item.complex_conditions} catalog={catalog} />
        <ConditionList title="優先／加分條件" icon="★" tone="purple" items={item.bonus_conditions} catalog={catalog} showUserValue />
      </div>

      <div className="mt-4 grid gap-2 border-t border-slate-100 pt-3 text-sm sm:grid-cols-2">
        <div className="space-y-1">
          <div>
            <span className="text-xs font-medium text-slate-500">申請方式</span>
            <div className="text-slate-700">
              {labels.of('channel', application.channel ?? 'unknown')}
              {application.effort ? <span className="ml-2 text-xs text-slate-500">準備負擔：{EFFORT_LABELS[application.effort] ?? application.effort}</span> : null}
            </div>
            {application.method ? <div className="text-xs text-slate-600">{application.method}</div> : null}
          </div>
          {application.documents?.length ? (
            <details className="text-xs text-slate-500">
              <summary className="cursor-pointer select-none">應備文件（{application.documents.length}）</summary>
              <ul className="mt-1 list-inside list-disc">
                {application.documents.map((doc, index) => (
                  <li key={index}>{doc}</li>
                ))}
              </ul>
            </details>
          ) : null}
        </div>
        <div className="flex flex-col gap-1 sm:items-end">
          <span className="inline-flex items-center gap-1">
            🔗 官方來源：
            {item.source_url ? (
              <a href={item.source_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline" onClick={() => void send('clicked_source')}>
                {item.source_name || item.source_url}
              </a>
            ) : (
              <span className="text-slate-500">{item.source_name || '—'}</span>
            )}
          </span>
          <Link to={`/data-center/${item.benefit_id}`} className="text-xs text-slate-500 hover:text-indigo-700 hover:underline">
            查看原始公告與解析證據 →
          </Link>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            {feedback === 'applied' ? (
              <Badge tone="green">已記錄：我申請了</Badge>
            ) : feedback === 'not_interested' ? (
              <Badge tone="gray">已記錄：不感興趣</Badge>
            ) : (
              <>
                <button type="button" disabled={sending} onClick={() => void send('applied')} className="rounded-md border border-emerald-300 bg-white px-2.5 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-50">
                  我申請了
                </button>
                <button type="button" disabled={sending} onClick={() => setShowReason((v) => !v)} className="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-600 hover:bg-slate-50 disabled:opacity-50">
                  不感興趣
                </button>
              </>
            )}
          </div>
          {showReason && !feedback ? (
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <select value={reason} onChange={(event) => setReason(event.target.value)} className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs">
                {NOT_INTERESTED_REASONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button type="button" disabled={sending} onClick={() => void send('not_interested', { reason })} className="rounded-md bg-slate-700 px-2.5 py-1 text-xs font-medium text-white hover:bg-slate-600 disabled:opacity-50">
                送出
              </button>
            </div>
          ) : null}
          {feedbackError ? <span className="text-xs text-red-600">{feedbackError}</span> : null}
        </div>
      </div>
    </article>
  );
}
