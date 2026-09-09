"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import ProfileWizard from "@/components/ProfileWizard";
import { addProfile, useHydrated, useProfiles } from "@/lib/store";

export default function EntryPage() {
  const router = useRouter();
  const [started, setStarted] = useState(false);
  const profiles = useProfiles();
  const hydrated = useHydrated();

  if (started) {
    return (
      <main className="mx-auto flex min-h-dvh w-full max-w-2xl flex-col px-6 py-10">
        <div className="flex min-h-[34rem] flex-1 flex-col rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <ProfileWizard
            onCancel={() => setStarted(false)}
            onComplete={(draft) => {
              addProfile(draft);
              router.push("/dashboard");
            }}
          />
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-2xl flex-col justify-center px-6 py-16">
      <span className="inline-flex w-fit items-center gap-2 rounded-full bg-brand-100 px-3 py-1 text-xs font-medium text-brand-700">
        福利資源導引平台
      </span>
      <h1 className="mt-6 text-4xl leading-tight font-semibold tracking-tight">
        找補助，不用先知道
        <br />
        它叫什麼名字
      </h1>
      <p className="mt-5 text-base leading-relaxed text-ink-600">
        回答幾個問題，建立一份屬於你的狀況檔案。系統會依照地區、身分與年齡幫你篩選可申請的福利；
        不知道怎麼找的時候，也可以直接和 AI 助理聊聊，由它幫你把需求整理出來。
      </p>

      <ul className="mt-8 space-y-3 text-sm text-ink-600">
        {[
          "一份檔案 = 一個服務對象，家人可以分別建檔",
          "找不到資源時，需求會送給承辦人員評估",
          "有新補助上架，符合條件就主動通知你",
        ].map((t) => (
          <li key={t} className="flex gap-3">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            {t}
          </li>
        ))}
      </ul>

      <div className="mt-10 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => setStarted(true)}
          className="rounded-lg bg-brand-500 px-7 py-3.5 font-medium text-white transition hover:bg-brand-600"
        >
          開始建立我的檔案
        </button>
        {hydrated && profiles.length > 0 && (
          <button
            type="button"
            onClick={() => router.push("/dashboard")}
            className="rounded-lg border border-slate-200 bg-white px-6 py-3.5 text-sm text-ink-600 transition hover:border-brand-300"
          >
            我已經建過檔案，直接進入
          </button>
        )}
      </div>

      <p className="mt-10 text-xs text-ink-400">
        全程不需要註冊，資料只留在你的裝置上。
      </p>
    </main>
  );
}
