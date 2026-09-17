"use client";

import { useMemo, useState } from "react";
import type { BenefitCard, MatchResult } from "./api";
import BenefitCardView from "./BenefitCardView";
import { ProfileInvite } from "./ProfilePanel";
import { FACETS, emptyFilters, facetCounts, searchCards, type FacetKey, type Filters, type SortKey } from "./search";

const PAGE = 20;

export default function SearchPanel({ cards, loadError, results, matching, profileName, query, setQuery, onlyMatch, setOnlyMatch, savedIds, onToggleSave, onOpen, onGoProfile, onCreateProfile, onGap }: {
  cards: BenefitCard[] | null;
  loadError: string;
  results: Record<string, MatchResult> | null;
  matching: boolean;
  profileName: string | null;
  query: string;
  setQuery: (value: string) => void;
  onlyMatch: boolean;
  setOnlyMatch: (value: boolean) => void;
  savedIds: Set<string>;
  onToggleSave: (card: BenefitCard) => void;
  onOpen: (id: string) => void;
  onGoProfile: () => void;
  onCreateProfile: () => void;
  onGap: (title: string) => void;
}) {
  const [filters, setFilters] = useState<Filters>(emptyFilters);
  const [sort, setSort] = useState<SortKey>("match");
  const [shown, setShown] = useState(PAGE);
  const [expanded, setExpanded] = useState<Set<FacetKey>>(new Set());

  const all = useMemo(() => cards ?? [], [cards]);
  const facets = useMemo(() => Object.fromEntries(FACETS.map(f => [f.key, facetCounts(all, f.key)])) as Record<FacetKey, [string, number][]>, [all]);
  const list = useMemo(() => searchCards(all, { query, filters, onlyMatch: onlyMatch && !!results, sort, results: results ?? undefined }), [all, query, filters, onlyMatch, sort, results]);
  const quick = useMemo(() => [...facets.audiences.slice(0, 4).map(([v]) => ["audiences", v] as const), ...facets.domain.slice(0, 6).map(([v]) => ["domain", v] as const)], [facets]);

  const toggle = (key: FacetKey, value: string) => {
    setFilters(previous => {
      const next = { ...previous, [key]: new Set(previous[key]) };
      if (next[key].has(value)) next[key].delete(value); else next[key].add(value);
      return next;
    });
    setShown(PAGE);
  };
  const clearAll = () => { setFilters(emptyFilters()); setQuery(""); setOnlyMatch(false); setShown(PAGE); };

  return <section aria-label="查詢補助與服務">
    {!profileName && <ProfileInvite onCreate={onCreateProfile} />}
    <div className="hero">
      <div className="searchbar">
        <div className="searchbox">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
          <input type="search" value={query} onChange={e => { setQuery(e.target.value); setShown(PAGE); }} placeholder="輸入需求，例如：租屋、學費、長照、送餐、失業" aria-label="關鍵字搜尋" />
          {query && <button className="clear" type="button" aria-label="清除關鍵字" onClick={() => setQuery("")}>✕</button>}
        </div>
        <button className="chip" type="button" aria-pressed={onlyMatch && !!results} disabled={!results} onClick={() => { setOnlyMatch(!onlyMatch); setShown(PAGE); }} title={results ? "" : "建立資料卡後即可使用"}>只看我可能符合的</button>
      </div>
      <div className="quick">
        <span className="lab">快速篩選</span>
        {quick.map(([key, value]) => <button key={`${key}:${value}`} className="chip" type="button" aria-pressed={filters[key].has(value)} onClick={() => toggle(key, value)}>{value}</button>)}
      </div>
      {profileName && <p className="profile-line">目前依「{profileName}」的資料卡標示比對結果{matching ? "（比對中…）" : ""}。<button type="button" onClick={onGoProfile}>查看比對結果</button></p>}
    </div>

    <div className="layout">
      <aside className="filters" aria-label="篩選條件">
        <h2>篩選條件</h2>
        {FACETS.map(({ key, label, show }) => {
          const options = facets[key];
          if (!options.length) return null;
          const open = expanded.has(key);
          const visible = open ? options : options.slice(0, show).concat(options.slice(show).filter(([v]) => filters[key].has(v)));
          return <div className="fgroup" key={key}>
            <h3>{label}</h3>
            {visible.map(([value, count]) => <label key={value}>
              <input type="checkbox" checked={filters[key].has(value)} onChange={() => toggle(key, value)} />
              <span>{value}</span><span className="cnt">{count}</span>
            </label>)}
            {options.length > show && <button type="button" className="more" onClick={() => setExpanded(prev => { const next = new Set(prev); if (open) next.delete(key); else next.add(key); return next; })}>{open ? "收合" : `顯示全部 ${options.length} 項`}</button>}
          </div>;
        })}
        <button className="btn sec reset" type="button" onClick={clearAll}>清除全部條件</button>
      </aside>

      <div>
        <div className="resbar">
          <div className="count" aria-live="polite">{cards ? <>找到 <b>{list.length}</b> 項補助或服務</> : loadError ? "無法載入補助資料" : "載入中…"}</div>
          <label className="sr" htmlFor="wui-sort">排序方式</label>
          <select id="wui-sort" value={sort} onChange={e => setSort(e.target.value as SortKey)}>
            <option value="match">依比對結果排序</option>
            <option value="deadline">依截止日排序（快截止的在前）</option>
            <option value="title">依名稱排序</option>
            <option value="updated">依官方公告時間</option>
          </select>
        </div>

        {loadError && <div className="alert" role="alert">{loadError}</div>}
        {cards && list.length === 0 && <div className="empty">
          <h3>找不到符合條件的補助</h3>
          <p>試試放寬篩選條件，或把您的需求提到訴求專區，讓更多人一起附議。</p>
          <div className="actions" style={{ justifyContent: "center" }}>
            <button className="btn sec" type="button" onClick={clearAll}>清除篩選條件</button>
            <button className="btn" type="button" onClick={() => onGap(query)}>我要提出訴求</button>
          </div>
        </div>}

        <div className="cards">
          {list.slice(0, shown).map(card => <BenefitCardView key={card.id} card={card} result={results?.[card.id]} saved={savedIds.has(card.id)} onOpen={onOpen} onToggleSave={onToggleSave} />)}
        </div>
        {list.length > shown && <div className="loadmore"><button type="button" className="btn sec" onClick={() => setShown(n => n + PAGE)}>顯示更多（還有 {list.length - shown} 項）</button></div>}
      </div>
    </div>
  </section>;
}
