import { useState } from 'react';
import type { MetaOptions } from '../types';
import { DISLIKE_LABELS, DOMAIN_LABELS, NEED_TYPE_LABELS } from '../utils/labels';
import { ChipSelect, ChoiceButtons, inputClass } from './FormControls';

export interface Needs {
  need_type: string;
  dislikes: string[];
  current_benefits: string[];
}

export const EMPTY_NEEDS: Needs = { need_type: 'unknown', dislikes: [], current_benefits: [] };

function toOptions(labels: Record<string, string>) {
  return Object.entries(labels).map(([value, label]) => ({ value, label }));
}

/** 三種輸入模式共用：需求類型、不想要的類型、目前已領補助、想找的領域。 */
export function NeedsHeader({ needs, onChange, domains, onDomainsChange, options }: { needs: Needs; onChange: (needs: Needs) => void; domains: string[]; onDomainsChange: (domains: string[]) => void; options: MetaOptions | null }) {
  const [benefitText, setBenefitText] = useState('');
  const needOptions = options?.need_types ?? toOptions(NEED_TYPE_LABELS);
  const dislikeOptions = options?.dislikes ?? toOptions(DISLIKE_LABELS);
  const domainOptions = options?.domains ?? toOptions(DOMAIN_LABELS);

  const addBenefit = () => {
    const items = benefitText
      .split(/[,，、\n]/)
      .map((item) => item.trim())
      .filter(Boolean);
    if (!items.length) return;
    onChange({ ...needs, current_benefits: Array.from(new Set([...needs.current_benefits, ...items])) });
    setBenefitText('');
  };

  return (
    <div className="space-y-4 rounded-lg border border-emerald-100 bg-emerald-50/40 p-4">
      <div>
        <div className="mb-1 text-sm font-semibold text-slate-800">你現在最需要的是？</div>
        <p className="mb-2 text-xs text-slate-500">需求類型會影響推薦排序與「其他可申請」的分流；不確定也沒關係。</p>
        <ChoiceButtons options={needOptions} value={needs.need_type} onChange={(value) => onChange({ ...needs, need_type: value })} />
      </div>
      <div>
        <div className="mb-1 text-sm font-semibold text-slate-800">不想要的類型（可複選）</div>
        <p className="mb-2 text-xs text-slate-500">勾選的類型會被大幅降權或排除。</p>
        <ChipSelect options={dislikeOptions} selected={needs.dislikes} onChange={(selected) => onChange({ ...needs, dislikes: selected })} />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <div className="mb-1 text-sm font-semibold text-slate-800">目前已領的補助（選填）</div>
          <p className="mb-2 text-xs text-slate-500">用來排除註明「不得重複領取」的項目；輸入名稱後按 Enter 或「加入」。</p>
          <div className="flex gap-2">
            <input
              type="text"
              className={inputClass}
              value={benefitText}
              placeholder="例如：低收入戶生活補助"
              onChange={(event) => setBenefitText(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  addBenefit();
                }
              }}
            />
            <button type="button" onClick={addBenefit} className="whitespace-nowrap rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50">
              加入
            </button>
          </div>
          {needs.current_benefits.length ? (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {needs.current_benefits.map((item) => (
                <span key={item} className="inline-flex items-center gap-1 rounded-full border border-slate-300 bg-white px-2.5 py-0.5 text-xs text-slate-700">
                  {item}
                  <button type="button" aria-label={`移除 ${item}`} className="text-slate-400 hover:text-red-600" onClick={() => onChange({ ...needs, current_benefits: needs.current_benefits.filter((b) => b !== item) })}>
                    ×
                  </button>
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <div>
          <div className="mb-1 text-sm font-semibold text-slate-800">想找的領域（可複選，選填）</div>
          <p className="mb-2 text-xs text-slate-500">只比對所選領域的補助，表單與追問也只顯示相關屬性；不選代表全部。</p>
          <ChipSelect options={domainOptions} selected={domains} onChange={onDomainsChange} />
        </div>
      </div>
    </div>
  );
}
