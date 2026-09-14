import { useRef, useState } from 'react';
import { api, errorMessage } from '../services/api';
import type { Labels } from '../hooks/useApi';
import type { FieldSpec, ParsedField, Profile, ProfileParseResponse, Question } from '../types';
import { formatConfidence } from '../utils/format';
import { applyAnswer, attributeLabel, coerceAnswer, displayAttributeValue, normalizeProfile, skipAttribute } from '../utils/profile';
import { Badge, ExtractorBadge } from './Badge';
import { DataTable, type Column } from './DataTable';
import { ErrorBox, Notice, Spinner } from './Feedback';
import { inputClass, primaryButton, secondaryButton } from './FormControls';
import { ProfileSummary } from './ProfileSummary';
import { QuestionInput } from './QuestionInput';

interface Props {
  initial: Profile;
  initialText: string;
  cities: string[];
  catalog: Record<string, FieldSpec> | null;
  labels: Labels;
  domains: string[];
  busy: boolean;
  onMatch: (profile: Profile, text: string) => void;
}

const PLACEHOLDER = '例如：我是基隆人，海洋大學資工大二，平均80分，低收入戶，急需一筆錢';

export function QuickInput({ initial, initialText, cities, catalog, labels, domains, busy, onMatch }: Props) {
  const [text, setText] = useState(initialText);
  const [profile, setProfile] = useState<Profile>(initial);
  const [parsed, setParsed] = useState<ProfileParseResponse | null>(null);
  const [parsing, setParsing] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [candidateCount, setCandidateCount] = useState(0);
  const [complete, setComplete] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sequence = useRef(0);

  const fetchQuestions = async (nextProfile: Profile) => {
    const seq = ++sequence.current;
    setLoadingQuestions(true);
    try {
      const response = await api.nextQuestions({ profile: nextProfile, mode: 'dynamic', max_questions: 3, domains: domains.length ? domains : null });
      if (seq !== sequence.current) return;
      setQuestions(response.questions);
      setCandidateCount(response.candidate_count);
      setComplete(response.complete);
    } catch (err) {
      if (seq === sequence.current) setError(errorMessage(err));
    } finally {
      if (seq === sequence.current) setLoadingQuestions(false);
    }
  };

  const parse = async () => {
    if (!text.trim()) return;
    setParsing(true);
    setError(null);
    try {
      const response = await api.parseProfile({ text: text.trim(), base_profile: profile, use_llm: true });
      const nextProfile = normalizeProfile(response.profile);
      setParsed(response);
      setProfile(nextProfile);
      await fetchQuestions(nextProfile);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setParsing(false);
    }
  };

  const answer = (question: Question, value: unknown) => {
    const next = applyAnswer(profile, question.attribute_id, coerceAnswer(catalog?.[question.attribute_id], value));
    setProfile(next);
    void fetchQuestions(next);
  };

  const skip = (question: Question) => {
    const next = skipAttribute(profile, question.attribute_id);
    setProfile(next);
    void fetchQuestions(next);
  };

  const parsedColumns: Column<ParsedField>[] = [
    { key: 'field', header: '欄位', render: (row) => attributeLabel(row.attribute_id, catalog) },
    {
      key: 'value',
      header: '系統理解為',
      render: (row) => <span className="font-medium text-slate-900">{row.attribute_id === 'need_type' ? labels.of('need_type', String(row.value)) : displayAttributeValue(row.attribute_id, row.value, catalog)}</span>,
    },
    { key: 'excerpt', header: '你的原話', render: (row) => (row.excerpt ? <q className="text-slate-600">{row.excerpt}</q> : '—') },
    { key: 'extractor', header: '抽取方式', render: (row) => <ExtractorBadge extractor={row.extractor} /> },
    { key: 'confidence', header: '信心', className: 'text-right tabular-nums', render: (row) => formatConfidence(row.confidence) },
  ];

  const canMatch = parsed !== null || text.trim().length > 0;

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">用一句話描述你的情況</label>
        <textarea className={`${inputClass} min-h-28`} value={text} placeholder={PLACEHOLDER} onChange={(event) => setText(event.target.value)} />
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <button type="button" className={primaryButton} disabled={parsing || !text.trim()} onClick={() => void parse()}>
            {parsing ? <Spinner className="border-white/40 border-t-white" /> : null}
            解析
          </button>
          <button type="button" className={secondaryButton} onClick={() => setText(PLACEHOLDER.replace('例如：', ''))}>
            填入範例
          </button>
          <span className="text-xs text-slate-500">系統先用登錄表的別名做規則式解析，本地 AI 在線時再補充；每個理解結果都會附上你的原話讓你確認。</span>
        </div>
      </div>

      {error ? <ErrorBox title="解析失敗" message={error} /> : null}

      {parsed ? (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-800">系統理解為</h3>
            {parsed.llm_used ? <Badge tone="purple">本地 AI 補充解析</Badge> : <Badge tone="slate">規則式解析</Badge>}
          </div>
          <ProfileSummary chips={parsed.chips} extras={parsed.profile.need_type !== 'unknown' ? [{ label: '需求類型', value: labels.of('need_type', parsed.profile.need_type) }] : []} />
          <DataTable columns={parsedColumns} rows={parsed.parsed_fields} rowKey={(row) => `${row.attribute_id}-${row.excerpt}`} dense emptyText="沒有解析出任何欄位，請試著寫得更具體一點（縣市、學校、年級、成績、身分、需求）。" />
          {parsed.unparsed_hints.length ? (
            <Notice tone="warn">
              <div className="font-medium">尚未理解的部分：</div>
              <ul className="mt-1 list-inside list-disc">
                {parsed.unparsed_hints.map((hint, index) => (
                  <li key={index}>{hint}</li>
                ))}
              </ul>
            </Notice>
          ) : null}
        </div>
      ) : null}

      {parsed ? (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-800">再補充幾個問題會更準確</h3>
            {loadingQuestions ? <Spinner /> : null}
            {candidateCount ? <span className="text-xs text-slate-500">目前有 {candidateCount} 筆補助還需要更多資料才能判斷；問題依「回答後能翻轉最多結果」排序。</span> : null}
          </div>
          {complete && questions.length === 0 ? (
            <Notice tone="success">資料已足夠，沒有其他需要追問的欄位。</Notice>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {questions.map((question) => (
                <QuestionInput key={question.attribute_id} question={question} cities={cities} busy={loadingQuestions || busy} onAnswer={(value) => answer(question, value)} onSkip={() => skip(question)} />
              ))}
            </div>
          )}
        </div>
      ) : null}

      <div className="flex flex-wrap items-center justify-end gap-2 border-t border-slate-100 pt-3">
        <button type="button" className={primaryButton} disabled={busy || !canMatch} onClick={() => onMatch(profile, text.trim())} title={parsed ? undefined : '建議先按「解析」確認系統的理解'}>
          {busy ? '比對中…' : '開始比對'}
        </button>
      </div>
    </div>
  );
}
