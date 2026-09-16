import type { AssistantEngine, AssistantState, AssistantTurn } from "./types";
import { toMatchingProfile } from "../benefit-profile";
import type { Profile } from "../types";

/** 對話本身的狀態（找哪類補助、搜尋關鍵字、跳過的題目）；使用者資料一律以資料卡為準，每輪重新帶入 */
function conversationState(guidance: Record<string, unknown> | undefined) {
 const keep = ["_domains", "_scope_skipped", "_search_keyword", "asked", "skipped"];
 return Object.fromEntries(Object.entries(guidance ?? {}).filter(([key]) => keep.includes(key)));
}

async function turn(state: AssistantState, profile: Profile | null, userText?: string): Promise<AssistantTurn> {
 const history = [...(state.history || []), ...(userText ? [{ role: "user" as const, content: userText }] : [])];
 if (history.filter(m => m.role === "user").length > 9) throw new Error("這段對話已達長度上限，請按「重新開始」。");
 // 有資料卡時以資料卡（含先前對話寫回的資料）為準；沒有資料卡時沿用對話中累積的資料
 const guidance = profile ? { ...toMatchingProfile(profile), ...conversationState(state.guidanceProfile) } : state.guidanceProfile || {};
 let response: Response;
 try {
  response = await fetch("/api/assistant", {
   method: "POST", headers: { "Content-Type": "application/json" },
   body: JSON.stringify({ profile, messages: history, guidance_profile: guidance, question_attribute: state.questionAttribute || "" }), signal: AbortSignal.timeout(330000),
  });
 } catch {
  throw new Error("小幫手暫時連不上，請稍後再試。您仍可以直接在資料卡填寫條件。");
 }
 const data = await response.json().catch(() => null);
 if (!response.ok) {
  // 4xx 是對話本身的限制（例如輪數上限），訊息可直接給使用者看；5xx 的技術細節不顯示
  throw new Error(response.status < 500 && typeof data?.detail === "string" ? data.detail : "小幫手暫時無法回應，請稍後再試。您仍可以直接在資料卡填寫條件。");
 }
 if (typeof data?.reply !== "string" || !data.reply.trim() || !Array.isArray(data.quickReplies) || !data.quickReplies.every((q: unknown) => typeof q === "string")) throw new Error("小幫手的回應不完整，請再試一次。");
 const draft = typeof data.summary === "string" && data.summary.trim() && typeof data.mainRequest === "string" && data.mainRequest.trim()
  ? { summary: data.summary, mainRequest: data.mainRequest, region: profile?.region || "", identities: profile?.identities || [], age: profile?.age ?? null } : undefined;
 return {
  search: data.search || undefined,
  learned: Array.isArray(data.learned) ? data.learned : [],
  state: { step: state.step + 1, answers: {}, turnCount: data.turn_count, candidateCount: data.candidate_count, completed: data.completed, guidanceProfile: data.guidance_profile, questionAttribute: data.question_attribute, history: [...history, { role: "assistant", content: data.reply }] },
  replies: [data.reply], quickReplies: data.quickReplies, multiSelect: false, allowFreeText: !data.completed, draft,
 };
}

export const engine: AssistantEngine = {
 start: profile => turn({ step: 0, answers: {} }, profile),
 reply: (state, text, profile) => turn(state, profile, text),
};
export * from "./types";
