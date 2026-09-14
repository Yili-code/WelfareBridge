import type { AssistantEngine, AssistantState, AssistantTurn } from "./types";
import type { Profile } from "../types";
async function turn(state: AssistantState, profile: Profile | null, userText?: string): Promise<AssistantTurn> {
 const history = [...(state.history || []), ...(userText ? [{ role: "user" as const, content: userText }] : [])];
 if (history.length > 40) throw new Error("這段對話已達長度上限，請重新開始。");
 const response = await fetch("/api/assistant", {
  method: "POST", headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ profile, messages: history }), signal: AbortSignal.timeout(330000),
 });
 const data = await response.json().catch(() => null);
 if (!response.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "助理暫時無法連線，請重試。");
 if (typeof data?.reply !== "string" || !data.reply.trim() || !Array.isArray(data.quickReplies) || !data.quickReplies.every((q: unknown) => typeof q === "string")) throw new Error("助理回應格式不完整，請重試。");
 const draft = typeof data.summary === "string" && data.summary.trim() && typeof data.mainRequest === "string" && data.mainRequest.trim()
  ? { summary: data.summary, mainRequest: data.mainRequest, region: profile?.region || "", identities: profile?.identities || [], age: profile?.age ?? null } : undefined;
 return { state: { step: state.step + 1, answers: {}, history: [...history, { role: "assistant", content: data.reply }] }, replies: [data.reply], quickReplies: data.quickReplies, multiSelect: false, allowFreeText: true, draft };
}
export const engine: AssistantEngine = {
 start: profile => turn({ step: 0, answers: {} }, profile),
 reply: (state, text, profile) => turn(state, profile, text),
};
export * from "./types";
