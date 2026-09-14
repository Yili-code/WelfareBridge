import { useNavigate } from 'react-router-dom';
import type { BenefitSummary } from '../types';
import { formatAmount, formatDeadline, isExpired } from '../utils/format';
import { Badge, ReviewBadge } from './Badge';
import { DataTable, type Column } from './DataTable';

export function BenefitTable({ items }: { items: BenefitSummary[] }) {
  const navigate = useNavigate();

  const columns: Column<BenefitSummary>[] = [
    {
      key: 'title',
      header: '名稱',
      className: 'min-w-[18rem]',
      render: (row) => (
        <div>
          <div className="font-medium text-slate-900">{row.title}</div>
          <div className="mt-0.5 flex flex-wrap items-center gap-1 text-[11px] text-slate-500">
            {row.domain_label ? <Badge tone="indigo">{row.domain_label}</Badge> : null}
            {row.is_overview ? <Badge tone="amber">彙整頁</Badge> : null}
            {row.uncertain ? <Badge tone="red" title={row.classification_basis}>疑似補助待確認</Badge> : null}
            {!row.uncertain && row.category_uncertain ? <Badge tone="amber" title={row.classification_basis}>類別待確認</Badge> : null}
            {row.categories_secondary_labels?.length ? <Badge tone="gray" title={`次類別（同頁也涵蓋）：${row.categories_secondary_labels.join('、')}`}>+{row.categories_secondary_labels.length} 次類別</Badge> : null}
            {row.quality_tier === 'needs_review' && row.missing_fields.length ? <Badge tone="gray" title={`官方頁面未抽到：${row.missing_fields.join('、')}`}>待補：{row.missing_fields.join('、')}</Badge> : null}
            {row.is_repost ? <Badge tone="gray">轉知</Badge> : null}
            {!row.is_canonical ? <Badge tone="gray">重複來源</Badge> : null}
            {row.residence_cities.length ? <span>戶籍：{row.residence_cities.join('、')}</span> : null}
          </div>
        </div>
      ),
    },
    {
      key: 'provider',
      header: '提供機關',
      className: 'min-w-[10rem]',
      render: (row) => (
        <div>
          <div>{row.provider || <span className="text-slate-400">原文未載明</span>}</div>
          <div className="text-[11px] text-slate-500">{row.provider_type_label}</div>
        </div>
      ),
    },
    { key: 'category', header: '類別', render: (row) => (row.category_label ? <Badge tone="blue">{row.category_label}</Badge> : <span className="text-slate-400">—</span>) },
    { key: 'form', header: '給付形式', render: (row) => (row.benefit_form_label ? <Badge tone="emerald">{row.benefit_form_label}</Badge> : <span className="text-slate-400">—</span>) },
    { key: 'amount', header: '金額', className: 'whitespace-nowrap', render: (row) => <span title={row.amount?.description || undefined}>{formatAmount(row.amount)}</span> },
    {
      key: 'deadline',
      header: '申請期限',
      className: 'whitespace-nowrap',
      render: (row) => {
        const expired = row.status === 'expired' || isExpired(row.application_period);
        return (
          <span className="inline-flex items-center gap-1">
            <span className={expired ? 'text-slate-400 line-through' : ''} title={row.application_period?.description || undefined}>
              {formatDeadline(row.application_period)}
            </span>
            {expired ? <Badge tone="gray">已截止</Badge> : null}
          </span>
        );
      },
    },
    {
      key: 'source',
      header: '來源',
      render: (row) => (
        <span className="inline-flex items-center gap-1">
          <span>{row.source_name || row.source_id}</span>
          {row.source_url ? (
            <a href={row.source_url} target="_blank" rel="noopener noreferrer" onClick={(event) => event.stopPropagation()} title={`開啟官方公告：${row.source_url}`} className="text-blue-600 hover:underline">
              🔗
            </a>
          ) : null}
        </span>
      ),
    },
    { key: 'review', header: '檢核', render: (row) => <ReviewBadge needsReview={row.needs_review} reviewReasons={row.review_reasons} /> },
    {
      key: 'rules',
      header: '規則',
      className: 'whitespace-nowrap text-right tabular-nums',
      render: (row) => (
        <span title={`可自動判斷 ${row.simple_rules} 條・需語意判斷 ${row.complex_rules} 條`}>
          {row.simple_rules} <span className="text-slate-400">/ {row.complex_rules}</span>
        </span>
      ),
    },
    {
      key: 'llm',
      header: 'AI',
      render: (row) => (row.llm_processed ? <Badge tone="purple" title={`${row.llm_model || ''}・採納 ${row.llm_accepted} 項`}>已補齊</Badge> : <span className="text-slate-400">—</span>),
    },
  ];

  return <DataTable columns={columns} rows={items} rowKey={(row) => row.id} onRowClick={(row) => navigate(`/data-center/${row.id}`)} emptyText="沒有符合條件的資料" />;
}
