"use client";
import Link from "next/link";
import { ageLabel } from '@/lib/questionnaire';

import type { Notification, Profile } from "@/lib/types";

export default function Sidebar({
  profiles,
  activeId,
  notifications,
  onSelect,
  onCreate,
  onRemove,
}: {
  profiles: Profile[];
  activeId: string | null;
  notifications: Notification[];
  onSelect: (id: string) => void;
  onCreate: () => void;
  onRemove: (id: string) => void;
}) {
  const unreadFor = (id: string) =>
    notifications.filter((n) => n.profileId === id && !n.read).length;

  return (
    <aside className="flex w-72 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="px-5 py-6">
        <div className="text-sm font-semibold tracking-tight">福利資源導引</div>
        <p className="mt-1 text-xs text-ink-400">切換對象，看不同的資源</p>
      </div>

      <div className="flex-1 overflow-y-auto px-3">
        <p className="px-2 pb-2 text-xs font-medium text-ink-400">服務對象</p>
        <ul className="space-y-1">
          {profiles.map((p) => {
            const unread = unreadFor(p.id);
            const active = p.id === activeId;
            return (
              <li key={p.id} className="group relative">
                <button
                  type="button"
                  onClick={() => onSelect(p.id)}
                  className={`w-full rounded-lg px-3 py-3 text-left transition ${
                    active
                      ? "bg-brand-50 ring-1 ring-brand-300"
                      : "hover:bg-slate-50"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="truncate text-sm font-medium">
                      {p.nickname}
                    </span>
                    {unread > 0 && (
                      <span className="ml-auto rounded-full bg-brand-500 px-1.5 py-0.5 text-[10px] font-medium text-white">
                        {unread}
                      </span>
                    )}
                  </div>
                  <div className="mt-1 truncate text-xs text-ink-400">
                    {p.region}・{ageLabel(p)}
                    {p.identities.length > 0 &&
                      `・${p.identities.filter((i) => i !== "以上皆非").slice(0, 2).join("、")}`}
                  </div>
                </button>
                {profiles.length > 1 && (
                  <button
                    type="button"
                    aria-label={`刪除 ${p.nickname}`}
                    onClick={() => onRemove(p.id)}
                    className="absolute top-2 right-2 hidden rounded px-1.5 text-xs text-ink-400 hover:text-red-500 group-hover:block"
                  >
                    ×
                  </button>
                )}
              </li>
            );
          })}
        </ul>

        <button
          type="button"
          onClick={onCreate}
          className="mt-3 w-full rounded-lg border border-dashed border-slate-300 px-3 py-3 text-sm text-ink-400 transition hover:border-brand-300 hover:text-brand-600"
        >
          ＋ 新增服務對象
        </button>

        <p className="mt-3 px-2 text-[11px] leading-relaxed text-ink-400">
          例如：想知道 17 歲的孩子能申請什麼，就替孩子單獨建一份檔案。
        </p>
      </div>

      <div className="border-t border-slate-200 px-5 py-4">
        <Link href="/data-center" className="mb-3 block text-xs text-brand-600">官方補助資料中心 →</Link>
        <a href="/my-benefits" className="mb-3 block text-xs text-brand-600">完整資格媒合 →</a>
        <a
          href="/admin"
          className="text-xs text-ink-400 transition hover:text-brand-600"
        >
          後台（需求登記與資源管理）→
        </a>
      </div>
    </aside>
  );
}
