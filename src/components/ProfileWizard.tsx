"use client";

import { useMemo, useState } from "react";
import {
  AGE_PRESETS,
  ECONOMY,
  IDENTITIES,
  NEEDS,
  REGIONS,
  RELATIONS,
} from "@/lib/options";
import type { Profile, Relation } from "@/lib/types";

type Draft = Omit<Profile, "id" | "createdAt">;

const EMPTY: Draft = {
  nickname: "",
  relation: "self",
  region: "",
  district: "",
  age: 0,
  identities: [],
  economy: "",
  needs: [],
};

const STEP_TITLES = [
  "這份檔案是為誰建立？",
  "住在哪裡？",
  "年齡是？",
  "有哪些身分或狀況？",
  "目前最需要哪方面的協助？",
];

const STEP_HINTS = [
  "之後可以再建立其他對象的檔案，例如孩子或長輩。",
  "很多補助以戶籍或居住地為條件，填了才找得準。",
  "年齡會決定托育、就學、長照等資源是否適用。",
  "可以複選，不確定的先跳過也沒關係。",
  "可以複選。之後有符合的新資源上架，我們會主動通知。",
];

function defaultNick(relation: Relation) {
  const map: Record<Relation, string> = {
    self: "我自己",
    child: "我的孩子",
    parent: "我的長輩",
    spouse: "我的配偶",
    other: "",
  };
  return map[relation];
}

function Chip({
  label,
  selected,
  onClick,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selected}
      className={`rounded-full border px-4 py-2 text-sm transition ${
        selected
          ? "border-brand-500 bg-brand-500 text-white shadow-sm"
          : "border-slate-200 bg-white text-ink-600 hover:border-brand-300 hover:bg-brand-50"
      }`}
    >
      {label}
    </button>
  );
}

