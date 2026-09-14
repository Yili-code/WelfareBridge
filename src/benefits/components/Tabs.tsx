import type { ReactNode } from 'react';

export interface TabItem {
  id: string;
  label: ReactNode;
  badge?: ReactNode;
}

export function Tabs({ tabs, active, onChange }: { tabs: TabItem[]; active: string; onChange: (id: string) => void }) {
  return (
    <div className="overflow-x-auto border-b border-slate-200">
      <nav className="-mb-px flex min-w-max gap-1" aria-label="Tabs">
        {tabs.map((tab) => {
          const selected = tab.id === active;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onChange(tab.id)}
              aria-current={selected ? 'page' : undefined}
              className={`inline-flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
                selected ? 'border-blue-600 text-blue-700' : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700'
              }`}
            >
              {tab.label}
              {tab.badge !== undefined ? <span className={`rounded-full px-2 py-0.5 text-xs ${selected ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>{tab.badge}</span> : null}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
