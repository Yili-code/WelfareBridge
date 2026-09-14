// 後端列舉值 → 中文標籤。
// 原則：API 有提供 label（*_label 欄位、/api/meta/options、/api/stats 的 label）時一律以 API 為準；
// 這裡的表只是 API 尚未載入時的備援，內容與 backend/app/api/serializers.py、registry/taxonomy.yaml 一致。

import type { Option } from '../types';

export const DOMAIN_LABELS: Record<string, string> = {
  education: '教育',
  youth: '青年',
  social_welfare: '社會福利',
  long_term_care: '長期照顧',
  disability: '身心障礙',
  labor: '勞工就業',
  housing: '住宅',
  health: '醫療健康',
};

export const CATEGORY_LABELS: Record<string, string> = {
  scholarship: '獎學金',
  student_aid: '助學金',
  tuition_waiver: '學雜費減免',
  education_subsidy: '就學補助',
  housing_support: '住宿補助',
  emergency_aid_student: '學生急難救助',
  student_loan: '就學貸款',
  study_abroad: '留學獎助',
  youth_employment: '青年就業獎勵',
  youth_entrepreneurship: '青年創業',
  youth_development: '青年發展',
  low_income_allowance: '低收入戶生活補助',
  special_circumstances_aid: '特殊境遇家庭扶助',
  birth_incentive: '生育獎勵金',
  insurance_premium_subsidy: '保險費補助',
  child_allowance: '育兒津貼',
  childcare_subsidy: '托育補助',
  parental_leave_allowance: '育嬰留停津貼',
  emergency_relief: '急難救助',
  elderly_allowance: '老人生活津貼',
  elderly_service: '老人福利服務',
  home_care: '居家服務',
  day_care: '日間照顧',
  family_care_home: '家庭托顧',
  transport_service: '交通接送',
  assistive_device: '輔具與無障礙',
  respite_care: '喘息服務',
  meal_service: '營養餐飲',
  institutional_care_subsidy: '機構住宿補助',
  ltc_general: '長照服務總覽',
  disability_living_allowance: '身心障礙者生活補助',
  disability_assistive_device: '身心障礙輔具補助',
  disability_care_subsidy: '身心障礙照顧補助',
  disability_other: '身心障礙其他福利',
  unemployment_benefit: '失業給付',
  training_allowance: '職業訓練生活津貼',
  employment_incentive: '就業促進津貼',
  employer_subsidy: '雇主補助',
  worker_welfare: '勞工福利',
  rental_subsidy: '租金補貼',
  housing_loan_subsidy: '住宅貸款利息補貼',
  social_housing: '社會住宅',
  medical_subsidy: '醫療費用補助',
  health_service: '健康服務',
};

export const PROVIDER_TYPE_LABELS: Record<string, string> = {
  central_government: '中央政府',
  local_government: '地方政府',
  township: '鄉鎮市區公所',
  school: '學校',
  private_organization: '民間團體（經官方網站公告）',
  mixed: '多個機關',
  unknown: '未分類',
};

export const BENEFIT_FORM_LABELS: Record<string, string> = {
  cash: '現金',
  waiver: '減免',
  service: '服務',
  in_kind: '實物／輔具',
  voucher: '額度／券',
  loan: '貸款',
  mixed: '混合',
};

export const AWARD_BASIS_LABELS: Record<string, string> = {
  criteria: '符合即核發',
  competitive: '擇優',
  lottery: '抽籤',
  first_come: '先到先得',
  unknown: '未載明',
};

export const CHANNEL_LABELS: Record<string, string> = {
  school: '向學校申請',
  agency: '向機關申請',
  online: '線上申請',
  mail: '郵寄',
  unknown: '未載明',
};

export const NEED_TYPE_LABELS: Record<string, string> = {
  cash_now: '急需一筆錢',
  reduce_burden: '長期減輕負擔',
  honor: '榮譽／履歷',
  service: '需要照顧服務',
  unknown: '不確定',
};

export const DISLIKE_LABELS: Record<string, string> = {
  interview: '要面試',
  essay: '要寫自傳／計畫',
  recommendation: '要推薦函',
  obligations: '得獎後有義務',
  financial_proof: '要交財力證明',
  office_proof: '要公所／村里長證明',
  loan: '貸款',
  competitive: '擇優競爭',
};

export const LEVEL_LABELS: Record<string, string> = {
  elementary: '國小',
  junior_high: '國中',
  senior_high: '高中',
  vocational_high: '高職',
  junior_college: '五專',
  university: '大學／大專（含科大、技術學院）',
  master: '碩士',
  doctoral: '博士',
};

export const NAMESPACE_LABELS: Record<string, string> = {
  applicant: '基本資料',
  education: '就學',
  academic: '成績',
  residence: '戶籍與居住',
  household: '家庭經濟',
  financial: '補助與保險',
  identity: '身分',
  disability: '身心障礙',
  care: '長期照顧',
  health: '健康',
  employment: '就業',
  housing: '住宅',
  family: '家庭',
};

// 以下為純 UI 用詞（後端沒有對應 label 表）：只翻譯列舉值本身，不新增資訊。
export const EFFORT_LABELS: Record<string, string> = { low: '低', medium: '中', high: '高' };

export const EXCLUSIVE_LABELS: Record<string, string> = {
  none: '無不得兼領規定',
  any_other: '不得與任何其他補助兼領',
  government_benefit: '不得與政府補助兼領',
  public_funding: '不得與公費／公部門補助兼領',
  same_provider: '不得與同一機關其他補助兼領',
  same_category: '不得與同類補助兼領',
};

