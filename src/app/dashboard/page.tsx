"use client";
import { ageLabel } from '@/lib/questionnaire';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AssistantWidget from "@/components/AssistantWidget";
import ProfileWizard from "@/components/ProfileWizard";
import Sidebar from "@/components/Sidebar";
import OfficialBenefits from "@/components/OfficialBenefits";
import { matchResources } from "@/lib/matching";
import {
  addProfile,
  updateProfile,
  markNotificationsRead,
  removeProfile,
  setActiveProfileId,
  useActiveProfileId,
  useHydrated,
  useNotifications,
  useProfiles,
  useResources,
} from "@/lib/store";

export default function DashboardPage() {
  const router = useRouter();
  const hydrated = useHydrated();
  const profiles = useProfiles();
  const activeId = useActiveProfileId();
  const resources = useResources();
  const notifications = useNotifications();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const empty = hydrated && profiles.length === 0;

  useEffect(() => {
    if (empty) router.replace("/");
  }, [empty, router]);

  if (!hydrated || profiles.length === 0) return null;

  const active = profiles.find((p) => p.id === activeId) ?? profiles[0];
  const editing = profiles.find(p => p.id === editingId);
  const matches = matchResources(resources, active);
  const myNotifications = notifications.filter((n) => n.profileId === active.id);
  const unread = myNotifications.filter((n) => !n.read).length;

  return (
    <div className="flex min-h-dvh">
      <Sidebar
        profiles={profiles}
        activeId={active.id}
        notifications={notifications}
        onSelect={setActiveProfileId}
        onCreate={() => setCreating(true)}
        onRemove={removeProfile}
      />

      <main className="flex-1 overflow-y-auto">
        <header className="border-b border-slate-200 bg-white px-8 py-6">
          <div className="flex flex-wrap items-start gap-4">
            <div className="flex-1">
              <h1 className="text-2xl font-semibold tracking-tight">
                {active.nickname}
              </h1>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {[
                  active.region + (active.district ? ` ${active.district}` : ""),
                  ageLabel(active),
                  active.economy,
                  ...active.identities.filter((i) => i !== "以上皆非"),
                ].map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-ink-600"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <button type="button" onClick={() => setEditingId(active.id)} className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-brand-600 hover:bg-brand-50">編輯身分</button>
            {unread > 0 && (
              <button
                type="button"
                onClick={() => markNotificationsRead(active.id)}
                className="rounded-full bg-brand-100 px-3 py-1.5 text-xs font-medium text-brand-700"
              >
                {unread} 則新通知・點此標記已讀
              </button>
            )}
          </div>
          <p className="mt-3 text-sm text-ink-400">
            關注需求：{active.needs.join("、")}
          </p>
        </header>

        <div className="px-8 py-8">
          <OfficialBenefits key={JSON.stringify(active)} profile={active} />
          {myNotifications.length > 0 && (
            <section className="mb-8">
              <h2 className="mb-3 text-sm font-medium">主動通知</h2>
              <ul className="space-y-2">
                {myNotifications.map((n) => (
                  <li
                    key={n.id}
                    className={`rounded-xl border p-4 ${
                      n.read
                        ? "border-slate-200 bg-white"
                        : "border-brand-300 bg-brand-50"
                    }`}
                  >
                    <div className="text-sm font-medium">
                      新資源上架：{n.resourceTitle}
                    </div>
                    <div className="mt-1 text-xs text-ink-400">{n.reason}</div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section>
            <h2 className="mb-3 text-sm font-medium">符合的資源</h2>
            {matches.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-8 py-16 text-center">
                <p className="text-base font-medium">目前還沒有符合的資源</p>
                <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-ink-400">
                  資源清單還在建置中。如果不確定自己能申請什麼，
                  可以點右下角的助理聊聊，它會問幾個問題並把你的需求整理出來，
                  送給承辦人員評估。
                </p>
              </div>
            ) : (
              <ul className="grid gap-3 md:grid-cols-2">
                {matches.map(({ resource, reason }) => (
                  <li
                    key={resource.id}
                    className="rounded-xl border border-slate-200 bg-white p-5"
                  >
                    <div className="text-xs text-ink-400">{resource.agency}</div>
                    <div className="mt-1 font-medium">{resource.title}</div>
                    <p className="mt-2 text-sm leading-relaxed text-ink-600">
                      {resource.summary}
                    </p>
                    <p className="mt-3 text-xs text-brand-600">{reason}</p>
                    {resource.link && (
                      <a
                        href={resource.link}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-3 inline-block text-xs text-brand-600 underline"
                      >
                        前往申請頁面
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </main>

      <AssistantWidget key={JSON.stringify(active)} profile={active} />

      {(creating || editing) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
          <div className="flex h-[36rem] max-h-[calc(100dvh-2rem)] w-full max-w-xl flex-col rounded-2xl bg-white p-7 shadow-xl">
            <ProfileWizard
              key={editing?.id || "new"}
              initialProfile={editing}
              onCancel={() => { setCreating(false); setEditingId(null); }}
              onComplete={(draft) => {
                if (editing) updateProfile(editing.id, draft);
                else addProfile(draft);
                setEditingId(null);
                setCreating(false);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
