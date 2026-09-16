"use client";

import { useEffect, useRef, useState } from "react";
import { fetchBenefit, STATUS_LABEL, type BenefitDetail, type MatchResult } from "./api";

const ICON: Record<string, string> = { satisfied: "✓", unknown: "?", unsure: "!", violated: "✕" };

export default function DetailDrawer({ id, result, hasProfile, onClose, onGoProfile, onGap, onAskAssistant }: {
  id: string | null;
  result: MatchResult | undefined;
  hasProfile: boolean;
  onClose: () => void;
  onGoProfile: () => void;
  onGap: (title: string) => void;
  onAskAssistant: () => void;
}) {
  const [detail, setDetail] = useState<{ id: string; data?: BenefitDetail; error?: string } | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    const controller = new AbortController();
    fetchBenefit(id, controller.signal)
      .then(data => setDetail({ id, data }))
      .catch(error => { if (!controller.signal.aborted) setDetail({ id, error: error instanceof Error ? error.message : "載入失敗，請再試一次。" }); });
    bodyRef.current?.scrollTo({ top: 0 });
    closeRef.current?.focus({ preventScroll: true });
    return () => controller.abort();
  }, [id]);

  useEffect(() => {
    if (!id) return;
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => { window.removeEventListener("keydown", onKey); document.body.style.overflow = previous; };
  }, [id, onClose]);

  const current = detail && detail.id === id ? detail : null;
  const data = current?.data;

  return <>
    <div className={`scrim${id ? " on" : ""}`} onClick={onClose} aria-hidden="true" />
    <aside className={`drawer${id ? " on" : ""}`} role="dialog" aria-modal="true" aria-labelledby="wui-detail-title" aria-hidden={!id}>
      <div className="drawer-head">
        <h2 id="wui-detail-title">{data?.title ?? (current?.error ? "無法載入" : "補助詳情")}</h2>
        <button ref={closeRef} className="x" type="button" aria-label="關閉" onClick={onClose}>✕</button>
      </div>
      <div className="drawer-body" ref={bodyRef}>
        {!current && id && <p className="loading" role="status">正在載入補助內容…</p>}
        {current?.error && <div className="alert" role="alert">{current.error}</div>}
        {data && <>
          <div className="sec">
            <h3>資格初步比對</h3>
            <div className="matchbox">
              {hasProfile && result ? <>
                <span className={`badge ${result.status}`}>{STATUS_LABEL[result.status]}</span>
                <ul className="reasons">{result.reasons.map(reason => <li key={reason.text} className={reason.state}><span className="ic" aria-hidden="true">{ICON[reason.state]}</span><span>{reason.text}</span></li>)}</ul>
                {result.needs.length > 0 && <>
                  <p className="lead">補充這些資料就能確認：{result.needs.join("、")}</p>
                  <div className="actions"><button type="button" className="btn sm" onClick={onAskAssistant}>請小幫手問我這幾題</button><button type="button" className="btn sm sec" onClick={onGoProfile}>到資料卡填寫</button></div>
                </>}
              </> : hasProfile ? <p role="status">正在比對您的資料卡…</p> : <>
                <p>建立資料卡後，這裡會自動比對您是否可能符合資格。</p>
                <div className="actions"><button type="button" className="btn sm" onClick={onGoProfile}>建立我的資料卡</button></div>
              </>}
            </div>
          </div>

          {data.price && <div className="sec">
            <h3>補助金額</h3>
            <div className="pricebox">
              <div><span className="unit">{data.price.unit}</span><b>{data.price.amount}</b>{data.price.note && <small>{data.price.note}</small>}</div>
              {data.price.type === "soft" && <small>官方公告沒有列出明確金額，實際補助由主辦機關核定。</small>}
            </div>
          </div>}

          <div className="sec">
            <h3>申請資格</h3>
            {data.eligibility.main.length > 0 && <><p className="lead">主要條件：</p><ul className="tick">{data.eligibility.main.map(t => <li key={t}>{t}</li>)}</ul></>}
            {data.eligibility.summary && <><p className="lead">適用對象：</p><p>{data.eligibility.summary}</p></>}
            {data.eligibility.excluded.length > 0 && <><p className="lead">要注意：</p><ul className="tick warn">{data.eligibility.excluded.map(t => <li key={t}>{t}</li>)}</ul></>}
            {!data.eligibility.main.length && !data.eligibility.summary && <p className="none">官方公告沒有明確的資格條件，建議直接查看官方頁面或洽詢承辦單位。</p>}
            {data.eligibility.official.length > 0 && <details className="raw"><summary>查看官方公告的資格條文（節錄）</summary><ul>{data.eligibility.official.map(t => <li key={t}>{t}</li>)}</ul></details>}
          </div>

          {data.content.length > 0 && <div className="sec"><h3>補助內容</h3>{data.content.map(t => <p key={t}>{t}</p>)}</div>}

          <div className="sec">
            <h3>基本資訊</h3>
            <dl className="kv">
              <dt>主辦機關</dt><dd>{data.agency || "—"}</dd>
              <dt>服務地區</dt><dd>{data.region}</dd>
              <dt>補助領域</dt><dd>{data.domain}</dd>
              <dt>補助類型</dt><dd>{data.service_type}</dd>
              <dt>適用對象</dt><dd>{data.audiences.join("、")}</dd>
              <dt>申請期間</dt><dd>{data.application.period || "請見官方公告"}</dd>
              {data.updated && <><dt>官方公告</dt><dd>{data.updated}</dd></>}
            </dl>
          </div>

          <div className="sec">
            <h3>申請方式</h3>
            {data.application.channel || data.application.method ? <p>{[data.application.channel, data.application.method].filter(Boolean).join("：")}</p> : <p className="none">官方公告沒有寫明申請方式，建議點下方「前往官方頁面」查看。</p>}
            {data.application.documents.length > 0 && <><p className="lead">應備文件：</p><ul className="tick plain">{data.application.documents.map(t => <li key={t}>{t}</li>)}</ul></>}
            {Object.keys(data.application.contact).length > 0 && <><p className="lead">聯絡方式：</p><p>{[data.application.contact.department, data.application.contact.phone, data.application.contact.email].filter(Boolean).join("　")}</p></>}
          </div>

          {data.attachments.length > 0 && <div className="sec">
            <h3>相關附件（{data.attachments.length}）</h3>
            {data.attachments.map(file => <a key={file.url} className="att" href={file.url} target="_blank" rel="noopener noreferrer">📄 {file.name}{file.type && <span className="file">{file.type}</span>}</a>)}
          </div>}
        </>}
      </div>
      <div className="drawer-foot">
        {data?.source_url && <a className="btn" href={data.source_url} target="_blank" rel="noopener noreferrer">前往官方頁面 ↗</a>}
        {data && <button className="btn sec" type="button" onClick={() => onGap(`「${data.title}」在我的地區找不到或不夠用`)}>這項服務我這裡沒有</button>}
      </div>
    </aside>
  </>;
}
