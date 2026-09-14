import { useMemo, useState } from 'react';
import { Badge } from '../components/Badge';
import { DataTable, type Column } from '../components/DataTable';
import { ErrorBox, LoadingBlock, Notice, Section } from '../components/Feedback';
import { ExternalLink, KeyValueTable, TagList } from '../components/KeyValueTable';
import { StatCard } from '../components/StatCard';
import { useAsync, useMetaOptions } from '../hooks/useApi';
import { api } from '../services/api';
import type { IdentityTag, KeywordRow, RegistryAttribute, TaxonomyNode } from '../types';
import { formatDateTime, formatNumber } from '../utils/format';
import { ATTRIBUTE_TYPE_LABELS, CATEGORY_LABELS, KEYWORD_GROUP_LABELS, SENSITIVITY_LABELS, UNIT_LABELS } from '../utils/labels';
import { namespaceLabel } from '../utils/profile';

function AttributeGroup({ namespace, label, attributes, labelOfDomain }: { namespace: string; label: string; attributes: RegistryAttribute[]; labelOfDomain: (domain: string) => string }) {
  const [open, setOpen] = useState(true);
  const columns: Column<RegistryAttribute>[] = [
    {
      key: 'id',
      header: '屬性',
      className: 'min-w-[12rem]',
      render: (row) => (
        <div>
          <div className="font-medium text-slate-900">
            {row.label}
            {row.deprecated ? <Badge tone="gray" className="ml-1">已停用</Badge> : null}
          </div>
          <div className="mono text-[11px] text-slate-400">{row.id}</div>
          {row.question ? <div className="text-[11px] text-slate-500">追問：{row.question}</div> : null}
          {row.help ? <div className="text-[11px] text-slate-400">{row.help}</div> : null}
        </div>
      ),
    },
    {
      key: 'type',
      header: '型別',
      render: (row) => (
        <div>
          <Badge tone="slate">{ATTRIBUTE_TYPE_LABELS[row.type] ?? row.type}</Badge>
          {row.ordered ? <span className="ml-1 text-[11px] text-slate-500">有序</span> : null}
          {row.values.length ? <div className="mt-0.5 max-w-[16rem] text-[11px] text-slate-500">{row.values.map((v) => v.label).join('／')}</div> : null}
        </div>
      ),
    },
    { key: 'unit', header: '單位', render: (row) => (row.unit ? `${UNIT_LABELS[row.unit] ?? row.unit}` : '—') },
    { key: 'domains', header: '領域', render: (row) => <TagList items={row.domains.map((d) => (d === 'all' ? '全部' : labelOfDomain(d)))} tone="indigo" /> },
    { key: 'sensitivity', header: '敏感度', render: (row) => <Badge tone={row.sensitivity === 'high' ? 'red' : row.sensitivity === 'medium' ? 'amber' : 'slate'}>{SENSITIVITY_LABELS[row.sensitivity] ?? row.sensitivity}</Badge> },
    { key: 'hard', header: '硬過濾', render: (row) => (row.hard_filter ? <Badge tone="green">是</Badge> : <span className="text-slate-400">—</span>) },
    { key: 'priority', header: '追問優先', className: 'text-right tabular-nums', render: (row) => (row.derived ? <span className="text-slate-400" title={`推導：${row.derived}`}>推導</span> : row.ask_priority) },
    { key: 'aliases', header: '別名', className: 'text-right tabular-nums', render: (row) => <span title={row.aliases.join('、')}>{row.aliases.length}</span> },
    {
      key: 'mined',
      header: '語料別名',
      className: 'text-right tabular-nums',
      render: (row) => (row.mined_aliases.length ? <span title={row.mined_aliases.map((m) => `${m.term}（z=${m.z}）`).join('、')}>{row.mined_aliases.length}</span> : <span className="text-slate-400">0</span>),
    },
    { key: 'rules', header: '規則使用', className: 'text-right tabular-nums', render: (row) => formatNumber(row.rules_using) },
  ];
  return (
    <div className="rounded-lg border border-slate-200">
      <button type="button" onClick={() => setOpen((v) => !v)} className="flex w-full items-center justify-between rounded-t-lg bg-slate-50 px-3 py-2 text-left text-sm font-semibold text-slate-800">
        <span>
          {label} <span className="mono text-xs font-normal text-slate-400">{namespace}</span> <span className="font-normal text-slate-500">（{attributes.length}）</span>
        </span>
        <span className="text-xs text-slate-500">{open ? '收合 ▲' : '展開 ▼'}</span>
      </button>
      {open ? <DataTable columns={columns} rows={attributes} rowKey={(row) => row.id} dense /> : null}
    </div>
  );
}

