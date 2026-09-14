import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAsync } from '../hooks/useApi';
import { api } from '../services/api';
import type { RawDocument, SourceListItem } from '../types';
import { formatDateTime, truncate } from '../utils/format';
import { CATEGORY_LABELS, PROCESSING_STATUS_LABELS } from '../utils/labels';
import { Badge, ProcessingStatusBadge } from './Badge';
import { DataTable, type Column } from './DataTable';
import { ErrorBox, LoadingBlock } from './Feedback';
import { Pagination } from './Pagination';

const PAGE_SIZE = 50;
const STATUS_ORDER = ['extracted', 'needs_review', 'filtered_out', 'provider_data', 'skipped', 'new', 'error'];

const selectCls = 'rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200';
const labelCls = 'flex flex-col gap-1 text-xs font-medium text-slate-600';

function ClassificationCell({ doc }: { doc: RawDocument }) {
  const c = doc.classification;
  return (
    <div className="space-y-0.5 text-xs">
      {doc.skip_reason ? <div className="text-slate-700">略過原因：{doc.skip_reason}</div> : null}
      {doc.processing_error ? <div className="text-red-700">{doc.processing_error}</div> : null}
      {c ? (
        <>
          <div className="flex flex-wrap items-center gap-1">
            {typeof c.is_benefit === 'boolean' ? <Badge tone={c.is_benefit ? 'green' : 'slate'}>{c.is_benefit ? '判定為補助' : '判定非補助'}</Badge> : null}
            {c.category ? <Badge tone="blue">{CATEGORY_LABELS[c.category] ?? c.category}</Badge> : null}
            {typeof c.signal_score === 'number' ? (
              <span className="text-slate-500">
                訊號 {c.signal_score}
                {typeof c.threshold === 'number' ? ` / 門檻 ${c.threshold}` : ''}
              </span>
            ) : null}
            {c.method ? <span className="mono text-slate-400">{c.method}</span> : null}
          </div>
          {c.reason ? <div className="text-slate-600">{c.reason}</div> : null}
          {c.reasons?.length ? <div className="text-slate-600">{c.reasons.join('；')}</div> : null}
        </>
      ) : !doc.skip_reason && !doc.processing_error ? (
        <span className="text-slate-400">尚未分類</span>
      ) : null}
    </div>
  );
}

export function RawDocumentsPanel({ refreshKey = 0, sources }: { refreshKey?: number; sources: SourceListItem[] | null }) {
  const [status, setStatus] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [keyword, setKeyword] = useState('');
  const [applied, setApplied] = useState('');
  const [page, setPage] = useState(1);

  const list = useAsync(() => api.listRawDocuments({ processing_status: status || undefined, source_id: sourceId || undefined, keyword: applied || undefined, page, page_size: PAGE_SIZE }), [status, sourceId, applied, page, refreshKey]);

  const columns: Column<RawDocument>[] = [
    {
      key: 'title',
      header: '文件',
      className: 'min-w-[16rem]',
      render: (doc) => (
        <div>
          <div className="font-medium text-slate-900">{doc.title || <span className="text-slate-400">（無標題）</span>}</div>
          <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-[11px] text-slate-500">
            <span>{doc.source_name || doc.source_id}</span>
            {doc.source_url ? (
              <a href={doc.source_url} target="_blank" rel="noopener noreferrer" className="break-all text-blue-600 hover:underline" title={doc.source_url}>
                🔗 {truncate(doc.source_url, 60)}
              </a>
            ) : null}
          </div>
        </div>
      ),
    },
    { key: 'type', header: '格式', render: (doc) => <span className="mono text-xs">{doc.content_type || '—'}</span> },
    { key: 'crawl', header: '爬取時間', className: 'whitespace-nowrap', render: (doc) => formatDateTime(doc.crawl_time) },
    { key: 'status', header: '處理狀態', render: (doc) => <ProcessingStatusBadge status={doc.processing_status} /> },
    { key: 'classification', header: '分類結果 / 原因', className: 'min-w-[16rem]', render: (doc) => <ClassificationCell doc={doc} /> },
    {
      key: 'benefit',
      header: '補助',
      render: (doc) =>
        doc.benefit_id ? (
          <Link to={`/data-center/${doc.benefit_id}`} className="text-blue-600 hover:underline">
            查看 →
          </Link>
        ) : (
          <span className="text-slate-400">—</span>
        ),
    },
    { key: 'attachments', header: '附件', className: 'text-right tabular-nums', render: (doc) => doc.attachments.length || '—' },
  ];

  return (
    <div className="space-y-3">
      <p className="text-xs text-slate-500">每一份爬到的頁面都在這裡（GET /api/raw-documents），含來源網址、爬取時間與分類原因；沒有被抽成補助的文件會顯示為什麼。</p>
      <form
        className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3"
        onSubmit={(event) => {
          event.preventDefault();
          setApplied(keyword.trim());
          setPage(1);
        }}
      >
        <label className={`${labelCls} min-w-[12rem] flex-1`}>
          關鍵字（標題或網址）
          <input type="search" value={keyword} onChange={(event) => setKeyword(event.target.value)} className={selectCls} />
        </label>
        <label className={labelCls}>
          處理狀態
          <select
            className={selectCls}
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
          >
            <option value="">全部</option>
            {STATUS_ORDER.map((value) => (
              <option key={value} value={value}>
                {PROCESSING_STATUS_LABELS[value] ?? value}
              </option>
            ))}
          </select>
        </label>
        <label className={labelCls}>
          來源
          <select
            className={selectCls}
            value={sourceId}
            onChange={(event) => {
              setSourceId(event.target.value);
              setPage(1);
            }}
          >
            <option value="">全部</option>
            {(sources ?? []).map((source) => (
              <option key={source.id} value={source.id}>
                {source.name}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-blue-500">
          搜尋
        </button>
      </form>
      {list.loading && !list.data ? (
        <LoadingBlock text="載入原始文件…" />
      ) : list.error ? (
        <ErrorBox message={list.error} onRetry={list.reload} />
      ) : list.data ? (
        <>
          <div className={list.loading ? 'opacity-60 transition-opacity' : ''}>
            <DataTable columns={columns} rows={list.data.items} rowKey={(doc) => doc.id} dense emptyText="沒有符合條件的原始文件" />
          </div>
          <Pagination page={list.data.page} pageSize={list.data.page_size} total={list.data.total} onChange={setPage} />
        </>
      ) : null}
    </div>
  );
}
