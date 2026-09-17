"use client";

import type { MouseEvent } from "react";
import { STATUS_LABEL, type BenefitCard, type MatchResult } from "./api";
import { deadlineInfo } from "./deadline";

export function PriceBlock({ card }: { card: BenefitCard }) {
  if (!card.price) return null;
  return <div className={`price${card.price.type === "soft" ? " soft" : ""}`}>
    <span className="unit">{card.price.unit}</span>
    <b>{card.price.amount}</b>
    {card.price.note && <small>{card.price.note}</small>}
  </div>;
}

export function DeadlineTag({ card }: { card: { deadline: string; rolling: boolean } }) {
  const info = deadlineInfo(card);
  if (!info) return null;
  return <span className={`tag due ${info.tone}`}>{info.tone === "urgent" ? "⏰ " : ""}{info.label}</span>;
}

/**
 * 補助卡片（查詢頁、資料卡結果、收藏清單共用）。
 * 整張卡片可以點開詳情；鍵盤使用者用卡片裡的「查看詳情」與「收藏」按鈕。
 */
export default function BenefitCardView({ card, result, saved, onOpen, onToggleSave }: {
  card: BenefitCard;
  result?: MatchResult;
  saved: boolean;
  onOpen: (id: string) => void;
  onToggleSave: (card: BenefitCard) => void;
}) {
  const open = (event: MouseEvent) => {
    if ((event.target as HTMLElement).closest("button, a")) return;
    onOpen(card.id);
  };
  return <article className="card" onClick={open} aria-labelledby={`wui-card-${card.id}`}>
    <div className="card-main">
      <div className="card-head">
        <h3 id={`wui-card-${card.id}`}>{card.title}</h3>
        {result && <span className={`badge ${result.status}`}>{STATUS_LABEL[result.status]}</span>}
      </div>
      <div className="meta">
        <span className="tag svc">{card.service_type}</span>
        {card.audiences.slice(0, 3).map(a => <span key={a} className="tag aud">{a}</span>)}
        <span className="tag">{card.region}</span>
        <DeadlineTag card={card} />
      </div>
      <ul className="points">{card.points.map(point => <li key={point}>{point}</li>)}</ul>
      {result?.status === "maybe" && result.needs.length > 0 && <div className="needs">補充「{result.needs.slice(0, 3).join("、")}」就能確認</div>}
      <div className="card-agency">{card.agency}{card.updated ? `　官方公告 ${card.updated}` : ""}</div>
    </div>
    <div className={`card-side${card.price ? (card.price.type === "soft" ? " has-soft" : " has-price") : ""}`}>
      <PriceBlock card={card} />
      <div className="card-actions">
        <button type="button" className="btn sm" onClick={() => onOpen(card.id)}>查看詳情 →</button>
        <button type="button" className={`save${saved ? " on" : ""}`} aria-pressed={saved} onClick={() => onToggleSave(card)}>{saved ? "★ 已收藏" : "☆ 收藏"}</button>
      </div>
    </div>
  </article>;
}
