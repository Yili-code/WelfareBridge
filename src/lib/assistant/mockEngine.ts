import { ageLabel } from '../questionnaire';
import type { Profile } from "../types";
import type {
  AppealDraft,
  AssistantEngine,
  AssistantState,
  AssistantTurn,
} from "./types";

/**
 * 原型階段的引導式對話：一份寫死的腳本。
 * 之後改接 Gemini 時，只要換掉這個 engine 的實作（介面不變），
 * UI 與後台的需求登記流程都不用動。
 */

interface Step {
  key: string;
  ask: (profile: Profile | null) => string[];
  quickReplies: string[];
  multiSelect?: boolean;
  allowFreeText?: boolean;
}

const STEPS: Step[] = [
  {
    key: "topic",
    ask: (p) => [
      p
        ? `我先確認一下：這次是要幫「${p.nickname}」找資源，居住在${p.region}，${ageLabel(p)}，對嗎？`
        : "我先了解一下您的狀況。",
      "現在最讓您困擾的是哪一件事？",
    ],
    quickReplies: [
      "家裡經濟壓力大",
      "照顧家人很吃力",
      "看病或醫療費用",
      "學費或就學開銷",
      "找不到工作",
      "住的地方有困難",
    ],
    allowFreeText: true,
  },
  {
    key: "duration",
    ask: () => ["了解。這個狀況大概持續多久了？"],
    quickReplies: ["最近才發生", "1～6 個月", "半年以上", "長期都是這樣"],
  },
  {
    key: "applied",
    ask: () => ["目前有申請過任何補助或服務嗎？"],
    quickReplies: [
      "完全沒有申請過",
      "有申請，但不夠用",
      "申請過但沒通過",
      "不知道可以申請什麼",
    ],
  },
  {
    key: "want",
    ask: () => ["如果可以優先幫您處理一件事，您最希望是什麼？"],
    quickReplies: [
      "一次性的急難救助金",
      "每個月固定的補助",
      "有人可以到府協助",
      "課程或職業訓練",
      "只是想先知道能申請什麼",
    ],
    multiSelect: true,
  },
  {
    key: "extra",
    ask: () => [
      "最後，有沒有想補充的？例如家裡成員、健康狀況、或急迫的時間點。",
    ],
    quickReplies: ["沒有了，這樣就好"],
    allowFreeText: true,
  },
];

function buildDraft(
  answers: Record<string, string>,
  profile: Profile | null,
): AppealDraft {
  const main = answers.want || answers.topic || "尋找可申請的福利資源";
  const lines = [
    `狀況：${answers.topic ?? "未說明"}`,
    `持續時間：${answers.duration ?? "未說明"}`,
    `申請經驗：${answers.applied ?? "未說明"}`,
    `最希望獲得的協助：${answers.want ?? "未說明"}`,
  ];
  const extra = answers.extra?.trim();
  if (extra && extra !== "沒有了，這樣就好") lines.push(`補充：${extra}`);

  return {
    region: profile?.region ?? "未填寫",
    identities: profile?.identities ?? [],
    age: profile?.age ?? null,
    mainRequest: main,
    summary: lines.join("\n"),
  };
}

function summaryText(draft: AppealDraft, profile: Profile | null) {
  const who = profile ? profile.nickname : "您";
  const identity = draft.identities.filter((i) => i !== "以上皆非");
  return [
    `我幫${who}整理成這樣：`,
    "",
    `・地區：${draft.region}`,
    `・年齡：${draft.age != null ? `${draft.age} 歲` : "未填寫"}`,
    `・身分：${identity.length ? identity.join("、") : "未特別註記"}`,
    `・主要訴求：${draft.mainRequest}`,
    "",
    draft.summary,
  ].join("\n");
}

function turnFor(
  state: AssistantState,
  profile: Profile | null,
  prefix: string[] = [],
): AssistantTurn {
  const step = STEPS[state.step];
  if (!step) {
    const draft = buildDraft(state.answers, profile);
    return {
      state,
      replies: [
        ...prefix,
        summaryText(draft, profile),
        "我在目前的資源清單裡沒有找到完全符合的項目。您可以把這份需求送出登記，承辦人員會看到並評估是否新增對應的資源；之後有符合的補助上架，我們也會主動通知您。",
      ],
      quickReplies: [],
      multiSelect: false,
      allowFreeText: false,
      draft,
    };
  }
  return {
    state,
    replies: [...prefix, ...step.ask(profile)],
    quickReplies: step.quickReplies,
    multiSelect: step.multiSelect ?? false,
    allowFreeText: step.allowFreeText ?? false,
  };
}

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const mockEngine: AssistantEngine = {
  async start(profile) {
    await delay(300);
    const state: AssistantState = { step: 0, answers: {} };
    return turnFor(state, profile, [
      "您好，我是福利資源引導助理。不確定該找什麼沒關係，我問幾個問題就好，最後會幫您整理成一份需求。",
    ]);
  },

  async reply(state, userText, profile) {
    await delay(450);
    const step = STEPS[state.step];
    if (!step) return turnFor(state, profile);
    const next: AssistantState = {
      step: state.step + 1,
      answers: { ...state.answers, [step.key]: userText },
    };
    return turnFor(next, profile);
  },
};
