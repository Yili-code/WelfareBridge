"use client";

import { useMemo, useState } from "react";
import { REGIONS, RELATIONS } from "@/lib/options";
import { AGE_RANGES, QUESTIONS, profileTags, selectAnswer } from "@/lib/questionnaire";
import { addProfile, removeProfile, setActiveProfileId, updateProfile } from "@/lib/store";
import type { AssistantAttribute, Profile, Relation } from "@/lib/types";
import { STATUS_LABEL, type BenefitCard, type MatchResponse } from "./api";
import { editLearned, needDomains, rankForProfile } from "./assistant-memory";

type Answers = Record<string, string[]>;
const REQUIRED = ["needs", "age", "residence"];

function initialAnswers(profile: Profile | null): Answers {
  const saved: Answers = { ...(profile?.screening ?? {}) };
  if (profile && !saved.age && profile.age != null) {
    const index = AGE_RANGES.findIndex(([min, max]) => profile.age! >= min && profile.age! <= max);
    if (index >= 0) saved.age = [QUESTIONS[1].options[index]];
  }
  return saved;
}

function ProfileForm({ profile, onSaved, onCancel }: { profile: Profile | null; onSaved: (message: string) => void; onCancel?: () => void }) {
  const [answers, setAnswers] = useState<Answers>(() => initialAnswers(profile));
  const [relation, setRelation] = useState<Relation>(profile?.relation ?? "self");
  const [nickname, setNickname] = useState(profile?.nickname ?? "");
  const [exactAge, setExactAge] = useState(profile?.age == null ? "" : String(profile.age));
  const [region, setRegion] = useState(profile?.region ?? "");
  const [currentRegion, setCurrentRegion] = useState(profile?.currentRegion ?? "");
  const [tried, setTried] = useState(false);

  const residence = answers.residence?.[0];
  const sameCity = QUESTIONS[2].options.slice(0, 2).includes(residence);
  const noHousehold = residence === QUESTIONS[2].options[3];
  const ageRange = AGE_RANGES[QUESTIONS[1].options.indexOf(answers.age?.[0])];
  const ageValid = exactAge === "" || (Number.isInteger(Number(exactAge)) && ageRange && Number(exactAge) >= ageRange[0] && Number(exactAge) <= ageRange[1]);
  const missing = REQUIRED.filter(key => !answers[key]?.length);
  const cityMissing = sameCity && !region;
  const valid = !missing.length && ageValid && !cityMissing;

  const choose = (key: string, value: string) => {
    const question = QUESTIONS.find(q => q.key === key)!;
    setAnswers(previous => ({ ...previous, [key]: selectAnswer(previous[key] ?? [], question, value) }));
    if (key === "age") setExactAge("");
    if (key === "residence") { setRegion(""); setCurrentRegion(""); }
  };

  const save = () => {
    setTried(true);
    if (!valid) return;
    const draft = {
      nickname: nickname.trim() || RELATIONS.find(r => r.value === relation)!.label,
      relation,
      region: noHousehold ? "" : region,
      district: profile?.region === region && !noHousehold ? profile.district : undefined,
      currentRegion: sameCity ? region : currentRegion,
      age: exactAge === "" ? null : Number(exactAge),
      screening: answers,
      assistantAttributes: profile?.assistantAttributes,
      ...profileTags(answers),
    };
    if (profile) { updateProfile(profile.id, draft); onSaved("資料卡已更新，正在重新比對補助"); }
    else { const created = addProfile(draft); setActiveProfileId(created.id); onSaved("資料卡已儲存，正在為您比對補助"); }
  };

  const citySelect = (id: string, label: string, value: string, change: (value: string) => void) => <div className="field">
    <label htmlFor={id}>{label}</label>
    <select id={id} value={value} onChange={e => change(e.target.value)} aria-invalid={tried && id.endsWith("home") && cityMissing}>
      <option value="">不確定／尚未填寫</option>
      {REGIONS.map(city => <option key={city}>{city}</option>)}
    </select>
    {tried && id.endsWith("home") && cityMissing && <p className="err">請選擇戶籍與居住的縣市。</p>}
  </div>;

  return <form onSubmit={e => { e.preventDefault(); save(); }} noValidate>
    <div className="row2">
      <div className="field">
        <label htmlFor="wui-relation">這張資料卡是為誰建立</label>
        <select id="wui-relation" value={relation} onChange={e => setRelation(e.target.value as Relation)}>
          {RELATIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
      </div>
      <div className="field">
        <label htmlFor="wui-nickname">稱呼（選填）</label>
        <input id="wui-nickname" value={nickname} maxLength={20} onChange={e => setNickname(e.target.value)} placeholder="例如：媽媽" />
      </div>
    </div>

    {QUESTIONS.map((question, index) => {
      const selected = answers[question.key] ?? [];
      const required = REQUIRED.includes(question.key);
      return <fieldset key={question.key} className="field" style={{ border: 0, padding: 0, margin: "0 0 1.1rem" }}>
        <legend className="flabel">{index + 1}. {question.title}{required ? "（必填）" : "（選填）"}{question.multi ? "・可複選" : ""}</legend>
        <p className="why">{question.why}</p>
        <div className="checks">
          {question.options.map(option => <label key={option}>
            <input type={question.multi ? "checkbox" : "radio"} name={`wui-${question.key}`} checked={selected.includes(option)} onChange={() => choose(question.key, option)} />
            {option}
          </label>)}
        </div>
        {tried && required && !selected.length && <p className="err">請選擇一項。</p>}
        {question.key === "age" && selected.length > 0 && <div className="field" style={{ marginTop: ".7rem" }}>
          <label htmlFor="wui-age">實際年齡（選填，填了比對會更準）</label>
          <input id="wui-age" type="number" inputMode="numeric" min={0} max={120} value={exactAge} onChange={e => setExactAge(e.target.value)} aria-invalid={!ageValid} placeholder="例如：72" />
          {!ageValid && <p className="err">請填入所選年齡區間內的整數。</p>}
        </div>}
        {question.key === "residence" && selected.length > 0 && <div className="row2" style={{ marginTop: ".7rem" }}>
          {!noHousehold && citySelect("wui-city-home", sameCity ? "戶籍及居住縣市" : "戶籍縣市", region, setRegion)}
          {!sameCity && citySelect("wui-city-now", "目前居住縣市", currentRegion, setCurrentRegion)}
        </div>}
      </fieldset>;
    })}

    <div className="actions">
      <button className="btn" type="submit">{profile ? "儲存並重新比對" : "儲存並比對"}</button>
      {onCancel && <button className="btn sec" type="button" onClick={onCancel}>取消</button>}
      {tried && !valid && <span className="err" role="alert">還有必填項目沒有完成。</span>}
    </div>
  </form>;
}

function LearnedList({ profile, onSaved }: { profile: Profile; onSaved: (message: string) => void }) {
  const entries = Object.entries(profile.assistantAttributes ?? {});
  if (!entries.length) return null;
  const save = (next: Record<string, AssistantAttribute>, message: string) => { updateProfile(profile.id, { assistantAttributes: next }); onSaved(message); };
  return <div style={{ marginTop: "1.4rem" }}>
    <h3>小幫手幫您補充的資料</h3>
    <p className="hint">這些是您在聊天中回答的內容，比對時會優先採用。說錯了可以直接修改或刪除。</p>
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
  </div>;
}

export default function ProfilePanel({ profiles, active, cards, match, matching, matchError, onSaved, onOpen, onAskAssistant, onOnlyMatch }: {
  profiles: Profile[];
  active: Profile | null;
  cards: BenefitCard[] | null;
  match: MatchResponse | null;
  matching: boolean;
  matchError: string;
  onSaved: (message: string) => void;
  onOpen: (id: string) => void;
  onAskAssistant: () => void;
  onOnlyMatch: () => void;
}) {
  const [creating, setCreating] = useState(false);
  const editing = creating ? null : active;
  const domains = useMemo(() => needDomains(active), [active]);
  const grouped = useMemo(() => {
    if (!cards || !match) return null;
    const yes = rankForProfile(cards.filter(c => match.results[c.id]?.status === "yes"), match.results, domains);
    const maybe = rankForProfile(cards.filter(c => match.results[c.id]?.status === "maybe"), match.results, domains);
    return { yes, maybe };
  }, [cards, match, domains]);

  return <section aria-label="我的資料卡">
    <div className="people" role="group" aria-label="切換家人的資料卡">
      <span className="lab">資料卡</span>
      {profiles.map(person => <span key={person.id} className="person" aria-current={!creating && person.id === active?.id}>
        <button type="button" onClick={() => { setCreating(false); setActiveProfileId(person.id); }}>{person.nickname}</button>
        <button type="button" className="del" aria-label={`刪除「${person.nickname}」的資料卡`} onClick={() => { if (window.confirm(`確定要刪除「${person.nickname}」的資料卡嗎？`)) { removeProfile(person.id); onSaved("已刪除資料卡"); } }}>✕</button>
      </span>)}
      <button type="button" className="chip" aria-pressed={creating} onClick={() => setCreating(true)}>＋ 新增家人</button>
    </div>

    <div className="grid2">
      <div className="box">
        <h2>{editing ? `${editing.nickname}的資料卡` : "建立我的資料卡"}</h2>
        <p className="hint">資料卡存在這台裝置的瀏覽器裡；比對補助時，填寫的條件會送到平台伺服器計算。填寫越完整，比對結果越準確。</p>
        <ProfileForm key={editing?.id ?? "new"} profile={editing} onCancel={creating && profiles.length ? () => setCreating(false) : undefined} onSaved={message => { setCreating(false); onSaved(message); }} />
        {editing && <LearnedList profile={editing} onSaved={onSaved} />}
      </div>

      <div className="box" aria-live="polite">
        <h2>比對結果</h2>
        <p className="hint">依官方公告的資格條件初步比對，不是正式審核結果。</p>
        {!active || creating ? <p className="hint">填寫左側資料卡並按「儲存並比對」，這裡會列出您可能符合的補助。</p>
          : matchError ? <div className="alert" role="alert">{matchError}</div>
          : !grouped ? <p className="loading" role="status">正在比對 {cards?.length ?? ""} 項補助…</p>
          : <>
            <div className="stats">
              <div className="stat yes"><b>{match!.counts.yes}</b><span>{STATUS_LABEL.yes}</span></div>
              <div className="stat maybe"><b>{match!.counts.maybe}</b><span>需進一步確認</span></div>
              <div className="stat no"><b>{match!.counts.no}</b><span>{STATUS_LABEL.no}</span></div>
            </div>
            {matching && <p className="hint" role="status">資料已更新，正在重新比對…</p>}
            {grouped.yes.length > 0 && <>
              <h3>主動提醒：您可能符合</h3>
              <div className="reclist">{grouped.yes.slice(0, 8).map(card => <button key={card.id} type="button" className="rec" onClick={() => onOpen(card.id)}>
                <span className="rec-main">{card.title}<small>{card.agency}・{card.region}</small></span><span className="tag svc">{card.service_type}</span>→
              </button>)}</div>
            </>}
            {grouped.maybe.length > 0 && <>
              <h3>需要進一步確認</h3>
              <div className="reclist">{grouped.maybe.slice(0, 6).map(card => <button key={card.id} type="button" className="rec" onClick={() => onOpen(card.id)}>
                <span className="rec-main">{card.title}<small>{match!.results[card.id]?.needs.length ? `補充：${match!.results[card.id].needs.slice(0, 3).join("、")}` : `${card.agency}・${card.region}`}</small></span><span className="tag svc">{card.service_type}</span>→
              </button>)}</div>
            </>}
            <div className="actions" style={{ marginTop: "1rem" }}>
              <button type="button" className="btn" onClick={onOnlyMatch}>查看全部 {match!.counts.yes + match!.counts.maybe} 項</button>
              {match!.counts.maybe > 0 && <button type="button" className="btn sec" onClick={onAskAssistant}>請小幫手幫我補充資料</button>}
            </div>
          </>}
      </div>
    </div>
  </section>;
}
