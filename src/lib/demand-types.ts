/** 訴求專區的服務類型（前台表單與 API 驗證共用） */
export const DEMAND_TYPES = ["交通接送", "居家照顧", "日間照顧", "家庭托顧", "餐飲服務", "輔具與無障礙", "機構住宿", "照顧者支持", "失智照顧", "醫療照護", "就學與學費", "就業與職訓", "住宅與租金", "育兒與托育", "申請與給付", "其他福利"];

/** 附議達這個數字進入待認領（與 src/lib/server/demands.mjs 的 THRESHOLD 一致） */
export const DEMAND_THRESHOLD = 10;

export type DemandStatus = "collecting" | "pending" | "claimed" | "done";

export interface Demand {
  id: string;
  title: string;
  type: string;
  region: string;
  detail: string;
  status: DemandStatus;
  owner: string;
  result: string;
  supports: number;
  created: string;
  voted: boolean;
}
