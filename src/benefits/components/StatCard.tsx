import type { ReactNode } from 'react';

type Tone = 'blue' | 'green' | 'red' | 'amber' | 'slate' | 'indigo';

const ACCENT: Record<Tone, string> = {
  blue: 'border-l-blue-500',
  green: 'border-l-green-500',
  red: 'border-l-red-500',
  amber: 'border-l-amber-500',
  slate: 'border-l-slate-400',
  indigo: 'border-l-indigo-500',
};

export function StatCard({ label, value, sub, tone = 'blue', title }: { label: string; value: ReactNode; sub?: ReactNode; tone?: Tone; title?: string }) {
  return (
    <div title={title} className={`rounded-lg border border-slate-200 border-l-4 bg-white px-4 py-3 shadow-sm ${ACCENT[tone]}`}>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-slate-900">{value}</div>
      {sub ? <div className="mt-1 text-xs text-slate-500">{sub}</div> : null}
    </div>
  );
}
