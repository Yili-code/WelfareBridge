"use client";
import { useState } from "react";
import { useProfiles } from "@/lib/store";
import { toBenefitProfile } from "@/lib/benefit-profile";

type Condition = { rule_id: string; group_id: string; attribute_id: string; human_readable: string; operator: string; value: unknown; user_value: unknown; reason: string; excerpt: string; confidence: number; inferred: boolean; status: string };
type Item = { benefit_id: string; title: string; status: string; source_url: string; explanation: string[]; retrieval_exclusions: string[]; ranking_stage: string; ranking_reasons: string[]; rule_count: number; matched_conditions: Condition[]; missing_conditions: Condition[]; failed_conditions: Condition[]; complex_conditions: Condition[]; bonus_conditions: Condition[] };
type Report = { items: Item[]; total: number; returned: number; truncated: boolean; profile_used: unknown; profile_notes: string[] };
const labels: Record<string, string> = { high_match: "初步符合", possible_match: "可能符合", insufficient_data: "資料不足", not_match: "條件不符", match: "符合", unknown: "未知", eligible: "可列入推薦", removed_deadline: "截止時間篩除", removed_exclusive: "兼領限制篩除", removed_need: "需求不符", removed_dislike: "偏好篩除", other_need: "其他需求", not_ranked: "未進入推薦排序" };
const value = (v: unknown) => v == null ? "未提供" : typeof v === "boolean" ? v ? "是" : "否" : JSON.stringify(v);

export default function MatchingDiagnostics() {
 const profiles = useProfiles();
 const [id, setId] = useState(profiles[0]?.id || "");
 const [search, setSearch] = useState("");
 const [report, setReport] = useState<Report | null>(null);
 const [snapshot, setSnapshot] = useState("");
 const [error, setError] = useState("");
 const [busy, setBusy] = useState(false);
 const profile = profiles.find(p => p.id === id);
 async function run() {
  if (!profile || busy) return;
  setBusy(true); setError(""); setReport(null);
  setSnapshot(JSON.stringify(profile, null, 2));
  try {
   const response = await fetch('/api/matching/diagnose', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ profile: toBenefitProfile(profile), search }), signal: AbortSignal.timeout(60000) });
   if (!response.ok) throw new Error("無法取得診斷，請確認後端已更新並啟動。");
   setReport(await response.json());
  } catch (e) { setError(e instanceof Error ? e.message : "診斷失敗"); }
  finally { setBusy(false); }
 }
 return <section className="mt-6 space-y-4">
  <h2 className="text-lg font-semibold">為什麼沒有配對到？</h2>
  <p className="text-sm text-ink-400">選擇此瀏覽器的身分，用目前資料與規則重新檢查；不讀取其他使用者的歷史紀錄，也不寫入媒合紀錄。本次不使用 LLM。</p>
  <div className="flex flex-wrap gap-3">
   <label className="text-sm">檢查對象<select aria-label="檢查對象" disabled={busy} value={id} onChange={e => { setId(e.target.value); setReport(null); }} className="ml-2 rounded border p-2"><option value="">選擇身分</option>{profiles.map(p => <option key={p.id} value={p.id}>{p.nickname}</option>)}</select></label>
   <input aria-label="補助名稱" placeholder="輸入配不到的補助名稱" value={search} disabled={busy} onChange={e => { setSearch(e.target.value); setReport(null); }} className="min-w-64 rounded border px-3 py-2" />
   <button disabled={!profile || busy} onClick={() => void run()} className="rounded bg-brand-500 px-4 py-2 text-white disabled:opacity-50">{busy ? "檢查中…" : "開始診斷"}</button>
  </div>
  {!profiles.length && <p>此瀏覽器尚未建立身分，請先到首頁建檔。</p>}
  {error && <p role="alert" className="text-red-700">{error}</p>}
  {report && <>
   <details className="rounded border p-4"><summary className="cursor-pointer font-medium">檢查問卷原始答案與引擎收到的條件</summary><div className="mt-3 grid gap-4 md:grid-cols-2"><div><h3>問卷快照</h3><pre className="overflow-auto whitespace-pre-wrap text-xs">{snapshot}</pre></div><div><h3>引擎實際條件（沒有的欄位視為未知）</h3><pre className="overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(report.profile_used, null, 2)}</pre>{report.profile_notes.map(n => <p key={n}>{n}</p>)}</div></div></details>
   <p className="text-sm">找到 {report.total} 筆，顯示 {report.returned} 筆。{report.truncated && "結果超過上限，請輸入更完整的補助名稱。"}</p>
   {!report.total && <p>資料庫沒有找到這個名称，請縮短關鍵字，或到資料中心確認是否已爬取。</p>}
   <p className="text-xs text-ink-400">同組條件是 OR、不同組是 AND。通過資格仍可能因前台只顯示前六筆而看不到；這裡不重現前台名次或 AI 判斷。</p>
   {report.items.map(item => <details key={item.benefit_id} className="rounded-xl border bg-white p-4">
    <summary className="cursor-pointer font-medium">{item.title} · {item.retrieval_exclusions.length ? "候選檢索已排除" : labels[item.status]}</summary>
    <div className="mt-3 space-y-3 text-sm">
     {[...item.retrieval_exclusions, ...item.explanation].map((reason, i) => <p key={i}>{reason}</p>)}
     {!item.rule_count && <p className="text-amber-700">沒有抽取到資格規則，無法確認是否符合。請檢查官方原文與資料處理結果。</p>}
     <p>推薦階段：{labels[item.ranking_stage] || item.ranking_stage}（獨立評估；被候選檢索排除者不會實際進入推薦）</p>
     {item.ranking_reasons.map((r, i) => <p key={i}>{r}</p>)}
     <div className="overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr>{['群組／欄位', '資格要求', '使用者值', '判斷與證據'].map(h => <th key={h} className="border-b p-2">{h}</th>)}</tr></thead><tbody>{[...item.matched_conditions, ...item.missing_conditions, ...item.failed_conditions, ...item.complex_conditions, ...item.bonus_conditions].map((c, i) => <tr key={`${c.rule_id}-${i}`}><td className="border-b p-2">{c.group_id}<br />{c.attribute_id}</td><td className="border-b p-2">{c.human_readable}<br />{c.operator} {value(c.value)}</td><td className="border-b p-2">{value(c.user_value)}</td><td className="border-b p-2">{labels[c.status] || c.status}：{c.reason}<br />抽取信心 {c.confidence} · {c.inferred ? '推定條件' : '非推定'}<blockquote className="mt-1 text-ink-400">{c.excerpt || '未附原文證據'}</blockquote></td></tr>)}</tbody></table></div>
     <a href={`/data-center/${encodeURIComponent(item.benefit_id)}`} className="text-brand-600 underline">檢查補助資料與規則</a>
     {/^https?:\/\//.test(item.source_url) && <a href={item.source_url} target="_blank" rel="noreferrer" className="ml-4 text-brand-600 underline">官方原文</a>}
    </div>
   </details>)}
  </>}
 </section>;
}
