"use client";

import { useState } from "react";
import { IDENTITIES, NEEDS, REGIONS } from "@/lib/options";
import {
  publishResource,
  setAppealStatus,
  useAppeals,
  useProfiles,
  useResources,
} from "@/lib/store";
import type { Appeal, Resource } from "@/lib/types";

const STATUS_LABEL: Record<Appeal["status"], string> = {
  new: "待處理",
  reviewing: "評估中",
  resolved: "已回應",
};

export default function AdminPage() {
  const [tab, setTab] = useState<"appeals" | "resources">("appeals");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [actionError, setActionError] = useState("");
  const { appeals, error, loading, refresh } = useAppeals(password);
  const resources = useResources();
  const profileCount = useProfiles().length;

  return (
    <div className="mx-auto min-h-dvh w-full max-w-5xl px-6 py-10">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">後台管理</h1>
          <p className="mt-1 text-sm text-ink-400">
            目前 {profileCount} 份使用者檔案・{appeals.length} 筆需求登記・
            {resources.length} 項已上架資源
          </p>
        </div>
        <a href="/dashboard" className="text-sm text-brand-600 hover:underline">
          ← 回到使用者介面
        </a>
      </header>

      <form className="mt-6 flex gap-2" onSubmit={e => { e.preventDefault(); setPassword(passwordInput); refresh(); }}>
        <input aria-label="後台密碼" type="password" autoComplete="current-password" placeholder="輸入後台密碼" value={passwordInput} onChange={e => setPasswordInput(e.target.value)} className="rounded border px-3 py-2" />
        <button type="submit" className="rounded border px-3 py-2">讀取需求</button>
        {password && <button type="button" onClick={() => { setPassword(""); setPasswordInput(""); }}>登出</button>}
      </form>
      <p className="mt-2 text-xs text-ink-400">需求登記由共用資料庫讀取，每 10 秒更新。資源管理與個人檔案目前仍儲存在此瀏覽器。</p>
      {(error || actionError) && <p role="alert" className="mt-2 text-sm text-red-700">{error || actionError}</p>}
      {loading && <p role="status">正在讀取需求…</p>}
      <nav className="mt-6 flex gap-1 border-b border-slate-200">
        {(
          [
            ["appeals", "需求登記"],
            ["resources", "資源上架"],
          ] as const
        ).map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`-mb-px border-b-2 px-4 py-2.5 text-sm transition ${
              tab === key
                ? "border-brand-500 font-medium text-brand-700"
                : "border-transparent text-ink-400 hover:text-ink-600"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {tab === "appeals" ? (
        <section className="mt-6 space-y-3">
          {appeals.length === 0 && (
            <p className="rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center text-sm text-ink-400">
              {!password ? "請輸入後台密碼查看需求。" : error ? "需求讀取失敗，請檢查密碼或連線。" : loading ? "讀取中…" : "還沒有需求登記。使用者送出需求後，會出現在這裡。"}
            </p>
          )}
          {appeals.map((a) => (
            <article
              key={a.id}
              className="rounded-xl border border-slate-200 bg-white p-5"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded-full px-2.5 py-1 text-xs ${
                    a.status === "new"
                      ? "bg-brand-100 text-brand-700"
                      : "bg-slate-100 text-ink-600"
                  }`}
                >
                  {STATUS_LABEL[a.status]}
                </span>
                <span className="text-sm font-medium">{a.mainRequest}</span>
                <span className="ml-auto text-xs text-ink-400">
                  {new Date(a.createdAt).toLocaleString("zh-TW")}
                </span>
              </div>

              <dl className="mt-3 grid gap-x-6 gap-y-1 text-xs text-ink-600 sm:grid-cols-4">
                <div>
                  <dt className="text-ink-400">對象</dt>
                  <dd>{a.profileNickname}</dd>
                </div>
                <div>
                  <dt className="text-ink-400">地區</dt>
                  <dd>{a.region}</dd>
                </div>
                <div>
                  <dt className="text-ink-400">年齡</dt>
                  <dd>{a.age != null ? `${a.age} 歲` : "未填"}</dd>
                </div>
                <div>
                  <dt className="text-ink-400">身分</dt>
                  <dd>
                    {a.identities.filter((i) => i !== "以上皆非").join("、") ||
                      "未註記"}
                  </dd>
                </div>
              </dl>

              <pre className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-relaxed whitespace-pre-wrap text-ink-600">
                {a.summary}
              </pre>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                {(["new", "reviewing", "resolved"] as const).map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={async () => { try { setActionError(""); await setAppealStatus(a.id, s, password); refresh(); } catch (e) { setActionError(e instanceof Error ? e.message : "更新失敗"); } }}
                    className={`rounded-full border px-3 py-1 text-xs transition ${
                      a.status === s
                        ? "border-brand-500 text-brand-700"
                        : "border-slate-200 text-ink-400 hover:border-brand-300"
                    }`}
                  >
                    {STATUS_LABEL[s]}
                  </button>
                ))}
                <button
                  type="button"
                  onClick={() => setExpanded(expanded === a.id ? null : a.id)}
                  className="ml-auto text-xs text-brand-600 hover:underline"
                >
                  {expanded === a.id ? "收合對話紀錄" : "查看對話紀錄"}
                </button>
              </div>

              {expanded === a.id && (
                <ul className="mt-3 space-y-1.5 border-t border-slate-200 pt-3">
                  {a.transcript.map((t, i) => (
                    <li key={i} className="text-xs leading-relaxed">
                      <span className="text-ink-400">
                        {t.role === "user" ? "使用者" : "助理"}：
                      </span>
                      <span className="whitespace-pre-wrap text-ink-600">
                        {t.text}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </section>
      ) : (
        <ResourcesTab resources={resources} />
      )}
    </div>
  );
}

function ResourcesTab({ resources }: { resources: Resource[] }) {
  const [title, setTitle] = useState("");
  const [agency, setAgency] = useState("");
  const [summary, setSummary] = useState("");
  const [link, setLink] = useState("");
  const [regions, setRegions] = useState<string[]>(["全國"]);
  const [identities, setIdentities] = useState<string[]>([]);
  const [needs, setNeeds] = useState<string[]>([]);
  const [minAge, setMinAge] = useState("");
  const [maxAge, setMaxAge] = useState("");
  const [flash, setFlash] = useState("");

  const toggle = (
    list: string[],
    setList: (v: string[]) => void,
    value: string,
  ) =>
    setList(
      list.includes(value) ? list.filter((v) => v !== value) : [...list, value],
    );

  const submit = () => {
    if (!title.trim()) return;
    publishResource({
      title: title.trim(),
      agency: agency.trim() || "未填寫單位",
      summary: summary.trim(),
      link: link.trim() || undefined,
      regions,
      identities,
      needs,
      minAge: minAge ? Number(minAge) : undefined,
      maxAge: maxAge ? Number(maxAge) : undefined,
    });
    setFlash(`已上架「${title.trim()}」，符合條件的使用者已收到通知。`);
    setTitle("");
    setAgency("");
    setSummary("");
    setLink("");
    setIdentities([]);
    setNeeds([]);
    setMinAge("");
    setMaxAge("");
  };

  const chip = (label: string, on: boolean, onClick: () => void) => (
    <button
      key={label}
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3 py-1.5 text-xs transition ${
        on
          ? "border-brand-500 bg-brand-500 text-white"
          : "border-slate-200 text-ink-600 hover:border-brand-300"
      }`}
    >
      {label}
    </button>
  );

  return (
    <section className="mt-6 grid gap-6 lg:grid-cols-2">
      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-medium">上架新資源</h2>
        <p className="mt-1 text-xs text-ink-400">
          上架後系統會立刻比對所有使用者檔案，符合條件者收到主動通知。
        </p>

        <div className="mt-4 space-y-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="資源名稱，例如：高中職學生就學補助"
            className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-brand-500"
          />
          <input
            value={agency}
            onChange={(e) => setAgency(e.target.value)}
            placeholder="主辦單位"
            className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-brand-500"
          />
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="補助內容摘要"
            rows={3}
            className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-brand-500"
          />
          <input
            value={link}
            onChange={(e) => setLink(e.target.value)}
            placeholder="申請連結（選填）"
            className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-brand-500"
          />
          <div className="flex gap-3">
            <input
              inputMode="numeric"
              value={minAge}
              onChange={(e) => setMinAge(e.target.value.replace(/\D/g, ""))}
              placeholder="最小年齡"
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-brand-500"
            />
            <input
              inputMode="numeric"
              value={maxAge}
              onChange={(e) => setMaxAge(e.target.value.replace(/\D/g, ""))}
              placeholder="最大年齡"
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <p className="mb-2 text-xs text-ink-400">適用地區</p>
            <div className="flex flex-wrap gap-1.5">
              {["全國", ...REGIONS].map((r) =>
                chip(r, regions.includes(r), () =>
                  toggle(regions, setRegions, r),
                ),
              )}
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs text-ink-400">適用身分（不選＝不限）</p>
            <div className="flex flex-wrap gap-1.5">
              {IDENTITIES.filter((i) => i !== "以上皆非").map((i) =>
                chip(i, identities.includes(i), () =>
                  toggle(identities, setIdentities, i),
                ),
              )}
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs text-ink-400">對應需求（不選＝不限）</p>
            <div className="flex flex-wrap gap-1.5">
              {NEEDS.map((n) =>
                chip(n, needs.includes(n), () => toggle(needs, setNeeds, n)),
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={submit}
            disabled={!title.trim()}
            className="w-full rounded-lg bg-brand-500 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:bg-slate-200 disabled:text-slate-400"
          >
            上架並通知符合的使用者
          </button>
          {flash && <p className="text-xs text-brand-600">{flash}</p>}
        </div>
      </div>

      <div>
        <h2 className="text-sm font-medium">已上架資源</h2>
        <ul className="mt-3 space-y-2">
          {resources.length === 0 && (
            <li className="rounded-xl border border-dashed border-slate-300 bg-white px-5 py-10 text-center text-sm text-ink-400">
              尚未上架任何資源。
            </li>
          )}
          {resources.map((r) => (
            <li
              key={r.id}
              className="rounded-xl border border-slate-200 bg-white p-4"
            >
              <div className="text-xs text-ink-400">{r.agency}</div>
              <div className="mt-0.5 text-sm font-medium">{r.title}</div>
              <div className="mt-1.5 text-xs text-ink-400">
                {r.regions.join("、")}
                {r.identities.length > 0 && `・${r.identities.join("、")}`}
                {(r.minAge != null || r.maxAge != null) &&
                  `・${r.minAge ?? 0}–${r.maxAge ?? "不限"} 歲`}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
