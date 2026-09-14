export function Pagination({ page, pageSize, total, onChange }: { page: number; pageSize: number; total: number; onChange: (page: number) => void }) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(total, page * pageSize);

  const numbers: number[] = [];
  const start = Math.max(1, page - 2);
  const end = Math.min(pages, start + 4);
  for (let i = start; i <= end; i += 1) numbers.push(i);

  const btn = 'rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40';

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
      <div>
        顯示第 {from}–{to} 筆，共 {total} 筆
      </div>
      <div className="flex items-center gap-1">
        <button type="button" className={btn} disabled={page <= 1} onClick={() => onChange(1)}>
          «
        </button>
        <button type="button" className={btn} disabled={page <= 1} onClick={() => onChange(page - 1)}>
          上一頁
        </button>
        {numbers.map((n) => (
          <button key={n} type="button" onClick={() => onChange(n)} className={`${btn} ${n === page ? 'border-blue-500 bg-blue-50 font-semibold text-blue-700' : ''}`}>
            {n}
          </button>
        ))}
        <button type="button" className={btn} disabled={page >= pages} onClick={() => onChange(page + 1)}>
          下一頁
        </button>
        <button type="button" className={btn} disabled={page >= pages} onClick={() => onChange(pages)}>
          »
        </button>
      </div>
    </div>
  );
}
