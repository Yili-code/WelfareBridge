import type { ReactNode } from 'react';

export function Spinner({ className = '' }: { className?: string }) {
  return (
    <span
      role="status"
      aria-label="載入中"
      className={`inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-blue-600 align-[-2px] ${className}`}
    />
  );
}

export function LoadingBlock({ text = '載入中…' }: { text?: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-dashed border-slate-200 bg-white px-4 py-6 text-sm text-slate-500">
      <Spinner /> {text}
    </div>
  );
}

export function ErrorBox({ title = '載入失敗', message, onRetry }: { title?: string; message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="font-semibold">{title}</div>
          <div className="mt-0.5 break-all">{message}</div>
        </div>
        {onRetry ? (
          <button type="button" onClick={onRetry} className="rounded-md border border-red-300 bg-white px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-100">
            重試
          </button>
        ) : null}
      </div>
    </div>
  );
}

export function EmptyState({ text, children }: { text: string; children?: ReactNode }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-200 bg-white px-4 py-8 text-center text-sm text-slate-400">
      {text}
      {children}
    </div>
  );
}

export function Notice({ tone = 'info', children }: { tone?: 'info' | 'warn' | 'success'; children: ReactNode }) {
  const cls = tone === 'warn' ? 'border-amber-200 bg-amber-50 text-amber-900' : tone === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-900' : 'border-blue-200 bg-blue-50 text-blue-900';
  return <div className={`rounded-lg border px-4 py-3 text-sm ${cls}`}>{children}</div>;
}

/** 頁面區塊容器 */
export function Section({ title, description, actions, children, className = '' }: { title: ReactNode; description?: ReactNode; actions?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5 ${className}`}>
      <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          {description ? <p className="mt-0.5 text-xs text-slate-500">{description}</p> : null}
        </div>
        {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
      </div>
      {children}
    </section>
  );
}
