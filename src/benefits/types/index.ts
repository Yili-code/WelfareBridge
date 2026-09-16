// 與後端 v2 JSON 對應的型別（見 backend/app/api/serializers.py、api/*.py、schemas/api.py、matching/*.py、registry/loader.py）。

// ---------- 共用 ----------
export interface Option {
  value: string;
  label: string;
}

export interface DomainOption extends Option {
  description?: string;
}

export interface CategoryOption extends Option {
  domain: string;
  domain_label?: string;
  need_types?: string[];
}

export interface Amount {
  type?: string; // fixed | range | tiered | unknown
  value?: number | null;
  min?: number | null;
  max?: number | null;
  unit?: string; // TWD
  period?: string; // month | semester | year | once | day | unknown
  count_per_year?: number | null;
  description?: string;
  tiers?: Array<{ value: number }>;
}

export interface ApplicationPeriod {
  start_date?: string;
  end_date?: string;
  rolling?: boolean;
  description?: string;
  by_school_deadline?: boolean;
}

export interface ApplicationContact {
  phone?: string;
  email?: string;
  department?: string;
}

export interface ApplicationInfo {
  channel?: string; // school | agency | online | mail | unknown
  effort?: string; // low | medium | high
  documents?: string[];
  requires_interview?: boolean;
  requires_recommendation?: boolean;
  requires_essay?: boolean;
  requires_office_proof?: boolean;
  requires_financial_proof?: boolean;
  method?: string;
  contact?: ApplicationContact;
}

/** benefits.benefit（標準 Schema 的給付 metadata） */
export interface BenefitMeta {
  benefit_form?: string;
  benefit_form_inferred?: boolean;
  amount?: Amount;
  amount_annualized?: number | null;
  application_period?: ApplicationPeriod;
  award_basis?: string;
  quota?: number | null;
  quota_tiers?: unknown[];
  application?: ApplicationInfo;
  obligations?: string[];
  exclusive_with?: string[]; // public_funding | government_benefit | same_provider | same_category | any_other | none
  renewable?: boolean | null;
  decision_lead_days?: number | null;
  target_population_text?: string;
}

// ---------- 補助（benefit_summary） ----------
export interface BenefitSummary {
  id: string;
  canonical_id: string;
  is_canonical: boolean;
  title: string;
  domain: string;
  domain_label: string;
  category: string;
  category_label: string;
  provider: string;
  provider_type: string;
  provider_type_label: string;
  provider_region: string;
  benefit_form: string;
  benefit_form_label: string;
  amount: Amount;
  amount_annualized: number | null;
  application_period: ApplicationPeriod;
  award_basis: string;
  award_basis_label: string;
  quota: number | null;
  application_channel: string;
  application_effort: string;
  exclusive_with: string[];
  residence_cities: string[];
  education_levels: string[];
  tags_required: string[];
  status: string; // active | expired | needs_review | superseded
  is_overview: boolean;
  record_kind: string; // program | portal
  quality_tier: string; // verified | needs_review | portal
  missing_fields: string[];
  categories_secondary: string[];
  categories_secondary_labels: string[];
  category_confidence: string; // high | medium | low
  uncertain: boolean; // 閘門三方不一致：疑似補助，待人工確認（不進媒合）
  category_uncertain: boolean; // 類別三方不一致：主類別待確認（仍可媒合）
  classification_basis: string;
  needs_review: boolean;
  review_reasons: string[];
  source_id: string;
  source_name: string;
  source_url: string;
  official_domain: string;
  source_type: string;
  source_verified: boolean;
  is_repost: boolean;
  content_type: string;
  data_confidence: number | null;
  confidence: number | null;
  llm_processed: boolean;
  llm_model: string;
  llm_accepted: number;
  rules_count: number;
  simple_rules: number;
  complex_rules: number;
  keywords: string[];
  extraction_version: string;
  registry_version: number | null;
  first_seen_at: string | null;
  updated_at: string | null;
}

