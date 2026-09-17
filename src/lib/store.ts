"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import type { Appeal, Notification, Profile, Resource } from "./types";
import { matchReason } from "./matching";

/**
 * 資料層：需求登記使用伺服器 API，其餘資料仍存在 localStorage。
 * 之後接後端時，只要把這一層的讀寫換成 API 呼叫，UI 不需要改。
 *
 * 讀取結果會快取，讓同一份資料在沒有寫入時保持同一個參照，
 * 這樣才能直接餵給 useSyncExternalStore。
 */

const KEYS = {
  profiles: "wf.profiles",
  activeProfile: "wf.activeProfile",
  resources: "wf.resources",
  appeals: "wf.appeals",
  notifications: "wf.notifications",
  saved: "wf.saved",
} as const;

type Key = (typeof KEYS)[keyof typeof KEYS];

const EMPTY_PROFILES: Profile[] = [];
const EMPTY_RESOURCES: Resource[] = [];
const EMPTY_APPEALS: Appeal[] = [];
const EMPTY_NOTIFICATIONS: Notification[] = [];

const cache = new Map<Key, unknown>();
const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((fn) => fn());
}

function onStorage() {
  cache.clear();
  emit();
}

export function subscribe(fn: () => void) {
  if (listeners.size === 0 && typeof window !== "undefined") {
    window.addEventListener("storage", onStorage);
  }
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
    if (listeners.size === 0 && typeof window !== "undefined") {
      window.removeEventListener("storage", onStorage);
    }
  };
}

function read<T>(key: Key, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  if (cache.has(key)) return cache.get(key) as T;
  let value = fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (raw) value = JSON.parse(raw) as T;
  } catch {
    value = fallback;
  }
  cache.set(key, value);
  return value;
}

function write(key: Key, value: unknown) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
  cache.set(key, value);
  emit();
}

