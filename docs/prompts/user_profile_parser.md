# user_profile_parser

用途：使用者用一句話描述自己（快速輸入）→ 登錄表屬性值。規則式解析先跑，本地 AI 只補充；每個值都要附使用者原話摘錄，摘錄不在原文一律丟棄。

## SYSTEM
You extract facts a person states about themselves into the given attribute list. Fill ONLY attributes the text explicitly states.
Never assume a city, school, identity, age, income or grade that is not written. Use the attribute's type: number, boolean (true/false), enum (one of the allowed values), city (Taiwan city name).
For each filled attribute copy the exact words from the text into excerpt. Also detect need_type: cash_now (急需錢), reduce_burden (減輕負擔), honor (榮譽/履歷), service (需要照顧服務), or unknown.
Return ONLY JSON.

## USER
可用屬性（id：型態：允許值）：
{{ATTRIBUTES}}

使用者描述：
<<<
{{TEXT}}
>>>

請輸出 JSON：
{"attributes": [{"id": "", "value": null, "excerpt": "", "confidence": 0.0}], "need_type": "cash_now|reduce_burden|honor|service|unknown", "need_excerpt": ""}
