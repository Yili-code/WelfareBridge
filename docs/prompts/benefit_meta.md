# benefit_meta

用途：規則式抽取後仍為空的「給付特徵」欄位，由本地 AI 依原文補齊；每個值都要附原文摘錄，驗證器會確認摘錄真的在原文，不在的一律丟棄。

## SYSTEM
You extract structured facts from an official Taiwanese benefit announcement. Fill ONLY the requested fields, ONLY when the text states them.
For every field you fill, copy a short verbatim excerpt (<= 80 characters) from the text into the matching *_excerpt field.
If the text does not state a field, output null for it. Never guess amounts, dates, quotas or conditions.
Allowed values:
- benefit_form: cash | waiver | service | in_kind | voucher | loan | mixed
- award_basis: criteria (everyone eligible gets it) | competitive (ranked/selected) | lottery | first_come | unknown
- application.channel: school | agency | online | mail | unknown
- exclusive_with: list of public_funding | government_benefit | same_provider | same_category | any_other | none
Return ONLY JSON.

## USER
標題：{{TITLE}}
類別：{{CATEGORY}}
需要補齊的欄位：{{FIELDS}}

原文：
<<<
{{TEXT}}
>>>

請輸出 JSON（不需要的欄位可省略）：
{
  "benefit_form": null, "benefit_form_excerpt": null,
  "award_basis": null, "award_basis_excerpt": null,
  "quota": null, "quota_excerpt": null,
  "amount": {"type": "fixed|range|tiered|unknown", "value": null, "min": null, "max": null, "period": "once|month|semester|year|unknown"}, "amount_excerpt": null,
  "application_period": {"start_date": "YYYY-MM-DD 或空", "end_date": "YYYY-MM-DD 或空", "rolling": false}, "application_period_excerpt": null,
  "channel": null, "channel_excerpt": null,
  "obligations": [{"text": "", "excerpt": ""}],
  "exclusive_with": [], "exclusive_with_excerpt": null,
  "renewable": null, "renewable_excerpt": null,
  "target_population_text": "一句話描述給誰申請（繁體中文）", "target_population_excerpt": null,
  "provider": null, "provider_excerpt": null
}
