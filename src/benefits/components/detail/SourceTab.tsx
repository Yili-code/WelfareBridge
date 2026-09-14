import { Link } from 'react-router-dom';
import type { BenefitSummary, Provider, RelatedRecord, Source } from '../../types';
import type { Labels } from '../../hooks/useApi';
import { displayValue, formatConfidence, formatDateTime, formatNumber } from '../../utils/format';
import { Badge, CrawlStatusBadge } from '../Badge';
import { DataTable, type Column } from '../DataTable';
import { EmptyState } from '../Feedback';
import { ExternalLink, KeyValueTable, TagList, type KeyValueRow } from '../KeyValueTable';

export function SourceTab({ source, related, benefit, providers, labels }: { source: Source | null; related: RelatedRecord[]; benefit: BenefitSummary; providers: Provider[]; labels: Labels }) {
  const details = source?.verification_details ?? null;
  const rows: KeyValueRow[] = source
    ? [
        { label: '名稱', value: source.name },
        { label: '機關', value: source.organization || '—' },
        { label: '機關類型', value: <Badge tone="slate">{source.provider_type_label}</Badge> },
        { label: '領域', value: source.domains.length ? <TagList items={source.domains.map((domain) => labels.of('domain', domain))} tone="indigo" /> : '—' },
        { label: '來源類型', value: source.source_type || '—' },
        { label: 'base_url', value: <ExternalLink href={source.base_url} /> },
        { label: '官方網域', value: <span className="mono text-xs">{source.official_domain || '—'}</span> },
        {
          label: '官方驗證',
          value: (
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                {source.source_verified ? <Badge tone="green">✅ 已驗證</Badge> : <Badge tone="amber">⚠ 待確認</Badge>}
                {source.source_verification_method ? <span className="text-xs text-slate-600">方法：{source.source_verification_method}</span> : null}
                {source.source_status ? <span className="text-xs text-slate-500">狀態：{source.source_status}</span> : null}
              </div>
              {details?.reasons?.length ? (
                <ul className="list-inside list-disc text-xs text-slate-600">
                  {details.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              ) : null}
              {details?.domain_type ? <div className="text-xs text-slate-500">網域類型：{details.domain_type}</div> : null}
            </div>
          ),
        },
        { label: '資料信心（data_confidence）', value: formatConfidence(source.data_confidence) },
        { label: '爬蟲類別', value: <span className="mono text-xs">{source.crawler_class || '—'}</span> },
        { label: '啟用 / 追蹤連結', value: `${source.enabled ? '啟用' : '停用'}／${source.follow_links ? '會追蹤頁內連結' : '不追蹤連結'}` },
        { label: '請求間隔', value: `${source.request_delay_seconds} 秒` },
        { label: '頁面數 / 略過', value: `${formatNumber(source.pages_total)} / ${formatNumber(source.pages_skipped)}` },
        {
          label: '最近執行',
          value: (
            <span className="inline-flex flex-wrap items-center gap-2">
              <CrawlStatusBadge status={source.last_status || 'never'} />
              <span className="text-xs text-slate-600">{formatDateTime(source.last_run_at)}</span>
              <span className="text-xs text-slate-500">{formatNumber(source.last_record_count)} 筆</span>
              {source.last_error ? <span className="text-xs text-red-700">{source.last_error}</span> : null}
            </span>
          ),
        },
        { label: '備註', value: source.notes || '—' },
      ]
    : [];

  const providerColumns: Column<Provider>[] = [
    { key: 'name', header: '名稱', className: 'min-w-[12rem]', render: (row) => row.name || '—' },
    { key: 'kind', header: '類型', render: (row) => (row.service_kind ? <Badge tone="indigo">{row.service_kind}</Badge> : '—') },
    { key: 'city', header: '縣市', render: (row) => row.city || '—' },
    { key: 'address', header: '地址', className: 'min-w-[12rem]', render: (row) => row.address || '—' },
    { key: 'phone', header: '電話', render: (row) => row.phone || '—' },
    {
      key: 'record',
      header: '原始欄位',
      render: (row) =>
        Object.keys(row.record).length ? (
          <details className="text-xs">
            <summary className="cursor-pointer text-slate-500">查看</summary>
            <ul className="mt-1 space-y-0.5">
              {Object.entries(row.record).map(([key, value]) => (
                <li key={key}>
                  <span className="text-slate-500">{key}：</span>
                  {displayValue(value)}
                </li>
              ))}
            </ul>
          </details>
        ) : (
          '—'
        ),
    },
    { key: 'source', header: '來源', render: (row) => <ExternalLink href={row.source_url} className="text-xs">{row.source_name || '資料集'} →</ExternalLink> },
  ];

  return (
    <div className="space-y-5">
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">來源資訊</h3>
        {source ? <KeyValueTable rows={rows} /> : <EmptyState text="找不到來源資訊。" />}
      </div>
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">
          本筆公告 <span className="mono text-xs text-slate-500">canonical_id: {benefit.canonical_id}</span>
        </h3>
        <KeyValueTable
          rows={[
            { label: '官方公告網址', value: <ExternalLink href={benefit.source_url} /> },
            { label: '來源名稱', value: `${benefit.source_name || '—'}（${benefit.official_domain || '—'}）` },
            { label: '是否為主要紀錄', value: benefit.is_canonical ? <Badge tone="green">是（canonical）</Badge> : <Badge tone="gray">否（重複來源）</Badge> },
            { label: '是否為轉知', value: benefit.is_repost ? '是' : '否' },
            { label: '抽取版本 / 登錄表版本', value: `${benefit.extraction_version || '—'}／v${benefit.registry_version ?? '—'}` },
            { label: '首次收錄 / 最後更新', value: `${formatDateTime(benefit.first_seen_at)}／${formatDateTime(benefit.updated_at)}` },
          ]}
        />
      </div>
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">相同公告的其他來源（related_records，{related.length}）</h3>
        {related.length ? (
          <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white text-sm">
            {related.map((record) => (
              <li key={record.id} className="flex flex-wrap items-center justify-between gap-2 px-3 py-2">
                <div className="flex flex-wrap items-center gap-2">
                  <Link to={`/data-center/${record.id}`} className="font-medium text-blue-600 hover:underline">
                    {record.source_name || record.source_id}
                  </Link>
                  <span className="text-xs text-slate-500">{record.provider}</span>
                  <span className="text-xs text-slate-400">{record.title}</span>
                  {record.is_canonical ? <Badge tone="green">canonical</Badge> : null}
                </div>
                <ExternalLink href={record.source_url} className="text-xs">
                  官方連結 →
                </ExternalLink>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState text="沒有其他來源轉載同一公告。" />
        )}
      </div>
      {providers.length ? (
        <div>
          <h3 className="mb-2 text-sm font-semibold text-slate-800">附近的服務提供者（providers_nearby，{providers.length}）</h3>
          <p className="mb-2 text-xs text-slate-500">長照／社福／身心障礙類補助會附上同縣市的服務單位名單（來自政府開放資料集），僅供查詢，不代表該單位承辦此補助。</p>
          <DataTable columns={providerColumns} rows={providers} rowKey={(row) => row.id} dense />
        </div>
      ) : null}
    </div>
  );
}
