import { useState } from 'react';
import { BenefitFilters, DEFAULT_FILTERS, type Filters } from '../components/BenefitFilters';
import { BenefitTable } from '../components/BenefitTable';
import { CrawlerPanel } from '../components/CrawlerPanel';
import { ErrorBox, LoadingBlock, Section } from '../components/Feedback';
import { Pagination } from '../components/Pagination';
import { RawDocumentsPanel } from '../components/RawDocumentsPanel';
import { StatsPanel } from '../components/StatsPanel';
import { Tabs } from '../components/Tabs';
import { useAsync, useMetaOptions } from '../hooks/useApi';
import { api } from '../services/api';

const PAGE_SIZE = 50;

export default function DataCenterPage() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [refreshKey, setRefreshKey] = useState(0);
  const [tab, setTab] = useState<'benefits' | 'raw'>('benefits');
  const { options } = useMetaOptions();
  const sources = useAsync(() => api.listSources(), [refreshKey]);

  const list = useAsync(
    () =>
      api.listBenefits({
        keyword: filters.keyword || undefined,
        domain: filters.domain || undefined,
        category: filters.category || undefined,
        benefit_form: filters.benefit_form || undefined,
        provider_type: filters.provider_type || undefined,
        region: filters.region || undefined,
        application_status: filters.application_status,
        overview: filters.overview,
        kind: filters.kind,
        needs_review: filters.needs_review ? true : undefined,
        canonical_only: !filters.show_duplicates,
        sort: filters.sort,
        page,
        page_size: PAGE_SIZE,
      }),
    [filters, page, refreshKey],
  );

  const changeFilters = (next: Filters) => {
    setFilters(next);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">資料中心</h1>
        <p className="mt-1 text-sm text-slate-600">系統實際爬取的官方資料：統計、每個來源的爬蟲與解析狀態、每一份原始文件的分類原因，以及每一筆補助的原文、標準化 Schema、資格規則與解析證據。</p>
      </div>

      <StatsPanel refreshKey={refreshKey} />
      <CrawlerPanel onFinished={() => setRefreshKey((key) => key + 1)} />

      <Section
        title="補助資料"
        description="GET /api/benefits；點任一列可查看原始資料、Schema、資格規則、解析證據與本地 AI 補齊結果。"
        actions={tab === 'benefits' && list.data ? <span className="text-xs text-slate-500">共 {list.data.total.toLocaleString('zh-TW')} 筆</span> : null}
      >
        <div className="space-y-3">
          <Tabs
            tabs={[
              { id: 'benefits', label: '補助清單', badge: list.data ? list.data.total : undefined },
              { id: 'raw', label: '原始文件' },
            ]}
            active={tab}
            onChange={(id) => setTab(id as 'benefits' | 'raw')}
          />
          {tab === 'benefits' ? (
            <>
              <BenefitFilters value={filters} onChange={changeFilters} options={options} />
              {list.loading && !list.data ? (
                <LoadingBlock text="載入資料…" />
              ) : list.error ? (
                <ErrorBox message={list.error} onRetry={list.reload} />
              ) : list.data ? (
                <>
                  <div className={list.loading ? 'opacity-60 transition-opacity' : ''}>
                    <BenefitTable items={list.data.items} />
                  </div>
                  <Pagination page={list.data.page} pageSize={list.data.page_size} total={list.data.total} onChange={setPage} />
                </>
              ) : null}
            </>
          ) : (
            <RawDocumentsPanel refreshKey={refreshKey} sources={sources.data} />
          )}
        </div>
      </Section>
    </div>
  );
}
