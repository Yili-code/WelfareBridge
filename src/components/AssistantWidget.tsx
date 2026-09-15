"use client";

import { useEffect, useRef, useState } from "react";
import { engine } from "@/lib/assistant";
import type { AppealDraft, AssistantState, ChatMessage } from "@/lib/assistant";
import { addAppeal, uid } from "@/lib/store";
import type { Profile } from "@/lib/types";

export default function AssistantWidget({
  profile,
}: {
  profile: Profile | null;
}) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [state, setState] = useState<AssistantState>({ step: 0, answers: {} });
  const [quickReplies, setQuickReplies] = useState<string[]>([]);
  const [multiSelect, setMultiSelect] = useState(false);
  const [allowFreeText, setAllowFreeText] = useState(false);
  const [picked, setPicked] = useState<string[]>([]);
  const [draft, setDraft] = useState<AppealDraft | null>(null);
  const submissionKey = useRef("");
  const [submitError, setSubmitError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [chatError, setChatError] = useState("");
  const pending = useRef<string | null>(null);
  const inFlight = useRef(false);
  const [text, setText] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const push = (role: ChatMessage["role"], lines: string[]) =>
    setMessages((m) => [
      ...m,
      ...lines.map((t) => ({ id: uid("m"), role, text: t })),
    ]);

  const applyTurn = (turn: Awaited<ReturnType<typeof engine.start>>) => {
    setState(turn.state);
    push("assistant", turn.replies);
    setQuickReplies(turn.quickReplies);
    setMultiSelect(turn.multiSelect);
    setAllowFreeText(turn.allowFreeText);
    setPicked([]);
    setDraft(turn.draft ?? null);
  };

  const begin = async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    pending.current = null;
    setChatError("");
    setState({ step: 0, answers: {} });
    setQuickReplies([]);
    setAllowFreeText(false);
    setMessages([]);
    setDraft(null);
    setSubmitted(false);
    submissionKey.current = typeof crypto.randomUUID === "function" ? crypto.randomUUID() : uid("request") + uid("retry");
    setSubmitError("");
    setBusy(true);
    try { applyTurn(await engine.start(profile)); }
    catch (e) { setChatError(e instanceof Error ? e.message : "助理連線失敗"); }
    finally { setBusy(false); inFlight.current = false; }
  };

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, busy, draft]);

  const send = async (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || inFlight.current) return;
    inFlight.current = true;
    pending.current = trimmed;
    setChatError("");
    push("user", [trimmed]);
    setQuickReplies([]);
    setText("");
    setBusy(true);
    try { applyTurn(await engine.reply(state, trimmed, profile)); pending.current = null; }
    catch (e) { setChatError(e instanceof Error ? e.message : "助理連線失敗"); }
    finally { setBusy(false); inFlight.current = false; }
  };

  const retry = async () => {
    if (inFlight.current) return;
    if (pending.current === null) return begin();
    inFlight.current = true; setBusy(true); setChatError("");
    try { applyTurn(await engine.reply(state, pending.current, profile)); pending.current = null; }
    catch (e) { setChatError(e instanceof Error ? e.message : "助理連線失敗"); }
    finally { setBusy(false); inFlight.current = false; }
  };

  const submitAppeal = async () => {
    if (!draft || busy) return;
    setBusy(true); setSubmitError("");
    try { await addAppeal({
      profileId: profile?.id ?? null,
      profileNickname: profile?.nickname ?? "未建檔使用者",
      region: draft.region,
      identities: draft.identities,
      age: draft.age,
      mainRequest: draft.mainRequest,
      summary: draft.summary,
      transcript: messages.map(({ role, text }) => ({ role, text })),
    }, submissionKey.current);
    setSubmitted(true);
    } catch (e) { setSubmitError(e instanceof Error ? e.message : "送出失敗，請重試。"); }
    finally { setBusy(false); }
  };

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => {
          setOpen(true);
          if (messages.length === 0) void begin();
        }}
        className="fixed right-6 bottom-6 z-40 flex items-center gap-2 rounded-full bg-brand-500 py-3.5 pr-5 pl-4 text-sm font-medium text-white shadow-lg transition hover:bg-brand-600"
      >
        <span aria-hidden className="text-base">💬</span>
        不知道怎麼找？問問助理
      </button>
    );
  }

  return (
    <div className="animate-rise fixed right-6 bottom-6 z-40 flex h-[36rem] max-h-[calc(100dvh-3rem)] w-[24rem] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
      <header className="flex items-center gap-3 border-b border-slate-200 px-4 py-3">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm">
          🤝
        </span>
        <div className="flex-1">
          <div className="text-sm font-medium">資源引導助理</div>
          <div className="text-[11px] text-ink-400">
            {profile ? `正在協助「${profile.nickname}」` : "尚未選擇對象"}
          </div>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={() => void begin()}
          className="rounded px-2 py-1 text-xs text-ink-400 hover:text-brand-600"
        >
          重新開始
        </button>
        <button
          type="button"
          aria-label="關閉"
          onClick={() => setOpen(false)}
          className="rounded px-2 py-1 text-ink-400 hover:text-ink-600"
        >
          ×
        </button>
      </header>

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        <p className="text-xs text-ink-400">已回答 {state.turnCount ?? 0} / 9 輪 · {state.completed ? '已整理摘要' : '第 9 輪後自動整理摘要'}{state.candidateCount != null ? ` · 候選 ${state.candidateCount} 筆` : ''}</p>
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <p
              className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                m.role === "user"
                  ? "rounded-br-sm bg-brand-500 text-white"
                  : "rounded-bl-sm bg-slate-100 text-ink-600"
              }`}
            >
              {m.text}
            </p>
          </div>
        ))}

        {busy && (
          <div className="flex justify-start">
            <p className="rounded-2xl rounded-bl-sm bg-slate-100 px-3.5 py-2.5 text-sm text-ink-400">
              輸入中…
            </p>
          </div>
        )}

        {chatError && <div role="alert" className="text-sm text-red-700">{chatError}<button type="button" disabled={busy} onClick={() => void retry()} className="ml-2 underline">重試</button></div>}
        {submitError && <p role="alert" className="text-sm text-red-700">{submitError}</p>}
        {draft && !busy && (
          <div className="rounded-xl border border-brand-300 bg-brand-50 p-3.5">
            {submitted ? (
              <p className="text-sm leading-relaxed text-brand-700">
                需求已儲存至伺服器，承辦人員可在後台查看這筆登記。
              </p>
            ) : (
              <>
                <p className="text-xs text-ink-400">找不到現成資源時</p>
                <p className="mt-1 text-sm font-medium text-brand-700">
                  送出這份需求登記
                </p>
                <button
                  type="button"
                  onClick={submitAppeal}
                  className="mt-3 w-full rounded-lg bg-brand-500 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
                >
                  送出需求
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {(quickReplies.length > 0 || allowFreeText) && !submitted && !chatError && (
        <div className="border-t border-slate-200 px-4 py-3">
          {quickReplies.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-1.5">
              {quickReplies.map((q) => {
                const on = picked.includes(q);
                return (
                  <button
                    key={q}
                    type="button"
                    disabled={busy}
                    onClick={() => {
                      if (!multiSelect) return void send(q);
                      setPicked((p) =>
                        p.includes(q) ? p.filter((x) => x !== q) : [...p, q],
                      );
                    }}
                    className={`rounded-full border px-3 py-1.5 text-xs transition disabled:opacity-50 ${
                      on
                        ? "border-brand-500 bg-brand-500 text-white"
                        : "border-slate-200 text-ink-600 hover:border-brand-300 hover:bg-brand-50"
                    }`}
                  >
                    {q}
                  </button>
                );
              })}
            </div>
          )}

          {multiSelect && (
            <button
              type="button"
              disabled={picked.length === 0 || busy}
              onClick={() => void send(picked.join("、"))}
              className="mb-2 w-full rounded-lg bg-brand-500 py-2 text-xs font-medium text-white transition hover:bg-brand-600 disabled:bg-slate-200 disabled:text-slate-400"
            >
              確認選擇（{picked.length}）
            </button>
          )}

          {allowFreeText && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void send(text);
              }}
              className="flex gap-2"
            >
              <input
                maxLength={2000}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="也可以直接打字說明…"
                className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500"
              />
              <button
                type="submit"
                disabled={!text.trim() || busy}
                className="rounded-lg bg-brand-500 px-4 text-sm font-medium text-white transition hover:bg-brand-600 disabled:bg-slate-200 disabled:text-slate-400"
              >
                送出
              </button>
            </form>
          )}
          {allowFreeText && !draft && <button type="button" disabled={busy} onClick={() => void send("請依照我們的對話整理需求登記，讓我確認後再送出。") } className="mt-2 text-xs text-brand-600 underline">整理需求登記</button>}
        </div>
      )}
    </div>
  );
}
