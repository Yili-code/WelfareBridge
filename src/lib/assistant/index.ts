import type { AssistantEngine } from "./types";
import { mockEngine } from "./mockEngine";

/**
 * 目前使用寫死腳本的 mockEngine。
 * 之後要接 Gemini 時：實作一個同樣符合 AssistantEngine 介面的 geminiEngine
 * （建議在 /api/assistant 這支 route 裡呼叫，避免金鑰外流到瀏覽器），
 * 然後把下面這行換掉即可，元件不用改。
 */
export const engine: AssistantEngine = mockEngine;

export * from "./types";
