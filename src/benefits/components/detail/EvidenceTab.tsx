import type { Evidence } from '../../types';
import { displayValue, formatConfidence } from '../../utils/format';
import { Badge, ExtractorBadge } from '../Badge';
import { DataTable, type Column } from '../DataTable';

export function EvidenceTab({ evidence }: { evidence: Evidence[] }) {
  const columns: Column<Evidence>[] = [
    { key: 'field', header: '欄位', className: 'whitespace-nowrap', render: (row) => <span className="mono text-xs">{row.field}</span> },
    { key: 'value', header: '值', className: 'min-w-[10rem]', render: (row) => <span className="break-words">{displayValue(row.value)}</span> },
    { key: 'excerpt', header: '原文摘錄', className: 'min-w-[16rem]', render: (row) => (row.excerpt ? <q className="text-slate-600">{row.excerpt}</q> : <span className="text-slate-400">—</span>) },
    { key: 'extractor', header: '抽取方式', render: (row) => <ExtractorBadge extractor={row.extractor} /> },
    { key: 'confidence', header: '信心', className: 'text-right tabular-nums', render: (row) => formatConfidence(row.confidence) },
    {
      key: 'inferred',
      header: '推定',
      render: (row) =>
        row.inferred ? (
          <span className="inline-flex flex-col">
            <Badge tone="amber">推定</Badge>
            {row.inference_basis ? <span className="mt-0.5 max-w-[14rem] text-[11px] text-slate-500">{row.inference_basis}</span> : null}
          </span>
        ) : (
          <span className="text-slate-400">—</span>
        ),
    },
  ];

  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-500">每個 Schema 欄位都能追溯到原文：這裡列出欄位值、其對應的原文摘錄與抽取方式。標示「推定」者表示原文未明寫、由機關名稱等資訊推定；摘錄不在原文中的證據在驗證階段已被丟棄。</p>
      <DataTable columns={columns} rows={evidence} rowKey={(row) => `${row.field}-${row.excerpt}-${displayValue(row.value)}`} dense emptyText="沒有解析證據紀錄" />
    </div>
  );
}
