import type {
  BenefitDetail,
  BenefitListParams,
  BenefitListResponse,
  CategoryOption,
  CrawlJob,
  CrawlLog,
  CrawlRunRequest,
  CrawlerStatus,
  FeedbackRequest,
  FeedbackResponse,
  HealthResponse,
  KeywordsResponse,
  MatchRequest,
  MatchResponse,
  MetaOptions,
  PipelineRequest,
  PipelineStatus,
  ProfileParseRequest,
  ProfileParseResponse,
  ProviderListResponse,
  QuestionsRequest,
  QuestionsResponse,
  RawDocument,
  RawDocumentListParams,
  RawDocumentListResponse,
  Registry,
  ReviewActionRequest,
  ReviewListResponse,
  SaveProfileRequest,
  SaveProfileResponse,
  SourceDetail,
  SourceListItem,
  Stats,
  TaskRecord,
  TaskResponse,
} from '../types';

const BASE_URL: string = '';

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

type QueryValue = string | number | boolean | null | undefined;

function buildQuery(params: Record<string, QueryValue>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : '';
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (init?.body) headers['Content-Type'] = 'application/json';
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new ApiError(`無法連線到後端 API（${reason}）`, 0);
  }
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    let detail: unknown;
    try {
      const body: unknown = await response.json();
      detail = body;
      if (body && typeof body === 'object' && 'detail' in body) {
        const d = (body as { detail: unknown }).detail;
        message = typeof d === 'string' ? d : JSON.stringify(d);
      } else {
        message = JSON.stringify(body);
      }
    } catch {
      // 非 JSON 回應，保留 HTTP 狀態碼
    }
    throw new ApiError(`${message}（HTTP ${response.status}）`, response.status, detail);
  }
  return (await response.json()) as T;
}

function get<T>(path: string, params: Record<string, QueryValue> = {}): Promise<T> {
  return request<T>(`${path}${buildQuery(params)}`);
}

function post<T>(path: string, body: unknown, params: Record<string, QueryValue> = {}): Promise<T> {
  return request<T>(`${path}${buildQuery(params)}`, { method: 'POST', body: JSON.stringify(body) });
}

export const api = {
  baseUrl: BASE_URL,

  // ---- 系統 / 儀表板 / 登錄表 ----
  health: () => get<HealthResponse>('/api/health'),
  stats: () => get<Stats>('/api/stats'),
  registry: () => get<Registry>('/api/registry'),
  keywords: () => get<KeywordsResponse>('/api/keywords'),
  categories: () => get<CategoryOption[]>('/api/categories'),
  metaOptions: () => get<MetaOptions>('/api/meta/options'),

  // ---- 補助資料 ----
  listBenefits: (params: BenefitListParams = {}) => get<BenefitListResponse>('/api/benefits', { ...params }),
  searchBenefits: (keyword: string, params: Pick<BenefitListParams, 'domain' | 'category' | 'application_status' | 'page' | 'page_size'> = {}) =>
    get<BenefitListResponse>('/api/benefits/search', { ...params, keyword }),
  getBenefit: (id: string, includeHtml = false) => get<BenefitDetail>(`/api/benefits/${encodeURIComponent(id)}`, { include_html: includeHtml || undefined }),
  getBenefitRaw: (id: string) => get<RawDocument>(`/api/benefits/${encodeURIComponent(id)}/raw`),
  listRawDocuments: (params: RawDocumentListParams = {}) => get<RawDocumentListResponse>('/api/raw-documents', { ...params }),
  listProviders: (params: { city?: string; kind?: string; keyword?: string; limit?: number } = {}) => get<ProviderListResponse>('/api/providers', params),

  // ---- 來源 ----
  listSources: () => get<SourceListItem[]>('/api/sources'),
  getSource: (id: string) => get<SourceDetail>(`/api/sources/${encodeURIComponent(id)}`),

  // ---- 爬蟲 ----
  crawlerStatus: () => get<CrawlerStatus>('/api/crawler/status'),
  runCrawler: (body: CrawlRunRequest = {}) => post<TaskResponse>('/api/crawler/run', body),
  crawlerJobs: (limit = 20, sourceId?: string) => get<CrawlJob[]>('/api/crawler/jobs', { limit, source_id: sourceId }),
  crawlerLogs: (params: { job_id?: string; source_id?: string; limit?: number } = {}) => get<CrawlLog[]>('/api/crawler/logs', params),
  crawlerTasks: () => get<TaskRecord[]>('/api/crawler/tasks'),

  // ---- 解析 pipeline ----
  runPipeline: (body: PipelineRequest = {}) => post<TaskResponse>('/api/pipeline/run', body),
  runLlmFill: (limit?: number) => post<TaskResponse>('/api/pipeline/llm-fill', {}, { limit }),
  mineKeywords: () => post<TaskResponse>('/api/pipeline/mine-keywords', {}),
  pipelineStatus: () => get<PipelineStatus>('/api/pipeline/status'),

  // ---- 審核佇列 ----
  listReview: (status = 'open', limit = 100) => get<ReviewListResponse>('/api/review', { status, limit }),
  resolveReview: (id: string, body: ReviewActionRequest) => post<{ ok: boolean }>(`/api/review/${encodeURIComponent(id)}`, body),

  // ---- 使用者資料 / 媒合 / 回饋 ----
  parseProfile: (body: ProfileParseRequest) => post<ProfileParseResponse>('/api/profile/parse', body),
  nextQuestions: (body: QuestionsRequest) => post<QuestionsResponse>('/api/profile/questions', body),
  runMatching: (body: MatchRequest) => post<MatchResponse>('/api/matching', body),
  saveProfile: (body: SaveProfileRequest) => post<SaveProfileResponse>('/api/users/profile', body),
  sendFeedback: (body: FeedbackRequest) => post<FeedbackResponse>('/api/feedback', body),
};

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return String(error);
}
