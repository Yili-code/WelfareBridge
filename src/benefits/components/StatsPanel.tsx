import { useAsync } from '../hooks/useApi';
import { api } from '../services/api';
import { formatDateTime, formatNumber } from '../utils/format';
import { PROCESSING_STATUS_LABELS } from '../utils/labels';
import { Badge, LlmOnlineBadge } from './Badge';
import { ErrorBox, LoadingBlock, Section } from './Feedback';
import { StatCard } from './StatCard';

const smallBtn = 'rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50';

function CountBadges({ label, items, tone }: { label: string; items: Array<[string, { count: number; label: string }]>; tone: 'blue' | 'slate' | 'indigo' | 'emerald' }) {
  return (
    <div className="flex flex-wrap items-center gap-1">
      <span className="font-medium text-slate-500">{label}：</span>
      {items.length === 0 ? <span>—</span> : null}
      {items.map(([key, item]) => (
        <Badge key={key} tone={tone} title={key}>
          {item.label || key} {formatNumber(item.count)}
        </Badge>
      ))}
    </div>
  );
}

export function StatsPanel({ refreshKey = 0 }: { refreshKey?: number }) {
  const { data, loading, error, reload } = useAsync(() => api.stats(), [refreshKey]);

  const rawStatus = data ? Object.entries(data.raw_documents_by_status).map(([status, count]) => `${PROCESSING_STATUS_LABELS[status] ?? status} ${count}`).join('・') : '';
  const byCount = (record: Record<string, { count: number; label: string }>) => Object.entries(record).sort((a, b) => b[1].count - a[1].count);
  const corpus = data?.keyword_stats?.corpus;

  return (
    <Section
      title="資料總覽"
      description="所有數字皆直接來自後端資料庫（GET /api/stats），沒有任何人工加工。"
      actions={
        <>
          {data ? <LlmOnlineBadge online={data.llm.online} model={data.llm.model} provider={data.llm.provider} /> : null}
          <button type="button" onClick={reload} className={smallBtn}>
            重新整理
          </button>
        </>
      }
    >
      {loading && !data ? (
        <LoadingBlock text="載入統計資料…" />
      ) : error && !data ? (
        <ErrorBox message={error} onRetry={reload} />
      ) : data ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <StatCard
              label="補助方案（去重後）"
              value={formatNumber(data.benefits_programs)}
              sub={`資料完整 ${formatNumber(data.quality_verified)} 筆・待確認 ${formatNumber(data.uncertain ?? 0)}・全部紀錄 ${formatNumber(data.benefits_total)}・開放中 ${formatNumber(data.benefits_active)}・已截止 ${formatNumber(data.benefits_expired)}・彙整頁 ${formatNumber(data.benefits_portals)}（不進清單與媒合）`}
            />
            <StatCard label="今日新增" value={formatNumber(data.today_new)} tone="green" sub={`以 first_seen_at 計算・已抽出規則 ${formatNumber(data.with_rules)} 筆`} />
            <StatCard label="最後更新" value={<span className="text-base">{formatDateTime(data.last_updated)}</span>} sub={`最近一次爬取完成：${formatDateTime(data.last_crawl)}`} tone="slate" />
            <StatCard label="官方來源數" value={`${data.official_sources} / ${data.sources_total}`} sub={`已通過官方網域驗證 / 全部來源・啟用 ${data.sources_enabled}`} />
            <StatCard label="成功爬蟲" value={formatNumber(data.crawlers_success)} tone="green" sub={`尚未執行 ${data.crawlers_never_run}`} />
            <StatCard label="失敗爬蟲" value={formatNumber(data.crawlers_failed)} tone={data.crawlers_failed > 0 ? 'red' : 'slate'} sub="含 failed / skipped" />
            <StatCard label="待人工確認" value={formatNumber(data.needs_review)} tone={data.needs_review > 0 ? 'amber' : 'slate'} sub={`審核佇列待處理 ${formatNumber(data.review_open)} 件`} />
            <StatCard
              label="本地 AI 已補齊"
              value={formatNumber(data.llm_processed)}
              tone="indigo"
              sub={data.llm.provider && data.llm.provider !== 'none' ? `${data.llm.provider}・${data.llm.model || '—'}・${data.llm.online ? '在線' : '離線'}` : '未啟用本地 AI'}
              title={data.llm.detail}
            />
            <StatCard label="原始文件" value={formatNumber(data.raw_documents_total)} tone="slate" sub={rawStatus || '尚無原始文件'} />
            <StatCard label="服務提供者" value={formatNumber(data.providers_total)} tone="slate" sub="長照／社福機構名單（providers）" />
            <StatCard
              label="屬性登錄表"
              value={`v${data.registry.version}`}
              tone="indigo"
              sub={`${data.registry.attributes} 個屬性・${data.registry.domains} 領域・${data.registry.categories} 類別・${data.registry.tags} 個身分標籤`}
            />
            <StatCard
              label="關鍵字統計"
              value={data.keyword_stats.benefit_terms !== null && data.keyword_stats.benefit_terms !== undefined ? `${formatNumber(data.keyword_stats.benefit_terms)} 詞` : '—'}
              tone="slate"
              sub={
                corpus
                  ? `語料 ${formatNumber(corpus.documents ?? null)} 份（正例 ${formatNumber(corpus.positives ?? null)}）・排除詞 ${formatNumber(data.keyword_stats.negative_terms)}・產生於 ${formatDateTime(data.keyword_stats.generated_at)}`
                  : '尚未執行關鍵字統計'
              }
            />
          </div>
          <div className="flex flex-col gap-2 text-xs text-slate-600">
            <CountBadges label="依領域" items={byCount(data.by_domain)} tone="indigo" />
            <CountBadges label="依類別" items={byCount(data.by_category)} tone="blue" />
            <CountBadges label="依給付形式" items={byCount(data.by_benefit_form)} tone="emerald" />
            <CountBadges label="依機關類型" items={byCount(data.by_provider_type)} tone="slate" />
          </div>
        </div>
      ) : null}
    </Section>
  );
}
