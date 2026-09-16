"use client";

import "./welfare.css";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toMatchingProfile } from "@/lib/benefit-profile";
import { useActiveProfileId, useHydrated, useProfiles } from "@/lib/store";
import { fetchBenefits, matchProfile, type BenefitCard, type MatchResponse } from "./api";
import ChatWidget, { type ChatHandle } from "./ChatWidget";
import DetailDrawer from "./DetailDrawer";
import GapPanel from "./GapPanel";
import ProfilePanel from "./ProfilePanel";
import SearchPanel from "./SearchPanel";

type Tab = "search" | "profile" | "gap";
const TABS: { id: Tab; label: string }[] = [{ id: "search", label: "查詢補助與服務" }, { id: "profile", label: "我的資料卡" }, { id: "gap", label: "訴求專區" }];
const DEFAULT_DISCLAIMER = "本結果僅供福利導覽與初步篩選，實際資格及補助額度以主管機關評估、核定為準。";

// 伺服器端 render 時沒有 window；hydrate 完成前畫面只顯示「載入中」，所以兩邊初始值不同不會造成畫面不一致
function readMode(): "normal" | "elder" {
  if (typeof window === "undefined") return "normal";
  try { return window.localStorage.getItem("wf.mode") === "elder" ? "elder" : "normal"; } catch { return "normal"; }
}

function readTab(): Tab {
  if (typeof window === "undefined") return "search";
  const fromHash = window.location.hash.replace("#", "");
  return TABS.find(t => t.id === fromHash)?.id ?? "search";
}

