import type { Profile } from "../types";

export interface ChatMessage {
  id: string;
  role: "assistant" | "user";
  text: string;
}

/** 助理彙整出的需求草稿，找不到資源時會送進後台 */
export interface AppealDraft {
  region: string;
  identities: string[];
  age: number | null;
  mainRequest: string;
  summary: string;
}

export interface AssistantState {
  history?: { role: "user" | "assistant"; content: string }[];
  step: number;
  answers: Record<string, string>;
}

export interface AssistantTurn {
  state: AssistantState;
  /** 助理這一輪要說的話（可能多則） */
  replies: string[];
  /** 快速回覆選項；空陣列代表請使用者自由輸入 */
  quickReplies: string[];
  /** 是否允許複選 */
  multiSelect: boolean;
  /** 是否允許自行輸入文字 */
  allowFreeText: boolean;
  /** 對話結束時附上的需求摘要 */
  draft?: AppealDraft;
}

export interface AssistantEngine {
  start(profile: Profile | null): Promise<AssistantTurn>;
  reply(
    state: AssistantState,
    userText: string,
    profile: Profile | null,
  ): Promise<AssistantTurn>;
}
