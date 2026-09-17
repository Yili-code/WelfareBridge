"use client";

import { useMemo } from "react";
import { toggleSaved, type SavedBenefit } from "@/lib/store";
import type { BenefitCard, MatchResult } from "./api";
import BenefitCardView from "./BenefitCardView";
import { compareDeadline, deadlineInfo } from "./deadline";
import type { PrintJob } from "./PrintSheet";

/** 收藏清單：依截止日排列，7 天內截止的放最上面提醒；已經截止或下架的也列出來，方便移除 */
export default function SavedPanel({ saved, cards, results, onOpen, onToggleSave, onPrint, onBrowse }: {
  saved: SavedBenefit[];
  cards: BenefitCard[] | null;
  results: Record<string, MatchResult> | null;
  onOpen: (id: string) => void;
  onToggleSave: (card: BenefitCard) => void;
  onPrint: (job: PrintJob) => void;
  onBrowse: () => void;
}) {
  const { live, gone, urgent } = useMemo(() => {
    const byId = new Map((cards ?? []).map(card => [card.id, card]));
    const live = saved.map(s => byId.get(s.id)).filter((card): card is BenefitCard => !!card).sort((a, b) => compareDeadline(a, b) || a.title.localeCompare(b.title, "zh-Hant"));
    const gone = cards ? saved.filter(s => !byId.has(s.id)) : [];
    const urgent = live.filter(card => deadlineInfo(card)?.tone === "urgent");
    return { live, gone, urgent };
  }, [saved, cards]);

  return <section aria-label="收藏清單">
    <div className="resbar">
      <h2 className="group-title" style={{ margin: 0 }}>收藏清單<span className="n">{saved.length}</span></h2>
      {live.length > 0 && <button type="button" className="btn sec" style={{ marginLeft: "auto" }} onClick={() => onPrint({ title: "我收藏的補助", subtitle: "收藏清單", sections: [{ heading: "收藏的補助", cards: live }] })}>🖨 列印／存成 PDF</button>}
    </div>
    <p className="hint">收藏存在這台裝置的瀏覽器，所有資料卡共用。有截止日的補助，會在截止前 7 天提醒您。</p>

    {urgent.length > 0 && <div className="notice warn" role="status">
      <b>⏰ 即將截止：</b>{urgent.map(card => `「${card.title}」${deadlineInfo(card)!.label}`).join("；")}。請盡早準備文件、向承辦單位確認。
    </div>}

    {!saved.length && <div className="empty">
      <h3>還沒有收藏的補助</h3>
      <p>在補助卡片或詳情按「☆ 收藏」，就會出現在這裡，方便之後比較、列印和注意截止日。</p>
      <div className="actions" style={{ justifyContent: "center" }}><button type="button" className="btn" onClick={onBrowse}>去查詢補助</button></div>
    </div>}
    {!cards && saved.length > 0 && <p className="loading" role="status">載入中…</p>}

    <div className="cards">{live.map(card => <BenefitCardView key={card.id} card={card} result={results?.[card.id]} saved onOpen={onOpen} onToggleSave={onToggleSave} />)}</div>

    {gone.length > 0 && <div className="box" style={{ marginTop: "1.3rem" }}>
      <h3 style={{ marginTop: 0 }}>已經截止或下架</h3>
      <ul className="gone">{gone.map(item => <li key={item.id}>
        <span>{item.title}</span>
        <button type="button" className="rm" onClick={() => toggleSaved(item)}>移除</button>
      </li>)}</ul>
    </div>}
  </section>;
}
