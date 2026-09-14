# eligibility_sentences

用途：規則式抽取一句資格條件都沒抓到時，請本地 AI 從官方原文「逐字」找出資格句（誰可以申請、誰不能申請）。
輸出只會經過「逐段必須存在於原文」的驗證後，作為待對應的條件句進入屬性對應流程；不會直接變成規則。

## SYSTEM
You extract eligibility sentences from an official Taiwanese benefit page. Return up to {{MAX}} sentences copied VERBATIM from the text
(do not paraphrase, do not merge, do not translate; keep the original punctuation). Only sentences that state who is eligible
(age, residence, income, identity, student status, employment, care level, etc.) or who is excluded. Skip application procedures, documents,
amounts, contact info and general descriptions. If there are none, return an empty list. Return ONLY JSON.

## USER
標題：{{TITLE}}

原文：
<<<
{{TEXT}}
>>>

請輸出 JSON：
{"sentences": [{"excerpt": "逐字複製的資格句", "role": "required 或 exclusion"}]}
