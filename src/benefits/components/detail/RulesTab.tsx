import type { Rule } from '../../types';
import { displayValue, formatConfidence, formatUnit } from '../../utils/format';
import { COMPLEXITY_LABELS, OPERATOR_LABELS } from '../../utils/labels';
import { Badge, ExtractorBadge, RoleBadge } from '../Badge';


export function RulesTab({ rules }: { rules: Rule[] }) {
  const groupIds = Array.from(new Set(rules.map((rule) => rule.group_id || rule.id)));

  const bonusCount = rules.filter((rule) => rule.role === 'bonus').length;
  const exclusionCount = rules.filter((rule) => rule.role === 'exclusion').length;


  return (
    <div className="min-w-0 space-y-4">
      <div className="rounded-lg border border-blue-100 bg-blue-50 px-3 py-2 text-xs text-blue-900">
        <strong>群組語意：</strong>同一群組（group_id 相同）的規則之間為 <span className="mono">OR</span>（任一成立即可）；不同群組之間為 <span className="mono">AND</span>（全部成立才符合）。
        <span className="ml-2">
          角色為「加分／優先」的規則不參與資格判定，只在結果頁標示為優先條件（{bonusCount} 條）；「排除」規則成立即不符合（{exclusionCount} 條）。
        </span>
        <span className="ml-2">「需語意判斷」的規則無法純靠規則引擎判斷，比對時會標示為「需進一步確認」，本地 AI 在線時可協助判讀。</span>
      </div>
      {!rules.length && <p className="p-6 text-sm text-slate-500">此筆資料尚未產生資格規則</p>}
      {rules.map((rule, index) => <article key={rule.id} className="min-w-0 rounded-xl border border-slate-200 bg-white p-5">
        <header className="flex flex-wrap items-center gap-2"><span className="text-xs text-slate-500">條件 {index + 1} · 第 {groupIds.indexOf(rule.group_id || rule.id) + 1} 組</span><RoleBadge role={rule.role} /><Badge tone={rule.complexity === 'complex' ? 'amber' : 'green'}>{COMPLEXITY_LABELS[rule.complexity] ?? rule.complexity}</Badge>{rule.inferred && <Badge tone="amber">推定，待確認</Badge>}</header>
        <h3 className="mt-3 break-words text-base font-semibold leading-7">{rule.attribute_label || rule.attribute_id || '其他資格限制'}</h3>
        <p className="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{rule.human_readable || `${OPERATOR_LABELS[rule.operator] || rule.operator} ${rule.value_label ?? displayValue(rule.value)}`}</p>
        {rule.unit && <p className="mt-1 text-xs text-slate-500">單位：{formatUnit(rule.unit)}</p>}
        <div className="mt-4 rounded-lg bg-slate-50 p-4"><p className="mb-2 text-xs font-medium text-slate-500">官方原文摘錄</p><blockquote className="whitespace-pre-wrap break-words text-sm leading-7 text-slate-700">{rule.evidence?.excerpt || '未附原文摘錄，請至來源頁核對。'}</blockquote>{rule.evidence?.condition_text && rule.evidence.condition_text !== rule.evidence.excerpt && <p className="mt-2 whitespace-pre-wrap break-words text-sm leading-7">條件句：{rule.evidence.condition_text}</p>}</div>
        <details className="mt-4 border-t border-slate-100 pt-3"><summary className="cursor-pointer text-sm text-blue-700">查看規則欄位與抽取資訊</summary><dl className="mt-3 grid min-w-0 gap-3 text-xs sm:grid-cols-2">{[['欄位名稱',rule.attribute_id || '未指定'],['運算子',`${OPERATOR_LABELS[rule.operator] || rule.operator}（${rule.operator}）`],['原始值',displayValue(rule.value)],['群組',rule.group_id || '單獨'],['抽取信心',formatConfidence(rule.confidence)],['推定依據',rule.inference_basis || (rule.inferred ? '未提供' : '非推定條件')]].map(([label,value]) => <div key={label} className="min-w-0"><dt className="text-slate-500">{label}</dt><dd className="mt-1 whitespace-pre-wrap break-all leading-6">{value}</dd></div>)}<div><dt className="text-slate-500">抽取方式</dt><dd className="mt-1"><ExtractorBadge extractor={rule.evidence?.extractor} /></dd></div></dl></details>
      </article>)}
    </div>
  );
}
