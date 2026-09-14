import { useEffect, useRef, useState } from 'react';
import { useAsync, useInterval, useMetaOptions } from '../hooks/useApi';
import { api, errorMessage } from '../services/api';
import type { CrawlerSource, TaskRecord } from '../types';
import { formatDateTime, formatNumber, truncate } from '../utils/format';
import { PROCESSING_STATUS_LABELS, TASK_KIND_LABELS, TASK_STATUS_LABELS } from '../utils/labels';
import { Badge, CrawlStatusBadge, LlmOnlineBadge, VerifiedBadge } from './Badge';
import { DataTable, type Column } from './DataTable';
import { ErrorBox, LoadingBlock, Notice, Section, Spinner } from './Feedback';

const smallBtn = 'rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50';
const primaryBtn = 'inline-flex items-center gap-2 rounded-md bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50';
const indigoBtn = 'inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50';

type Action = 'crawl' | 'pipeline' | 'llm_fill' | 'mine_keywords';

export function CrawlerPanel({ onFinished }: { onFinished?: () => void }) {
  const { data, loading, error, reload } = useAsync(() => api.crawlerStatus(), []);
  const pipeline = useAsync(() => api.pipelineStatus(), []);
  const { labels } = useMetaOptions();
  const [pending, setPending] = useState<Action | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [showTasks, setShowTasks] = useState(false);
  const wasRunning = useRef(false);
  const onFinishedRef = useRef(onFinished);
  useEffect(() => { onFinishedRef.current = onFinished; }, [onFinished]);

  const running = (data?.running ?? false) || (pipeline.data?.running ?? false);
  const runningKinds = Array.from(new Set([...(data?.running_kinds ?? []), ...(pipeline.data?.running_kinds ?? [])]));
  useInterval(() => {
    reload();
    pipeline.reload();
  }, running || pending ? 3000 : null);

  useEffect(() => {
    if (!data) return;
    if (wasRunning.current && !running) {
      setMessage('背景工作已完成，統計與資料列表已重新整理。');
      onFinishedRef.current?.();
    }
    wasRunning.current = running;
  }, [data, running]);

  const trigger = async (action: Action, sourceIds?: string[]) => {
    setPending(action);
    setActionError(null);
    setMessage(null);
    try {
      const response =
        action === 'crawl'
          ? await api.runCrawler({ source_ids: sourceIds ?? null, run_pipeline: true })
          : action === 'pipeline'
            ? await api.runPipeline({ source_ids: sourceIds ?? null, force: true })
            : action === 'llm_fill'
              ? await api.runLlmFill()
              : await api.mineKeywords();
      setMessage(response.message);
      wasRunning.current = true;
      reload();
      pipeline.reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setPending(null);
    }
  };

  const busy = running || pending !== null;
  const llmOnline = pipeline.data?.llm.online ?? false;

  const columns: Column<CrawlerSource>[] = [
    {
      key: 'name',
      header: '名稱',
      className: 'min-w-[12rem]',
      render: (row) => (
        <div>
          <div className="font-medium text-slate-900">{row.name}</div>
          <div className="mono text-[11px] text-slate-400">{row.id}</div>
        </div>
      ),
    },
    { key: 'organization', header: '機關', render: (row) => row.organization || '—' },
    { key: 'type', header: '類型', render: (row) => <Badge tone="slate">{row.provider_type_label}</Badge> },
    {
      key: 'domains',
      header: '領域',
      render: (row) =>
        row.domains.length ? (
          <span className="flex flex-wrap gap-1">
            {row.domains.map((domain) => (
              <Badge key={domain} tone="indigo">
                {labels.of('domain', domain)}
              </Badge>
            ))}
          </span>
        ) : (
          <span className="text-slate-400">—</span>
        ),
    },
    { key: 'verified', header: '官方驗證', render: (row) => <VerifiedBadge verified={row.source_verified} method={row.source_verification_method} /> },
    { key: 'last_run', header: '最近執行', className: 'whitespace-nowrap', render: (row) => formatDateTime(row.last_run_at) },
    {
      key: 'status',
      header: '狀態',
      render: (row) => (
        <div>
          <span title={row.last_error || undefined}>
            <CrawlStatusBadge status={row.last_status || 'never'} />
          </span>
          {row.last_error ? (
            <details className="mt-1 max-w-xs">
              <summary className="cursor-pointer text-[11px] text-red-600">查看錯誤</summary>
              <pre className="mt-1 max-h-32 overflow-auto whitespace-pre-wrap rounded bg-red-50 p-2 text-[11px] text-red-800">{row.last_error}</pre>
            </details>
          ) : null}
        </div>
      ),
    },
    {
      key: 'pages',
      header: '頁面 / 略過',
      className: 'whitespace-nowrap text-right tabular-nums',
      render: (row) => (
        <span title="pages_total / pages_skipped">
          {formatNumber(row.pages_total)} / {formatNumber(row.pages_skipped)}
        </span>
      ),
    },
    { key: 'count', header: '抓取筆數', className: 'text-right tabular-nums', render: (row) => formatNumber(row.last_record_count) },
    { key: 'docs', header: '原始文件', className: 'text-right tabular-nums', render: (row) => formatNumber(row.raw_documents) },
    { key: 'benefits', header: '補助', className: 'text-right tabular-nums', render: (row) => formatNumber(row.benefits) },
    { key: 'enabled', header: '啟用', render: (row) => (row.enabled ? <span className="text-green-600">✅</span> : <span className="text-slate-400">—</span>) },
    {
      key: 'actions',
      header: '操作',
      render: (row) => (
        <button type="button" className={smallBtn} disabled={busy || !row.enabled} onClick={() => void trigger('crawl', [row.id])} title={row.enabled ? `只執行 ${row.name}` : '此來源已停用'}>
          執行
        </button>
      ),
    },
  ];

  const taskColumns: Column<TaskRecord>[] = [
    { key: 'kind', header: '工作', render: (task) => <Badge tone="blue">{TASK_KIND_LABELS[task.kind] ?? task.kind}</Badge> },
    {
      key: 'status',
      header: '狀態',
      render: (task) => <Badge tone={task.status === 'failed' ? 'red' : task.status === 'finished' ? 'green' : 'amber'}>{TASK_STATUS_LABELS[task.status] ?? task.status}</Badge>,
    },
    { key: 'backend', header: '執行方式', render: (task) => <span className="mono text-xs">{task.backend}</span> },
    { key: 'queued', header: '送出', className: 'whitespace-nowrap', render: (task) => formatDateTime(task.queued_at) },
    { key: 'finished', header: '完成', className: 'whitespace-nowrap', render: (task) => formatDateTime(task.finished_at ?? null) },
    {
      key: 'result',
      header: '結果 / 錯誤',
      render: (task) =>
        task.error ? (
          <span className="text-red-700" title={task.error}>
            {truncate(task.error, 120)}
          </span>
        ) : task.result ? (
          <details className="text-xs">
            <summary className="cursor-pointer text-slate-500">查看結果</summary>
            <pre className="mt-1 max-h-40 max-w-md overflow-auto whitespace-pre-wrap rounded bg-slate-50 p-2 text-[11px]">{JSON.stringify(task.result, null, 1)}</pre>
          </details>
        ) : (
          '—'
        ),
    },
  ];

  const tasks = data?.tasks?.length ? data.tasks : (pipeline.data?.tasks ?? []);

  return (
    <Section
      title="爬蟲與解析狀態"
      description="每個官方來源的最近一次執行結果（GET /api/crawler/status）與解析 pipeline 狀態（GET /api/pipeline/status）；執行爬蟲後會自動跑解析。"
      actions={
        <>
          {data ? <Badge tone={data.redis ? 'indigo' : 'slate'}>{data.redis ? 'Redis 佇列' : '執行緒模式'}</Badge> : null}
          {pipeline.data ? <LlmOnlineBadge online={pipeline.data.llm.online} model={pipeline.data.llm.model} provider={pipeline.data.llm.provider} /> : null}
          {running ? (
            <span className="inline-flex items-center gap-1 text-xs text-blue-700">
              <Spinner /> 執行中：{runningKinds.map((kind) => TASK_KIND_LABELS[kind] ?? kind).join('、') || '背景工作'}
            </span>
          ) : null}
          <button
            type="button"
            className={smallBtn}
            onClick={() => {
              reload();
              pipeline.reload();
            }}
            disabled={loading}
          >
            重新整理
          </button>
        </>
      }
    >
      {actionError ? (
        <div className="mb-3">
          <ErrorBox title="無法送出背景工作" message={actionError} />
        </div>
      ) : null}
      {message ? (
        <div className="mb-3">
          <Notice tone={running ? 'info' : 'success'}>{message}</Notice>
        </div>
      ) : null}
      {loading && !data ? (
        <LoadingBlock text="載入爬蟲狀態…" />
      ) : error && !data ? (
        <ErrorBox message={error} onRetry={reload} />
      ) : data ? (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
            <button type="button" className={primaryBtn} disabled={busy} onClick={() => void trigger('crawl')} title="POST /api/crawler/run（全部啟用的來源，完成後自動解析）">
              {pending === 'crawl' ? <Spinner className="border-white/40 border-t-white" /> : null}
              執行全部爬蟲
            </button>
            <button type="button" className={smallBtn} disabled={busy} onClick={() => void trigger('pipeline')} title="POST /api/pipeline/run（force=true：所有原始文件重新解析）">
              重新解析（force）
            </button>
            <button type="button" className={indigoBtn} disabled={busy || !llmOnline} onClick={() => void trigger('llm_fill')} title={llmOnline ? 'POST /api/pipeline/llm-fill' : '本地 AI 離線，無法補齊'}>
              本地 AI 補齊
            </button>
            <button type="button" className={smallBtn} disabled={busy} onClick={() => void trigger('mine_keywords')} title="POST /api/pipeline/mine-keywords（由語料統計關鍵字）">
              重算關鍵字
            </button>
            {pipeline.data ? (
              <span className="ml-auto flex flex-wrap items-center gap-2 text-xs text-slate-600">
                <span>待解析 {formatNumber(pipeline.data.pending)}</span>
                <span>本地 AI 待補齊 {formatNumber(pipeline.data.llm_pending)} / {formatNumber(pipeline.data.benefits_total)}</span>
                <span title={Object.entries(pipeline.data.raw_documents_by_status).map(([k, v]) => `${PROCESSING_STATUS_LABELS[k] ?? k} ${v}`).join('・')}>
                  原始文件 {Object.values(pipeline.data.raw_documents_by_status).reduce((a, b) => a + b, 0)} 份
                </span>
              </span>
            ) : null}
          </div>
          <DataTable columns={columns} rows={data.sources} rowKey={(row) => row.id} dense emptyText="尚未註冊任何來源" />
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
            <span>最近一次爬取完成：{formatDateTime(data.last_crawl)}</span>
            <button type="button" className="text-blue-600 hover:underline" onClick={() => setShowTasks((v) => !v)}>
              {showTasks ? '隱藏' : '顯示'}最近背景工作（{tasks.length}）
            </button>
          </div>
          {showTasks ? <DataTable columns={taskColumns} rows={tasks} rowKey={(task) => task.task_id} dense emptyText="尚無背景工作" /> : null}
        </div>
      ) : null}
    </Section>
  );
}