function TaxonomyTree({ nodes, needLabel }: { nodes: TaxonomyNode[]; needLabel: (value: string) => string }) {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const domains = nodes.filter((node) => !node.parent);
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {domains.map((domain) => (
        <div key={domain.id} className="rounded-lg border border-slate-200 bg-white p-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold text-slate-900">{domain.label}</span>
            <span className="mono text-[11px] text-slate-400">{domain.id}</span>
            <span className="text-xs text-slate-500">{domain.children.length} 類</span>
          </div>
          {domain.description ? <div className="mt-0.5 text-xs text-slate-500">{domain.description}</div> : null}
          <ul className="mt-2 space-y-1.5 border-l border-slate-200 pl-3">
            {domain.children.map((childId) => {
              const leaf = byId.get(childId);
              if (!leaf) return null;
              return (
                <li key={childId} className="text-sm">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-slate-800">{leaf.label}</span>
                    <span className="mono text-[11px] text-slate-400">{leaf.id}</span>
                    {leaf.need_types.map((need) => (
                      <Badge key={need} tone="emerald">
                        {needLabel(need)}
                      </Badge>
                    ))}
                    {leaf.default_benefit_form ? <span className="text-[11px] text-slate-400">預設給付：{leaf.default_benefit_form}</span> : null}
                  </div>
                  {leaf.description ? <div className="text-xs text-slate-500">{leaf.description}</div> : null}
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default function RegistryPage() {
  const registry = useAsync(() => api.registry(), []);
  const keywords = useAsync(() => api.keywords(), []);
  const { options, labels } = useMetaOptions();
  const [keywordGroup, setKeywordGroup] = useState('');

  const groups = useMemo(() => {
    const map = new Map<string, RegistryAttribute[]>();
    for (const attribute of registry.data?.attributes ?? []) {
      const list = map.get(attribute.namespace) ?? [];
      list.push(attribute);
      map.set(attribute.namespace, list);
    }
    return Array.from(map.entries());
  }, [registry.data]);

  const keywordGroups = useMemo(() => Array.from(new Set((keywords.data?.table ?? []).map((row) => row.group))), [keywords.data]);
  const keywordRows = useMemo(() => (keywords.data?.table ?? []).filter((row) => !keywordGroup || row.group === keywordGroup).sort((a, b) => b.weight - a.weight), [keywords.data, keywordGroup]);

  const tagColumns: Column<IdentityTag>[] = [
    {
      key: 'label',
      header: '身分標籤',
      render: (row) => (
        <div>
          <span className="font-medium text-slate-900">{row.label}</span> <span className="mono text-[11px] text-slate-400">{row.id}</span>
          {row.virtual ? <Badge tone="gray" className="ml-1">虛擬（只能由 implies 推得）</Badge> : null}
        </div>
      ),
    },
    { key: 'aliases', header: '別名', className: 'min-w-[14rem]', render: (row) => <TagList items={row.aliases} /> },
    { key: 'implies', header: '蘊含（具備此身分即視為具備）', render: (row) => <TagList items={row.implies.map((id) => registry.data?.identity_ontology.find((t) => t.id === id)?.label ?? id)} tone="emerald" /> },
    { key: 'attribute', header: '對應屬性', render: (row) => (row.attribute ? <span className="mono text-xs">{row.attribute}</span> : <span className="text-slate-400">—</span>) },
    { key: 'basis', header: '依據', className: 'min-w-[12rem] text-xs text-slate-500', render: (row) => row.basis || '—' },
  ];

  const keywordColumns: Column<KeywordRow>[] = [
    { key: 'group', header: '群組', render: (row) => <Badge tone={row.group === 'negative' ? 'red' : row.group === 'benefit_signal' ? 'green' : 'blue'}>{KEYWORD_GROUP_LABELS[row.group] ?? CATEGORY_LABELS[row.group] ?? row.group}</Badge> },
    { key: 'term', header: '詞', render: (row) => <span className="font-medium text-slate-800">{row.term}</span> },
    { key: 'weight', header: '權重', className: 'text-right tabular-nums', render: (row) => row.weight },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">屬性登錄表與類別</h1>
        <p className="mt-1 text-sm text-slate-600">系統只能用登錄表裡定義的屬性抽取規則與比對資格；領域／類別樹決定分類器的候選清單；身分本體決定「低收入戶」等身分的同義詞與蘊含關係。全部來自 GET /api/registry 與 GET /api/keywords。</p>
      </div>

      {registry.loading && !registry.data ? (
        <LoadingBlock text="載入登錄表…" />
      ) : registry.error && !registry.data ? (
        <ErrorBox message={registry.error} onRetry={registry.reload} />
      ) : registry.data ? (
        <>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <StatCard label="登錄表版本" value={`v${registry.data.version}`} tone="indigo" sub={`taxonomy v${registry.data.taxonomy_version}`} />
            <StatCard label="屬性" value={formatNumber(registry.data.attributes.length)} sub={`${groups.length} 個命名空間`} />
            <StatCard label="領域 / 類別" value={`${registry.data.taxonomy.filter((n) => !n.parent).length} / ${registry.data.taxonomy.filter((n) => n.is_leaf).length}`} tone="blue" />
            <StatCard
              label="最低生活費表"
              value={registry.data.poverty_line.verified ? '已核對' : '未核對'}
              tone={registry.data.poverty_line.verified ? 'green' : 'amber'}
              sub={registry.data.poverty_line.verified ? `${registry.data.poverty_line.year ?? ''} 年` : '未核對前不會用於任何判定'}
            />
          </div>

          {!registry.data.poverty_line.verified ? (
            <Notice tone="warn">
              各縣市「最低生活費」尚未核對（poverty_line.verified = false），家庭所得相對最低生活費的推導屬性會回「資料不足」，不會據此判定不符合。請至{' '}
              <ExternalLink href={registry.data.poverty_line.source_url}>衛福部社會救助網</ExternalLink> 核對後更新。
            </Notice>
          ) : null}

          <Section title="屬性登錄表（attributes）" description="每個屬性：型別、允許值、單位、適用領域、敏感度、是否可做候選檢索（硬過濾）、追問優先順序、別名數，以及目前有多少條規則用到它。">
            <div className="space-y-3">
              {groups.map(([namespace, attributes]) => (
                <AttributeGroup key={namespace} namespace={namespace} label={namespaceLabel(namespace, options?.namespaces)} attributes={attributes} labelOfDomain={(domain) => labels.of('domain', domain)} />
              ))}
            </div>
          </Section>

          <Section title="領域／類別樹（taxonomy）" description="8 個領域、42 個葉節點類別；每個類別標示能滿足的需求類型（用於結果頁的需求分流）與預設給付形式。">
            <TaxonomyTree nodes={registry.data.taxonomy} needLabel={(value) => labels.of('need_type', value)} />
          </Section>

          <Section title="身分本體（identity_ontology）" description="身分標籤的標準名稱、同義詞、蘊含關係與對應的 profile 屬性；比對「身分：清寒」時會依 implies 展開（低收入戶 → 清寒 → 弱勢學生）。">
            <DataTable columns={tagColumns} rows={registry.data.identity_ontology} rowKey={(row) => row.id} dense />
          </Section>
        </>
      ) : null}

      <Section
        title="關鍵字表（keywords）"
        description="分類器用來判斷「這頁是不是補助公告」與「屬於哪個類別」的詞與權重。標示「語料統計」者是由已爬取語料以統計方法產生，不是人工挑選。"
        actions={keywords.data ? <Badge tone={keywords.data.source === 'mined' ? 'indigo' : 'slate'}>{keywords.data.source === 'mined' ? '語料統計（mined）' : '人工種子（seed）'}</Badge> : null}
      >
        {keywords.loading && !keywords.data ? (
          <LoadingBlock text="載入關鍵字表…" />
        ) : keywords.error && !keywords.data ? (
          <ErrorBox message={keywords.error} onRetry={keywords.reload} />
        ) : keywords.data ? (
          <div className="space-y-3">
            <KeyValueTable
              rows={[
                { label: '產生時間', value: formatDateTime(keywords.data.generated_at) },
                { label: '方法', value: keywords.data.method || '—' },
                { label: '判定門檻', value: `訊號分數 ≥ ${keywords.data.threshold}` },
                {
                  label: '語料',
                  value: keywords.data.corpus ? (
                    <span className="text-xs">
                      {formatNumber(keywords.data.corpus.documents ?? null)} 份文件（正例 {formatNumber(keywords.data.corpus.positives ?? null)}、負例 {formatNumber(keywords.data.corpus.negatives ?? null)}、未標記{' '}
                      {formatNumber(keywords.data.corpus.unlabeled ?? null)}）・{formatNumber(keywords.data.corpus.sentences ?? null)} 句（條件句 {formatNumber(keywords.data.corpus.condition_sentences ?? null)}）・來源{' '}
                      {keywords.data.corpus.sources?.length ?? 0} 個
                    </span>
                  ) : (
                    '—'
                  ),
                },
                { label: '條件句提示詞', value: <TagList items={keywords.data.condition_cues} /> },
                { label: '報告', value: keywords.data.report_path ? <span className="mono break-all text-xs">{keywords.data.report_path}</span> : '—' },
              ]}
            />
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-500">群組：</span>
              <button type="button" onClick={() => setKeywordGroup('')} className={`rounded-full border px-2.5 py-0.5 ${!keywordGroup ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-300 bg-white text-slate-600'}`}>
                全部（{keywords.data.table.length}）
              </button>
              {keywordGroups.map((group) => (
                <button
                  key={group}
                  type="button"
                  onClick={() => setKeywordGroup(group)}
                  className={`rounded-full border px-2.5 py-0.5 ${keywordGroup === group ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-300 bg-white text-slate-600'}`}
                >
                  {KEYWORD_GROUP_LABELS[group] ?? CATEGORY_LABELS[group] ?? group}（{keywords.data?.table.filter((row) => row.group === group).length}）
                </button>
              ))}
            </div>
            <DataTable columns={keywordColumns} rows={keywordRows} rowKey={(row) => `${row.group}-${row.term}`} dense emptyText="沒有關鍵字" />
          </div>
        ) : null}
      </Section>
    </div>
  );
}
