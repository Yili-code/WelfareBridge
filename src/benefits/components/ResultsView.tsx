import { useMemo, useState, type ReactNode } from 'react';
import type { Labels } from '../hooks/useApi';
import type { FieldSpec, MatchItem, MatchResponse, RankedItem } from '../types';
import { DISCLAIMER, MATCH_STATUS_META } from '../utils/labels';
import { Badge } from './Badge';
import { Spinner } from './Feedback';
import { ProfileSummary } from './ProfileSummary';
import { ResultCard, type CardItem } from './ResultCard';

interface Props {
  result: MatchResponse;
  catalog: Record<string, FieldSpec> | null;
  cities: string[];
  labels: Labels;
  extras: Array<{ label: string; value: string }>;
  busy: boolean;
  onEdit: () => void;
  onSupplement: (attributeId: string, value: unknown) => void;
}

type SortKey = 'recommended' | 'amount' | 'deadline' | 'easiest';

const SORTS: Array<{ id: SortKey; label: string; hint: string }> = [
  { id: 'recommended', label: '推薦', hint: '依適合度（期望價值 × 時效 × 省力 × 偏好）' },
  { id: 'amount', label: '金額', hint: '依年化金額，未載明者排最後' },
  { id: 'deadline', label: '截止日', hint: '依剩餘天數，未載明者排最後' },
  { id: 'easiest', label: '最省力', hint: '依準備成本（文件、面試、證明）' },
];

const PAGE = 20;

function sortItems(items: RankedItem[], key: SortKey): RankedItem[] {
  const list = [...items];
  const num = (value: number | null | undefined, fallback: number) => (typeof value === 'number' ? value : fallback);
  switch (key) {
    case 'amount':
      return list.sort((a, b) => num(b.suitability.annual_value ?? b.benefit?.amount?.max, -1) - num(a.suitability.annual_value ?? a.benefit?.amount?.max, -1));
    case 'deadline':
      return list.sort((a, b) => num(a.suitability.days_left, 9999) - num(b.suitability.days_left, 9999));
    case 'easiest':
      return list.sort((a, b) => num(a.suitability.cost, 1) - num(b.suitability.cost, 1) || num(b.suitability.total, 0) - num(a.suitability.total, 0));
    default:
      return list.sort((a, b) => num(b.suitability.total, 0) - num(a.suitability.total, 0));
  }
}

function Group({ title, emoji, count, description, tone, defaultOpen, children }: { title: string; emoji: string; count: number; description: string; tone: string; defaultOpen: boolean; children: ReactNode }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="space-y-3">
      <button type="button" onClick={() => setOpen((v) => !v)} className={`flex w-full items-center justify-between rounded-lg border px-4 py-2.5 text-left ${tone}`} aria-expanded={open}>
        <span className="flex flex-wrap items-center gap-2">
          <span className="text-base font-semibold">
            {emoji} {title}
          </span>
          <span className="rounded-full bg-white/70 px-2 py-0.5 text-xs font-semibold">{count}</span>
          <span className="text-xs opacity-80">{description}</span>
        </span>
        <span className="text-xs">{open ? '收合 ▲' : '展開 ▼'}</span>
      </button>
      {open ? children : null}
    </section>
  );
}

function CardList({ items, render }: { items: CardItem[]; render: (item: CardItem) => ReactNode }) {
  const [limit, setLimit] = useState(PAGE);
  if (items.length === 0) return <p className="px-2 text-sm text-slate-400">此類別沒有項目。</p>;
  return (
    <div className="space-y-3">
      {items.slice(0, limit).map(render)}
      {items.length > limit ? (
        <button type="button" onClick={() => setLimit((n) => n + PAGE)} className="w-full rounded-lg border border-dashed border-slate-300 bg-white py-2 text-sm text-slate-600 hover:bg-slate-50">
          顯示更多（還有 {items.length - limit} 筆）
        </button>
      ) : null}
    </div>
  );
}

