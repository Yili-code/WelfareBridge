import type { Condition, FieldSpec } from '../../types';
import { CONDITION_STATUS_LABELS } from '../../utils/labels';
import { attributeLabel } from '../../utils/profile';
import { Badge, RoleBadge, type Tone } from '../Badge';
import { DataTable, type Column } from '../DataTable';

function statusTone(status: string): Tone {
  switch (status) {
    case 'mapped':
      return 'green';
    case 'complex':
      return 'amber';
    case 'unmapped':
    case 'unresolved':
      return 'red';
    default:
      return 'gray';
  }
}

export function ConditionsTab({ conditions, catalog }: { conditions: Condition[]; catalog: Record<string, FieldSpec> | null }) {
  const counts = conditions.reduce<Record<string, number>>((acc, condition) => {
    acc[condition.status] = (acc[condition.status] ?? 0) + 1;
    return acc;
  }, {});

  const columns: Column<Condition>[] = [
    { key: 'index', header: '#', className: 'text-right tabular-nums text-slate-400', render: (row) => conditions.indexOf(row) + 1 },
    { key: 'text', header: '條件句（原文）', className: 'min-w-[20rem]', render: (row) => <span className="text-slate-800">{row.text || row.excerpt}</span> },
    { key: 'role', header: '角色', render: (row) => <RoleBadge role={row.role} /> },
    { key: 'status', header: '狀態', render: (row) => <Badge tone={statusTone(row.status)}>{CONDITION_STATUS_LABELS[row.status] ?? row.status}</Badge> },
    {
      key: 'attribute',
      header: '對應屬性',
      render: (row) =>
        row.attribute_id ? (
          <span>
            {attributeLabel(row.attribute_id, catalog)} <span className="mono text-[11px] text-slate-400">{row.attribute_id}</span>
          </span>
        ) : row.candidates?.length ? (
          <details className="text-xs text-slate-500">
            <summary className="cursor-pointer">候選屬性（{row.candidates.length}）</summary>
            <ul className="mt-1 list-inside list-disc">
              {row.candidates.map((candidate) => (
                <li key={candidate}>
                  {attributeLabel(candidate, catalog)} <span className="mono text-[11px] text-slate-400">{candidate}</span>
                </li>
              ))}
            </ul>
          </details>
        ) : (
          <span className="text-slate-400">—</span>
        ),
    },
    { key: 'method', header: '方法', render: (row) => <Badge tone={row.method === 'llm' ? 'purple' : 'slate'}>{row.method === 'llm' ? '本地 AI' : row.method === 'rule' ? '規則式' : row.method}</Badge> },
  ];

  return (
    <div className="space-y-2">
      <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700">
        原文中被辨識為「資格條件」的句子。<strong>已對應屬性</strong>的句子已轉為資格規則；<strong>未對應屬性</strong>／<strong>複雜條件</strong>會交給本地 AI 在候選屬性中選擇，仍無法對應者以「需語意判斷」規則保留；<strong>程序性說明</strong>（申請方式、文件等）不參與資格判定。
        <span className="ml-2 text-slate-500">{Object.entries(counts).map(([status, count]) => `${CONDITION_STATUS_LABELS[status] ?? status} ${count}`).join('・') || '—'}</span>
      </div>
      <DataTable columns={columns} rows={conditions} rowKey={(row) => `${row.text}-${conditions.indexOf(row)}`} dense emptyText="原文中沒有辨識出條件句" />
    </div>
  );
}
