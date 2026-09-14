import { useState } from 'react';

type ExpandMode = 'default' | 'all' | 'none';

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function Primitive({ value }: { value: unknown }) {
  if (value === null) return <span className="text-slate-400">null</span>;
  if (value === undefined) return <span className="text-slate-400">undefined</span>;
  if (typeof value === 'string') return <span className="whitespace-pre-wrap break-all text-emerald-700">&quot;{value}&quot;</span>;
  if (typeof value === 'number') return <span className="text-blue-700">{String(value)}</span>;
  if (typeof value === 'boolean') return <span className="text-purple-700">{String(value)}</span>;
  return <span>{String(value)}</span>;
}

function JsonNode({ name, value, depth, defaultDepth, mode }: { name: string | null; value: unknown; depth: number; defaultDepth: number; mode: ExpandMode }) {
  const initialOpen = mode === 'all' ? true : mode === 'none' ? false : depth < defaultDepth;
  const [open, setOpen] = useState(initialOpen);
  const isArray = Array.isArray(value);
  const isObj = isObject(value);

  if (!isArray && !isObj) {
    return (
      <div className="flex gap-1 leading-6">
        {name !== null ? <span className="text-slate-600">{name}:</span> : null}
        <Primitive value={value} />
      </div>
    );
  }

  const entries: Array<[string, unknown]> = isArray ? (value as unknown[]).map((item, index): [string, unknown] => [String(index), item]) : Object.entries(value as Record<string, unknown>);
  const summary = isArray ? `[${entries.length} 項]` : `{${entries.length} 個欄位}`;
  const empty = entries.length === 0;

  return (
    <div className="leading-6">
      <button type="button" onClick={() => setOpen((v) => !v)} className="inline-flex items-center gap-1 rounded px-1 text-left hover:bg-slate-100" disabled={empty}>
        <span className="inline-block w-3 text-slate-400">{empty ? '' : open ? '▾' : '▸'}</span>
        {name !== null ? <span className="text-slate-600">{name}:</span> : null}
        <span className="text-slate-400">{empty ? (isArray ? '[]' : '{}') : open ? (isArray ? '[' : '{') : summary}</span>
      </button>
      {open && !empty ? (
        <div className="ml-4 border-l border-slate-200 pl-3">
          {entries.map(([key, child]) => (
            <JsonNode key={key} name={key} value={child} depth={depth + 1} defaultDepth={defaultDepth} mode={mode} />
          ))}
          <div className="text-slate-400">{isArray ? ']' : '}'}</div>
        </div>
      ) : null}
    </div>
  );
}

/** 可收合的 JSON 樹狀檢視；附「全部展開／收合」與複製。 */
export function JsonViewer({ value, defaultDepth = 2, className = '' }: { value: unknown; defaultDepth?: number; className?: string }) {
  const [mode, setMode] = useState<ExpandMode>('default');
  const [version, setVersion] = useState(0);
  const [copied, setCopied] = useState(false);

  const setExpand = (next: ExpandMode) => {
    setMode(next);
    setVersion((v) => v + 1);
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(value, null, 2));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className={`rounded-lg border border-slate-200 bg-slate-50 ${className}`}>
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 px-3 py-1.5 text-xs text-slate-500">
        <button type="button" onClick={() => setExpand('all')} className="rounded px-2 py-0.5 hover:bg-slate-200">
          全部展開
        </button>
        <button type="button" onClick={() => setExpand('none')} className="rounded px-2 py-0.5 hover:bg-slate-200">
          全部收合
        </button>
        <button type="button" onClick={() => setExpand('default')} className="rounded px-2 py-0.5 hover:bg-slate-200">
          預設
        </button>
        <span className="flex-1" />
        <button type="button" onClick={copy} className="rounded px-2 py-0.5 hover:bg-slate-200">
          {copied ? '已複製' : '複製 JSON'}
        </button>
      </div>
      <div className="mono max-h-[36rem] overflow-auto px-3 py-2 text-xs">
        <JsonNode key={version} name={null} value={value} depth={0} defaultDepth={defaultDepth} mode={mode} />
      </div>
    </div>
  );
}