export const PERIOD_LABELS: Record<string, string> = { month: '每月', semester: '每學期', year: '每年', once: '一次', day: '每日', unknown: '' };

export const AMOUNT_TYPE_LABELS: Record<string, string> = { fixed: '固定', range: '區間', tiered: '分級', unknown: '未載明' };

export const ROLE_LABELS: Record<string, string> = { required: '必要', exclusion: '排除', bonus: '加分／優先', procedural: '程序' };

export const COMPLEXITY_LABELS: Record<string, string> = { simple: '可自動判斷', complex: '需語意判斷' };

export const CONDITION_STATUS_LABELS: Record<string, string> = { mapped: '已對應屬性', unmapped: '未對應屬性', complex: '複雜條件', procedural: '程序性說明', unresolved: '未解析' };

export const SENSITIVITY_LABELS: Record<string, string> = { low: '低', medium: '中', high: '高（敏感）' };

export const ATTRIBUTE_TYPE_LABELS: Record<string, string> = { number: '數值', boolean: '是／否', enum: '單選', multi_enum: '多選', city: '縣市', date: '日期', text: '文字' };

export const UNIT_LABELS: Record<string, string> = { years: '年', months: '個月', score: '分', gpa: 'GPA', percent: '%', TWD: '元', TWD_year: '元／年', TWD_month: '元／月', level: '級', multiple: '倍' };

export const SOURCE_LABELS: Record<string, string> = { asked: '追問回答', parsed: '文字解析', form: '表單填寫', inferred: '系統推導', skipped: '已跳過', unsure: '不確定' };

export const FUNNEL_STAGE_LABELS: Record<string, string> = {
  eligible: '可申請',
  removed_deadline: '申請期限問題',
  removed_exclusive: '與已領補助互斥',
  removed_need: '與需求不符',
  removed_dislike: '你標記為不想要',
  other_need: '需求類型不同',
};

export const TASK_KIND_LABELS: Record<string, string> = { crawl: '爬蟲', pipeline: '重新解析', llm_fill: '本地 AI 補齊', mine_keywords: '關鍵字統計' };

export const TASK_STATUS_LABELS: Record<string, string> = { queued: '排隊中', running: '執行中', finished: '完成', failed: '失敗' };

export const BENEFIT_STATUS_LABELS: Record<string, string> = {
  active: '開放中',
  expired: '已截止',
  needs_review: '待人工確認',
  superseded: '已被取代',
};

export const CRAWL_STATUS_LABELS: Record<string, string> = {
  success: '成功',
  partial: '部分成功',
  failed: '失敗',
  skipped: '略過',
  never: '尚未執行',
};

export const PROCESSING_STATUS_LABELS: Record<string, string> = {
  new: '待解析',
  extracted: '已抽取為補助',
  filtered_out: '分類為非補助',
  needs_review: '待人工確認',
  provider_data: '服務提供者名單',
  skipped: '略過',
  error: '解析錯誤',
};

export const MATCH_STATUS_META: Record<string, { label: string; emoji: string }> = {
  high_match: { label: '高度符合', emoji: '🟢' },
  possible_match: { label: '可能符合', emoji: '🟡' },
  not_match: { label: '目前不符合', emoji: '🔴' },
  insufficient_data: { label: '資料不足', emoji: '⚪' },
};

export const OPERATOR_LABELS: Record<string, string> = {
  '=': '等於',
  '!=': '不等於',
  '>': '大於',
  '>=': '大於等於',
  '<': '小於',
  '<=': '小於等於',
  between: '介於',
  in: '屬於',
  not_in: '不屬於',
  contains: '包含',
  exists: '需具備',
};

export const KEYWORD_GROUP_LABELS: Record<string, string> = { benefit_signal: '補助訊號詞', negative: '排除詞' };

export function extractorLabel(extractor: string | undefined | null): string {
  switch (extractor) {
    case 'structured_field':
      return '來源標籤欄位';
    case 'rule_based':
      return '規則式';
    case 'pattern':
      return '樣式比對';
    case 'llm':
      return '本地 AI';
    case 'llm_supplement':
      return '本地 AI 補充';
    default:
      return extractor || '—';
  }
}

/** 優先用 API 的選項 label，其次備援表，最後回傳原值。 */
export function optionLabel(options: Option[] | null | undefined, value: string | null | undefined, fallback?: Record<string, string>): string {
  if (value === null || value === undefined || value === '') return '—';
  return options?.find((option) => option.value === value)?.label ?? fallback?.[value] ?? value;
}

export function levelLabel(level: string, lookup?: Record<string, string>): string {
  return lookup?.[level] ?? LEVEL_LABELS[level] ?? level;
}

/** 與 backend/app/schemas/api.py 的 DISCLAIMER 完全一致 */
export const DISCLAIMER = '以上為系統依官方公告內容進行的初步資格比對，實際資格仍以主辦機關審核結果為準。';

/** /api/meta/options 尚未載入時的縣市備援清單（與 services/normalization.py CITIES 一致） */
export const CITIES_FALLBACK = [
  '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市',
  '基隆市', '新竹市', '新竹縣', '苗栗縣', '彰化縣', '南投縣',
  '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣',
  '臺東縣', '澎湖縣', '金門縣', '連江縣',
];
