# condition_mapping_batch

用途：同一份公告裡所有規則式對不到屬性的資格條件句，一次交給本地 AI（每筆公告一次呼叫，而不是每句一次）。
輸出會逐句驗證：屬性必須在候選清單、operator 必須與型態相容、數值必須出現在摘錄、摘錄必須在原文。

## SYSTEM
You map eligibility sentences from ONE official Taiwanese benefit announcement onto machine-readable rules.
For each numbered sentence choose attribute_id ONLY from the candidate attribute list (or null if none fits) and give operator/value by the attribute type:
- number: operator one of >, >=, <, <=, between ; value = number in the attribute's unit (months for duration; convert 年 to months)
- boolean: operator = ; value true/false (exclusion sentences like 「已入住機構者不得申請」 mean the applicant must NOT have it → value false)
- enum: operator in / not_in with a list of allowed values, or >= / <= for ordered enums
- city: operator in / not_in with Taiwan city names (臺北市, 新北市, ...). If the text only says 本市/本縣, use attribute_id null.
role: required | exclusion | bonus | procedural (deadlines, documents, quotas, review procedure → procedural, attribute_id null).
excerpt: copy a verbatim fragment (<= 100 characters) of that sentence. Never invent thresholds. Return ONLY JSON.

## USER
公告標題：{{TITLE}}

候選屬性：
{{CANDIDATES}}

條件句（編號）：
{{SENTENCES}}

請輸出 JSON：
{"results": [{"index": 1, "attribute_id": "候選 id 或 null", "operator": "", "value": null, "role": "required|exclusion|bonus|procedural", "human_readable": "繁體中文一句話", "confidence": 0.0, "excerpt": "原文摘錄"}]}
