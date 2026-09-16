import { useCallback, useState } from 'react';
import { getActiveProfileId, getProfiles } from '@/lib/store';
import { toMatchingProfile } from '@/lib/benefit-profile';
import { ErrorBox, Notice } from '../components/Feedback';
import { EMPTY_NEEDS, NeedsHeader, type Needs } from '../components/NeedsHeader';
import { ProfileForm } from '../components/ProfileForm';
import { QuickInput } from '../components/QuickInput';
import { ResultsView } from '../components/ResultsView';
import { StepWizard } from '../components/StepWizard';
import { useMetaOptions } from '../hooks/useApi';
import { api, errorMessage } from '../services/api';
import type { InputMode, MatchResponse, Profile } from '../types';
import { CITIES_FALLBACK, DISCLAIMER } from '../utils/labels';
import { applyAnswer, emptyProfile } from '../utils/profile';

const MODES: Array<{ id: InputMode; label: string; description: string; icon: string }> = [
  { id: 'form', label: '完整填寫', description: '依屬性登錄表一次填好，結果最完整', icon: '📝' },
  { id: 'step', label: '逐步回答', description: '一次一題，回答到哪比對到哪', icon: '🪜' },
  { id: 'quick', label: '快速輸入', description: '用一句話描述，系統幫你整理', icon: '⚡' },
];

