"use client";

import { useEffect, useImperativeHandle, useRef, useState, type Ref } from "react";
import { engine, type AppealDraft, type AssistantState, type AssistantTurn } from "@/lib/assistant";
import { addAppeal, uid, updateProfile } from "@/lib/store";
import type { Profile } from "@/lib/types";
import type { MatchStatus } from "./api";
import { mergeLearned } from "./assistant-memory";

type Counts = Record<MatchStatus, number>;
type Message =
  | { id: string; role: "assistant" | "user"; text: string }
  | { id: string; role: "update"; written: string[]; before: Counts | null }
  | { id: string; role: "search"; keyword: string }
  | { id: string; role: "need-profile" };

const key = () => (typeof crypto.randomUUID === "function" ? crypto.randomUUID() : uid("request") + uid("retry"));

export interface ChatHandle { open: () => void }

export default function ChatWidget({ ref, profile, counts, matching, onSearch, onGoProfile, onGoSearch }: {
  ref?: Ref<ChatHandle>;
  profile: Profile | null;
  counts: Counts | null;
  matching: boolean;
  onSearch: (keyword: string) => void;
  onGoProfile: () => void;
  onGoSearch: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [state, setState] = useState<AssistantState>({ step: 0, answers: {} });
  const [quickReplies, setQuickReplies] = useState<string[]>([]);
  const [allowFreeText, setAllowFreeText] = useState(false);
  const [draft, setDraft] = useState<AppealDraft | null>(null);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [chatError, setChatError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const submissionKey = useRef("");
  const pending = useRef<string | null>(null);
  const inFlight = useRef(false);
  const warnedNoProfile = useRef(false);
  const lastKeyword = useRef("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const profileId = profile?.id ?? null;
  const startedFor = useRef<string | null>(null);

  const add = (...items: Message[]) => setMessages(list => [...list, ...items]);

  const apply = (turn: AssistantTurn) => {
    setState(turn.state);
    setQuickReplies(turn.quickReplies);
    setAllowFreeText(turn.allowFreeText);
    setDraft(turn.draft ?? null);
    const extra: Message[] = [];
    if (turn.learned?.length) {
      if (profile) {
        const { next, changed } = mergeLearned(profile.assistantAttributes, turn.learned);
        if (changed.length) {
          updateProfile(profile.id, { assistantAttributes: next });
          extra.push({ id: uid("m"), role: "update", written: changed.map(c => `${c.label}：${c.valueLabel}`), before: counts });
        }
      } else if (!warnedNoProfile.current) {
        warnedNoProfile.current = true;
        extra.push({ id: uid("m"), role: "need-profile" });
      }
    }
    const keyword = turn.search?.queries?.join(" ").trim();
    // 後端在同一段對話裡會一直帶著搜尋關鍵字；只有新的關鍵字才帶到查詢頁，避免每回答一題就被切換頁面
    if (keyword && keyword !== lastKeyword.current) { lastKeyword.current = keyword; onSearch(keyword); extra.push({ id: uid("m"), role: "search", keyword }); }
    add(...turn.replies.map(t => ({ id: uid("m"), role: "assistant" as const, text: t })), ...extra);
  };

  const begin = async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    startedFor.current = profileId;
    lastKeyword.current = "";
    pending.current = null;
    submissionKey.current = key();
    setMessages([]); setState({ step: 0, answers: {} }); setQuickReplies([]); setAllowFreeText(false);
    setDraft(null); setSubmitted(false); setSubmitError(""); setChatError(""); setBusy(true);
    try { apply(await engine.start(profile)); }
    catch (e) { setChatError(e instanceof Error ? e.message : "小幫手暫時無法回應，請稍後再試。"); }
    finally { setBusy(false); inFlight.current = false; }
  };

  const send = async (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || inFlight.current) return;
    inFlight.current = true;
    pending.current = trimmed;
    add({ id: uid("m"), role: "user", text: trimmed });
    setQuickReplies([]); setText(""); setChatError(""); setBusy(true);
    try { apply(await engine.reply(state, trimmed, profile)); pending.current = null; }
    catch (e) { setChatError(e instanceof Error ? e.message : "小幫手暫時無法回應，請稍後再試。"); }
    finally { setBusy(false); inFlight.current = false; }
  };

  const retry = async () => {
    if (inFlight.current) return;
    if (pending.current === null) return begin();
    inFlight.current = true; setBusy(true); setChatError("");
    try { apply(await engine.reply(state, pending.current, profile)); pending.current = null; }
    catch (e) { setChatError(e instanceof Error ? e.message : "小幫手暫時無法回應，請稍後再試。"); }
    finally { setBusy(false); inFlight.current = false; }
  };

  const openChat = () => {
    setOpen(true);
    // 第一次打開，或換成另一位家人的資料卡時，重新開始對話
    if (messages.length === 0 || startedFor.current !== profileId) void begin();
  };

  // 補助詳情、資料卡的「請小幫手問我」由父層呼叫 open()
  useImperativeHandle(ref, () => ({ open: openChat }));

  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }); }, [messages, busy, draft, open]);

  const submitAppeal = async () => {
    if (!draft || busy) return;
    setBusy(true); setSubmitError("");
    try {
      await addAppeal({
        profileId: profile?.id ?? null, profileNickname: profile?.nickname ?? "未建檔使用者", region: draft.region, identities: draft.identities, age: draft.age,
        mainRequest: draft.mainRequest, summary: draft.summary,
        transcript: messages.flatMap(m => (m.role === "assistant" || m.role === "user" ? [{ role: m.role, text: m.text }] : [])),
      }, submissionKey.current);
      setSubmitted(true);
    } catch (e) { setSubmitError(e instanceof Error ? e.message : "送出失敗，請再試一次。"); }
    finally { setBusy(false); }
  };

  if (!open) return <button type="button" className="chat-open" onClick={openChat}>💬 不知道怎麼找？問問小幫手</button>;

  const lastUpdate = [...messages].reverse().find(m => m.role === "update")?.id;

  return <div className="chat" role="dialog" aria-label="福利小幫手">
    <div className="chat-head">
      <div className="t">
        <b>福利小幫手</b>
        <small>{profile ? `正在協助「${profile.nickname}」・回答會寫進資料卡` : "尚未建立資料卡"}</small>
      </div>
      <button type="button" className="restart" disabled={busy} onClick={() => void begin()}>重新開始</button>
      <button type="button" className="x" aria-label="關閉小幫手" onClick={() => setOpen(false)}>✕</button>
    </div>

    <div className="chat-body" ref={scrollRef} aria-live="polite">
      {messages.map(message => {
        if (message.role === "need-profile") return <div key={message.id} className="msg update">
          先建立資料卡，您在這裡的回答才能保存，並用來更新補助比對結果。
          <div className="go"><button type="button" className="btn sm" onClick={onGoProfile}>建立我的資料卡</button></div>
        </div>;
        if (message.role === "search") return <div key={message.id} className="msg update">
          已在「查詢補助與服務」搜尋「{message.keyword}」，結果顯示在畫面上。
          <div className="go"><button type="button" className="btn sm" onClick={onGoSearch}>查看搜尋結果</button></div>
        </div>;
        if (message.role === "update") {
          const before = message.id === lastUpdate ? message.before : null;
          return <div key={message.id} className="msg update">
            <b>已寫進資料卡：</b>{message.written.join("、")}
            {message.id === lastUpdate && (matching || !counts ? <div>正在重新比對補助…</div>
              : before ? <div>比對結果已更新：可能符合 {before.yes} → <b>{counts.yes}</b> 項、需進一步確認 {before.maybe} → <b>{counts.maybe}</b> 項</div>
              : <div>比對結果已更新。</div>)}
            <div className="go"><button type="button" className="btn sm" onClick={onGoSearch}>查看補助</button><button type="button" className="btn sm sec" onClick={onGoProfile}>查看資料卡</button></div>
          </div>;
        }
        return <p key={message.id} className={`msg ${message.role}`}>{message.text}</p>;
      })}
      {busy && <p className="msg assistant" role="status">小幫手正在想…</p>}
      {chatError && <div className="alert" role="alert">{chatError}<div className="go" style={{ marginTop: ".4rem" }}><button type="button" className="btn sm" disabled={busy} onClick={() => void retry()}>再試一次</button></div></div>}
      {draft && !busy && <div className="draft">
        {submitted ? <p>需求登記已送給承辦人員，他們會依此評估是否需要新增服務（不會公開）。</p> : <>
          <p><b>要把這份需求登記送給承辦人員嗎？</b>（不會公開；想讓大家附議，可以到「訴求專區」提出）</p>
          <div className="go" style={{ marginTop: ".4rem" }}><button type="button" className="btn sm" onClick={() => void submitAppeal()}>送出需求登記</button></div>
        </>}
        {submitError && <p className="err" role="alert">{submitError}</p>}
      </div>}
    </div>

    {(quickReplies.length > 0 || allowFreeText) && !submitted && !chatError && <div className="chat-foot">
      {quickReplies.length > 0 && <div className="qr">{quickReplies.map(reply => <button key={reply} type="button" className="chip" disabled={busy} onClick={() => void send(reply)}>{reply}</button>)}</div>}
      {allowFreeText && <form onSubmit={e => { e.preventDefault(); void send(text); }}>
        <label className="sr" htmlFor="wui-chat-input">輸入訊息</label>
        <input id="wui-chat-input" maxLength={2000} value={text} onChange={e => setText(e.target.value)} placeholder="也可以直接打字說明…" />
        <button type="submit" className="btn sm" disabled={!text.trim() || busy}>送出</button>
      </form>}
      {allowFreeText && !draft && <button type="button" className="chip" disabled={busy} onClick={() => void send("請依照我們的對話整理需求登記，讓我確認後再送出。")}>整理需求登記給承辦人員</button>}
    </div>}
  </div>;
}
