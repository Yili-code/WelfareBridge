"use client";

import { useSyncExternalStore } from "react";
import type { Appeal, Notification, Profile, Resource } from "./types";
import { matchReason } from "./matching";

/**
 * 原型階段的資料層：全部存在 localStorage。
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

export function addAppeal(input: Omit<Appeal, "id" | "createdAt" | "status">) {
  const appeal: Appeal = {
    ...input,
    id: uid("a"),
    status: "new",
    createdAt: new Date().toISOString(),
  };
  write(KEYS.appeals, [appeal, ...getAppeals()]);
  return appeal;
}

export function setAppealStatus(id: string, status: Appeal["status"]) {
  write(
    KEYS.appeals,
    getAppeals().map((a) => (a.id === id ? { ...a, status } : a)),
  );
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

export function useAppeals() {
  return useSyncExternalStore(subscribe, getAppeals, () => EMPTY_APPEALS);
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
