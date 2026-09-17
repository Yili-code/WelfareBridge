"use client";

import { STATUS_LABEL, type BenefitCard, type MatchResult } from "./api";
import { deadlineInfo, localToday } from "./deadline";

export interface PrintJob {
  title: string;
  subtitle: string;
  sections: { heading: string; cards: BenefitCard[]; note?: string }[];
}

/**
 * 列印／存成 PDF 用的清單：畫面上看不到，列印時只印這一頁（見 welfare.css 的 @media print）。
 * 紙本點不了連結，所以官方網址直接印出來。
 */
export default function PrintSheet({ job, results, disclaimer }: { job: PrintJob | null; results: Record<string, MatchResult> | null; disclaimer: string }) {
  if (!job) return null;
  return <div className="print-sheet" aria-hidden="true">
    <h1>{job.title}</h1>
    <p className="print-sub">{job.subtitle}・列印日期 {localToday()}</p>
    {job.sections.map(section => <section key={section.heading}>
      <h2>{section.heading}（{section.cards.length} 項）</h2>
      <ol>
        {section.cards.map(card => {
          const result = results?.[card.id];
          const due = deadlineInfo(card);
          const apply = card.points.find(point => point.startsWith("申請："));
          return <li key={card.id}>
            <b>{card.title}</b>{result && <span className="print-status">［{STATUS_LABEL[result.status]}］</span>}
            <div>{card.agency}・{card.region}{card.price ? `・${card.price.unit} ${card.price.amount}` : ""}{due ? `・${due.label}` : ""}</div>
            {apply && <div>{apply}</div>}
            {result?.status === "maybe" && result.needs.length > 0 && <div>還需要確認：{result.needs.join("、")}</div>}
            {card.source_url && <div className="print-url">官方網址：{card.source_url}</div>}
            <div className="print-check">□ 已詢問　□ 已備齊文件　□ 已送出申請</div>
          </li>;
        })}
      </ol>
      {section.note && <p className="print-note">{section.note}</p>}
    </section>)}
    <p className="print-note">{disclaimer}</p>
  </div>;
}
