/** 前台只呼叫 /api/public/*：後端只回傳使用者該看到的欄位。 */

export type MatchStatus = "yes" | "maybe" | "no";

export interface Price { type: "amount" | "soft"; unit: string; amount: string; note: string }

export interface BenefitCard {
  id: string;
  title: string;
  domain_id: string;
  domain: string;
  service_type: string;
  audiences: string[];
  region: string;
  agency: string;
  points: string[];
  price: Price | null;
  updated: string;
  /** 申請截止日（YYYY-MM-DD），沒有寫明時為空字串 */
  deadline: string;
  /** 隨時可以申請 */
  rolling: boolean;
  source_url: string;
}

export interface BenefitDetail extends BenefitCard {
  eligibility: { main: string[]; excluded: string[]; official: string[]; summary: string };
  content: string[];
  application: { period: string; channel: string; method: string; documents: string[]; contact: { department?: string; phone?: string; email?: string } };
  attachments: { name: string; url: string; type: string }[];
}

export interface Reason { state: "satisfied" | "unknown" | "unsure" | "violated"; text: string }
export interface MatchResult { status: MatchStatus; reasons: Reason[]; needs: string[] }
/** 「補這幾題就能確認更多」：需要進一步確認的補助最常缺的資料 */
export interface QuickQuestion { attribute_id: string; label: string; question: string; help: string; type: string; unit: string; options: { value: string; label: string }[]; affected: number }
export interface MatchResponse { results: Record<string, MatchResult>; counts: Record<MatchStatus, number>; questions: QuickQuestion[]; disclaimer: string }

export const STATUS_LABEL: Record<MatchStatus, string> = { yes: "可能符合", maybe: "需要進一步確認", no: "目前較不符合" };

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch {
    throw new Error("目前無法連線到補助資料服務，請確認網路後再試一次。");
  }
  if (!response.ok) {
    if (response.status === 404) throw new Error("找不到這項補助，可能已經下架或截止。");
    throw new Error("補助資料服務暫時無法使用，請稍後再試。");
  }
  return (await response.json()) as T;
}

export function fetchBenefits(signal?: AbortSignal) {
  return request<{ items: BenefitCard[]; total: number; disclaimer: string }>("/api/public/benefits", { signal });
}

export function fetchBenefit(id: string, signal?: AbortSignal) {
  return request<BenefitDetail>(`/api/public/benefits/${encodeURIComponent(id)}`, { signal });
}

export function matchProfile(profile: unknown, signal?: AbortSignal) {
  return request<MatchResponse>("/api/public/match", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile }), signal });
}
