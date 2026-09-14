import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { api, errorMessage } from '../services/api';
import type { FieldSpec, MetaOptions, Option } from '../types';
import {
  AWARD_BASIS_LABELS,
  BENEFIT_FORM_LABELS,
  CATEGORY_LABELS,
  CHANNEL_LABELS,
  DISLIKE_LABELS,
  DOMAIN_LABELS,
  LEVEL_LABELS,
  NAMESPACE_LABELS,
  NEED_TYPE_LABELS,
  PROVIDER_TYPE_LABELS,
  optionLabel,
} from '../utils/labels';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

/** 依 deps 重新載入的簡易資料抓取 hook；忽略過期回應。 */
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const loaderRef = useRef(loader);
  useEffect(() => { loaderRef.current = loader; }, [loader]);

  useEffect(() => {
    let cancelled = false;
    Promise.resolve().then(() => {
      if (cancelled) return new Promise<T>(() => {});
      setLoading(true);
      setError(null);
      return loaderRef.current();
    })
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(errorMessage(err));
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { data, loading, error, reload };
}

let metaPromise: Promise<MetaOptions> | null = null;
let metaCache: MetaOptions | null = null;

export function loadMetaOptions(): Promise<MetaOptions> {
  if (metaCache) return Promise.resolve(metaCache);
  if (!metaPromise) {
    metaPromise = api
      .metaOptions()
      .then((options) => {
        metaCache = options;
        return options;
      })
      .catch((err: unknown) => {
        metaPromise = null;
        throw err;
      });
  }
  return metaPromise;
}

export type LabelKind = 'domain' | 'category' | 'provider_type' | 'benefit_form' | 'award_basis' | 'channel' | 'need_type' | 'dislike' | 'education_level' | 'namespace';

export interface Labels {
  /** 依種類把列舉值轉成中文（API 選項優先，備援表其次） */
  of: (kind: LabelKind, value: string | null | undefined) => string;
}

function makeLabels(options: MetaOptions | null): Labels {
  const fallback: Record<LabelKind, Record<string, string>> = {
    domain: DOMAIN_LABELS,
    category: CATEGORY_LABELS,
    provider_type: PROVIDER_TYPE_LABELS,
    benefit_form: BENEFIT_FORM_LABELS,
    award_basis: AWARD_BASIS_LABELS,
    channel: CHANNEL_LABELS,
    need_type: NEED_TYPE_LABELS,
    dislike: DISLIKE_LABELS,
    education_level: LEVEL_LABELS,
    namespace: options?.namespaces ?? NAMESPACE_LABELS,
  };
  const lists: Record<LabelKind, Option[] | undefined> = {
    domain: options?.domains,
    category: options?.categories,
    provider_type: options?.provider_types,
    benefit_form: options?.benefit_forms,
    award_basis: options?.award_basis,
    channel: options?.channels,
    need_type: options?.need_types,
    dislike: options?.dislikes,
    education_level: options?.education_levels,
    namespace: undefined,
  };
  return { of: (kind, value) => optionLabel(lists[kind], value, fallback[kind]) };
}

export interface MetaState {
  options: MetaOptions | null;
  loading: boolean;
  error: string | null;
  levelLabels: Record<string, string>;
  catalog: Record<string, FieldSpec> | null;
  cities: string[];
  labels: Labels;
}

/** /api/meta/options 共用快取（縣市、領域、類別、需求類型、欄位目錄...）。 */
export function useMetaOptions(): MetaState {
  const [options, setOptions] = useState<MetaOptions | null>(metaCache);
  const [loading, setLoading] = useState(!metaCache);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (metaCache) return;
    let cancelled = false;
    loadMetaOptions()
      .then((result) => {
        if (!cancelled) {
          setOptions(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(errorMessage(err));
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return useMemo(() => {
    const levelLabels: Record<string, string> = {};
    for (const item of options?.education_levels ?? []) levelLabels[item.value] = item.label;
    return {
      options,
      loading,
      error,
      levelLabels,
      catalog: options?.catalog ?? options?.field_catalog ?? null,
      cities: options?.cities ?? [],
      labels: makeLabels(options),
    };
  }, [options, loading, error]);
}

/** 週期性輪詢（delayMs=null 時停止）。 */
export function useInterval(callback: () => void, delayMs: number | null): void {
  const saved = useRef(callback);
  useEffect(() => { saved.current = callback; }, [callback]);
  useEffect(() => {
    if (delayMs === null) return;
    const id = window.setInterval(() => saved.current(), delayMs);
    return () => window.clearInterval(id);
  }, [delayMs]);
}
