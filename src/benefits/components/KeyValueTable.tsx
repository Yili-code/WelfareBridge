import type { ReactNode } from 'react';

export interface KeyValueRow {
  label: ReactNode;
  value: ReactNode;
}

/** 標籤／值 兩欄表格（metadata、schema 摘要用）。 */
export function KeyValueTable({ rows, className = '' }: { rows: KeyValueRow[]; className?: string }) {
  return (
    <dl className={`divide-y divide-slate-100 overflow-hidden rounded-lg border border-slate-200 bg-white text-sm ${className}`}>
      {rows.map((row, index) => (
        <div key={index} className="grid grid-cols-1 gap-1 px-3 py-2 sm:grid-cols-[11rem_1fr] sm:gap-3">
          <dt className="text-xs font-medium text-slate-500 sm:pt-0.5">{row.label}</dt>
          <dd className="min-w-0 break-words text-slate-800">{row.value ?? '—'}</dd>
        </div>
      ))}
    </dl>
  );
}

export function ExternalLink({ href, children, className = '' }: { href: string | null | undefined; children?: ReactNode; className?: string }) {
  if (!href) return <span className="text-slate-400">—</span>;
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={`break-all text-blue-600 underline-offset-2 hover:underline ${className}`}>
      {children ?? href}
    </a>
  );
}

export function TagList({ items, tone = 'slate' }: { items: string[] | undefined | null; tone?: 'slate' | 'indigo' | 'emerald' }) {
  if (!items || items.length === 0) return <span className="text-slate-400">—</span>;
  const cls = tone === 'indigo' ? 'bg-indigo-50 text-indigo-700' : tone === 'emerald' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700';
  return (
    <span className="flex flex-wrap gap-1">
      {items.map((item, index) => (
        <span key={`${item}-${index}`} className={`rounded px-1.5 py-0.5 text-xs ${cls}`}>
          {item}
        </span>
      ))}
    </span>
  );
}