export default function MyBenefitsPage() {
  const { options, catalog, cities: apiCities, labels, error: metaError } = useMetaOptions();
  const [mode, setMode] = useState<InputMode>('form');
  const [needs, setNeeds] = useState<Needs>(EMPTY_NEEDS);
  const [domains, setDomains] = useState<string[]>([]);
  const [profile, setProfile] = useState<Profile>(() => { const profiles = getProfiles(); const selected = profiles.find(item => item.id === getActiveProfileId()) ?? profiles[0]; let initial = emptyProfile(); if (selected) for (const [id, value] of Object.entries(toMatchingProfile(selected).attributes)) initial = applyAnswer(initial, id, value); return initial; });
  const [rawInput, setRawInput] = useState('');
  const [lastMode, setLastMode] = useState<InputMode>('form');
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [view, setView] = useState<'input' | 'results'>('input');
  const [matching, setMatching] = useState(false);
  const [matchError, setMatchError] = useState<string | null>(null);
  const [useLlm, setUseLlm] = useState(true);

  const cities = apiCities.length ? apiCities : CITIES_FALLBACK;

  /** 把共用的需求資訊合併進 profile；快速輸入若解析出需求類型且使用者沒選，沿用解析結果。 */
  const withNeeds = useCallback(
    (base: Profile): Profile => ({
      ...base,
      need_type: needs.need_type !== 'unknown' ? needs.need_type : base.need_type || 'unknown',
      dislikes: needs.dislikes,
      current_benefits: needs.current_benefits,
    }),
    [needs],
  );

  const runMatch = useCallback(
    async (nextProfile: Profile, inputMode: InputMode, raw = '') => {
      const merged = withNeeds(nextProfile);
      setMatching(true);
      setMatchError(null);
      setProfile(merged);
      setLastMode(inputMode);
      setRawInput(raw);
      try {
        const response = await api.runMatching({ profile: merged, input_mode: inputMode, raw_input: raw, include_expired: false, use_llm: useLlm, domains: domains.length ? domains : null, user_id: result?.user_id });
        setResult(response);
        setView('results');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (err) {
        setMatchError(errorMessage(err));
      } finally {
        setMatching(false);
      }
    },
    [withNeeds, domains, useLlm, result],
  );

  const supplement = (attributeId: string, value: unknown) => {
    void runMatch(applyAnswer(profile, attributeId, value), lastMode, rawInput);
  };

  const extras = [
    ...(profile.need_type && profile.need_type !== 'unknown' ? [{ label: '需求類型', value: labels.of('need_type', profile.need_type) }] : []),
    ...(profile.dislikes.length ? [{ label: '不想要', value: profile.dislikes.map((d) => labels.of('dislike', d)).join('、') }] : []),
    ...(profile.current_benefits.length ? [{ label: '已領補助', value: profile.current_benefits.join('、') }] : []),
    ...(domains.length ? [{ label: '領域', value: domains.map((d) => labels.of('domain', d)).join('、') }] : []),
  ];

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-gradient-to-r from-indigo-600 to-emerald-500 px-6 py-8 text-white shadow-md">
        <h1 className="text-2xl font-bold sm:text-3xl">找到你可能符合的補助</h1>
        <p className="mt-2 text-sm text-indigo-50 sm:text-base">請告訴我們一些資料，系統會依官方公告抽出的資格規則逐條比對，說明每一項符合或不符合的原因，並依你的需求排出最值得申請的順序。</p>
        <p className="mt-3 inline-block rounded-md bg-white/15 px-3 py-1 text-xs text-white/90">{DISCLAIMER}</p>
      </section>

      {metaError ? <Notice tone="warn">無法載入表單選項（{metaError}），部分欄位將無法顯示；請確認後端是否在線。</Notice> : null}
      {matchError ? <ErrorBox title="比對失敗" message={matchError} /> : null}

      {view === 'results' && result ? (
        <ResultsView result={result} catalog={catalog} cities={cities} labels={labels} extras={extras} busy={matching} onEdit={() => setView('input')} onSupplement={supplement} />
      ) : (
        <div className="space-y-4">
          <NeedsHeader needs={needs} onChange={setNeeds} domains={domains} onDomainsChange={setDomains} options={options} />

          <div className="grid gap-3 sm:grid-cols-3">
            {MODES.map((item) => {
              const active = item.id === mode;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setMode(item.id)}
                  aria-pressed={active}
                  className={`rounded-xl border p-4 text-left transition-colors ${active ? 'border-indigo-500 bg-indigo-50 shadow-sm' : 'border-slate-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/40'}`}
                >
                  <div className="text-lg">{item.icon}</div>
                  <div className={`mt-1 font-semibold ${active ? 'text-indigo-800' : 'text-slate-800'}`}>{item.label}</div>
                  <div className="text-xs text-slate-500">{item.description}</div>
                </button>
              );
            })}
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
            <label className="mb-4 flex flex-wrap items-center gap-2 rounded-lg border border-purple-100 bg-purple-50/50 px-3 py-2 text-xs text-slate-700">
              <input type="checkbox" checked={useLlm} onChange={(event) => setUseLlm(event.target.checked)} className="h-4 w-4 rounded border-slate-300" />
              <span className="font-medium">比對時用本地 AI 判讀「需語意判斷」的條件</span>
              <span className="text-slate-500">（只針對可能符合的前幾筆；每個條件需數秒，整體可能要等一到數分鐘。關閉則只用規則引擎，立即回覆。）</span>
            </label>
            {result ? (
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-600">
                <span>上次比對結果仍保留，修改資料後可再次比對。</span>
                <button type="button" className="text-indigo-700 hover:underline" onClick={() => setView('results')}>
                  回到上次結果 →
                </button>
              </div>
            ) : null}
            {mode === 'form' ? (
              <ProfileForm key={`form-${domains.join(',')}`} initial={profile} catalog={catalog} namespaces={options?.namespaces ?? null} cities={cities} domains={domains} busy={matching} onSubmit={(next) => void runMatch(next, 'form')} />
            ) : null}
            {mode === 'step' ? <StepWizard key={`step-${domains.join(',')}`} initial={profile} cities={cities} catalog={catalog} domains={domains} busy={matching} onMatch={(next) => void runMatch(next, 'step')} /> : null}
            {mode === 'quick' ? (
              <QuickInput key="quick" initial={profile} initialText={rawInput} cities={cities} catalog={catalog} labels={labels} domains={domains} busy={matching} onMatch={(next, text) => void runMatch(next, 'quick', text)} />
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