export default function WelfareApp() {
  const hydrated = useHydrated();
  const profiles = useProfiles();
  const activeId = useActiveProfileId();
  const active = profiles.find(p => p.id === activeId) ?? profiles[0] ?? null;

  const [tab, setTab] = useState<Tab>(readTab);
  const [mode, setMode] = useState<"normal" | "elder">(readMode);
  const [cards, setCards] = useState<BenefitCard[] | null>(null);
  const [disclaimer, setDisclaimer] = useState(DEFAULT_DISCLAIMER);
  const [loadError, setLoadError] = useState("");
  const [match, setMatch] = useState<{ key: string; data?: MatchResponse; error?: string } | null>(null);
  const [query, setQuery] = useState("");
  const [onlyMatch, setOnlyMatch] = useState(false);
  const [detailId, setDetailId] = useState<string | null>(null);
  const [gapPrefill, setGapPrefill] = useState({ title: "", key: 0 });
  const [toast, setToast] = useState("");
  const [scrolled, setScrolled] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLElement>(null);
  const chatRef = useRef<ChatHandle>(null);

  useEffect(() => {
    // 長者模式把整頁字級放大（樣式都用 rem），離開這頁時還原
    document.documentElement.style.fontSize = mode === "elder" ? "21px" : "";
    return () => { document.documentElement.style.fontSize = ""; };
  }, [mode]);

  useEffect(() => {
    const controller = new AbortController();
    fetchBenefits(controller.signal)
      .then(data => { setCards(data.items); if (data.disclaimer) setDisclaimer(data.disclaimer); })
      .catch(error => { if (!controller.signal.aborted) setLoadError(error instanceof Error ? error.message : "無法載入補助資料。"); });
    return () => controller.abort();
  }, []);

  const matchingProfile = useMemo(() => (active ? toMatchingProfile(active) : null), [active]);
  const matchKey = matchingProfile ? JSON.stringify(matchingProfile) : "";
  useEffect(() => {
    if (!matchingProfile) return;
    const controller = new AbortController();
    matchProfile(matchingProfile, controller.signal)
      .then(data => setMatch({ key: matchKey, data }))
      .catch(error => { if (!controller.signal.aborted) setMatch({ key: matchKey, error: error instanceof Error ? error.message : "比對失敗，請再試一次。" }); });
    return () => controller.abort();
  }, [matchKey, matchingProfile]);

  // 資料卡剛改過、新結果還沒回來時，先沿用上一次的結果（畫面不閃爍），同時標示「比對中」
  const current = active ? match : null;
  const matching = !!active && current?.key !== matchKey;
  const results = current?.data?.results ?? null;
  const counts = current?.data?.counts ?? null;
  const matchError = current && current.key === matchKey ? current.error ?? "" : "";

  useEffect(() => {
    const header = headerRef.current;
    const root = rootRef.current;
    if (!header || !root) return;
    const sync = () => root.style.setProperty("--head", `${Math.round(header.getBoundingClientRect().height)}px`);
    const observer = new ResizeObserver(sync);
    observer.observe(header);
    let collapsed = false;
    const onScroll = () => {
      const y = window.scrollY;
      if (!collapsed && y > 140) { collapsed = true; setScrolled(true); }
      else if (collapsed && y < 60) { collapsed = false; setScrolled(false); }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => { observer.disconnect(); window.removeEventListener("scroll", onScroll); };
  }, [hydrated]);

  const showToast = useCallback((message: string) => setToast(message), []);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 2600);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const goto = useCallback((next: Tab) => {
    setTab(next);
    window.history.replaceState(null, "", next === "search" ? window.location.pathname : `#${next}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);
  const switchMode = (next: "normal" | "elder") => {
    setMode(next);
    try { window.localStorage.setItem("wf.mode", next); } catch { /* 無痕模式存不了也沒關係 */ }
  };
  const openGap = useCallback((title: string) => {
    setDetailId(null);
    setGapPrefill(previous => ({ title, key: previous.key + 1 }));
    goto("gap");
  }, [goto]);
  const closeDetail = useCallback(() => setDetailId(null), []);

  if (!hydrated) return <div className="wui" data-mode="normal"><main><p className="loading" role="status">載入中…</p></main></div>;

  return <div className="wui" data-mode={mode} ref={rootRef}>
    <header className={`top${scrolled ? " scrolled" : ""}`} ref={headerRef}>
      <div className="top-in">
        <h1>福利補助導覽</h1>
        <p className="sub">查詢補助與服務 ｜ 資格初步比對 ｜ 服務缺口訴求</p>
        <div className="top-right">
          <div className="switch" data-on={mode} role="group" aria-label="顯示模式">
            <span className="thumb" aria-hidden="true" />
            <button type="button" aria-pressed={mode === "normal"} onClick={() => switchMode("normal")}>一般模式</button>
            <button type="button" aria-pressed={mode === "elder"} onClick={() => switchMode("elder")}>長者模式</button>
          </div>
        </div>
      </div>
      <nav className="tabs" role="tablist" aria-label="主要功能">
        {TABS.map(t => <button key={t.id} type="button" role="tab" id={`wui-tab-${t.id}`} aria-controls={`wui-panel-${t.id}`} aria-selected={tab === t.id} onClick={() => goto(t.id)}>
          {t.label}{t.id === "profile" && counts && <span className="dot" aria-label={`${counts.yes} 項可能符合`}>{counts.yes}</span>}
        </button>)}
      </nav>
    </header>

    <main>
      <div role="tabpanel" id="wui-panel-search" aria-labelledby="wui-tab-search" hidden={tab !== "search"}>
        <SearchPanel cards={cards} loadError={loadError} results={results} matching={matching} profileName={active?.nickname ?? null} query={query} setQuery={setQuery} onlyMatch={onlyMatch} setOnlyMatch={setOnlyMatch}
          onOpen={setDetailId} onGoProfile={() => goto("profile")} onGap={openGap} />
      </div>
      <div role="tabpanel" id="wui-panel-profile" aria-labelledby="wui-tab-profile" hidden={tab !== "profile"}>
        <ProfilePanel profiles={profiles} active={active} cards={cards} match={current?.data ?? null} matching={matching} matchError={matchError}
          onSaved={showToast} onOpen={setDetailId} onAskAssistant={() => chatRef.current?.open()} onOnlyMatch={() => { setOnlyMatch(true); goto("search"); }} />
      </div>
      <div role="tabpanel" id="wui-panel-gap" aria-labelledby="wui-tab-gap" hidden={tab !== "gap"}>
        <GapPanel key={gapPrefill.key} prefill={gapPrefill.title} defaultRegion={active?.region ?? ""} onToast={showToast} />
      </div>
    </main>

    <footer className="foot">
      <p>{disclaimer}</p>
      <p>補助資料來自各級政府與學校的官方公告，每項補助都附官方頁面連結；申請前請以官方公告為準。</p>
    </footer>

    <DetailDrawer id={detailId} result={detailId ? results?.[detailId] : undefined} hasProfile={!!active} onClose={closeDetail}
      onGoProfile={() => { setDetailId(null); goto("profile"); }} onGap={openGap} onAskAssistant={() => { setDetailId(null); chatRef.current?.open(); }} />

    <ChatWidget ref={chatRef} profile={active} counts={counts} matching={matching}
      onSearch={keyword => { setQuery(keyword); goto("search"); }} onGoProfile={() => goto("profile")} onGoSearch={() => goto("search")} />

    <div className={`toast${toast ? " on" : ""}`} role="status" aria-live="polite">{toast}</div>
  </div>;
}
