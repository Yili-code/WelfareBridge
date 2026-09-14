import { useState, type ReactNode } from 'react';

export const inputClass =
  'w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200 disabled:bg-slate-50';

export const primaryButton = 'inline-flex items-center justify-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50';
export const secondaryButton = 'inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50';

export function Field({ label, hint, children, className = '' }: { label: ReactNode; hint?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <label className={`block ${className}`}>
      <span className="mb-1 block text-xs font-medium text-slate-600">{label}</span>
      {children}
      {hint ? <span className="mt-1 block text-[11px] text-slate-400">{hint}</span> : null}
    </label>
  );
}

export function TextInput({ value, onChange, placeholder, autoFocus, onEnter }: { value: string | null; onChange: (value: string | null) => void; placeholder?: string; autoFocus?: boolean; onEnter?: () => void }) {
  return (
    <input
      type="text"
      className={inputClass}
      value={value ?? ''}
      placeholder={placeholder}
      autoFocus={autoFocus}
      onChange={(event) => onChange(event.target.value === '' ? null : event.target.value)}
      onKeyDown={(event) => {
        if (event.key === 'Enter' && onEnter) {
          event.preventDefault();
          onEnter();
        }
      }}
    />
  );
}

export function NumberInput({
  value,
  onChange,
  placeholder,
  min,
  max,
  step,
  autoFocus,
  onEnter,
}: {
  value: number | null;
  onChange: (value: number | null) => void;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  autoFocus?: boolean;
  onEnter?: () => void;
}) {
  const [text, setText] = useState(value === null ? '' : String(value));
  const [previousValue, setPreviousValue] = useState(value);
  if (value !== previousValue) {
    setPreviousValue(value);
    const parsed = text === '' ? null : Number(text);
    if (parsed !== value && !(Number.isNaN(parsed) && value === null)) {
      setText(value === null ? '' : String(value));
    }
  }
  return (
    <input
      type="number"
      inputMode="decimal"
      className={inputClass}
      value={text}
      placeholder={placeholder}
      min={min}
      max={max}
      step={step ?? 'any'}
      autoFocus={autoFocus}
      onChange={(event) => {
        const raw = event.target.value;
        setText(raw);
        if (raw === '') {
          onChange(null);
          return;
        }
        const parsed = Number(raw);
        if (!Number.isNaN(parsed)) onChange(parsed);
      }}
      onKeyDown={(event) => {
        if (event.key === 'Enter' && onEnter) {
          event.preventDefault();
          onEnter();
        }
      }}
    />
  );
}

export function Select({ value, onChange, options, placeholder = '請選擇', disabled }: { value: string | null; onChange: (value: string | null) => void; options: Array<{ value: string; label: string }>; placeholder?: string; disabled?: boolean }) {
  return (
    <select className={inputClass} value={value ?? ''} disabled={disabled} onChange={(event) => onChange(event.target.value === '' ? null : event.target.value)}>
      <option value="">{placeholder}</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

const segment = 'flex-1 px-3 py-1.5 text-sm transition-colors first:rounded-l-md last:rounded-r-md';

/** 三態：是 / 否 / 未填（null） */
export function TriState({ value, onChange }: { value: boolean | null; onChange: (value: boolean | null) => void }) {
  const items: Array<{ key: string; label: string; v: boolean | null; active: string }> = [
    { key: 'yes', label: '是', v: true, active: 'bg-indigo-600 text-white' },
    { key: 'no', label: '否', v: false, active: 'bg-slate-700 text-white' },
    { key: 'na', label: '未填', v: null, active: 'bg-slate-200 text-slate-800' },
  ];
  return (
    <div className="inline-flex w-full overflow-hidden rounded-md border border-slate-300 bg-white">
      {items.map((item) => (
        <button key={item.key} type="button" onClick={() => onChange(item.v)} className={`${segment} ${value === item.v ? item.active : 'text-slate-600 hover:bg-slate-50'}`}>
          {item.label}
        </button>
      ))}
    </div>
  );
}

/** 單選按鈕群 */
export function ChoiceButtons<V extends string | number | boolean>({ options, value, onChange }: { options: Array<{ value: V; label: string }>; value: V | null; onChange: (value: V) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const selected = value === option.value;
        return (
          <button
            key={String(option.value)}
            type="button"
            onClick={() => onChange(option.value)}
            className={`rounded-md border px-3 py-1.5 text-sm transition-colors ${selected ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-slate-300 bg-white text-slate-700 hover:border-indigo-400 hover:bg-indigo-50'}`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

/** 多選 chips */
export function ChipSelect({ options, selected, onChange }: { options: Array<{ value: string; label: string }>; selected: string[]; onChange: (selected: string[]) => void }) {
  const toggle = (value: string) => {
    onChange(selected.includes(value) ? selected.filter((item) => item !== value) : [...selected, value]);
  };
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const active = selected.includes(option.value);
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => toggle(option.value)}
            aria-pressed={active}
            className={`rounded-full border px-3 py-1 text-sm transition-colors ${active ? 'border-emerald-600 bg-emerald-600 text-white' : 'border-slate-300 bg-white text-slate-700 hover:border-emerald-400 hover:bg-emerald-50'}`}
          >
            {active ? '✓ ' : ''}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
