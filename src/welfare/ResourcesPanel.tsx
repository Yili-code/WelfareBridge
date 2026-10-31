"use client";

import { useEffect, useState } from "react";
import { fetchResources, type ResourcesResponse } from "./api";

/** 附近教育資源：教育部開放資料（政府資料開放平臺）裡的服務據點，依縣市與類型查詢，並標示資料集出處與授權 */
export default function ResourcesPanel({ defaultCity }: { defaultCity: string }) {
  const [city, setCity] = useState(defaultCity);
  const [kind, setKind] = useState("");
  const [data, setData] = useState<{ key: string; value?: ResourcesResponse; error?: string } | null>(null);
  const key = `${city}|${kind}`;

  useEffect(() => { setCity(defaultCity); }, [defaultCity]);
  useEffect(() => {
    const controller = new AbortController();
    fetchResources(city, kind, controller.signal)
      .then(value => setData({ key, value }))
      .catch(error => { if (!controller.signal.aborted) setData({ key, error: error instanceof Error ? error.message : "載入失敗，請再試一次。" }); });
    return () => controller.abort();
  }, [city, kind, key]);

  const current = data && data.key === key ? data : null;
  const value = data?.value;

  return <section aria-label="附近教育資源">
    <div className="resbar">
      <h2 className="group-title" style={{ margin: 0 }}>附近教育資源<span className="n">{current?.value?.total ?? "…"}</span></h2>
      <label className="sr" htmlFor="wui-res-city">縣市</label>
      <select id="wui-res-city" value={city} onChange={event => setCity(event.target.value)}>
        <option value="">全國</option>
        {(value?.cities ?? []).map(name => <option key={name} value={name}>{name}</option>)}
      </select>
    </div>
    <p className="hint">這些據點來自教育部開放資料，包含長者學習、新住民學習與兒童課後照顧。補助資格以官方公告為準，前往前請先電話確認服務時間。</p>

    <div className="chips" role="group" aria-label="服務類型" style={{ display: "flex", gap: ".5rem", flexWrap: "wrap", margin: "0 0 1rem" }}>
      <button type="button" className="chip" aria-pressed={kind === ""} onClick={() => setKind("")}>全部</button>
      {Object.entries(value?.kinds ?? {}).map(([name, count]) => <button key={name} type="button" className="chip" aria-pressed={kind === name} onClick={() => setKind(name)}>{name}（{count}）</button>)}
    </div>

    {!current && <p className="loading" role="status">正在載入…</p>}
    {current?.error && <div className="alert" role="alert">{current.error}</div>}
    {current?.value && current.value.items.length === 0 && <div className="empty"><h3>這個縣市目前沒有這類據點</h3><p>可以改選「全國」或其他服務類型。</p></div>}
    {current?.value && current.value.items.length > 0 && <ul className="res-list">
      {current.value.items.map(item => <li key={item.id} className="res-item">
        <span className="res-kind">{item.kind}</span>
        <h3>{item.name}</h3>
        <p>{[item.city, item.district].filter(Boolean).join(" ")}{item.address ? `｜${item.address}` : ""}</p>
        {item.phone && <p>電話：<a href={`tel:${item.phone.replace(/[^\d+]/g, "")}`}>{item.phone}</a></p>}
        {item.operator && <p className="res-op">承辦單位：{item.operator}</p>}
      </li>)}
    </ul>}
    {current?.value && current.value.total > current.value.items.length && <p className="hint">只顯示前 {current.value.items.length} 筆，共 {current.value.total} 筆；可以改選縣市或類型縮小範圍。</p>}

    <div className="notice" role="note">
      <b>資料來源：政府資料開放平臺（教育部）</b>
      <ul style={{ margin: ".4rem 0 0", paddingLeft: "1.2rem" }}>
        {(value?.datasets ?? []).map(dataset => <li key={dataset.nid}>
          <a href={dataset.url} target="_blank" rel="noreferrer">{dataset.title}</a>（{dataset.agency}，{dataset.count} 筆，{dataset.license}）
        </li>)}
      </ul>
    </div>
  </section>;
}
