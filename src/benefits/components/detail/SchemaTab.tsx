import type { BenefitSchema, BenefitSummary } from '../../types';
import type { Labels } from '../../hooks/useApi';
import { formatAmount, formatAnnualized, formatNumber, formatPeriod } from '../../utils/format';
import { AMOUNT_TYPE_LABELS, EFFORT_LABELS, EXCLUSIVE_LABELS, levelLabel } from '../../utils/labels';
import { Badge } from '../Badge';
import { EmptyState } from '../Feedback';
import { JsonViewer } from '../JsonViewer';
import { KeyValueTable, TagList, type KeyValueRow } from '../KeyValueTable';

const NOT_STATED = <span className="text-slate-400">原文未載明</span>;

function List({ items }: { items: string[] | undefined | null }) {
  if (!items || items.length === 0) return NOT_STATED;
  return (
    <ul className="list-inside list-disc space-y-0.5">
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}

export function SchemaTab({ schema, benefit, labels, levelLabels }: { schema: BenefitSchema | null; benefit: BenefitSummary; labels: Labels; levelLabels: Record<string, string> }) {
  if (!schema) return <EmptyState text="此筆資料沒有標準 Schema。" />;
  const meta = schema.benefit ?? {};
  const amount = meta.amount;
  const period = meta.application_period;
  const application = meta.application ?? {};
  const contact = application.contact ?? {};
  const flags: Array<[string, boolean | undefined]> = [
    ['需面試', application.requires_interview],
    ['需推薦函', application.requires_recommendation],
    ['需自傳／計畫', application.requires_essay],
    ['需公所／村里長證明', application.requires_office_proof],
    ['需財力證明', application.requires_financial_proof],
  ];
  const requiredFlags = flags.filter(([, value]) => value).map(([label]) => label);

  const rows: KeyValueRow[] = [
    {
      label: '給付形式',
      value: (
        <span className="inline-flex flex-wrap items-center gap-2">
          <Badge tone="emerald">{labels.of('benefit_form', meta.benefit_form)}</Badge>
          {meta.benefit_form_inferred ? <Badge tone="amber">依類別預設推定</Badge> : null}
        </span>
      ),
    },
    {
      label: '金額',
      value: (
        <div className="space-y-0.5">
          <div>
            {formatAmount(amount)}
            {amount?.type ? <span className="ml-2 text-xs text-slate-500">（{AMOUNT_TYPE_LABELS[amount.type] ?? amount.type}）</span> : null}
          </div>
          <div className="text-xs text-slate-500">
            年化：{formatAnnualized(meta.amount_annualized)}
            {amount?.count_per_year ? `・每年 ${amount.count_per_year} 次` : ''}
          </div>
          {amount?.tiers?.length ? <div className="text-xs text-slate-500">分級：{amount.tiers.map((tier) => formatNumber(tier.value)).join(' / ')} 元</div> : null}
          {amount?.description ? <div className="text-xs text-slate-500">原文：{amount.description}</div> : null}
        </div>
      ),
    },
    {
      label: '申請期間',
      value: (
        <div className="space-y-0.5">
          <div className="flex flex-wrap items-center gap-2">
            <span>{formatPeriod(period)}</span>
            {period?.rolling ? <Badge tone="green">隨到隨辦</Badge> : null}
            {period?.by_school_deadline ? <Badge tone="amber">依各校公告截止日</Badge> : null}
          </div>
          {period?.description ? <div className="text-xs text-slate-500">原文：{period.description}</div> : null}
        </div>
      ),
    },
    { label: '核發方式', value: <Badge tone="slate">{labels.of('award_basis', meta.award_basis ?? 'unknown')}</Badge> },
    { label: '名額', value: typeof meta.quota === 'number' ? `${formatNumber(meta.quota)} 名` : NOT_STATED },
    {
      label: '申請管道',
      value: (
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="blue">{labels.of('channel', application.channel ?? 'unknown')}</Badge>
            {application.effort ? <span className="text-xs text-slate-600">準備負擔：{EFFORT_LABELS[application.effort] ?? application.effort}</span> : null}
            {requiredFlags.length ? <TagList items={requiredFlags} tone="indigo" /> : <span className="text-xs text-slate-400">無面試／推薦函／自傳／證明要求</span>}
          </div>
          {application.method ? <div className="text-xs text-slate-600">{application.method}</div> : null}
          {[contact.department, contact.phone, contact.email].filter(Boolean).length ? <div className="text-xs text-slate-500">聯絡：{[contact.department, contact.phone, contact.email].filter(Boolean).join('　')}</div> : null}
        </div>
      ),
    },
    { label: '應備文件', value: <List items={application.documents} /> },
    { label: '得獎後義務', value: <List items={meta.obligations} /> },
    {
      label: '不得兼領',
      value: meta.exclusive_with?.length ? (
        <ul className="space-y-0.5">
          {meta.exclusive_with.map((item) => (
            <li key={item}>
              {EXCLUSIVE_LABELS[item] ?? item} <span className="mono text-[11px] text-slate-400">{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        NOT_STATED
      ),
    },
    { label: '可續領', value: meta.renewable === true ? '可續領' : meta.renewable === false ? '不可續領' : NOT_STATED },
    { label: '審核天數', value: typeof meta.decision_lead_days === 'number' ? `${meta.decision_lead_days} 天` : NOT_STATED },
    { label: '目標族群', value: meta.target_population_text || NOT_STATED },
    {
      label: '機關 / 地區',
      value: (
        <span className="inline-flex flex-wrap items-center gap-2">
          <span>{benefit.provider || '原文未載明'}</span>
          <Badge tone="slate">{benefit.provider_type_label}</Badge>
          {benefit.provider_region ? <Badge tone="indigo">{benefit.provider_region === 'national' ? '全國' : benefit.provider_region}</Badge> : null}
        </span>
      ),
    },
    { label: '領域 / 類別', value: `${benefit.domain_label || '—'}／${benefit.category_label || '—'}` },
    { label: '適用教育階段（index）', value: benefit.education_levels.length ? <TagList items={benefit.education_levels.map((level) => levelLabel(level, levelLabels))} tone="indigo" /> : NOT_STATED },
    { label: '戶籍縣市（index）', value: benefit.residence_cities.length ? <TagList items={benefit.residence_cities} /> : NOT_STATED },
    { label: '需具備身分（index）', value: benefit.tags_required.length ? <TagList items={benefit.tags_required} tone="emerald" /> : NOT_STATED },
    { label: '說明', value: schema.description ? <span className="whitespace-pre-wrap text-xs">{schema.description}</span> : NOT_STATED },
    { label: '關鍵字', value: <TagList items={schema.keywords} /> },
    {
      label: '檢核',
      value: schema.review?.needs_review ? (
        <div>
          <Badge tone="amber">⚠ 待人工確認</Badge>
          <ul className="mt-1 list-inside list-disc text-xs text-slate-600">
            {(schema.review.reasons ?? []).map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
        </div>
      ) : (
        <Badge tone="green">✅ 通過檢核</Badge>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">Schema 摘要（benefits.benefit）</h3>
        <KeyValueTable rows={rows} />
      </div>
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-800">完整 Standard Schema（JSON）</h3>
        <JsonViewer value={schema} defaultDepth={1} />
      </div>
    </div>
  );
}
