import type { BenefitSummary, LlmReport } from '../../types';
import { displayValue, formatConfidence, formatDateTime } from '../../utils/format';
import { Badge } from '../Badge';
import { DataTable, type Column } from '../DataTable';
import { Notice } from '../Feedback';
import { JsonViewer } from '../JsonViewer';
import { KeyValueTable, type KeyValueRow } from '../KeyValueTable';

const TASK_LABELS: Record<string, string> = { benefit_meta: '補齊給付資訊（benefit_meta）', condition_mapping: '條件句對應屬性（condition_mapping）' };

export function LlmTab({ llm, benefit }: { llm: LlmReport | null; benefit: BenefitSummary }) {
  const processed = Boolean(llm?.processed);
  const accepted = llm?.accepted ?? [];
  const rejected = llm?.rejected ?? [];
  const errors = llm?.errors ?? [];
  const tasks = Object.entries(llm?.tasks ?? {});

  const rows: KeyValueRow[] = [
    { label: '本地 AI 已處理', value: processed ? <Badge tone="purple">是</Badge> : <Badge tone="slate">否</Badge> },
    { label: '提供者 / 模型', value: processed ? `${llm?.provider || '—'}／${llm?.model || benefit.llm_model || '—'}` : '—' },
    { label: '處理時間', value: formatDateTime(llm?.processed_at ?? null) },
    {
      label: '任務摘要',
      value: tasks.length ? (
        <ul className="space-y-0.5 text-xs">
          {tasks.map(([task, summary]) => (
            <li key={task}>
              <span className="font-medium text-slate-700">{TASK_LABELS[task] ?? task}</span>：採納 {summary.accepted}・拒絕 {summary.rejected}
              {typeof summary.proposed_attributes === 'number' ? `・提議新屬性 ${summary.proposed_attributes}` : ''}
            </li>
          ))}
        </ul>
      ) : (
        '—'
      ),
    },
    { label: '整體解析信心（confidence）', value: formatConfidence(benefit.confidence) },
    { label: '來源信心（data_confidence）', value: formatConfidence(benefit.data_confidence) },
    {
      label: '檢核',
      value: benefit.needs_review ? (
        <div>
          <Badge tone="amber">⚠ 需人工確認</Badge>
          {benefit.review_reasons.length ? (
            <ul className="mt-1 list-inside list-disc text-xs text-slate-600">
              {benefit.review_reasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : (
        <Badge tone="green">✅ 不需人工確認</Badge>
      ),
    },
  ];

  const acceptedColumns: Column<LlmReport['accepted'] extends (infer T)[] | undefined ? T : never>[] = [
    { key: 'field', header: '欄位 / 屬性', render: (row) => <span className="mono text-xs">{row.field ?? row.attribute_id ?? '—'}</span> },
    {
      key: 'value',
      header: '值',
      render: (row) => (
        <span>
          {row.operator ? <span className="mono text-xs text-slate-500">{row.operator} </span> : null}
          {row.result ? <Badge tone="amber">{row.result}</Badge> : displayValue(row.value)}
        </span>
      ),
    },
    { key: 'excerpt', header: '原文摘錄 / 條件句', className: 'min-w-[16rem]', render: (row) => (row.excerpt || row.sentence ? <q className="text-slate-600">{row.excerpt || row.sentence}</q> : '—') },
  ];

  const rejectedColumns: Column<LlmReport['rejected'] extends (infer T)[] | undefined ? T : never>[] = [
    { key: 'field', header: '欄位 / 條件句', className: 'min-w-[14rem]', render: (row) => (row.field ? <span className="mono text-xs">{row.field}</span> : row.sentence ? <q className="text-slate-600">{row.sentence}</q> : '—') },
    { key: 'reason', header: '拒絕原因', render: (row) => <span className="text-red-700">{row.reason}</span> },
  ];

  return (
    <div className="space-y-4">
      <KeyValueTable rows={rows} />
      {!processed ? (
        <Notice tone="info">此筆資料尚未經本地 AI 補齊，目前內容全由規則式解析器產生。可在資料中心按「本地 AI 補齊」（需 Ollama 在線）。</Notice>
      ) : (
        <>
          <p className="text-xs text-slate-500">本地 AI 的輸出只有在「摘錄確實存在於原文、屬性在候選清單內、值型態合法」時才會被採納；被拒絕的項目一律不寫入資料。</p>
          <div>
            <h3 className="mb-2 text-sm font-semibold text-slate-800">採納（{accepted.length}）</h3>
            <DataTable columns={acceptedColumns} rows={accepted} rowKey={(row) => `${row.field ?? row.sentence ?? ''}-${accepted.indexOf(row)}`} dense emptyText="沒有採納任何 AI 輸出" />
          </div>
          <div>
            <h3 className="mb-2 text-sm font-semibold text-slate-800">拒絕（{rejected.length}）</h3>
            <DataTable columns={rejectedColumns} rows={rejected} rowKey={(row) => `${row.field ?? row.sentence ?? ''}-${rejected.indexOf(row)}`} dense emptyText="沒有被拒絕的輸出" />
          </div>
          {errors.length ? (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-red-800">錯誤（{errors.length}）</h3>
              <ul className="list-inside list-disc rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-800">
                {errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          ) : null}
          <details>
            <summary className="cursor-pointer text-xs text-slate-500">完整 llm 區塊（JSON）</summary>
            <JsonViewer value={llm} defaultDepth={2} className="mt-2" />
          </details>
        </>
      )}
    </div>
  );
}
