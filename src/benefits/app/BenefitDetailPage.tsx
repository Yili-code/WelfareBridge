import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Badge, BenefitStatusBadge } from '../components/Badge';
import { ConditionsTab } from '../components/detail/ConditionsTab';
import { EvidenceTab } from '../components/detail/EvidenceTab';
import { LlmTab } from '../components/detail/LlmTab';
import { OriginalTab } from '../components/detail/OriginalTab';
import { RulesTab } from '../components/detail/RulesTab';
import { SchemaTab } from '../components/detail/SchemaTab';
import { SourceTab } from '../components/detail/SourceTab';
import { ErrorBox, LoadingBlock } from '../components/Feedback';
import { Tabs } from '../components/Tabs';
import { useAsync, useMetaOptions } from '../hooks/useApi';
import { api } from '../services/api';
import { formatAmount, formatConfidence, formatDateTime, formatPeriod } from '../utils/format';

export default function BenefitDetailPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { data, loading, error, reload } = useAsync(() => api.getBenefit(id), [id]);
  const { levelLabels, labels, catalog } = useMetaOptions();
  const [tab, setTab] = useState('original');

  if (loading && !data) return <LoadingBlock text="載入補助資料…" />;
  if (error && !data) {
    return (
      <div className="space-y-3">
        <Link to="/data-center" className="text-sm text-blue-600 hover:underline">
          ← 回資料中心
        </Link>
        <ErrorBox title="無法載入這筆資料" message={error} onRetry={reload} />
      </div>
    );
  }
  if (!data) return null;

  const { benefit, schema, rules, evidence, conditions, llm, classification, raw_document: doc, source, related_records: related, providers_nearby: providers } = data;
  const crawlTime = doc?.crawl_time ?? schema?.source?.crawl_time ?? null;

  const tabs = [
    { id: 'original', label: '原始資料' },
    { id: 'schema', label: '標準 Schema' },
    { id: 'rules', label: '資格規則', badge: rules.length },
    { id: 'evidence', label: '解析證據', badge: evidence.length },
    { id: 'conditions', label: '條件句', badge: conditions.length },
    { id: 'llm', label: '本地 AI', badge: benefit.llm_processed ? '已補齊' : '未使用' },
    { id: 'source', label: '來源', badge: related.length ? `+${related.length}` : undefined },
  ];

  return (
    <div className="space-y-5">
      <Link to="/data-center" className="text-sm text-blue-600 hover:underline">
        ← 回資料中心
      </Link>

      <header className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0 flex-1 space-y-2">
            <h1 className="text-xl font-bold leading-snug text-slate-900">{benefit.title}</h1>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="text-slate-700">{benefit.provider || '（原文未載明機關）'}</span>
              <Badge tone="slate">{benefit.provider_type_label}</Badge>
              {benefit.domain_label ? <Badge tone="indigo">{benefit.domain_label}</Badge> : null}
              {benefit.category_label ? <Badge tone="blue">{benefit.category_label}</Badge> : null}
              {benefit.benefit_form_label ? <Badge tone="emerald">{benefit.benefit_form_label}</Badge> : null}
              <BenefitStatusBadge status={benefit.status} needsReview={benefit.needs_review} reviewReasons={benefit.review_reasons} />
              {benefit.is_overview ? <Badge tone="amber">彙整頁</Badge> : null}
              {benefit.is_repost ? <Badge tone="gray">轉知</Badge> : null}
              {!benefit.is_canonical ? <Badge tone="gray">重複來源</Badge> : null}
              {benefit.source_verified ? <Badge tone="green">✅ 官方來源已驗證</Badge> : <Badge tone="amber">⚠ 來源待確認</Badge>}
              {benefit.llm_processed ? <Badge tone="purple">本地 AI 已補齊</Badge> : null}
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
              <span>
                資料來源：{benefit.source_name || benefit.source_id}
                {benefit.official_domain ? `（${benefit.official_domain}）` : ''}
              </span>
              <span>爬取時間：{formatDateTime(crawlTime)}</span>
              <span>最後更新：{formatDateTime(benefit.updated_at)}</span>
              <span>解析信心：{formatConfidence(benefit.confidence)}</span>
              <span>登錄表 v{data.registry_version}</span>
            </div>
            <div className="flex flex-wrap gap-x-6 gap-y-1 pt-1 text-sm text-slate-700">
              <span>💰 {formatAmount(benefit.amount)}</span>
              <span>📅 {formatPeriod(benefit.application_period)}</span>
              <span>🏷 {labels.of('award_basis', benefit.award_basis)}</span>
              <span>
                📜 規則 {benefit.simple_rules} 條可自動判斷／{benefit.complex_rules} 條需語意判斷
              </span>
            </div>
          </div>
          <div className="flex flex-col items-stretch gap-2">
            {benefit.source_url ? (
              <a
                href={benefit.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
              >
                查看官方公告 →
              </a>
            ) : null}
            <span className="mono break-all text-center text-[11px] text-slate-400">{benefit.id}</span>
          </div>
        </div>
      </header>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <Tabs tabs={tabs} active={tab} onChange={setTab} />
        <div className="p-4 sm:p-5">
          {tab === 'original' ? <OriginalTab doc={doc} schema={schema} classification={classification} /> : null}
          {tab === 'schema' ? <SchemaTab schema={schema} benefit={benefit} labels={labels} levelLabels={levelLabels} /> : null}
          {tab === 'rules' ? <RulesTab rules={rules} /> : null}
          {tab === 'evidence' ? <EvidenceTab evidence={evidence} /> : null}
          {tab === 'conditions' ? <ConditionsTab conditions={conditions} catalog={catalog} /> : null}
          {tab === 'llm' ? <LlmTab llm={llm} benefit={benefit} /> : null}
          {tab === 'source' ? <SourceTab source={source} related={related} benefit={benefit} providers={providers} labels={labels} /> : null}
        </div>
      </div>
    </div>
  );
}