export interface BenefitListResponse {
  items: BenefitSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface BenefitListParams {
  keyword?: string;
  domain?: string;
  category?: string;
  provider?: string;
  provider_type?: string;
  benefit_form?: string;
  region?: string;
  education_level?: string;
  min_amount?: number;
  application_status?: 'active' | 'expired' | 'all';
  needs_review?: boolean;
  canonical_only?: boolean;
  source_id?: string;
  overview?: 'all' | 'hide' | 'only';
  kind?: 'program' | 'portal' | 'all';
  sort?: 'updated' | 'deadline' | 'title';
  page?: number;
  page_size?: number;
}

export interface RuleEvidence {
  excerpt?: string;
  extractor?: string; // structured_field | rule_based | pattern | llm
  condition_text?: string;
}

export interface Rule {
  id: string;
  attribute_id: string;
  operator: string;
  value: unknown;
  unit: string;
  group_id: string;
  group_logic: string; // any
  complexity: string; // simple | complex
  role: string; // required | exclusion | bonus
  human_readable: string;
  evidence: RuleEvidence;
  confidence: number;
  inferred: boolean;
  inference_basis: string;
  registry_version?: number;
  attribute_label: string;
  attribute_type: string;
  value_label: string | null;
}

export interface Evidence {
  field: string;
  value: unknown;
  excerpt: string;
  extractor: string;
  confidence: number;
  inferred: boolean;
  inference_basis: string;
}

export interface Condition {
  text: string;
  excerpt: string;
  role: string; // required | exclusion | bonus | procedural
  status: string; // mapped | unmapped | complex | procedural | unresolved
  attribute_id: string | null;
  candidates?: string[];
  method: string; // rule | llm
}

export interface Attachment {
  url: string;
  name?: string;
  type?: string;
}

export interface Classification {
  is_benefit?: boolean;
  signal_score?: number;
  threshold?: number;
  category?: string;
  domain?: string;
  category_scores?: Record<string, number>;
  confidence?: number;
  matched_signal?: string[];
  matched_negative?: string[];
  matched_category?: Record<string, string[]>;
  regions?: string[];
  method?: string; // keyword | keyword+llm | rule | config
  rules_source?: string; // seed | mined
  reasons?: string[];
  reason?: string; // config / rule 型分類只有單一 reason
  llm?: unknown;
}

export interface RawDocument {
  id: string;
  source_id: string;
  source_name: string;
  source_url: string;
  title: string;
  content_type: string;
  raw_text: string;
  structured: Record<string, unknown>;
  meta: Record<string, unknown>;
  attachments: Attachment[];
  file_path: string;
  content_hash: string;
  crawl_time: string | null;
  first_seen_at: string | null;
  last_seen_at: string | null;
  last_crawled_at: string | null;
  published_date: string;
  classification: Classification | null;
  processing_status: string; // new | extracted | filtered_out | needs_review | provider_data | skipped | error
  processing_error: string;
  processed_at: string | null;
  skip_reason: string;
  benefit_id: string | null;
  rows_count: number | null;
  raw_html?: string;
}

export interface RawDocumentListResponse {
  items: RawDocument[];
  total: number;
  page: number;
  page_size: number;
}

export interface RawDocumentListParams {
  source_id?: string;
  processing_status?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
}

export interface VerificationDetails {
  url?: string;
  domain?: string;
  https?: boolean;
  verified?: boolean;
  status?: string;
  method?: string;
  domain_type?: string;
  organization?: string;
  provider_type?: string;
  source_type?: string;
  title_check?: boolean | null;
  reasons?: string[];
  [key: string]: unknown;
}

export interface Source {
  id: string;
  name: string;
  organization: string;
  provider_type: string;
  provider_type_label: string;
  source_type: string;
  base_url: string;
  official_domain: string;
  crawler_class: string;
  enabled: boolean;
  request_delay_seconds: number;
  source_verified: boolean;
  source_verification_method: string;
  source_status: string;
  verification_details: VerificationDetails | null;
  data_confidence: number | null;
  notes: string;
  domains: string[];
  pages_total: number;
  pages_skipped: number;
  follow_links: boolean;
  last_run_at: string | null;
  last_status: string; // success | partial | failed | skipped | never
  last_record_count: number;
  last_error: string;
}

export interface SourceListItem extends Source {
  raw_documents: number;
  benefits: number;
}

export interface CrawlerSource extends SourceListItem {
  jobs_success: number;
  jobs_failed: number;
  jobs_total: number;
}

export interface SourceDetail extends SourceListItem {
  recent_jobs: CrawlJob[];
  raw_by_status: Record<string, number>;
}

export interface RelatedRecord {
  id: string;
  source_id: string;
  source_name: string;
  source_url: string;
  is_canonical: boolean;
  provider: string;
  title: string;
}

export interface Provider {
  id: string;
  name: string;
  service_kind: string;
  city: string;
  address: string;
  phone: string;
  record: Record<string, unknown>;
  source_url: string;
  source_name: string;
  crawl_time: string | null;
}

export interface ProviderListResponse {
  items: Provider[];
  total: number;
  kinds: string[];
}

export interface LlmTaskSummary {
  accepted: number;
  rejected: number;
  proposed_attributes?: number;
}

/** llm.accepted 兩種形狀：benefit_meta → {field,value,excerpt}；condition_mapping → {sentence,attribute_id,operator,value} 或 {sentence,result} */
export interface LlmAccepted {
  field?: string;
  value?: unknown;
  excerpt?: string;
  sentence?: string;
  result?: string;
  attribute_id?: string;
  operator?: string;
}

export interface LlmRejected {
  field?: string;
  sentence?: string;
  reason: string;
}

export interface LlmReport {
  processed?: boolean;
  model?: string;
  provider?: string;
  processed_at?: string | null;
  tasks?: Record<string, LlmTaskSummary>;
  accepted?: LlmAccepted[];
  rejected?: LlmRejected[];
  errors?: string[];
}

/** benefits 集合的完整文件（benefit_detail）；欄位太多，只宣告會用到的。 */
export interface BenefitSchema {
  id: string;
  raw_document_id?: string;
  source_id?: string;
  title?: string;
  domain?: string;
  category?: string;
  category_label?: string;
  provider?: string;
  provider_type?: string;
  provider_region?: string;
  source?: {
    source_id?: string;
    source_name?: string;
    source_url?: string;
    official_domain?: string;
    source_type?: string;
    source_verified?: boolean;
    source_verification_method?: string;
    crawl_time?: string;
    published_date?: string;
    is_repost?: boolean;
    data_confidence?: number;
    content_type?: string;
    file_path?: string;
    [key: string]: unknown;
  };
  description?: string;
  is_overview?: boolean;
  status?: string;
  benefit?: BenefitMeta;
  keywords?: string[];
  attachments?: Attachment[];
  structured_fields?: Record<string, string>;
  review?: { needs_review?: boolean; reasons?: string[] };
  index?: Record<string, unknown>;
  original_text?: string;
  [key: string]: unknown;
}

export interface BenefitDetail {
  benefit: BenefitSummary;
  schema: BenefitSchema;
  rules: Rule[];
  evidence: Evidence[];
  conditions: Condition[];
  llm: LlmReport;
  classification: Classification;
  raw_document: RawDocument | null;
  source: Source | null;
  related_records: RelatedRecord[];
  providers_nearby: Provider[];
  registry_version: number;
}

// ---------- 儀表板 ----------
export interface CountLabel {
  count: number;
  label: string;
  domain?: string;
}

export interface LlmStatus {
  provider: string;
  online: boolean;
  detail: string;
  base_url?: string;
  model: string;
  max_documents_per_run?: number;
}

export interface KeywordCorpus {
  documents?: number;
  positives?: number;
  negatives?: number;
  unlabeled?: number;
  categories?: Record<string, number>;
  sources?: string[];
  sentences?: number;
  condition_sentences?: number;
}

export interface Stats {
  benefits_total: number;
  benefits_canonical: number;
  benefits_active: number;
  benefits_expired: number;
  benefits_overview: number;
  benefits_programs: number;
  benefits_portals: number;
  quality_verified: number;
  uncertain: number;
  today_new: number;
  needs_review: number;
  llm_processed: number;
  with_rules: number;
  providers_total: number;
  last_updated: string | null;
  last_crawl: string | null;
  official_sources: number;
  sources_enabled: number;
  sources_total: number;
  crawlers_success: number;
  crawlers_failed: number;
  crawlers_never_run: number;
  raw_documents_total: number;
  raw_documents_by_status: Record<string, number>;
  by_domain: Record<string, CountLabel>;
  by_category: Record<string, CountLabel>;
  by_provider_type: Record<string, CountLabel>;
  by_benefit_form: Record<string, CountLabel>;
  by_source: Record<string, number>;
  registry: { version: number; attributes: number; categories: number; domains: number; tags: number };
  keyword_stats: { generated_at: string | null; corpus: KeywordCorpus | null; benefit_terms: number | null; negative_terms: number | null; categories_mined: number | null };
  llm: LlmStatus;
  review_open: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  database_name: string;
  llm_provider: string;
  llm_model: string;
  llm_online: boolean;
  llm_detail: string;
  redis: boolean;
}

// ---------- 登錄表 / 表單選項 ----------
export type QuestionType = 'single_choice' | 'number' | 'text' | 'boolean' | 'city' | 'multi_choice';

export interface QuestionOption {
  value: string | number | boolean;
  label: string;
}

/** registry.catalog()：表單／追問用欄位目錄 */
export interface FieldSpec {
  label: string;
  question: string;
  help: string;
  type: QuestionType;
  options: QuestionOption[];
  namespace: string;
  domains: string[];
  sensitivity: string; // low | medium | high
  unit: string;
  derived: boolean;
  hard_filter: boolean;
  ask_priority: number;
}

export interface MinedAlias {
  term: string;
  z: number;
  df: number;
  sentences_with_seed?: number;
}

export interface RegistryAttribute {
  id: string;
  type: string; // number | boolean | enum | multi_enum | city | date | text
  label: string;
  question: string;
  help: string;
  values: QuestionOption[];
  ordered: boolean;
  unit: string;
  domains: string[];
  aliases: string[];
  mined_aliases: MinedAlias[];
  sensitivity: string;
  hard_filter: boolean;
  ask_priority: number;
  derived: string;
  deprecated: boolean;
  replaced_by: string;
  namespace: string;
  question_type: QuestionType;
  since_version: number;
  rules_using: number;
}

export interface TaxonomyNode {
  id: string;
  label: string;
  description: string;
  parent: string;
  domain: string;
  need_types: string[];
  default_benefit_form: string;
  children: string[];
  is_leaf: boolean;
}

export interface IdentityTag {
  id: string;
  label: string;
  aliases: string[];
  attribute: string;
  implies: string[];
  virtual: boolean;
  basis: string;
}

export interface PovertyLine {
  verified: boolean;
  year: number | null;
  source_url: string | null;
}

export interface Registry {
  version: number;
  taxonomy_version: number;
  attributes: RegistryAttribute[];
  taxonomy: TaxonomyNode[];
  identity_ontology: IdentityTag[];
  poverty_line: PovertyLine;
  catalog: Record<string, FieldSpec>;
}

export interface KeywordRow {
  group: string; // benefit_signal | negative | <category id>
  term: string;
  weight: number;
}

export interface KeywordsResponse {
  source: string; // seed | mined
  generated_at: string | null;
  method: string | null;
  corpus: KeywordCorpus | null;
  threshold: number;
  table: KeywordRow[];
  condition_cues: string[];
  report_path: string | null;
}

export interface MetaOptions {
  cities: string[];
  domains: DomainOption[];
  categories: CategoryOption[];
  provider_types: Option[];
  benefit_forms: Option[];
  award_basis: Option[];
  channels: Option[];
  need_types: Option[];
  dislikes: Option[];
  education_levels: Option[];
  catalog: Record<string, FieldSpec>;
  field_catalog: Record<string, FieldSpec>;
  step_order: string[];
  namespaces: Record<string, string>;
  registry_version: number;
}

// ---------- 使用者資料（matching/profile.py） ----------
export type AttributeSource = 'asked' | 'parsed' | 'form' | 'inferred' | 'skipped' | 'unsure';

export interface AttributeValue {
  value: unknown;
  source: AttributeSource | string;
  evidence?: string;
  confirmed?: boolean;
  confidence?: number;
}

export interface Profile {
  attributes: Record<string, AttributeValue>;
  need_type: string; // cash_now | reduce_burden | honor | service | unknown
  urgency: string; // high | normal | low
  dislikes: string[];
  current_benefits: string[];
  preferences: Record<string, unknown>;
  asked: string[];
  skipped: string[];
}

export interface ProfileChip {
  attribute_id: string;
  label: string;
  value: string;
  source: string;
  evidence: string;
}

export type InputMode = 'form' | 'step' | 'quick';

export interface SaveProfileRequest {
  profile: Profile;
  user_id?: string;
  input_mode?: InputMode;
  raw_input?: string;
}

export interface SaveProfileResponse {
  user_id: string;
  profile_id: string;
  profile: Profile;
}

// ---------- 快速輸入解析 ----------
export interface ParsedField {
  attribute_id: string; // 也可能是 need_type
  value: unknown;
  excerpt: string;
  extractor: string; // rule_based | llm
  confidence: number;
}

export interface ProfileParseRequest {
  text: string;
  base_profile?: Profile | null;
  use_llm?: boolean;
}

export interface ProfileParseResponse {
  profile: Profile;
  parsed_fields: ParsedField[];
  unparsed_hints: string[];
  llm_used: boolean;
  chips: ProfileChip[];
}

// ---------- 追問（matching/planner.py） ----------
export interface Question {
  attribute_id: string;
  question: string;
  type: QuestionType;
  options: QuestionOption[];
  reason: string;
  help: string;
  priority: number;
  affected: number;
  sensitivity: string;
}

export interface QuestionsRequest {
  profile: Profile;
  mode: 'step' | 'dynamic';
  max_questions?: number;
  domains?: string[] | null;
}

export interface QuestionsResponse {
  questions: Question[];
  complete: boolean;
  missing_attributes: string[];
  candidate_count: number;
}

// ---------- 媒合（matching/engine.py、ranking.py） ----------
export type MatchStatus = 'high_match' | 'possible_match' | 'not_match' | 'insufficient_data';

export interface ConditionResult {
  rule_id: string;
  attribute_id: string;
  operator: string;
  value: unknown;
  unit: string;
  group_id: string;
  role: string;
  human_readable: string;
  excerpt: string;
  status: string; // match | not_match | unknown
  reason: string;
  user_value: unknown;
  complexity: string; // simple | complex
  inferred: boolean;
  confidence: number;
  llm_used: boolean;
  rejectable: boolean;
}

export interface MatchItem {
  benefit_id: string;
  canonical_id: string;
  title: string;
  domain: string;
  category: string;
  category_label: string;
  provider: string;
  provider_type: string;
  benefit: BenefitMeta;
  source_url: string;
  source_name: string;
  status: MatchStatus;
  eligibility_score: number;
  matched_conditions: ConditionResult[];
  missing_conditions: ConditionResult[];
  failed_conditions: ConditionResult[];
  complex_conditions: ConditionResult[];
  bonus_conditions: ConditionResult[];
  missing_attributes: string[];
  explanation: string[];
  needs_review: boolean;
  llm_used: boolean;
  benefit_status: string;
  is_overview: boolean;
  matched_weight: number;
  /** 分層：tier1 ✅ 符合｜tier2 🟡 可能符合・需補充資料｜hidden 不顯示（舊資料沒有資格骨幹時由 status 推得） */
  tier?: 'tier1' | 'tier2' | 'hidden';
  /** 資格骨幹逐項判斷 */
  core?: CoreFacetResult[];
  /** 補哪些欄位可以確認 */
  needs?: string[];
  needs_labels?: string[];
  core_built?: boolean;
}

export interface CoreFacetResult {
  kind: string;
  status: 'confirmed' | 'uncertain';
  state: 'satisfied' | 'violated' | 'unknown';
  reason: string;
  needs: string[];
  label: string;
  signals: string[];
}

export interface Suitability {
  annual_value: number | null;
  win_probability: number;
  win_reason: string;
  urgency: number;
  urgency_reason: string;
  cost: number;
  cost_notes: string[];
  preference: number;
  penalty: number;
  days_left: number | null;
  expected_value_norm: number;
  total: number;
}

export type FunnelStage = 'eligible' | 'removed_deadline' | 'removed_exclusive' | 'removed_need' | 'removed_dislike' | 'other_need';

/** 被漏斗移除的項目 suitability 為空物件 */
export interface RankedItem extends MatchItem {
  funnel_stage: FunnelStage | string;
  why: string[];
  cautions: string[];
  suitability: Partial<Suitability>;
  in_bundle: boolean;
}

export interface Ranking {
  need_type: string;
  recommended: RankedItem[];
  bundle: string[];
  cards: { fastest: string | null; highest: string | null; easiest: string | null };
  other: RankedItem[];
  removed: RankedItem[];
}

export interface MatchRequest {
  profile: Profile;
  user_id?: string;
  input_mode?: InputMode;
  raw_input?: string;
  include_expired?: boolean;
  use_llm?: boolean;
  llm_budget?: number;
  limit?: number;
  domains?: string[] | null;
}

export interface MatchSummary {
  high_match: number;
  possible_match: number;
  insufficient_data: number;
  not_match: number;
  total: number;
}

export interface MatchResponse {
  matches: MatchItem[];
  summary: MatchSummary;
  ranking: Ranking;
  disclaimer: string;
  profile_used: Profile;
  profile_chips: ProfileChip[];
  user_id: string;
  profile_id: string;
  llm_used: boolean;
  llm_available: boolean;
  hard_filter_excluded: number;
}

export type FeedbackEvent = 'viewed' | 'expanded' | 'clicked_source' | 'applied' | 'awarded' | 'rejected' | 'not_interested' | 'reported_error';

export interface FeedbackRequest {
  benefit_id: string;
  profile_id?: string | null;
  event: FeedbackEvent;
  reason?: string | null;
  note?: string;
}

export interface FeedbackResponse {
  ok: boolean;
  id: string;
}

// ---------- 爬蟲 / pipeline / 審核 ----------
export interface TaskRecord {
  task_id: string;
  kind: string; // crawl | pipeline | llm_fill | mine_keywords
  params: Record<string, unknown>;
  status: string; // queued | running | finished | failed
  queued_at: string;
  started_at?: string;
  finished_at?: string;
  backend: string; // thread | redis
  result: unknown;
  error: string;
}

export interface CrawlerStatus {
  sources: CrawlerSource[];
  running: boolean;
  running_kinds: string[];
  tasks: TaskRecord[];
  redis: boolean;
  last_crawl: string | null;
}

export interface CrawlRunRequest {
  source_ids?: string[] | null;
  run_pipeline?: boolean;
  max_items?: number | null;
}

export interface TaskResponse {
  task: TaskRecord;
  message: string;
}

export interface CrawlJob {
  id: string;
  source_id: string;
  started_at: string | null;
  finished_at: string | null;
  status: string;
  triggered_by: string;
  discovered: number;
  fetched: number;
  new_documents: number;
  updated_documents: number;
  unchanged_documents: number;
  failed_items: number;
  error: string;
}

export interface CrawlLog {
  id: string;
  job_id: string | null;
  source_id: string | null;
  level: string | null;
  message: string | null;
  url: string | null;
  created_at: string | null;
}

export interface PipelineRequest {
  source_ids?: string[] | null;
  force?: boolean;
  use_llm?: boolean | null;
  limit?: number | null;
}

export interface PipelineStatus {
  raw_documents_by_status: Record<string, number>;
  pending: number;
  benefits_total: number;
  llm_pending: number;
  llm: LlmStatus;
  running: boolean;
  running_kinds: string[];
  tasks: TaskRecord[];
}

export interface ReviewItem {
  id: string;
  kind: string | null;
  benefit_id: string | null;
  raw_document_id: string | null;
  payload: unknown;
  status: string | null;
  action: string;
  created_at: string | null;
  resolved_at: string | null;
}

export interface ReviewListResponse {
  items: ReviewItem[];
  total: number;
}

export interface ReviewActionRequest {
  action: string; // accept | edit | mark_synonym | approve_attribute | reject
  note?: string;
  payload?: Record<string, unknown> | null;
}
