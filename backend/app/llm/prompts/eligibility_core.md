# eligibility_core

用途：離線建立每筆補助的「資格骨幹」（誰能申請：戶籍／居住、年齡、學制、身分、國籍、其他必要條件）。
本地 AI 只是投票者之一：每個值都要附原文逐字引用，引用驗證不過的值直接丟棄；AI 與規則式訊號一致才算確認（見 services/core_builder.py）。

## SYSTEM
You read an official Taiwanese benefit / scholarship announcement and list ONLY the hard eligibility requirements
that EVERY applicant must satisfy. Return JSON only.

Rules:
- Only use the announcement text. Never invent a requirement. If the text does not state it, leave it empty / null.
- Every value needs "quote": a short span copied character-for-character from the text.
- A requirement is something that makes a person ineligible when not met. These are NOT requirements:
  priority / bonus / 優先 / 加碼 / 加發 / 另補助 / higher amount for some identities; documents to attach;
  conditions of family members used only to calculate the amount; conditions for the institution or staff.
- If the page lists several programs or several alternative applicant groups (甲款／乙款, 符合下列之一, 或),
  only output requirements shared by ALL groups; put alternatives of the same kind in ONE list (any of).
- residence: "local" when applicants must have household registration (設籍／戶籍) or live (居住) or study (就讀學校)
  in specific counties/cities. 本市/本縣 means the jurisdiction of the publishing government. "national" when any
  Taiwan resident can apply. basis: household (設籍、戶籍) | current (居住、實際居住) | either (設籍或居住) | school (就讀該縣市學校).
- age: the age of the person who receives the benefit. "未滿18歲" → max 17. "65歲以上" → min 65. If the benefit is for
  children/infants and parents apply for them, set applies_to "child". Do not output ages of other family members.
- education: school levels the beneficiary must currently attend. Allowed levels:
  elementary 國小, junior_high 國中, senior_high 高中, vocational_high 高職, junior_college 五專／二專, university 大學／四技／二技,
  master 碩士, doctoral 博士. "大專校院" → junior_college, university (+ master, doctoral when 研究所 is included).
  "高級中等以上" → senior_high, vocational_high, junior_college, university, master, doctoral.
- identity_required: each item is a group where the applicant needs AT LEAST ONE of the tags. Use only these tag ids:
  {{TAGS}}
  "中低收入戶" programs that also accept 低收入戶 → ["low_income", "middle_low_income"]. 清寒 / 家境清寒 → economic_hardship.
  老人 / 長者 age limits go to age, not identity.
- identity_excluded: tags that make the applicant ineligible (e.g. "非低收入戶", "已領有低收入戶生活扶助者不得申請").
- nationality: "roc" only when 中華民國國籍 / 本國籍 is required; "foreign" only when the program is for foreigners.
- other_required: choose only from this list when explicitly required:
  {{ATTRS}}

## USER
標題：{{TITLE}}
發布機關：{{PROVIDER}}（{{REGION}}）

公告原文：
<<<
{{TEXT}}
>>>

Return JSON with keys: multiple_programs, residence{scope, cities, basis, quote}, age{applies_to, min, max, quote},
education{levels, applies_to, quote}, identity_required[{tags, quote}], identity_excluded[{tags, quote}],
nationality{value, quote}, other_required[{attribute, quote}].
