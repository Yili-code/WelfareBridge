"use client";

import { useEffect, useState } from "react";
import { DEMAND_THRESHOLD, DEMAND_TYPES, type Demand, type DemandStatus } from "@/lib/demand-types";

const FLOW: Record<DemandStatus, { label: string; note: string; badge: string }> = {
  collecting: { label: "蒐集中", note: `附議未達 ${DEMAND_THRESHOLD} 則`, badge: "none" },
  pending: { label: "待認領 A", note: "已達門檻，依附議數排序等待官方機關認領", badge: "maybe" },
  claimed: { label: "已認領 B", note: "官方機關已認領並回應處理中", badge: "info" },
  done: { label: "已實現 C", note: "已完成或已提供對應服務", badge: "yes" },
};

/** 每個瀏覽器一個隨機識別碼，用來避免重複附議；不含任何個人資料 */
function voterId() {
  try {
    let id = window.localStorage.getItem("wf.voter");
    if (!id) {
      id = typeof crypto.randomUUID === "function" ? crypto.randomUUID().replace(/-/g, "") : `v${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
      window.localStorage.setItem("wf.voter", id);
    }
    return id;
  } catch {
    return `v${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
  }
}

/** 從補助詳情「這項服務我這裡沒有」帶入標題時，父層會換 key 重新掛載，讓表單直接帶入 prefill。 */
export default function GapPanel({ prefill, defaultRegion, onToast }: { prefill: string; defaultRegion: string; onToast: (message: string) => void }) {
  const [items, setItems] = useState<Demand[] | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<DemandStatus | "all">("all");
  const [title, setTitle] = useState(prefill);
  const [type, setType] = useState(DEMAND_TYPES[0]);
  const [region, setRegion] = useState(defaultRegion);
  const [detail, setDetail] = useState("");
  const [sending, setSending] = useState(false);
  const [formError, setFormError] = useState("");

  const [version, setVersion] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/demands?voter=${encodeURIComponent(voterId())}`, { signal: controller.signal, cache: "no-store" })
      .then(res => (res.ok ? res.json() : Promise.reject(new Error())))
      .then((data: { items: Demand[] }) => { setItems(data.items); setError(""); })
      .catch(() => { if (!controller.signal.aborted) setError("暫時無法載入大家的訴求，請稍後再試。"); });
    return () => controller.abort();
  }, [version]);

  const submit = async () => {
    if (title.trim().length < 4) { setFormError("請用至少 4 個字描述「哪裡、缺什麼服務」。"); return; }
    setSending(true); setFormError("");
    try {
      const res = await fetch("/api/demands", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, type, region, detail, voter: voterId() }) });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(typeof data?.error === "string" ? data.error : "送出失敗，請再試一次。");
      setTitle(""); setDetail("");
      onToast(`訴求已送出，累積 ${DEMAND_THRESHOLD} 則附議後會進入待認領區`);
      setVersion(v => v + 1);
    } catch (e) { setFormError(e instanceof Error ? e.message : "送出失敗，請再試一次。"); }
    finally { setSending(false); }
  };

  const support = async (demand: Demand) => {
    try {
      const res = await fetch(`/api/demands/${encodeURIComponent(demand.id)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ voter: voterId() }) });
      if (!res.ok) throw new Error();
      const { item } = await res.json() as { item: Demand };
      setItems(list => list?.map(d => (d.id === item.id ? item : d)) ?? null);
      onToast(demand.status === "collecting" && item.status === "pending" ? `附議已達 ${DEMAND_THRESHOLD} 則，已送入待認領區` : "已送出附議，謝謝您的回報");
    } catch { onToast("附議沒有送出，請再試一次"); }
  };

  const count = (status: DemandStatus) => items?.filter(d => d.status === status).length ?? 0;
  const shown = (items ?? []).filter(d => filter === "all" || d.status === filter);

  return <section aria-label="訴求專區">
    <div className="notice">找不到需要的服務嗎？把它說出來。同類型訴求累積達 <b>{DEMAND_THRESHOLD}</b> 則附議即進入待認領區，依附議數排序等待官方機關認領。</div>
    <div className="flow">
      {(["pending", "claimed", "done"] as const).map(status => <div key={status} className="flowbox">
        <div className="h">{FLOW[status].label}<span className="n">{count(status)} 則</span></div>
        <p>{FLOW[status].note}</p>
      </div>)}
    </div>

    <div className="grid2 even">
      <div className="box">
        <h2>我要提出訴求</h2>
        <p className="hint">請描述「哪裡、缺什麼服務」，方便機關評估。這裡的內容會公開給所有人看，請不要填寫姓名、電話或病歷等個人資料。</p>
        <form onSubmit={e => { e.preventDefault(); void submit(); }} noValidate>
          <div className="field">
            <label htmlFor="wui-d-title">訴求標題</label>
            <input id="wui-d-title" value={title} maxLength={80} onChange={e => setTitle(e.target.value)} placeholder="例如：文山區缺少夜間長照接送" aria-invalid={!!formError} />
          </div>
          <div className="field">
            <label htmlFor="wui-d-type">服務類型</label>
            <select id="wui-d-type" value={type} onChange={e => setType(e.target.value)}>{DEMAND_TYPES.map(t => <option key={t}>{t}</option>)}</select>
          </div>
          <div className="field">
            <label htmlFor="wui-d-region">地區</label>
            <input id="wui-d-region" value={region} maxLength={40} onChange={e => setRegion(e.target.value)} placeholder="例如：臺北市文山區" />
          </div>
          <div className="field">
            <label htmlFor="wui-d-detail">詳細說明</label>
            <textarea id="wui-d-detail" value={detail} maxLength={1000} onChange={e => setDetail(e.target.value)} placeholder="遇到什麼困難？現在怎麼處理？" />
          </div>
          {formError && <p className="err" role="alert">{formError}</p>}
          <button className="btn" type="submit" disabled={sending}>{sending ? "送出中…" : "送出訴求"}</button>
        </form>
      </div>

      <div className="box">
        <div className="resbar" style={{ marginBottom: ".8rem" }}>
          <h2 style={{ margin: 0, fontSize: "1.3rem", fontWeight: 900 }}>大家的訴求</h2>
          <label className="sr" htmlFor="wui-g-filter">狀態篩選</label>
          <select id="wui-g-filter" value={filter} onChange={e => setFilter(e.target.value as DemandStatus | "all")}>
            <option value="all">全部狀態</option>
            {(Object.keys(FLOW) as DemandStatus[]).map(s => <option key={s} value={s}>{FLOW[s].label}</option>)}
          </select>
        </div>
        {error && <div className="alert" role="alert">{error}</div>}
        {!items && !error && <p className="loading" role="status">載入中…</p>}
        {items && shown.length === 0 && <div className="empty">
          <h3>{items.length ? "這個狀態目前沒有訴求" : "還沒有人提出訴求"}</h3>
          <p>{items.length ? "換個狀態看看，或提出您遇到的服務缺口。" : "您遇到的服務缺口，可以成為第一則訴求。"}</p>
        </div>}
        {shown.map(demand => {
          const flow = FLOW[demand.status];
          return <div key={demand.id} className="dcard">
            <div className="dtop"><h3>{demand.title}</h3><span className={`badge ${flow.badge}`}>{flow.label}</span></div>
            <div className="meta"><span className="tag svc">{demand.type}</span><span className="tag">{demand.region}</span>{demand.owner && <span className="tag aud">認領：{demand.owner}</span>}</div>
            {demand.detail && <p>{demand.detail}</p>}
            {demand.result && <p><b>處理結果：</b>{demand.result}</p>}
            <div className="bar" aria-hidden="true"><i style={{ width: `${Math.min(100, Math.round(demand.supports / DEMAND_THRESHOLD * 100))}%` }} /></div>
            <div className="dfoot">
              <span className="tag">附議 {demand.supports} / {DEMAND_THRESHOLD}</span>
              <span className="tag">{demand.created}</span>
              <button type="button" className="support" disabled={demand.voted} onClick={() => void support(demand)}>{demand.voted ? "✓ 已附議" : "＋ 我也需要"}</button>
            </div>
          </div>;
        })}
      </div>
    </div>
  </section>;
}
