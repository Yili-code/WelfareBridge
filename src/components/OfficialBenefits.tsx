"use client";
import { useEffect, useState } from "react";
import type { Profile } from "@/lib/types";
import type { MatchResponse } from "@/benefits/types";
import { toBenefitProfile } from "@/lib/benefit-profile";

const labels: Record<string, string> = { high_match: "初步符合", possible_match: "可能符合", insufficient_data: "需補充資料" };
export default function OfficialBenefits({ profile }: { profile: Profile }) {
 const [result, setResult] = useState<MatchResponse | null>(null);
 const [error, setError] = useState("");
 const [attempt, setAttempt] = useState(0);
 useEffect(() => {
  const controller = new AbortController();
  fetch("/api/matching", { method: "POST", headers: { "Content-Type": "application/json" },
   body: JSON.stringify({ profile: toBenefitProfile(profile), use_llm: false, limit: 2000 }),
   signal: controller.signal,
  }).then(async response => {
   if (!response.ok) throw new Error("補助資料服務暫時無法連線，請稍後重試。");
   const data = await response.json();
   if (!Array.isArray(data.matches)) throw new Error("補助資料格式不完整。");
   setResult(data);
  }).catch(err => { if (!controller.signal.aborted) setError(err.message); });
  return () => controller.abort();
 }, [profile, attempt]);
 const matches = result?.matches.filter(item => item.status !== "not_match") ?? [];
 matches.sort((a, b) => b.eligibility_score - a.eligibility_score);
 return <section className="mb-8" aria-label="官方補助媒合">
  <div className="mb-3 flex items-center justify-between gap-3">
   <h2 className="text-sm font-medium">官方補助・初步資格比對</h2>
   <a href="/my-benefits" className="text-xs text-brand-600 underline">補充條件與完整媒合</a>
  </div>
  <p className="mb-4 text-xs leading-relaxed text-ink-400">依已填寫的明確條件比對。年齡區間與不確定的答案仍保留為待確認，實際資格以主辦機關審核為準。</p>
  {error ? <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm">{error}<button className="ml-3 underline" onClick={() => { setError(""); setResult(null); setAttempt(value => value + 1); }}>重試</button></div>
   : !result ? <p role="status" className="text-sm text-ink-400">正在比對官方補助資料…</p>
   : matches.length === 0 ? <p className="text-sm text-ink-400">目前資料中沒有可推薦項目，可至資料中心查閱所有方案。</p>
   : <ul className="grid gap-3 md:grid-cols-2">{matches.slice(0, 6).map(item => <li key={item.benefit_id} className="rounded-xl border border-slate-200 bg-white p-5">
    <div className="flex justify-between gap-3 text-xs text-ink-400"><span>{item.provider}</span><span>{labels[item.status] || "待確認"}</span></div>
    <h3 className="mt-2 font-medium">{item.title}</h3>
    <p className="mt-2 text-xs leading-relaxed text-ink-600">{item.explanation.slice(0, 2).join("；")}</p>
    <a href={`/data-center/${encodeURIComponent(item.benefit_id)}`} className="mt-3 inline-block text-xs text-brand-600 underline">查看條件與官方來源</a>
   </li>)}</ul>}
 </section>;
}
