import type { ConditionResult, FieldSpec } from '../types';
import { displayValue, formatUnit } from '../utils/format';
import { OPERATOR_LABELS } from '../utils/labels';
import { attributeLabel } from '../utils/profile';
import { Badge } from './Badge';

type Tone = 'emerald' | 'amber' | 'red' | 'slate' | 'purple';

const TONE_CLASS: Record<Tone, { title: string; bullet: string }> = {
  emerald: { title: 'text-emerald-800', bullet: 'text-emerald-600' },
  amber: { title: 'text-amber-800', bullet: 'text-amber-600' },
  red: { title: 'text-red-800', bullet: 'text-red-600' },
  slate: { title: 'text-slate-700', bullet: 'text-slate-500' },
  purple: { title: 'text-purple-800', bullet: 'text-purple-600' },
};

export function conditionText(condition: ConditionResult, catalog?: Record<string, FieldSpec> | null): string {
  if (condition.human_readable) return condition.human_readable;
  const op = OPERATOR_LABELS[condition.operator] ?? condition.operator;
  return `${attributeLabel(condition.attribute_id, catalog)} ${op} ${displayValue(condition.value)}${condition.unit ? ` ${formatUnit(condition.unit)}` : ''}`;
}

export function ConditionList({
  title,
  icon,
  tone,
  items,
  catalog,
  showUserValue = false,
}: {
  title: string;
  icon: string;
  tone: Tone;
  items: ConditionResult[];
  catalog?: Record<string, FieldSpec> | null;
  showUserValue?: boolean;
}) {
  if (items.length === 0) return null;
  const cls = TONE_CLASS[tone];
  return (
    <div>
      <h4 className={`text-sm font-semibold ${cls.title}`}>
        {icon} {title} <span className="font-normal text-slate-400">({items.length})</span>
      </h4>
      <ul className="mt-1 space-y-1.5">
        {items.map((condition, index) => (
          <li key={`${condition.rule_id || condition.attribute_id}-${index}`} className="flex gap-2 text-sm">
            <span className={`mt-0.5 ${cls.bullet}`}>•</span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-1.5 text-slate-800">
                <span>{conditionText(condition, catalog)}</span>
                {condition.role === 'bonus' ? <Badge tone="purple">加分</Badge> : null}
                {condition.role === 'exclusion' ? <Badge tone="red">排除條件</Badge> : null}
                {condition.inferred ? <span className="text-xs text-purple-700">（依機關推定）</span> : null}
                {condition.complexity === 'complex' ? <Badge tone="amber">需語意判斷</Badge> : null}
                {condition.llm_used ? <Badge tone="purple">本地 AI 判讀</Badge> : null}
                {!condition.rejectable && condition.status !== 'match' && condition.complexity !== 'complex' ? <span className="text-[11px] text-slate-400">低信心抽取，不會用來排除</span> : null}
              </div>
              {condition.reason ? <div className="text-xs text-slate-500">{condition.reason}</div> : null}
              {showUserValue && condition.user_value !== null && condition.user_value !== undefined ? (
                <div className="text-xs text-slate-500">你的資料：{displayValue(condition.user_value)}</div>
              ) : null}
              {condition.excerpt ? (
                <details className="text-xs text-slate-500">
                  <summary className="cursor-pointer select-none">原文</summary>
                  <q className="text-slate-600">{condition.excerpt}</q>
                </details>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
