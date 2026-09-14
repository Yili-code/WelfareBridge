import { useState } from 'react';
import type { MetaOptions, Option } from '../types';
import { BENEFIT_FORM_LABELS, CATEGORY_LABELS, CITIES_FALLBACK, DOMAIN_LABELS, PROVIDER_TYPE_LABELS } from '../utils/labels';

export interface Filters {
  keyword: string;
  domain: string;
  category: string;
  benefit_form: string;
  provider_type: string;
  region: string;
  application_status: 'active' | 'expired' | 'all';
  overview: 'all' | 'hide' | 'only';
  kind: 'program' | 'portal' | 'all';
  needs_review: boolean;
  show_duplicates: boolean;
  sort: 'updated' | 'deadline' | 'title';
}

export const DEFAULT_FILTERS: Filters = {
  keyword: '',
  domain: '',
  category: '',
  benefit_form: '',
  provider_type: '',
  region: '',
  application_status: 'active',
  overview: 'all',
  kind: 'program',
  needs_review: false,
  show_duplicates: false,
  sort: 'updated',
};

const selectCls = 'rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200';
const labelCls = 'flex flex-col gap-1 text-xs font-medium text-slate-600';

function toOptions(labels: Record<string, string>): Option[] {
  return Object.entries(labels).map(([value, label]) => ({ value, label }));
}

export function BenefitFilters({ value, onChange, options }: { value: Filters; onChange: (filters: Filters) => void; options: MetaOptions | null }) {
  const [keyword, setKeyword] = useState(value.keyword);
  const update = (patch: Partial<Filters>) => onChange({ ...value, ...patch });

  const domainOptions: Option[] = options?.domains ?? toOptions(DOMAIN_LABELS);
  const categoryOptions = (options?.categories ?? toOptions(CATEGORY_LABELS).map((o) => ({ ...o, domain: '' }))).filter((option) => !value.domain || !option.domain || option.domain === value.domain);
  const formOptions = options?.benefit_forms ?? toOptions(BENEFIT_FORM_LABELS);
  const providerTypeOptions = options?.provider_types ?? toOptions(PROVIDER_TYPE_LABELS);
  const cities = options?.cities ?? CITIES_FALLBACK;

  return (
    <form
      className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3"
      onSubmit={(event) => {
        event.preventDefault();
        update({ keyword: keyword.trim() });
      }}
    >
      <label className={`${labelCls} min-w-[12rem] flex-1`}>
        關鍵字
        <input type="search" value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="名稱、機關、關鍵字或原文" className={selectCls} />
      </label>
      <label className={labelCls}>
        領域
        <select className={selectCls} value={value.domain} onChange={(event) => update({ domain: event.target.value, category: '' })}>
          <option value="">全部</option>
          {domainOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={labelCls}>
        類別
        <select className={selectCls} value={value.category} onChange={(event) => update({ category: event.target.value })}>
          <option value="">全部</option>
          {categoryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={labelCls}>
        給付形式
        <select className={selectCls} value={value.benefit_form} onChange={(event) => update({ benefit_form: event.target.value })}>
          <option value="">全部</option>
          {formOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={labelCls}>
        機關類型
        <select className={selectCls} value={value.provider_type} onChange={(event) => update({ provider_type: event.target.value })}>
          <option value="">全部</option>
          {providerTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className={labelCls}>
        地區
        <select className={selectCls} value={value.region} onChange={(event) => update({ region: event.target.value })}>
          <option value="">全部</option>
          {cities.map((city) => (
            <option key={city} value={city}>
              {city}
            </option>
          ))}
        </select>
      </label>
      <label className={labelCls}>
        狀態
        <select className={selectCls} value={value.application_status} onChange={(event) => update({ application_status: event.target.value as Filters['application_status'] })}>
          <option value="active">開放中</option>
          <option value="expired">已截止</option>
          <option value="all">全部</option>
        </select>
      </label>
      <label className={labelCls} title="收錄政策：預設只列補助方案；彙整頁（總整理、懶人包、專區）保留供查閱，不進媒合">
        紀錄類型
        <select className={selectCls} value={value.kind} onChange={(event) => update({ kind: event.target.value as Filters['kind'] })}>
          <option value="program">補助方案</option>
          <option value="all">含彙整頁</option>
          <option value="portal">只看彙整頁</option>
        </select>
      </label>
      <label className={labelCls}>
        排序
        <select className={selectCls} value={value.sort} onChange={(event) => update({ sort: event.target.value as Filters['sort'] })}>
          <option value="updated">最近更新</option>
          <option value="deadline">申請截止日</option>
          <option value="title">名稱</option>
        </select>
      </label>
      <label className="flex items-center gap-1.5 pb-1.5 text-xs text-slate-700">
        <input type="checkbox" checked={value.needs_review} onChange={(event) => update({ needs_review: event.target.checked })} className="h-4 w-4 rounded border-slate-300" />
        只看待確認
      </label>
      <label className="flex items-center gap-1.5 pb-1.5 text-xs text-slate-700">
        <input type="checkbox" checked={value.show_duplicates} onChange={(event) => update({ show_duplicates: event.target.checked })} className="h-4 w-4 rounded border-slate-300" />
        顯示重複來源
      </label>
      <div className="flex gap-2">
        <button type="submit" className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-blue-500">
          搜尋
        </button>
        <button
          type="button"
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
          onClick={() => {
            setKeyword('');
            onChange(DEFAULT_FILTERS);
          }}
        >
          清除
        </button>
      </div>
    </form>
  );
}
