"use client";

import { useMemo, useState } from "react";
import { REGIONS } from "@/lib/options";
import { QUESTIONS, ageLabel } from "@/lib/questionnaire";
import { removeProfile, setActiveProfileId, updateProfile } from "@/lib/store";
import type { AssistantAttribute, Profile } from "@/lib/types";
import { STATUS_LABEL, type BenefitCard, type MatchResponse } from "./api";
import { editLearned, needDomains, rankForProfile } from "./assistant-memory";
import BenefitCardView from "./BenefitCardView";
import type { PrintJob } from "./PrintSheet";
import QuickQuestions from "./QuickQuestions";

const PAGE = 10;
// 不用網址 #錨點：網址 hash 用來記住目前分頁
const scrollToGroup = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
const FACT_LABELS: Record<string, string> = { needs: "想找的補助", education: "在學狀態", economy: "家庭經濟", identity: "特定身分", employment: "工作狀態", housing: "居住方式", support: "需要的支援", benefits: "已領或申請中" };

export function ProfileInvite({ onCreate }: { onCreate: () => void }) {
  return <section className="invite" aria-labelledby="wui-invite-title">
    <div>
      <h2 id="wui-invite-title">花 2 分鐘建立資料卡，看看您可能符合哪些補助</h2>
      <p>回答 10 個簡單問題（只有 3 題必填），每項補助都會標示您是否可能符合，也會提醒還缺哪些資料。可以替家人分別建立。</p>
    </div>
    <button type="button" className="btn" onClick={onCreate}>開始建立資料卡</button>
  </section>;
}

