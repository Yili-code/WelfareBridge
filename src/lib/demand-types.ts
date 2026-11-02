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
  /** 小幫手需求登記自動公開的 demo 項目 */
  demo?: boolean;
}

/** 從需求登記的文字猜服務類型；猜不到就歸「其他福利」 */
const TYPE_HINTS: [string, string[]][] = [
  ["失智照顧", ["失智"]], ["居家照顧", ["居家", "看護", "照顧服務"]], ["日間照顧", ["日照", "日間"]], ["交通接送", ["接送", "交通"]],
  ["機構住宿", ["機構", "安養"]], ["輔具與無障礙", ["輔具", "無障礙"]], ["照顧者支持", ["喘息", "照顧者"]], ["醫療照護", ["醫療", "就醫"]],
  ["住宅與租金", ["租屋", "租金", "房租", "住宅"]], ["育兒與托育", ["育兒", "托育", "幼兒", "生育"]], ["就學與學費", ["學費", "獎學金", "助學", "就學"]],
  ["就業與職訓", ["失業", "就業", "職訓", "求職"]], ["餐飲服務", ["送餐", "餐"]], ["申請與給付", ["急難", "給付", "申請"]],
];
const REGIONS = ["臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"];
/** 資料卡沒有地區時，從需求文字找縣市（「台」「臺」都認）；找不到回傳空字串 */
export function guessDemandRegion(text: string) {
  const normalized = text.replaceAll("台", "臺");
  return REGIONS.find(city => normalized.includes(city)) ?? REGIONS.find(city => normalized.includes(city.slice(0, 2))) ?? "";
}

export function guessDemandType(text: string) {
  return TYPE_HINTS.find(([, words]) => words.some(word => text.includes(word)))?.[0] ?? "其他福利";
}