const CARD_META: Array<{ key: 'fastest' | 'highest' | 'easiest'; title: string; description: string; tone: string }> = [
  { key: 'fastest', title: '最快拿到／最有把握', description: '獲得機率最高、且還來得及申請', tone: 'border-emerald-300 bg-emerald-50/50' },
  { key: 'highest', title: '金額最高', description: '年化金額最高（需原文有金額）', tone: 'border-indigo-300 bg-indigo-50/50' },
  { key: 'easiest', title: '最省力', description: '應備文件最少、不需面試或證明', tone: 'border-sky-300 bg-sky-50/50' },
];

export function ResultsView({ result, catalog, cities, labels, extras, busy, onEdit, onSupplement }: Props) {
  const { summary, matches, ranking } = result;
  const [sort, setSort] = useState<SortKey>('recommended');
  const likely = (summary.high_match ?? 0) + (summary.possible_match ?? 0);
  const byId = useMemo(() => new Map<string, RankedItem>([...ranking.recommended, ...ranking.other, ...ranking.removed].map((item) => [item.benefit_id, item])), [ranking]);
  const byStatus = (status: MatchItem['status']) => matches.filter((item) => item.status === status);
  const recommended = useMemo(() => sortItems(ranking.recommended, sort), [ranking.recommended, sort]);
  const bundle = ranking.bundle.map((id) => byId.get(id)).filter((item): item is RankedItem => Boolean(item));
  const cards = CARD_META.map((meta) => ({ ...meta, item: ranking.cards[meta.key] ? byId.get(ranking.cards[meta.key] as string) ?? null : null }));

  const renderCard = (item: CardItem) => <ResultCard key={item.benefit_id} item={item} catalog={catalog} cities={cities} labels={labels} profileId={result.profile_id} onSupplement={onSupplement} busy={busy} />;

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-indigo-200 bg-gradient-to-r from-indigo-50 to-emerald-50 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              你目前可能符合 <span className="text-indigo-700">{likely}</span> 項，其中 <span className="text-emerald-700">{ranking.recommended.length}</span> 項建議申請
            </h2>
            <div className="mt-2 flex flex-wrap gap-2 text-xs">
              {(['high_match', 'possible_match', 'insufficient_data', 'not_match'] as const).map((status) => (
                <Badge key={status} tone={status === 'high_match' ? 'emerald' : status === 'possible_match' ? 'amber' : status === 'not_match' ? 'red' : 'slate'}>
                  {MATCH_STATUS_META[status].emoji} {MATCH_STATUS_META[status].label} {summary[status] ?? 0}
                </Badge>
              ))}
              <Badge tone="slate">共比對 {summary.total ?? matches.length} 筆</Badge>
              {result.hard_filter_excluded ? <Badge tone="gray" title="依你已確認的硬過濾屬性（戶籍、教育階段等）確定不符而排除，仍列在「目前不符合」">候選檢索排除 {result.hard_filter_excluded} 筆</Badge> : null}
              {result.llm_available ? (
                result.llm_used ? <Badge tone="purple">部分複雜條件由本地 AI 協助判讀</Badge> : <Badge tone="purple">本地 AI 在線（本次未使用）</Badge>
              ) : (
                <Badge tone="slate">規則式比對（本地 AI 未啟用或離線）</Badge>
              )}
              {busy ? (
                <span className="inline-flex items-center gap-1 text-indigo-700">
                  <Spinner /> 重新比對中…
                </span>
              ) : null}
            </div>
          </div>
        </div>
        <p className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">{result.disclaimer || DISCLAIMER}</p>
      </div>

      <ProfileSummary chips={result.profile_chips} extras={extras} onEdit={onEdit} />

      <section className="space-y-3">
        <h3 className="text-lg font-bold text-slate-900">為你推薦</h3>
        {cards.every((card) => !card.item) ? (
          <p className="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-6 text-center text-sm text-slate-500">目前沒有可推薦的項目：請補充更多資料，或放寬「不想要的類型」。</p>
        ) : (
          <div className="grid gap-3 lg:grid-cols-3">
            {cards.map((card) => (
              <div key={card.key} className={`rounded-xl border-2 p-3 ${card.tone}`}>
                <div className="mb-2">
                  <div className="text-sm font-bold text-slate-800">{card.title}</div>
                  <div className="text-[11px] text-slate-500">{card.description}</div>
                </div>
                {card.item ? <ResultCard item={card.item} catalog={catalog} cities={cities} labels={labels} profileId={result.profile_id} compact /> : <p className="text-xs text-slate-400">—（原文未載明足夠資訊）</p>}
              </div>
            ))}
          </div>
        )}
      </section>

      {bundle.length ? (
        <section className="space-y-2 rounded-xl border border-purple-200 bg-purple-50/40 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-bold text-slate-900">建議申請組合</h3>
            <Badge tone="purple">互不衝突，可同時申請</Badge>
            <span className="text-xs text-slate-500">依「不得兼領」條款在互斥圖上貪婪選出總期望價值最高的組合（最多 5 項）。</span>
          </div>
          <ol className="list-inside list-decimal space-y-1 text-sm">
            {bundle.map((item) => (
              <li key={item.benefit_id} className="text-slate-800">
                <a href={`#benefit-${item.benefit_id}`} className="hover:text-indigo-700 hover:underline">
                  {item.title}
                </a>
                <span className="ml-2 text-xs text-slate-500">{item.provider}</span>
                {item.why?.[0] ? <span className="ml-2 text-xs text-emerald-700">{item.why[0]}</span> : null}
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-lg font-bold text-slate-900">
            可申請清單 <span className="text-sm font-normal text-slate-500">（{ranking.recommended.length}）</span>
          </h3>
          <div className="flex flex-wrap items-center gap-1 text-xs">
            <span className="text-slate-500">排序：</span>
            {SORTS.map((option) => (
              <button
                key={option.id}
                type="button"
                title={option.hint}
                onClick={() => setSort(option.id)}
                className={`rounded-full border px-2.5 py-0.5 ${sort === option.id ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50'}`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <CardList
          items={recommended}
          render={(item) => (
            <div key={item.benefit_id} id={`benefit-${item.benefit_id}`}>
              {renderCard(item)}
            </div>
          )}
        />
      </section>

      <Group title="其他可申請（需求不同）" emoji="🔀" count={ranking.other.length} description="資格上可能符合，但類別或給付形式與你的需求不同" tone="border-sky-200 bg-sky-50 text-sky-900" defaultOpen={false}>
        <CardList items={ranking.other} render={renderCard} />
      </Group>
      <Group title="已排除" emoji="⛔" count={ranking.removed.length} description="已截止、與你已領補助互斥，或屬於你不想要的類型" tone="border-slate-300 bg-slate-100 text-slate-700" defaultOpen={false}>
        <CardList items={ranking.removed} render={renderCard} />
      </Group>
      <Group title="資料不足" emoji={MATCH_STATUS_META.insufficient_data.emoji} count={summary.insufficient_data ?? 0} description="目前資料不足以判斷任何條件（含彙整頁與尚未抽出規則的公告）" tone="border-slate-200 bg-slate-100 text-slate-700" defaultOpen={false}>
        <CardList items={byStatus('insufficient_data')} render={renderCard} />
      </Group>
      <Group title="目前不符合" emoji={MATCH_STATUS_META.not_match.emoji} count={summary.not_match ?? 0} description="依你提供的資料，有條件明確不符合" tone="border-red-200 bg-red-50 text-red-900" defaultOpen={false}>
        <CardList items={byStatus('not_match')} render={renderCard} />
      </Group>
    </div>
  );
}
