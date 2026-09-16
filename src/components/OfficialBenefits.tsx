"use client";
import { useEffect, useState } from "react";
import type { Profile } from "@/lib/types";
import type { MatchItem, MatchResponse } from "@/benefits/types";
import { toMatchingProfile } from "@/lib/benefit-profile";
import { officialRecommendations, residenceMismatch } from "@/lib/official-recommendations";

function BenefitCard({ item, tier }: { item: MatchItem; tier: "tier1" | "tier2" }) {
 const needs = item.needs_labels ?? [];
 const elsewhere = residenceMismatch(item);
 return <li className="rounded-xl border border-slate-200 bg-white p-5">
  <div className="flex justify-between gap-3 text-xs text-ink-400"><span>{item.provider}</span><span>{tier === "tier1" ? "✅ 符合" : "🟡 可能符合"}</span></div>
  <h3 className="mt-2 font-medium">{item.title}</h3>
  <p className="mt-2 text-xs leading-relaxed text-ink-600">{item.explanation.slice(0, 2).join("；")}</p>
  {elsewhere && <p className="mt-2 text-xs text-amber-700">此方案可能限「{elsewhere}」，與你填的戶籍縣市不同</p>}
  {tier === "tier2" && needs.length > 0 && <p className="mt-2 text-xs text-amber-700">需補充：{needs.slice(0, 4).join("、")}</p>}
  <a href={`/data-center/${encodeURIComponent(item.benefit_id)}`} className="mt-3 inline-block text-xs text-brand-600 underline">查看條件與官方來源</a>
 </li>;
}

export default function OfficialBenefits({ profile }: { profile: Profile }) {
 const [result, setResult] = useState<MatchResponse | null>(null);
 const [error, setError] = useState("");
 const [attempt, setAttempt] = useState(0);
 useEffect(() => {
  const controller = new AbortController();
  fetch("/api/matching", { method: "POST", headers: { "Content-Type": "application/json" },
   body: JSON.stringify({ profile: toMatchingProfile(profile), use_llm: false, limit: 2000 }),
   signal: controller.signal,
  }).then(async response => {
   if (!response.ok) throw new Error("補助資料服務暫時無法連線，請稍後重試。");
   const data = await response.json();
   if (!Array.isArray(data.matches)) throw new Error("補助資料格式不完整。");
   setResult(data);
  }).catch(err => { if (!controller.signal.aborted) setError(err.message); });
  return () => controller.abort();
 }, [profile, attempt]);
 const { confirmed, needsInfo, pending } = officialRecommendations(result, profile);
 return <section className="mb-8" aria-label="官方補助媒合">
  <div className="mb-3 flex items-center justify-between gap-3">
   <h2 className="text-sm font-medium">官方補助・初步資格比對</h2>
   <a href="/my-benefits" className="text-xs text-brand-600 underline">補充條件與完整媒合</a>
  </div>
  <p className="mb-4 text-xs leading-relaxed text-ink-400">依你選擇的需求「{profile.needs.join('、') || '尚未選擇'}」篩選。「符合」表示戶籍、年齡、學制、身分等主要資格都已比對相符；「可能符合」表示還缺少部分資料才能確認。實際資格仍以主辦機關審核為準。</p>
  {result && pending > 0 && <p className="mb-3 text-sm text-amber-700">另有 {pending} 筆相關補助缺少判斷資料，請點「補充條件與完整媒合」。</p>}
  {error ? <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm">{error}<button className="ml-3 underline" onClick={() => { setError(""); setResult(null); setAttempt(value => value + 1); }}>重試</button></div>
   : !result ? <p role="status" className="text-sm text-ink-400">正在比對官方補助資料…</p>
   : confirmed.length + needsInfo.length === 0 ? <p className="text-sm text-ink-400">目前沒有足夠依據推薦符合這些需求的方案。請補充資格條件，或編輯身分調整需求；這不代表沒有補助可申請。</p>
   : <div className="space-y-5">
    {confirmed.length > 0 && <div>
     <h3 className="mb-2 text-sm font-medium text-emerald-700">✅ 符合（{confirmed.length}）</h3>
     <ul className="grid gap-3 md:grid-cols-2">{confirmed.slice(0, 6).map(item => <BenefitCard key={item.benefit_id} item={item} tier="tier1" />)}</ul>
    </div>}
    {needsInfo.length > 0 && <div>
     <h3 className="mb-2 text-sm font-medium text-amber-700">🟡 可能符合・需補充資料（{needsInfo.length}）</h3>
     <ul className="grid gap-3 md:grid-cols-2">{needsInfo.slice(0, confirmed.length ? 4 : 6).map(item => <BenefitCard key={item.benefit_id} item={item} tier="tier2" />)}</ul>
     {needsInfo.length > (confirmed.length ? 4 : 6) && <a href="/my-benefits" className="mt-2 inline-block text-xs text-brand-600 underline">查看全部 {needsInfo.length} 筆並補充資料</a>}
    </div>}
   </div>}
 </section>;
}
