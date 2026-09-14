import { useCallback, useEffect, useRef, useState } from 'react';
import { api, errorMessage } from '../services/api';
import type { FieldSpec, Profile, Question } from '../types';
import { applyAnswer, attributeLabel, coerceAnswer, displayAttributeValue, skipAttribute } from '../utils/profile';
import { ErrorBox, Notice, Spinner } from './Feedback';
import { primaryButton, secondaryButton } from './FormControls';
import { QuestionInput } from './QuestionInput';

interface Props {
  initial: Profile;
  cities: string[];
  catalog: Record<string, FieldSpec> | null;
  domains: string[];
  busy: boolean;
  onMatch: (profile: Profile) => void;
}

interface HistoryItem {
  attribute_id: string;
  label: string;
  value: string;
}

export function StepWizard({ initial, cities, catalog, domains, busy, onMatch }: Props) {
  const [profile, setProfile] = useState<Profile>(initial);
  const [question, setQuestion] = useState<Question | null>(null);
  const [missing, setMissing] = useState<string[]>([]);
  const [candidateCount, setCandidateCount] = useState(0);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [complete, setComplete] = useState(false);
  const sequence = useRef(0);
  const onMatchRef = useRef(onMatch);
  useEffect(() => { onMatchRef.current = onMatch; }, [onMatch]);
  const initialRef = useRef(initial);
  const domainsRef = useRef(domains);
  useEffect(() => { domainsRef.current = domains; }, [domains]);

  const fetchNext = useCallback(async (nextProfile: Profile) => {
    const seq = ++sequence.current;
    setLoading(true);
    setError(null);
    try {
      const response = await api.nextQuestions({ profile: nextProfile, mode: 'step', max_questions: 1, domains: domainsRef.current.length ? domainsRef.current : null });
      if (seq !== sequence.current) return;
      setMissing(response.missing_attributes);
      setCandidateCount(response.candidate_count);
      setQuestion(response.questions[0] ?? null);
      setComplete(response.complete);
      if (response.complete) onMatchRef.current(nextProfile);
    } catch (err) {
      if (seq === sequence.current) setError(errorMessage(err));
    } finally {
      if (seq === sequence.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchNext(initialRef.current);
  }, [fetchNext]);

  const answer = (value: unknown) => {
    if (!question) return;
    const coerced = coerceAnswer(catalog?.[question.attribute_id], value);
    const next = applyAnswer(profile, question.attribute_id, coerced);
    const label = attributeLabel(question.attribute_id, catalog);
    const option = question.options.find((item) => String(item.value) === String(coerced));
    const shown = option ? option.label : displayAttributeValue(question.attribute_id, coerced, catalog);
    setHistory((items) => [...items.filter((item) => item.attribute_id !== question.attribute_id), { attribute_id: question.attribute_id, label, value: shown }]);
    setProfile(next);
    void fetchNext(next);
  };

  const skip = () => {
    if (!question) return;
    const next = skipAttribute(profile, question.attribute_id);
    setProfile(next);
    void fetchNext(next);
  };

  const answered = history.length;
  const total = answered + missing.length;
  const progress = total === 0 ? 100 : Math.round((answered / total) * 100);

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center justify-between text-xs text-slate-600">
          <span>
            已回答 {answered} 題{missing.length ? `，還有 ${missing.length} 題可問` : ''}
            {candidateCount ? `・目前 ${candidateCount} 筆補助還需要更多資料` : ''}
          </span>
          <span>{progress}%</span>
        </div>
        <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-200">
          <div className="h-full rounded-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
        </div>
        <p className="mt-1 text-[11px] text-slate-400">問題依屬性登錄表的追問優先順序（ask_priority）排列；只問候選補助用得到的屬性。</p>
      </div>

      {history.length || profile.skipped.length ? (
        <div className="flex flex-wrap gap-1.5">
          {history.map((item) => (
            <span key={item.attribute_id} className="rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs text-slate-700">
              <span className="text-slate-500">{item.label}</span> {item.value}
            </span>
          ))}
          {profile.skipped.map((attributeId) => (
            <span key={attributeId} className="rounded-full border border-dashed border-slate-300 bg-white px-2.5 py-0.5 text-xs text-slate-400">
              {attributeLabel(attributeId, catalog)}（跳過）
            </span>
          ))}
        </div>
      ) : null}

      {error ? <ErrorBox title="無法取得下一題" message={error} onRetry={() => void fetchNext(profile)} /> : null}

      {complete ? (
        <Notice tone="success">
          <span className="inline-flex items-center gap-2">
            {busy ? <Spinner /> : null}
            {busy ? '已收集足夠資料，正在比對…' : '已完成所有問題。'}
          </span>
          {!busy ? (
            <button type="button" className={`${primaryButton} ml-3`} onClick={() => onMatch(profile)}>
              重新比對
            </button>
          ) : null}
        </Notice>
      ) : loading && !question ? (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Spinner /> 準備問題中…
        </div>
      ) : question ? (
        <div className={loading ? 'opacity-60' : ''}>
          <QuestionInput key={question.attribute_id} question={question} cities={cities} busy={loading || busy} onAnswer={answer} onSkip={skip} />
        </div>
      ) : null}

      {!complete ? (
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3">
          <span className="text-xs text-slate-500">隨時可以直接比對；未回答的欄位會顯示為「資料不足」。</span>
          <button type="button" className={secondaryButton} disabled={busy} onClick={() => onMatch(profile)}>
            {busy ? '比對中…' : '直接比對'}
          </button>
        </div>
      ) : null}
    </div>
  );
}