export function uid(prefix: string) {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}${Date.now()
    .toString(36)
    .slice(-4)}`;
}

/* ---------- profiles ---------- */

export function getProfiles(): Profile[] {
  return read<Profile[]>(KEYS.profiles, EMPTY_PROFILES);
}

export function addProfile(input: Omit<Profile, "id" | "createdAt">): Profile {
  const profile: Profile = {
    ...input,
    id: uid("p"),
    createdAt: new Date().toISOString(),
  };
  write(KEYS.profiles, [...getProfiles(), profile]);
  setActiveProfileId(profile.id);
  return profile;
}

export function updateProfile(id: string, patch: Partial<Profile>) {
  write(
    KEYS.profiles,
    getProfiles().map((p) => (p.id === id ? { ...p, ...patch } : p)),
  );
}

export function removeProfile(id: string) {
  const rest = getProfiles().filter((p) => p.id !== id);
  write(KEYS.profiles, rest);
  if (getActiveProfileId() === id) setActiveProfileId(rest[0]?.id ?? null);
}

export function getActiveProfileId(): string | null {
  return read<string | null>(KEYS.activeProfile, null);
}

export function setActiveProfileId(id: string | null) {
  write(KEYS.activeProfile, id);
}

/* ---------- resources ---------- */

export function getResources(): Resource[] {
  return read<Resource[]>(KEYS.resources, EMPTY_RESOURCES);
}

/**
 * 上架新資源。上架的同時比對所有 profile，
 * 符合條件者產生一筆主動通知。
 */
export function publishResource(
  input: Omit<Resource, "id" | "createdAt">,
): Resource {
  const resource: Resource = {
    ...input,
    id: uid("r"),
    createdAt: new Date().toISOString(),
  };
  write(KEYS.resources, [resource, ...getResources()]);

  const fresh: Notification[] = [];
  for (const profile of getProfiles()) {
    const reason = matchReason(resource, profile);
    if (!reason) continue;
    fresh.push({
      id: uid("n"),
      profileId: profile.id,
      profileNickname: profile.nickname,
      resourceId: resource.id,
      resourceTitle: resource.title,
      reason,
      read: false,
      createdAt: new Date().toISOString(),
    });
  }
  if (fresh.length) write(KEYS.notifications, [...fresh, ...getNotifications()]);
  return resource;
}

/* ---------- appeals ---------- */

export function getAppeals(): Appeal[] {
  return read<Appeal[]>(KEYS.appeals, EMPTY_APPEALS);
}

export async function addAppeal(input: Omit<Appeal, "id" | "createdAt" | "status">, key: string) {
  return appealRequest("POST", input, "", key);
}

async function appealRequest(method: string, input?: unknown, password = "", key = "") {
  const res = await fetch("/api/appeals", {
    method, cache: "no-store",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + password, "Idempotency-Key": key },
    body: input === undefined ? undefined : JSON.stringify(input),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.error || "無法連線到伺服器，請稍後重試。");
  }
  return res.json();
}

export async function setAppealStatus(id: string, status: Appeal["status"], password: string) {
  return appealRequest("PATCH", { id, status }, password);
}

/* ---------- 收藏清單（存在這台裝置，所有資料卡共用） ---------- */

export interface SavedBenefit { id: string; title: string; deadline: string; savedAt: string }
const EMPTY_SAVED: SavedBenefit[] = [];

export function getSaved(): SavedBenefit[] {
  return read<SavedBenefit[]>(KEYS.saved, EMPTY_SAVED);
}

/** 加入或移出收藏；回傳加入後是否在清單裡 */
export function toggleSaved(item: { id: string; title: string; deadline: string }): boolean {
  const current = getSaved();
  if (current.some(s => s.id === item.id)) {
    write(KEYS.saved, current.filter(s => s.id !== item.id));
    return false;
  }
  write(KEYS.saved, [...current, { id: item.id, title: item.title, deadline: item.deadline, savedAt: new Date().toISOString() }]);
  return true;
}

export function useSaved() {
  return useSyncExternalStore(subscribe, getSaved, () => EMPTY_SAVED);
}

/* ---------- notifications ---------- */

export function getNotifications(): Notification[] {
  return read<Notification[]>(KEYS.notifications, EMPTY_NOTIFICATIONS);
}

export function markNotificationsRead(profileId?: string) {
  write(
    KEYS.notifications,
    getNotifications().map((n) =>
      !profileId || n.profileId === profileId ? { ...n, read: true } : n,
    ),
  );
}

/* ---------- react hooks ---------- */

export function useProfiles() {
  return useSyncExternalStore(subscribe, getProfiles, () => EMPTY_PROFILES);
}

export function useActiveProfileId() {
  return useSyncExternalStore(
    subscribe,
    getActiveProfileId,
    () => null as string | null,
  );
}

export function useResources() {
  return useSyncExternalStore(subscribe, getResources, () => EMPTY_RESOURCES);
}

export function useAppeals(password: string) {
  const [snapshot, setSnapshot] = useState<{ password: string; appeals: Appeal[]; error: string }>({ password: "", appeals: [], error: "" });
  const [loading, setLoading] = useState(false);
  const [version, setVersion] = useState(0);
  useEffect(() => {
    if (!password) return;
    let active = true;
    const refresh = async () => {
      setLoading(true);
      try {
        const appeals = await appealRequest("GET", undefined, password);
        if (active) setSnapshot({ password, appeals, error: "" });
      } catch (e) {
        if (active) setSnapshot({ password, appeals: [], error: e instanceof Error ? e.message : "讀取失敗" });
      } finally { if (active) setLoading(false); }
    };
    void refresh();
    const timer = setInterval(refresh, 10000);
    return () => { active = false; clearInterval(timer); };
  }, [password, version]);
  return { appeals: password && snapshot.password === password ? snapshot.appeals : EMPTY_APPEALS, error: password && snapshot.password === password ? snapshot.error : "", loading: !!password && loading, refresh: () => setVersion(v => v + 1) };
}

export function useNotifications() {
  return useSyncExternalStore(
    subscribe,
    getNotifications,
    () => EMPTY_NOTIFICATIONS,
  );
}

const noopSubscribe = () => () => {};

/** 是否已經在瀏覽器端 hydrate 完成（localStorage 可讀） */
export function useHydrated() {
  return useSyncExternalStore(
    noopSubscribe,
    () => true,
    () => false,
  );
}
