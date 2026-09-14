import { useMemo, useState } from 'react';
import type { FieldSpec, Profile } from '../types';
import { CITIES_FALLBACK } from '../utils/labels';
import { formatUnit } from '../utils/format';
import { answeredCount, demoProfile, emptyProfile, getValue, groupCatalogByNamespace, namespaceLabel, setAttribute } from '../utils/profile';
import { Badge } from './Badge';
import { EmptyState } from './Feedback';
import { ChipSelect, Field, NumberInput, Select, TextInput, TriState, primaryButton, secondaryButton } from './FormControls';

interface Props {
  initial: Profile;
  catalog: Record<string, FieldSpec> | null;
  namespaces: Record<string, string> | null;
  cities: string[];
  domains: string[];
  busy: boolean;
  onSubmit: (profile: Profile) => void;
}

function FieldInput({ id, spec, value, cities, onChange }: { id: string; spec: FieldSpec; value: unknown; cities: string[]; onChange: (value: unknown) => void }) {
  switch (spec.type) {
    case 'number':
      return <NumberInput value={typeof value === 'number' ? value : null} onChange={onChange} placeholder={spec.unit ? `單位：${formatUnit(spec.unit)}` : undefined} />;
    case 'boolean':
      return <TriState value={typeof value === 'boolean' ? value : null} onChange={onChange} />;
    case 'single_choice':
      return <Select value={value === null || value === undefined ? null : String(value)} onChange={onChange} options={spec.options.map((option) => ({ value: String(option.value), label: option.label }))} />;
    case 'multi_choice':
      return <ChipSelect options={spec.options.map((option) => ({ value: String(option.value), label: option.label }))} selected={Array.isArray(value) ? value.map(String) : []} onChange={onChange} />;
    case 'city': {
      const list = spec.options.length ? spec.options.map((option) => ({ value: String(option.value), label: option.label })) : (cities.length ? cities : CITIES_FALLBACK).map((city) => ({ value: city, label: city }));
      return <Select value={typeof value === 'string' ? value : null} onChange={onChange} options={list} placeholder="請選擇縣市" />;
    }
    default:
      return <TextInput value={typeof value === 'string' ? value : null} onChange={onChange} placeholder={id === 'education.school' ? '例如 國立臺灣海洋大學' : undefined} />;
  }
}

export function ProfileForm({ initial, catalog, namespaces, cities, domains, busy, onSubmit }: Props) {
  const [profile, setProfile] = useState<Profile>(initial);
  const groups = useMemo(() => groupCatalogByNamespace(catalog, domains), [catalog, domains]);
  const set = (id: string, value: unknown) => setProfile((current) => setAttribute(current, id, value, 'form'));

  if (!catalog) return <EmptyState text="表單欄位目錄（/api/meta/options）尚未載入，請稍候或重新整理。" />;

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit(profile);
      }}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-slate-600">
          所有欄位都是選填；沒填的項目會顯示為「資料不足」，不會被判定為不符合。欄位由屬性登錄表（{Object.keys(catalog).length} 個屬性）動態產生
          {domains.length ? '，已依你選的領域縮減' : ''}。
        </p>
        <div className="flex gap-2">
          <button type="button" className={secondaryButton} onClick={() => setProfile(demoProfile())}>
            使用 Demo 範例
          </button>
          <button type="button" className={secondaryButton} onClick={() => setProfile(emptyProfile())}>
            清除
          </button>
        </div>
      </div>

      {groups.map((group) => (
        <details key={group.namespace} open className="rounded-lg border border-slate-200 bg-white">
          <summary className="cursor-pointer select-none px-4 py-2.5 text-sm font-semibold text-slate-800">
            {namespaceLabel(group.namespace, namespaces)} <span className="mono text-xs font-normal text-slate-400">{group.namespace}</span>
            <span className="ml-2 text-xs font-normal text-slate-500">{group.fields.filter(([id]) => getValue(profile, id) !== null).length} / {group.fields.length} 已填</span>
          </summary>
          <div className="grid gap-3 border-t border-slate-100 p-4 sm:grid-cols-2 lg:grid-cols-3">
            {group.fields.map(([id, spec]) => (
              <Field
                key={id}
                className={spec.type === 'multi_choice' ? 'sm:col-span-2 lg:col-span-3' : ''}
                label={
                  <span className="inline-flex flex-wrap items-center gap-1">
                    {spec.label}
                    {spec.unit ? <span className="text-slate-400">（{formatUnit(spec.unit)}）</span> : null}
                    {spec.sensitivity === 'high' ? <Badge tone="amber">敏感資料（選填）</Badge> : null}
                    {spec.hard_filter ? <span className="text-[10px] text-indigo-500" title="此屬性會用來做候選檢索（確定不符者直接排除）">檢索</span> : null}
                  </span>
                }
                hint={spec.help || spec.question}
              >
                <FieldInput id={id} spec={spec} value={getValue(profile, id)} cities={cities} onChange={(value) => set(id, value)} />
              </Field>
            ))}
          </div>
        </details>
      ))}

      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs text-slate-500">已填 {answeredCount(profile)} 項</span>
        <button type="submit" className={primaryButton} disabled={busy}>
          {busy ? '比對中…' : '開始比對'}
        </button>
      </div>
    </form>
  );
}
