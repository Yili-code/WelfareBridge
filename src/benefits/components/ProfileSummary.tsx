import type { ProfileChip } from '../types';
import { SOURCE_LABELS } from '../utils/labels';

/** 系統理解的使用者資料摘要：chips 來自 API 的 profile_chips（label／value 已由後端依登錄表轉好）。 */
export function ProfileSummary({
  chips,
  extras = [],
  onEdit,
  editLabel = '修改',
}: {
  chips: ProfileChip[];
  /** 需求類型、不想要的類型等非屬性資訊 */
  extras?: Array<{ label: string; value: string }>;
  onEdit?: () => void;
  editLabel?: string;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-indigo-100 bg-indigo-50/60 px-3 py-2 text-sm">
      <span className="text-xs font-medium text-indigo-800">你提供的資料：</span>
      {chips.length === 0 && extras.length === 0 ? <span className="text-xs text-slate-500">（尚未提供任何資料）</span> : null}
      {extras.map((item) => (
        <span key={item.label} className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-white px-2.5 py-0.5 text-xs text-slate-700">
          <span className="text-slate-500">{item.label}</span>
          <span className="font-medium">{item.value}</span>
        </span>
      ))}
      {chips.map((chip) => (
        <span
          key={chip.attribute_id}
          title={[SOURCE_LABELS[chip.source] ?? chip.source, chip.evidence ? `原話：「${chip.evidence}」` : ''].filter(Boolean).join('　')}
          className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-white px-2.5 py-0.5 text-xs text-slate-700"
        >
          <span className="text-slate-500">{chip.label}</span>
          <span className="font-medium">{chip.value}</span>
          {chip.source === 'parsed' ? <span className="text-[10px] text-purple-600">解析</span> : null}
          {chip.source === 'asked' ? <span className="text-[10px] text-indigo-600">追問</span> : null}
        </span>
      ))}
      {onEdit ? (
        <button type="button" onClick={onEdit} className="ml-auto rounded-md border border-indigo-300 bg-white px-3 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-100">
          {editLabel}
        </button>
      ) : null}
    </div>
  );
}
