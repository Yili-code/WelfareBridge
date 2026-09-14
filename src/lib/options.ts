import type { Relation } from "./types";

export const RELATIONS: { value: Relation; label: string; hint: string }[] = [
  { value: "self", label: "我自己", hint: "為自己尋找資源" },
  { value: "child", label: "我的孩子", hint: "未成年或就學中的子女" },
  { value: "parent", label: "我的長輩", hint: "父母或需照顧的長者" },
  { value: "spouse", label: "我的配偶", hint: "伴侶或同住家人" },
  { value: "other", label: "其他對象", hint: "親友、個案或服務對象" },
];

export const REGIONS = [
  "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
  "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
  "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
  "臺東縣", "澎湖縣", "金門縣", "連江縣",
];

export const IDENTITIES = [
  "學生", "育兒家庭", "單親家庭", "新住民", "原住民",
  "身心障礙者", "身心障礙者家屬", "高齡長者", "長期照顧需求者",
  "待業／失業", "非典型就業", "獨居", "租屋族", "軍警消",
  "更生人", "遊民", "以上皆非",
];

export const ECONOMY = [
  "低收入戶",
  "中低收入戶",
  "近貧／經濟不穩定",
  "一般家庭",
  "不確定",
];

export const NEEDS = [
  "經濟補助", "醫療與健保", "就學與學費", "育兒與托育",
  "長照與照顧", "就業與職訓", "住宅與租金", "身心健康支持",
  "法律與權益", "生活物資", "交通接送", "喘息服務",
];

export const AGE_PRESETS = [
  { label: "未滿 6 歲", age: 4 },
  { label: "6–12 歲", age: 9 },
  { label: "13–17 歲", age: 15 },
  { label: "18–24 歲", age: 21 },
  { label: "25–44 歲", age: 34 },
  { label: "45–64 歲", age: 54 },
  { label: "65 歲以上", age: 70 },
];
