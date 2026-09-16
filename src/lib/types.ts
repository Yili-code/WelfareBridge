/** 建檔對象與本人的關係 */
export type Relation = "self" | "child" | "parent" | "spouse" | "other";

/** 一份「服務對象」檔案。一個使用者可以建立多份（自己、孩子、長輩…） */
export interface Profile {
  id: string;
  /** 顯示用稱呼，例如「我自己」「兒子 小明」 */
  nickname: string;
  relation: Relation;
  /** 縣市 */
  region: string;
  /** 鄉鎮市區，可留空 */
  district?: string;
  age: number | null;
  screening?: Record<string, string[]>;
  currentRegion?: string;
  /** 身分別，可複選 */
  identities: string[];
  /** 家庭經濟狀況 */
  economy: string;
  /** 主要需求類別，可複選 */
  needs: string[];
  /** 聊天助理問到或從回答判讀出的資料（依屬性 id）；比對時優先於問卷推得的值，使用者可在資料卡修改或刪除 */
  assistantAttributes?: Record<string, AssistantAttribute>;
  createdAt: string;
}

export interface AssistantAttribute {
  label: string;
  type: string;
  unit?: string;
  /** null 表示使用者回答「不確定」 */
  value: string | number | boolean | string[] | null;
  valueLabel: string;
  options?: { value: string; label: string }[];
  /** asked＝回答助理的提問；parsed＝從對話內容判讀，需要使用者確認；edited＝使用者在資料卡改過 */
  source: "asked" | "parsed" | "unsure" | "edited";
  evidence?: string;
  updatedAt: string;
}

/** 平台上架的福利／資源 */
export interface Resource {
  id: string;
  title: string;
  agency: string;
  summary: string;
  /** 適用縣市，"全國" 代表不限 */
  regions: string[];
  identities: string[];
  needs: string[];
  minAge?: number;
  maxAge?: number;
  link?: string;
  createdAt: string;
}

/**
 * 找不到現有資源時，AI 助理彙整出的需求登記。
 * 開發者／承辦人員可從後台 (/admin) 檢視，作為新增資源的依據。
 */
export interface Appeal {
  id: string;
  profileId: string | null;
  profileNickname: string;
  region: string;
  identities: string[];
  age: number | null;
  /** 主要訴求（一句話） */
  mainRequest: string;
  /** AI 摘要的完整敘述 */
  summary: string;
  /** 對話逐字紀錄，方便後台回溯 */
  transcript: { role: "assistant" | "user"; text: string }[];
  status: "new" | "reviewing" | "resolved";
  createdAt: string;
}

/** 新資源上架後，依 profile 條件比對產生的主動通知 */
export interface Notification {
  id: string;
  profileId: string;
  profileNickname: string;
  resourceId: string;
  resourceTitle: string;
  reason: string;
  read: boolean;
  createdAt: string;
}