function LearnedList({ profile, onSaved }: { profile: Profile; onSaved: (message: string) => void }) {
  const entries = Object.entries(profile.assistantAttributes ?? {});
  if (!entries.length) return null;
  const save = (next: Record<string, AssistantAttribute>, message: string) => { updateProfile(profile.id, { assistantAttributes: next }); onSaved(message); };
  return <details className="learned-box">
    <summary>補充的資料（{entries.length} 項，來自小幫手或快速回答）</summary>
    <p className="hint">比對時會優先採用這些回答。說錯了可以直接修改或刪除。</p>
    <ul className="learned">
      {entries.map(([id, entry]) => {
        const current = entry.value === null ? "" : Array.isArray(entry.value) ? entry.value[0] ?? "" : String(entry.value);
        const change = (raw: string) => save({ ...profile.assistantAttributes, [id]: editLearned(entry, raw) }, `已更新「${entry.label}」，正在重新比對`);
        return <li key={id}>
          <span className="name">{entry.label}{entry.source === "parsed" && <small>從對話內容判讀，請確認</small>}</span>
          {entry.type === "boolean" ? <select aria-label={entry.label} value={current} onChange={e => change(e.target.value)}><option value="">不確定</option><option value="true">是</option><option value="false">否</option></select>
            : entry.type === "number" ? <input aria-label={entry.label} type="number" defaultValue={current} onBlur={e => { if (e.target.value !== current) change(e.target.value); }} />
            : entry.type === "city" ? <select aria-label={entry.label} value={current} onChange={e => change(e.target.value)}><option value="">不確定</option>{REGIONS.map(c => <option key={c}>{c}</option>)}</select>
            : entry.options?.length ? <select aria-label={entry.label} value={current} onChange={e => change(e.target.value)}><option value="">不確定</option>{entry.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</select>
            : <span>{entry.valueLabel}</span>}
          <button type="button" className="rm" aria-label={`刪除「${entry.label}」`} onClick={() => { const next = { ...profile.assistantAttributes }; delete next[id]; save(next, `已刪除「${entry.label}」，正在重新比對`); }}>✕</button>
        </li>;
      })}
    </ul>
  </details>;
}

function Facts({ profile }: { profile: Profile }) {
  const answers = profile.screening ?? {};
  const residence = answers.residence?.[0];
  const place = [profile.region && `戶籍 ${profile.region}`, profile.currentRegion && profile.currentRegion !== profile.region && `居住 ${profile.currentRegion}`].filter(Boolean).join("、");
  const rows: [string, string][] = [
    ["想找的補助", (answers.needs ?? []).join("、")],
    ["年齡", ageLabel(profile)],
    ["戶籍與居住", [place, residence].filter(Boolean).join("；")],
    ...QUESTIONS.slice(3).map(q => [FACT_LABELS[q.key] ?? q.title, (answers[q.key] ?? []).join("、")] as [string, string]),
  ];
  return <dl className="facts">{rows.filter(([, value]) => value).map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>;
}

function Group({ id, title, hint, cards, match, savedIds, onOpen, onToggleSave }: { id: string; title: string; hint?: string; cards: BenefitCard[]; match: MatchResponse; savedIds: Set<string>; onOpen: (id: string) => void; onToggleSave: (card: BenefitCard) => void }) {
  const [shown, setShown] = useState(PAGE);
  if (!cards.length) return null;
  return <section className="group" aria-labelledby={id}>
    <h2 id={id} className="group-title">{title}<span className="n">{cards.length}</span></h2>
    {hint && <p className="hint">{hint}</p>}
    <div className="cards">{cards.slice(0, shown).map(card => <BenefitCardView key={card.id} card={card} result={match.results[card.id]} saved={savedIds.has(card.id)} onOpen={onOpen} onToggleSave={onToggleSave} />)}</div>
    {cards.length > shown && <div className="loadmore"><button type="button" className="btn sec" onClick={() => setShown(n => n + PAGE)}>顯示更多（還有 {cards.length - shown} 項）</button></div>}
  </section>;
}

export default function ProfilePanel({ profiles, active, cards, match, matching, matchError, savedIds, onSaved, onOpen, onAskAssistant, onBrowseAll, onEdit, onPrint, onToggleSave }: {
  profiles: Profile[];
  active: Profile | null;
  cards: BenefitCard[] | null;
  match: MatchResponse | null;
  matching: boolean;
  matchError: string;
  savedIds: Set<string>;
  onSaved: (message: string) => void;
  onOpen: (id: string) => void;
  onAskAssistant: () => void;
  onBrowseAll: () => void;
  /** 開啟資料卡小視窗；null＝新增 */
  onEdit: (profile: Profile | null) => void;
  onPrint: (job: PrintJob) => void;
  onToggleSave: (card: BenefitCard) => void;
}) {
  const domains = useMemo(() => needDomains(active), [active]);
  const grouped = useMemo(() => {
    if (!cards || !match) return null;
    const yes = rankForProfile(cards.filter(c => match.results[c.id]?.status === "yes"), match.results, domains);
    const maybe = rankForProfile(cards.filter(c => match.results[c.id]?.status === "maybe"), match.results, domains);
    return { yes, maybe };
  }, [cards, match, domains]);

  const print = () => {
    if (!active || !grouped) return;
    const maybe = grouped.maybe.slice(0, 20);
    onPrint({
      title: `${active.nickname}可能符合的補助`,
      subtitle: "依資料卡初步比對，實際資格以主辦機關審核為準",
      sections: [
        { heading: STATUS_LABEL.yes, cards: grouped.yes },
        { heading: "需要進一步確認", cards: maybe, note: grouped.maybe.length > maybe.length ? `另有 ${grouped.maybe.length - maybe.length} 項需要進一步確認，請上網查看。` : undefined },
      ],
    });
  };

  return <section aria-label="我的資料卡">
    <div className="people" role="group" aria-label="切換家人的資料卡">
      <span className="lab">資料卡</span>
      {profiles.map(person => <span key={person.id} className="person" aria-current={person.id === active?.id}>
        <button type="button" onClick={() => setActiveProfileId(person.id)}>{person.nickname}</button>
      </span>)}
      <button type="button" className="chip" onClick={() => onEdit(null)}>{profiles.length ? "＋ 新增家人" : "＋ 建立資料卡"}</button>
    </div>

    {!active ? <ProfileInvite onCreate={() => onEdit(null)} /> : <>
      <div className="box summary">
        <div className="summary-head">
          <h2>{active.nickname}的資料卡</h2>
          <div className="actions">
            <button type="button" className="btn" onClick={() => onEdit(active)}>編輯資料卡</button>
            <button type="button" className="btn sec" onClick={() => { if (window.confirm(`確定要刪除「${active.nickname}」的資料卡嗎？`)) { removeProfile(active.id); onSaved("已刪除資料卡"); } }}>刪除</button>
          </div>
        </div>
        <Facts profile={active} />
        <LearnedList profile={active} onSaved={onSaved} />
      </div>

      {matchError ? <div className="alert" role="alert">{matchError}</div>
        : !grouped || !match ? <p className="loading" role="status">正在比對 {cards?.length ?? ""} 項補助…</p>
        : <>
          <div className="result-bar" aria-live="polite">
            <div className="stats">
              <button type="button" className="stat yes" onClick={() => scrollToGroup("wui-group-yes")}><b>{match.counts.yes}</b><span>{STATUS_LABEL.yes}</span></button>
              <button type="button" className="stat maybe" onClick={() => scrollToGroup("wui-group-maybe")}><b>{match.counts.maybe}</b><span>需進一步確認</span></button>
              <div className="stat no"><b>{match.counts.no}</b><span>{STATUS_LABEL.no}</span></div>
            </div>
            <div className="actions">
              <button type="button" className="btn sec" onClick={print}>🖨 列印／存成 PDF</button>
              {match.counts.maybe > 0 && <button type="button" className="btn sec" onClick={onAskAssistant}>💬 請小幫手幫我補資料</button>}
            </div>
            {matching && <p className="hint" role="status">資料已更新，正在重新比對…</p>}
          </div>

          <QuickQuestions profile={active} questions={match.questions ?? []} onSaved={onSaved} />

          <Group id="wui-group-yes" title="可能符合" cards={grouped.yes} match={match} savedIds={savedIds} onOpen={onOpen} onToggleSave={onToggleSave}
            hint="主要資格（戶籍、年齡、身分、學制等）都已比對相符。申請前仍請以官方公告為準。" />
          <Group id="wui-group-maybe" title="需要進一步確認" cards={grouped.maybe} match={match} savedIds={savedIds} onOpen={onOpen} onToggleSave={onToggleSave}
            hint="沒有明確不符，但還缺一些資料。卡片上會寫要補充什麼，補完就能確認。" />
          {!grouped.yes.length && !grouped.maybe.length && <div className="empty">
            <h3>目前沒有可能符合的補助</h3>
            <p>可以編輯資料卡確認填寫的條件，或到「訴求專區」說出您需要的服務。</p>
          </div>}
          <p className="hint">另有 {match.counts.no} 項目前較不符合。<button type="button" className="linklike" onClick={onBrowseAll}>到「查詢補助與服務」查看全部補助</button></p>
        </>}
    </>}
  </section>;
}
