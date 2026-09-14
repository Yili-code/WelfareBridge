import { useState } from 'react';
import type { BenefitSchema, Classification, RawDocument } from '../../types';
import { displayValue, formatDateTime } from '../../utils/format';
import { CATEGORY_LABELS, DOMAIN_LABELS } from '../../utils/labels';
import { Badge, ProcessingStatusBadge } from '../Badge';
import { EmptyState } from '../Feedback';
import { JsonViewer } from '../JsonViewer';
import { ExternalLink, KeyValueTable, TagList, type KeyValueRow } from '../KeyValueTable';

/** 關鍵字分類結果（services/classifier.py ClassificationResult；config／rule 型只有 reason） */
export function ClassificationView({ classification }: { classification: Classification | null | undefined }) {
  if (!classification || Object.keys(classification).length === 0) return <span className="text-slate-400">—</span>;
  const c = classification;
  const scores = Object.entries(c.category_scores ?? {});
  const matched = c.matched_category ?? {};
  return (
    <div className="space-y-1 text-xs">
      <div className="flex flex-wrap gap-1">
        {typeof c.is_benefit === 'boolean' ? <Badge tone={c.is_benefit ? 'green' : 'red'}>{c.is_benefit ? '判定為補助' : '判定非補助'}</Badge> : null}
        {typeof c.signal_score === 'number' ? (
          <Badge tone="slate">
            訊號分數 {c.signal_score}
            {typeof c.threshold === 'number' ? ` / 門檻 ${c.threshold}` : ''}
          </Badge>
        ) : null}
        {c.domain ? <Badge tone="indigo">領域：{DOMAIN_LABELS[c.domain] ?? c.domain}</Badge> : null}
        {c.category ? <Badge tone="blue">類別：{CATEGORY_LABELS[c.category] ?? c.category}</Badge> : null}
        {typeof c.confidence === 'number' ? <Badge tone="slate">分類信心 {Math.round(c.confidence * 100)}%</Badge> : null}
        {c.method ? <Badge tone="gray">方法：{c.method}</Badge> : null}
        {c.rules_source ? <Badge tone="gray">關鍵字來源：{c.rules_source === 'mined' ? '語料統計' : c.rules_source}</Badge> : null}
      </div>
      {c.reason ? <div className="text-slate-700">{c.reason}</div> : null}
      {c.reasons?.length ? (
        <ul className="list-inside list-disc text-slate-600">
          {c.reasons.map((reason, index) => (
            <li key={index}>{reason}</li>
          ))}
        </ul>
      ) : null}
      {c.matched_signal?.length ? (
        <div className="flex flex-wrap items-center gap-1">
          <span className="text-slate-500">命中訊號詞：</span>
          <TagList items={c.matched_signal} tone="emerald" />
        </div>
      ) : null}
      {c.matched_negative?.length ? (
        <div className="flex flex-wrap items-center gap-1">
          <span className="text-slate-500">命中排除詞：</span>
          <TagList items={c.matched_negative} />
        </div>
      ) : null}
      {scores.length ? (
        <div className="flex flex-wrap items-center gap-1">
          <span className="text-slate-500">類別分數：</span>
          {scores.map(([category, score]) => (
            <span key={category} className="rounded bg-blue-50 px-1.5 py-0.5 text-blue-700">
              {CATEGORY_LABELS[category] ?? category} {score}
              {matched[category]?.length ? <span className="text-blue-500">（{matched[category].join('、')}）</span> : null}
            </span>
          ))}
        </div>
      ) : null}
      {c.regions?.length ? <div className="text-slate-500">文中縣市：{c.regions.join('、')}</div> : null}
      {c.llm ? (
        <details>
          <summary className="cursor-pointer text-purple-700">本地 AI 二次判斷</summary>
          <JsonViewer value={c.llm} defaultDepth={1} className="mt-1" />
        </details>
      ) : null}
    </div>
  );
}

