"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { REGIONS, RELATIONS } from "@/lib/options";
import { AGE_RANGES, QUESTIONS, profileTags, selectAnswer } from "@/lib/questionnaire";
import { addProfile, updateProfile } from "@/lib/store";
import type { Profile, Relation } from "@/lib/types";

type Answers = Record<string, string[]>;
const REQUIRED = new Set(["needs", "age", "residence"]);
/** 步驟 0 是「為誰建立」，之後一題一步 */
const STEPS = QUESTIONS.length + 1;

function initialAnswers(profile: Profile | null): Answers {
  const saved: Answers = { ...(profile?.screening ?? {}) };
  if (profile && !saved.age && profile.age != null) {
    const index = AGE_RANGES.findIndex(([min, max]) => profile.age! >= min && profile.age! <= max);
    if (index >= 0) saved.age = [QUESTIONS[1].options[index]];
  }
  return saved;
}

/**
 * 建立／修改資料卡的小視窗：一次一題，單選題選了就到下一題。
 * 修改時上方可以直接跳到任一題，隨時可以儲存。
 */
export default function ProfileDialog({ profile, onClose, onSaved }: { profile: Profile | null; onClose: () => void; onSaved: (message: string) => void }) {
  const editing = !!profile;
  const [step, setStep] = useState(editing ? 1 : 0);
  const [answers, setAnswers] = useState<Answers>(() => initialAnswers(profile));
  const [relation, setRelation] = useState<Relation>(profile?.relation ?? "self");
  const [nickname, setNickname] = useState(profile?.nickname ?? "");
  const [exactAge, setExactAge] = useState(profile?.age == null ? "" : String(profile.age));
  const [region, setRegion] = useState(profile?.region ?? "");
  const [currentRegion, setCurrentRegion] = useState(profile?.currentRegion ?? "");
  const [tried, setTried] = useState(false);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const advanceTimer = useRef<number | null>(null);

  const question = step > 0 ? QUESTIONS[step - 1] : null;
  const selected = question ? answers[question.key] ?? [] : [];
  const residence = answers.residence?.[0];
  const sameCity = QUESTIONS[2].options.slice(0, 2).includes(residence);
  const noHousehold = residence === QUESTIONS[2].options[3];
  const ageRange = AGE_RANGES[QUESTIONS[1].options.indexOf(answers.age?.[0])];
  const ageValid = exactAge === "" || (Number.isInteger(Number(exactAge)) && !!ageRange && Number(exactAge) >= ageRange[0] && Number(exactAge) <= ageRange[1]);
  const stepValid = !question || ((!REQUIRED.has(question.key) || selected.length > 0) && (question.key !== "age" || ageValid) && (question.key !== "residence" || !sameCity || !!region));
  const missing = [...REQUIRED].filter(key => !answers[key]?.length);
  const canSave = !missing.length && ageValid && (!sameCity || !!region);
  const snapshot = JSON.stringify([answers, relation, nickname, exactAge, region, currentRegion]);
  const [initial] = useState(snapshot);
  const dirty = snapshot !== initial;

  useEffect(() => { titleRef.current?.focus(); }, [step]);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = overflow; previous?.focus?.(); };
  }, []);
  useEffect(() => () => { if (advanceTimer.current) window.clearTimeout(advanceTimer.current); }, []);

  const close = () => {
    if (dirty && !window.confirm(editing ? "修改還沒儲存，確定要關閉嗎？" : "資料卡還沒儲存，確定要關閉嗎？")) return;
    onClose();
  };
  const go = (next: number) => {
    if (advanceTimer.current) window.clearTimeout(advanceTimer.current);
    setTried(false);
    setStep(Math.max(0, Math.min(STEPS - 1, next)));
  };
  const next = () => {
    if (!stepValid) { setTried(true); return; }
    if (step < STEPS - 1) go(step + 1); else save();
  };
  const choose = (value: string) => {
    if (!question) return;
    const updated = selectAnswer(answers[question.key] ?? [], question, value);
    setAnswers(previous => ({ ...previous, [question.key]: updated }));
    const changed = updated[0] !== answers[question.key]?.[0];
    if (question.key === "age" && changed) setExactAge("");
    if (question.key === "residence" && changed) { setRegion(""); setCurrentRegion(""); }
    // 單選題選完直接到下一題；年齡、戶籍還有要補的欄位，不自動跳
    if (!question.multi && !["age", "residence"].includes(question.key) && step < STEPS - 1) {
      advanceTimer.current = window.setTimeout(() => go(step + 1), 280);
    }
  };
  const save = () => {
    if (!canSave) {
      setTried(true);
      const first = QUESTIONS.findIndex(q => REQUIRED.has(q.key) && !answers[q.key]?.length);
      if (first >= 0) go(first + 1);
      else if (!ageValid) go(2);
      else go(3);
      return;
    }
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
    else { addProfile(draft); onSaved("資料卡已建立，正在為您比對補助"); }
    onClose();
  };

  // 小視窗開著時，Tab 只在視窗裡面循環；Esc 關閉
  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") { event.stopPropagation(); close(); return; }
    if (event.key !== "Tab") return;
    const items = [...event.currentTarget.querySelectorAll<HTMLElement>(".modal button:not([disabled]), .modal input, .modal select")];
    if (!items.length) return;
    const index = items.indexOf(document.activeElement as HTMLElement);
    if (event.shiftKey && index <= 0) { event.preventDefault(); items[items.length - 1].focus(); }
    else if (!event.shiftKey && index === items.length - 1) { event.preventDefault(); items[0].focus(); }
  };

  const citySelect = (id: string, label: string, value: string, change: (value: string) => void, required = false) => <div className="field">
    <label htmlFor={id}>{label}</label>
    <select id={id} value={value} onChange={e => change(e.target.value)} aria-invalid={tried && required && !value}>
      <option value="">不確定／尚未填寫</option>
      {REGIONS.map(city => <option key={city}>{city}</option>)}
    </select>
    {tried && required && !value && <p className="err">請選擇戶籍與居住的縣市。</p>}
  </div>;

  return <div className="modal-layer" onKeyDown={onKeyDown}>
    <div className="scrim on" onClick={close} aria-hidden="true" />
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="wui-profile-step-title">
      <div className="modal-head">
        <div className="modal-title">
          <b>{editing ? `修改「${profile!.nickname}」的資料卡` : "建立我的資料卡"}</b>
          <small>{step === 0 ? "開始之前" : `第 ${step} 題／共 ${QUESTIONS.length} 題`}{question ? (REQUIRED.has(question.key) ? "・必填" : "・選填") : ""}</small>
        </div>
        <button type="button" className="x" aria-label="關閉" onClick={close}>✕</button>
      </div>
      <div className="progress" aria-hidden="true"><i style={{ width: `${(step / (STEPS - 1)) * 100}%` }} /></div>
      {editing && <nav className="stepnav" aria-label="跳到某一題">
        {QUESTIONS.map((q, index) => <button key={q.key} type="button" aria-current={step === index + 1 ? "step" : undefined} className={answers[q.key]?.length ? "done" : ""} onClick={() => go(index + 1)} title={q.title}>{index + 1}</button>)}
      </nav>}

      <div className="modal-body">
        {step === 0 ? <>
          <h2 ref={titleRef} tabIndex={-1} id="wui-profile-step-title">這張資料卡是為誰建立的？</h2>
          <p className="why">可以為自己，也可以替家人分別建立。資料卡存在這台裝置的瀏覽器；比對補助時，填寫的條件會送到平台伺服器計算。</p>
          <div className="choices" role="group" aria-label="為誰建立">
            {RELATIONS.map(r => <button key={r.value} type="button" className="choice" aria-pressed={relation === r.value} onClick={() => setRelation(r.value)}>{r.label}<small>{r.hint}</small></button>)}
          </div>
          <div className="field" style={{ marginTop: "1rem" }}>
            <label htmlFor="wui-nickname">稱呼（選填）</label>
            <input id="wui-nickname" value={nickname} maxLength={20} onChange={e => setNickname(e.target.value)} placeholder="例如：媽媽、小明" />
          </div>
        </> : question && <>
          <h2 ref={titleRef} tabIndex={-1} id="wui-profile-step-title">{question.title}</h2>
          <p className="why">{question.why}{question.multi ? "（可複選）" : ""}</p>
          <div className="choices" role="group" aria-label={question.title}>
            {question.options.map(option => <button key={option} type="button" className="choice" aria-pressed={selected.includes(option)} onClick={() => choose(option)}>{option}</button>)}
          </div>
          {tried && REQUIRED.has(question.key) && !selected.length && <p className="err" role="alert">這一題必填，請選擇一項。</p>}
          {question.key === "age" && selected.length > 0 && <div className="field" style={{ marginTop: "1rem" }}>
            <label htmlFor="wui-age">實際年齡（選填，填了比對會更準）</label>
            <input id="wui-age" type="number" inputMode="numeric" min={0} max={120} value={exactAge} onChange={e => setExactAge(e.target.value)} aria-invalid={!ageValid} placeholder={ageRange ? `例如：${Math.min(ageRange[0] + 7, ageRange[1])}` : ""} />
            {!ageValid && <p className="err">請填入所選年齡區間內的整數。</p>}
          </div>}
          {question.key === "residence" && selected.length > 0 && <div className="row2" style={{ marginTop: "1rem" }}>
            {!noHousehold && citySelect("wui-city-home", sameCity ? "戶籍及居住縣市" : "戶籍縣市", region, setRegion, sameCity)}
            {!sameCity && citySelect("wui-city-now", "目前居住縣市", currentRegion, setCurrentRegion)}
          </div>}
        </>}
      </div>

      <div className="modal-foot">
        <button type="button" className="btn sec" onClick={() => go(step - 1)} disabled={step === 0}>上一步</button>
        <span className="spacer" />
        {question && !REQUIRED.has(question.key) && !selected.length && step < STEPS - 1 && <button type="button" className="btn sec" onClick={() => go(step + 1)}>跳過</button>}
        {editing && step < STEPS - 1 && <button type="button" className="btn sec" onClick={save}>儲存</button>}
        <button type="button" className="btn" onClick={next}>{step < STEPS - 1 ? "下一題 →" : editing ? "儲存並重新比對" : "完成並比對"}</button>
      </div>
    </div>
  </div>;
}
