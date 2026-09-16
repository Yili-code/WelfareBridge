"use client";

import { useEffect, useState } from "react";
import { DEMAND_THRESHOLD, type Demand } from "@/lib/demand-types";

const STATUS_LABEL: Record<Demand["status"], string> = { collecting: "蒐集中", pending: "待認領", claimed: "已認領", done: "已實現" };

/** 後台：公開訴求的認領與處理結果（前台訴求專區的 A 待認領 → B 已認領 → C 已實現） */
export default function DemandsAdmin({ password }: { password: string }) {
  const [items, setItems] = useState<Demand[] | null>(null);
  const [error, setError] = useState("");
  const [version, setVersion] = useState(0);
  const [drafts, setDrafts] = useState<Record<string, { owner: string; result: string }>>({});

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/demands", { signal: controller.signal, cache: "no-store" })
      .then(res => (res.ok ? res.json() : Promise.reject(new Error())))
      .then((data: { items: Demand[] }) => { setItems(data.items); setError(""); })
      .catch(() => { if (!controller.signal.aborted) setError("訴求讀取失敗。"); });
    return () => controller.abort();
  }, [version]);

  const update = async (demand: Demand, status: "open" | "claimed" | "done") => {
    const draft = drafts[demand.id] ?? { owner: demand.owner, result: demand.result };
    try {
      setError("");
      const res = await fetch(`/api/demands/${encodeURIComponent(demand.id)}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${password}` }, body: JSON.stringify({ status, ...draft }) });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(typeof data?.error === "string" ? data.error : "更新失敗");
      setVersion(v => v + 1);
    } catch (e) { setError(e instanceof Error ? e.message : "更新失敗"); }
  };

  if (!password) return <p className="mt-6 text-sm text-ink-400">請輸入後台密碼後管理訴求。</p>;
  return <section className="mt-6 space-y-3">
    <p className="text-sm text-ink-400">附議達 {DEMAND_THRESHOLD} 則的訴求會進入待認領。認領時請填寫認領機關；實現後填寫處理結果，前台會公開顯示。</p>
    {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
    {!items ? <p className="text-sm text-ink-400">讀取中…</p> : items.length === 0 ? <p className="text-sm text-ink-400">還沒有訴求。</p> : items.map(demand => {
      const draft = drafts[demand.id] ?? { owner: demand.owner, result: demand.result };
      const set = (patch: Partial<typeof draft>) => setDrafts(all => ({ ...all, [demand.id]: { ...draft, ...patch } }));
      return <article key={demand.id} className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="font-medium">{demand.title}</h3>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs">{STATUS_LABEL[demand.status]}</span>
          <span className="text-xs text-ink-400">{demand.type}・{demand.region}・附議 {demand.supports}・{demand.created}</span>
        </div>
        {demand.detail && <p className="mt-2 text-sm text-ink-600">{demand.detail}</p>}
        <div className="mt-3 grid gap-2 md:grid-cols-2">
          <label className="text-xs">認領機關<input className="mt-1 w-full rounded border px-2 py-1.5 text-sm" value={draft.owner} maxLength={80} onChange={e => set({ owner: e.target.value })} /></label>
          <label className="text-xs">處理結果<input className="mt-1 w-full rounded border px-2 py-1.5 text-sm" value={draft.result} maxLength={500} onChange={e => set({ result: e.target.value })} /></label>
        </div>
        <div className="mt-3 flex flex-wrap gap-2 text-sm">
          <button type="button" className="rounded border px-3 py-1" onClick={() => void update(demand, "open")}>設為蒐集中／待認領</button>
          <button type="button" className="rounded border px-3 py-1" onClick={() => void update(demand, "claimed")}>設為已認領</button>
          <button type="button" className="rounded border px-3 py-1" onClick={() => void update(demand, "done")}>設為已實現</button>
        </div>
      </article>;
    })}
  </section>;
}
