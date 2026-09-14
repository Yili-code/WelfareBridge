import { useState, type ReactElement } from 'react';
import type { Question, QuestionOption } from '../types';
import { ChipSelect, ChoiceButtons, NumberInput, Select, TextInput, primaryButton, secondaryButton } from './FormControls';

export type QuestionLike = Pick<Question, 'attribute_id' | 'question' | 'type' | 'options'> & Partial<Pick<Question, 'reason' | 'help' | 'affected' | 'sensitivity' | 'priority'>>;

interface Props {
  question: QuestionLike;
  onAnswer: (value: unknown) => void;
  onSkip?: () => void;
  cities?: string[];
  busy?: boolean;
  compact?: boolean;
}

function toStringOptions(options: QuestionOption[]): Array<{ value: string; label: string }> {
  return options.map((option) => ({ value: String(option.value), label: option.label }));
}

/** 依 Question.type 呈現單一題目的輸入 UI。 */
export function QuestionInput({ question, onAnswer, onSkip, cities = [], busy = false, compact = false }: Props) {
  const [text, setText] = useState<string | null>(null);
  const [num, setNum] = useState<number | null>(null);
  const [multi, setMulti] = useState<string[]>([]);

  const skipButton = onSkip ? (
    <button type="button" className={secondaryButton} disabled={busy} onClick={onSkip}>
      跳過
    </button>
  ) : null;

  const submitButtons = (onSubmit: () => void, disabled: boolean) => (
    <div className="mt-3 flex flex-wrap gap-2">
      <button type="button" className={primaryButton} disabled={busy || disabled} onClick={onSubmit}>
        確認
      </button>
      {skipButton}
    </div>
  );

  let body: ReactElement;
  switch (question.type) {
    case 'single_choice':
      body = (
        <>
          <ChoiceButtons options={question.options} value={null} onChange={(value) => onAnswer(value)} />
          {skipButton ? <div className="mt-3">{skipButton}</div> : null}
        </>
      );
      break;
    case 'boolean': {
      const options = question.options.length ? question.options : [{ value: true, label: '是' }, { value: false, label: '否' }];
      body = (
        <>
          <ChoiceButtons options={options} value={null} onChange={(value) => onAnswer(value === 'true' ? true : value === 'false' ? false : value)} />
          {skipButton ? <div className="mt-3">{skipButton}</div> : null}
        </>
      );
      break;
    }
    case 'city': {
      const options = question.options.length ? toStringOptions(question.options) : cities.map((city) => ({ value: city, label: city }));
      body = (
        <>
          <Select value={text} onChange={setText} options={options} placeholder="請選擇縣市" />
          {submitButtons(() => text && onAnswer(text), !text)}
        </>
      );
      break;
    }
    case 'number':
      body = (
        <>
          <NumberInput value={num} onChange={setNum} autoFocus onEnter={() => num !== null && onAnswer(num)} placeholder="請輸入數字" />
          {submitButtons(() => num !== null && onAnswer(num), num === null)}
        </>
      );
      break;
    case 'multi_choice':
      body = (
        <>
          <ChipSelect options={toStringOptions(question.options)} selected={multi} onChange={setMulti} />
          <p className="mt-2 text-xs text-slate-500">可複選；若都不符合，直接按「確認」代表「皆無」。</p>
          {submitButtons(() => onAnswer(multi), false)}
        </>
      );
      break;
    default:
      body = (
        <>
          <TextInput value={text} onChange={setText} autoFocus onEnter={() => text && onAnswer(text.trim())} placeholder="請輸入" />
          {submitButtons(() => text && onAnswer(text.trim()), !text)}
        </>
      );
  }

  return (
    <div className={compact ? '' : 'rounded-xl border border-indigo-100 bg-white p-4 shadow-sm'}>
      <div className={`font-medium text-slate-900 ${compact ? 'text-sm' : 'text-base'}`}>{question.question}</div>
      {question.reason ? <div className="mt-1 text-xs text-indigo-600">{question.reason}</div> : null}
      {question.help ? <div className="mt-1 text-xs text-slate-500">{question.help}</div> : null}
      {question.sensitivity === 'high' ? <div className="mt-1 text-[11px] text-amber-700">敏感資料（選填）：只用於比對資格，可直接跳過。</div> : null}
      <div className="mt-3">{body}</div>
    </div>
  );
}
