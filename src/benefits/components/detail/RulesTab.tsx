import type { Rule } from '../../types';
import { displayValue, formatConfidence, formatUnit } from '../../utils/format';
import { COMPLEXITY_LABELS, OPERATOR_LABELS } from '../../utils/labels';
import { Badge, ExtractorBadge, RoleBadge, type Tone } from '../Badge';
import { DataTable, type Column } from '../DataTable';

const GROUP_TONES: Tone[] = ['blue', 'emerald', 'purple', 'amber', 'indigo', 'red', 'slate'];

export function RulesTab({ rules }: { rules: Rule[] }) {
  const groupIds = Array.from(new Set(rules.map((rule) => rule.group_id || rule.id)));
  const toneOf = (rule: Rule): Tone => GROUP_TONES[groupIds.indexOf(rule.group_id || rule.id) % GROUP_TONES.length];
  const bonusCount = rules.filter((rule) => rule.role === 'bonus').length;
  const exclusionCount = rules.filter((rule) => rule.role === 'exclusion').length;

  const columns: Column<Rule>[] = [
    { key: 'position', header: '#', className: 'text-right tabular-nums text-slate-400', render: (rule) => rules.indexOf(rule) + 1 },
    {
      key: 'attribute',
      header: '屬性',
      className: 'min-w-[10rem]',
      render: (rule) => (
        <div>
          <div className="text-slate-900">{rule.attribute_label || rule.attribute_id}</div>
          <div className="mono text-[11px] text-slate-400">{rule.attribute_id}</div>
        </div>
      ),
    },
    { key: 'operator', header: '運算子', render: (rule) => <span className="mono text-xs" title={OPERATOR_LABELS[rule.operator] ?? rule.operator}>{rule.operator}</span> },
    {
      key: 'value',
      header: '值',
      className: 'min-w-[10rem]',
      render: (rule) => (
        <div>
          <div>{rule.value_label ?? displayValue(rule.value)}</div>
          {rule.value_label ? <div className="mono text-[11px] text-slate-400">{displayValue(rule.value)}</div> : null}
          {rule.unit ? <div className="text-[11px] text-slate-500">單位：{formatUnit(rule.unit)}</div> : null}
        </div>
      ),
    },
    { key: 'human', header: '人類可讀', className: 'min-w-[14rem]', render: (rule) => rule.human_readable || <span className="text-slate-400">—</span> },
    {
      key: 'group',
      header: '群組',
      render: (rule) => (
        <Badge tone={toneOf(rule)} title="同一群組內任一條件成立即可（OR）；不同群組之間必須同時成立（AND）">
          {rule.group_id || '（單獨）'}
        </Badge>
      ),
    },
    { key: 'role', header: '角色', render: (rule) => <RoleBadge role={rule.role} /> },
    { key: 'complexity', header: '複雜度', render: (rule) => <Badge tone={rule.complexity === 'complex' ? 'amber' : 'green'}>{COMPLEXITY_LABELS[rule.complexity] ?? rule.complexity}</Badge> },
    { key: 'confidence', header: '信心', className: 'text-right tabular-nums', render: (rule) => formatConfidence(rule.confidence) },
    {
      key: 'inferred',
      header: '推定',
      render: (rule) =>
        rule.inferred ? (
          <span className="inline-flex flex-col">
            <Badge tone="amber">推定</Badge>
            {rule.inference_basis ? <span className="mt-0.5 max-w-[12rem] text-[11px] text-slate-500">{rule.inference_basis}</span> : null}
          </span>
        ) : (
          <span className="text-slate-400">—</span>
        ),
    },
    { key: 'extractor', header: '抽取方式', render: (rule) => <ExtractorBadge extractor={rule.evidence?.extractor} /> },
    {
      key: 'excerpt',
      header: '原文摘錄',
      className: 'min-w-[16rem]',
      render: (rule) => (
        <div className="space-y-0.5">
          {rule.evidence?.excerpt ? <q className="text-slate-600">{rule.evidence.excerpt}</q> : <span className="text-slate-400">—</span>}
          {rule.evidence?.condition_text && rule.evidence.condition_text !== rule.evidence.excerpt ? <div className="text-[11px] text-slate-400">條件句：{rule.evidence.condition_text}</div> : null}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-2">
      <div className="rounded-lg border border-blue-100 bg-blue-50 px-3 py-2 text-xs text-blue-900">
        <strong>群組語意：</strong>同一群組（group_id 相同）的規則之間為 <span className="mono">OR</span>（任一成立即可）；不同群組之間為 <span className="mono">AND</span>（全部成立才符合）。
        <span className="ml-2">
          角色為「加分／優先」的規則不參與資格判定，只在結果頁標示為優先條件（{bonusCount} 條）；「排除」規則成立即不符合（{exclusionCount} 條）。
        </span>
        <span className="ml-2">「需語意判斷」的規則無法純靠規則引擎判斷，比對時會標示為「需進一步確認」，本地 AI 在線時可協助判讀。</span>
      </div>
      <DataTable columns={columns} rows={rules} rowKey={(rule) => rule.id} dense emptyText="此筆資料尚未產生資格規則" />
    </div>
  );
}