export function OriginalTab({ doc, schema, classification }: { doc: RawDocument | null; schema: BenefitSchema | null; classification: Classification | null }) {
  const [expanded, setExpanded] = useState(false);
  if (!doc) return <EmptyState text="此筆資料沒有對應的原始文件（raw_document 為空）。" />;

  const structured = Object.keys(doc.structured ?? {}).length ? doc.structured : (schema?.structured_fields ?? {});
  const structuredRows: KeyValueRow[] = Object.entries(structured).map(([key, value]) => ({ label: key, value: <span className="whitespace-pre-wrap">{displayValue(value)}</span> }));
  const effectiveClassification = doc.classification ?? classification;

  const metaRows: KeyValueRow[] = [
    { label: 'source_url（官方網址）', value: <ExternalLink href={doc.source_url} /> },
    { label: '文件標題', value: doc.title || '—' },
    { label: 'content_type', value: doc.content_type || '—' },
    { label: 'crawl_time（爬取時間）', value: formatDateTime(doc.crawl_time) },
    { label: 'first_seen_at', value: formatDateTime(doc.first_seen_at) },
    { label: 'last_seen_at', value: formatDateTime(doc.last_seen_at) },
    { label: 'last_crawled_at', value: formatDateTime(doc.last_crawled_at) },
    { label: 'content_hash', value: <span className="mono break-all text-xs">{doc.content_hash || '—'}</span> },
    { label: 'published_date', value: doc.published_date || '—' },
    {
      label: 'processing_status',
      value: (
        <span className="inline-flex flex-wrap items-center gap-2">
          <ProcessingStatusBadge status={doc.processing_status} />
          {doc.processed_at ? <span className="text-xs text-slate-500">{formatDateTime(doc.processed_at)}</span> : null}
          {doc.processing_error ? <span className="text-xs text-red-700">{doc.processing_error}</span> : null}
        </span>
      ),
    },
    { label: 'skip_reason', value: doc.skip_reason || '—' },
    { label: 'classification（分類）', value: <ClassificationView classification={effectiveClassification} /> },
    { label: 'file_path', value: doc.file_path ? <span className="mono break-all text-xs">{doc.file_path}</span> : '—' },
    { label: 'raw_document id', value: <span className="mono text-xs">{doc.id}</span> },
  ];

  const text = doc.raw_text || '';
  const long = text.length > 3000;

  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-slate-800">原文（raw_text，{text.length.toLocaleString('zh-TW')} 字）</h3>
          {long ? (
            <button type="button" className="text-xs text-blue-600 hover:underline" onClick={() => setExpanded((v) => !v)}>
              {expanded ? '收合' : '展開全文'}
            </button>
          ) : null}
        </div>
        <pre className={`whitespace-pre-wrap break-words rounded-lg border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed text-slate-800 ${expanded ? '' : 'max-h-96 overflow-auto'}`}>
          {text || '（原始文件沒有文字內容）'}
        </pre>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">結構化欄位（來源頁面本身的標籤欄位）</h3>
        {structuredRows.length ? <KeyValueTable rows={structuredRows} /> : <EmptyState text="此來源頁面沒有標籤化欄位。" />}
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">附件（{doc.attachments.length}）</h3>
        {doc.attachments.length ? (
          <ul className="space-y-1 text-sm">
            {doc.attachments.map((attachment, index) => (
              <li key={`${attachment.url}-${index}`} className="flex flex-wrap items-center gap-2">
                {attachment.type ? <Badge tone="slate">{attachment.type.toUpperCase()}</Badge> : null}
                <ExternalLink href={attachment.url}>{attachment.name || attachment.url}</ExternalLink>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState text="沒有附件。" />
        )}
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">中繼資料</h3>
        <KeyValueTable rows={metaRows} />
      </div>

      {doc.meta && Object.keys(doc.meta).length ? (
        <div>
          <h3 className="mb-2 text-sm font-semibold text-slate-800">爬蟲附加資訊（meta）</h3>
          <JsonViewer value={doc.meta} defaultDepth={1} />
        </div>
      ) : null}
    </div>
  );
}
