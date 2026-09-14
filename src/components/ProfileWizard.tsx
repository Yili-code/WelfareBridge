"use client";

import { useState } from 'react';
import { REGIONS, RELATIONS } from '@/lib/options';
import { AGE_RANGES, QUESTIONS, profileTags, selectAnswer } from '@/lib/questionnaire';
import type { Profile, Relation } from '@/lib/types';

type Draft = Omit<Profile, 'id' | 'createdAt'>;
const fieldClass = 'mt-2 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 outline-none focus:border-brand-500';

export default function ProfileWizard({ initialProfile, onComplete, onCancel }: { initialProfile?: Profile; onComplete: (draft: Draft) => void; onCancel?: () => void }) {
 const [step, setStep] = useState(0);
 const [answers, setAnswers] = useState<Record<string, string[]>>(() => {
   const saved = { ...initialProfile?.screening };
   if (!saved.age && initialProfile?.age != null) {
     const index = AGE_RANGES.findIndex(([min, max]) => initialProfile.age! >= min && initialProfile.age! <= max);
     if (index >= 0) saved.age = [QUESTIONS[1].options[index]];
   }
   return saved;
 });
 const [relation, setRelation] = useState<Relation>(initialProfile?.relation || 'self');
 const [nickname, setNickname] = useState(initialProfile?.nickname || '');
 const [exactAge, setExactAge] = useState(initialProfile?.age == null ? '' : String(initialProfile.age));
 const [region, setRegion] = useState(initialProfile?.region || '');
 const [currentRegion, setCurrentRegion] = useState(initialProfile?.currentRegion || '');
 const question = QUESTIONS[step];
 const selected = answers[question.key] || [];
 const residence = answers.residence?.[0];
 const sameCity = QUESTIONS[2].options.slice(0, 2).includes(residence);
 const noHousehold = residence === QUESTIONS[2].options[3];
 const ageRange = AGE_RANGES[QUESTIONS[1].options.indexOf(answers.age?.[0])];
 const ageValid = exactAge === '' || (Number.isInteger(Number(exactAge)) && Number(exactAge) >= 0 && Number(exactAge) <= 120 && ageRange && Number(exactAge) >= ageRange[0] && Number(exactAge) <= ageRange[1]);
 const canNext = selected.length > 0 && (step !== 1 || ageValid) && (step !== 2 || (!sameCity || !!region));
 const choose = (value: string) => {
   setAnswers(previous => ({ ...previous, [question.key]: selectAnswer(previous[question.key] || [], question, value) }));
   if (question.key === 'age') setExactAge('');
   if (question.key === 'residence') { setRegion(''); setCurrentRegion(''); }
 };
 const canSave = QUESTIONS.every(q => answers[q.key]?.length) && ageValid && (!sameCity || !!region);
 const save = () => {
   if (!canSave) return;
   onComplete({ nickname: nickname.trim() || RELATIONS.find(r => r.value === relation)!.label, relation, region: noHousehold ? '' : region, district: initialProfile?.region === region && !noHousehold ? initialProfile.district : undefined, currentRegion: sameCity ? region : currentRegion, age: exactAge === '' ? null : Number(exactAge), screening: answers, ...profileTags(answers) });
 };
 const next = () => {
   if (!canNext) return;
   if (step < QUESTIONS.length - 1) { setStep(step + 1); return; }
   save();
 };
 const citySelect = (label: string, value: string, change: (value: string) => void) => <label className="block"><span className="text-sm font-medium">{label}</span><select className={fieldClass} value={value} onChange={e => change(e.target.value)}><option value="">不確定／尚未填寫</option>{REGIONS.map(city => <option key={city}>{city}</option>)}</select></label>;
 return <div className="flex h-full flex-col">
   <div className="mb-6">
     <div className="flex gap-1.5" role="progressbar" aria-label="補助初篩進度" aria-valuenow={step + 1} aria-valuemin={1} aria-valuemax={QUESTIONS.length}>{QUESTIONS.map((q, i) => <span key={q.key} className={`h-1.5 flex-1 rounded-full ${i <= step ? 'bg-brand-500' : 'bg-slate-200'}`} />)}</div>
     <p className="mt-3 text-xs text-ink-400">問題 {step + 1} / {QUESTIONS.length} · {question.multi ? '可複選' : '單選'}</p>
   </div>
   {initialProfile && <div className="mb-4 space-y-2"><div className="flex items-center justify-between"><p className="font-medium">編輯身分</p><button type="button" onClick={onCancel} className="text-sm text-ink-400">取消編輯</button></div><label className="block text-sm">修改項目<select aria-label="修改項目" className={fieldClass} value={step} onChange={e => setStep(Number(e.target.value))}>{QUESTIONS.map((q, i) => <option key={q.key} value={i}>{i + 1}. {q.title}</option>)}</select></label><p className="text-xs text-ink-400">原答案已帶入；儲存後會重新比對補助。未完成的題目需先補齊。</p></div>}
   <h2 className="text-2xl font-semibold tracking-tight">{question.title}</h2>
   <p className="mt-2 text-sm leading-relaxed text-ink-400">為什麼問：{question.why}</p>
   <div key={question.key} className="mt-6 flex-1 space-y-5 animate-rise overflow-y-auto pr-1">
     {step === 0 && <details className="rounded-lg border border-slate-200 p-3"><summary className="cursor-pointer text-sm">申請對象：{nickname || RELATIONS.find(r => r.value === relation)!.label}（可更改）</summary><label className="mt-3 block text-sm">這份檔案是為誰建立？<select className={fieldClass} value={relation} onChange={e => setRelation(e.target.value as Relation)}>{RELATIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}</select></label><label className="mt-3 block text-sm">檔案稱呼（選填）<input className={fieldClass} value={nickname} onChange={e => setNickname(e.target.value)} placeholder="例如：媽媽" /></label></details>}
     <div className="grid gap-2" role="group" aria-label={question.title}>{question.options.map(value => <button key={value} type="button" aria-pressed={selected.includes(value)} onClick={() => choose(value)} className={`rounded-xl border px-4 py-3 text-left text-sm transition ${selected.includes(value) ? 'border-brand-500 bg-brand-50 text-brand-700' : 'border-slate-200 bg-white text-ink-600 hover:border-brand-300'}`}>{value}</button>)}</div>
     {step === 1 && <label className="block text-sm">實際年齡（選填，填寫可提高判斷精度）<input type="number" min={0} max={120} step={1} className={fieldClass} value={exactAge} onChange={e => setExactAge(e.target.value)} aria-invalid={!ageValid} placeholder="例如：23；未滿一歲填 0" />{!ageValid && <span className="mt-2 block text-red-600">請填入所選區間內的整數年齡（0～120 歲）。</span>}</label>}
     {step === 2 && selected.length > 0 && <div className="space-y-3">{!noHousehold && citySelect(sameCity ? '戶籍及居住縣市' : '戶籍縣市（可稍後補充）', region, setRegion)}{!sameCity && citySelect('目前居住縣市（可稍後補充）', currentRegion, setCurrentRegion)}<p className="text-xs text-ink-400">設籍日期等細節，仍需依個別補助規定確認。</p></div>}
     {step === 9 && <p className="text-sm text-ink-400">完成後會儲存這十題的答案，用於初步推薦；實際資格仍需核對各補助規定與證明。</p>}
   </div>
   <div className="mt-6 flex items-center justify-between border-t border-slate-200 pt-5"><button type="button" onClick={() => step === 0 ? onCancel?.() : setStep(step - 1)} disabled={step === 0 && !onCancel} className="rounded-lg px-4 py-2.5 text-sm text-ink-400 disabled:invisible">{step === 0 ? '取消' : '上一步'}</button><button type="button" onClick={initialProfile ? save : next} disabled={initialProfile ? !canSave : !canNext} className="rounded-lg bg-brand-500 px-6 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400">{initialProfile ? '儲存修改' : step === QUESTIONS.length - 1 ? '完成建檔' : '下一步'}</button></div>
 </div>;
}