export default function ProfileWizard({
  onComplete,
  onCancel,
}: {
  onComplete: (draft: Draft) => void;
  onCancel?: () => void;
}) {
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [customAge, setCustomAge] = useState("");

  const set = (patch: Partial<Draft>) => setDraft((d) => ({ ...d, ...patch }));

  const toggle = (key: "identities" | "needs", value: string) =>
    setDraft((d) => ({
      ...d,
      [key]: d[key].includes(value)
        ? d[key].filter((v) => v !== value)
        : [...d[key], value],
    }));

  const canNext = useMemo(() => {
    switch (step) {
      case 0:
        return draft.nickname.trim().length > 0;
      case 1:
        return draft.region.length > 0;
      case 2:
        return draft.age > 0;
      case 3:
        return draft.economy.length > 0;
      case 4:
        return draft.needs.length > 0;
      default:
        return false;
    }
  }, [step, draft]);

  const next = () => {
    if (step < STEP_TITLES.length - 1) setStep(step + 1);
    else onComplete({ ...draft, nickname: draft.nickname.trim() });
  };

  return (
    <div className="flex h-full flex-col">
      <div className="mb-6">
        <div
          className="flex gap-1.5"
          role="progressbar"
          aria-valuenow={step + 1}
          aria-valuemin={1}
          aria-valuemax={STEP_TITLES.length}
        >
          {STEP_TITLES.map((_, i) => (
            <span
              key={i}
              className={`h-1.5 flex-1 rounded-full transition ${
                i <= step ? "bg-brand-500" : "bg-slate-200"
              }`}
            />
          ))}
        </div>
        <p className="mt-3 text-xs text-ink-400">
          步驟 {step + 1} / {STEP_TITLES.length}
        </p>
      </div>

      <h2 className="text-2xl font-semibold tracking-tight">
        {STEP_TITLES[step]}
      </h2>
      <p className="mt-2 text-sm text-ink-400">{STEP_HINTS[step]}</p>

      <div className="mt-6 flex-1 animate-rise overflow-y-auto pr-1">
        {step === 0 && (
          <div className="space-y-5">
            <div className="grid gap-2 sm:grid-cols-2">
              {RELATIONS.map((r) => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() =>
                    set({
                      relation: r.value,
                      nickname:
                        draft.nickname &&
                        draft.nickname !== defaultNick(draft.relation)
                          ? draft.nickname
                          : defaultNick(r.value),
                    })
                  }
                  className={`rounded-xl border p-4 text-left transition ${
                    draft.relation === r.value
                      ? "border-brand-500 bg-brand-50"
                      : "border-slate-200 bg-white hover:border-brand-300"
                  }`}
                >
                  <div className="font-medium">{r.label}</div>
                  <div className="mt-1 text-xs text-ink-400">{r.hint}</div>
                </button>
              ))}
            </div>
            <label className="block">
              <span className="text-sm font-medium">這份檔案的稱呼</span>
              <input
                value={draft.nickname}
                onChange={(e) => set({ nickname: e.target.value })}
                placeholder="例如：我自己、兒子 小明、媽媽"
                className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 outline-none focus:border-brand-500"
              />
            </label>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-2">
              {REGIONS.map((r) => (
                <Chip
                  key={r}
                  label={r}
                  selected={draft.region === r}
                  onClick={() => set({ region: r })}
                />
              ))}
            </div>
            <label className="block">
              <span className="text-sm font-medium">鄉鎮市區（選填）</span>
              <input
                value={draft.district ?? ""}
                onChange={(e) => set({ district: e.target.value })}
                placeholder="例如：中正區"
                className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 outline-none focus:border-brand-500"
              />
            </label>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-2">
              {AGE_PRESETS.map((a) => (
                <Chip
                  key={a.label}
                  label={a.label}
                  selected={draft.age === a.age && customAge === ""}
                  onClick={() => {
                    setCustomAge("");
                    set({ age: a.age });
                  }}
                />
              ))}
            </div>
            <label className="block">
              <span className="text-sm font-medium">或直接填實際年齡</span>
              <input
                inputMode="numeric"
                value={customAge}
                onChange={(e) => {
                  const v = e.target.value.replace(/\D/g, "").slice(0, 3);
                  setCustomAge(v);
                  set({ age: v ? Number(v) : 0 });
                }}
                placeholder="例如：17"
                className="mt-2 block w-40 rounded-lg border border-slate-200 bg-white px-4 py-3 outline-none focus:border-brand-500"
              />
            </label>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <div>
              <p className="mb-3 text-sm font-medium">身分／狀況（可複選）</p>
              <div className="flex flex-wrap gap-2">
                {IDENTITIES.map((i) => (
                  <Chip
                    key={i}
                    label={i}
                    selected={draft.identities.includes(i)}
                    onClick={() => toggle("identities", i)}
                  />
                ))}
              </div>
            </div>
            <div>
              <p className="mb-3 text-sm font-medium">家庭經濟狀況</p>
              <div className="flex flex-wrap gap-2">
                {ECONOMY.map((e) => (
                  <Chip
                    key={e}
                    label={e}
                    selected={draft.economy === e}
                    onClick={() => set({ economy: e })}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="flex flex-wrap gap-2">
            {NEEDS.map((n) => (
              <Chip
                key={n}
                label={n}
                selected={draft.needs.includes(n)}
                onClick={() => toggle("needs", n)}
              />
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between border-t border-slate-200 pt-5">
        <button
          type="button"
          onClick={() => (step === 0 ? onCancel?.() : setStep(step - 1))}
          className="rounded-lg px-4 py-2.5 text-sm text-ink-400 transition hover:text-ink-600 disabled:invisible"
          disabled={step === 0 && !onCancel}
        >
          {step === 0 ? "取消" : "上一步"}
        </button>
        <button
          type="button"
          onClick={next}
          disabled={!canNext}
          className="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          {step === STEP_TITLES.length - 1 ? "完成建檔" : "下一步"}
        </button>
      </div>
    </div>
  );
}
