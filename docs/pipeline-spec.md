# Pipeline 規格（v2）：每一階段的輸入與輸出

所有階段都對應實際程式；「保存」欄位是該階段寫入 MongoDB 或檔案的內容。

```text
Stage 1  官方來源驗證
Input:   sources.yaml 的 base_url + 抓到的頁面 <title>
Process: crawler/base/source_validator.py（gov.tw / gov.taipei / edu.tw suffix、白名單、blocklist、公立學校清單、HTTPS、title 關鍵字）
Output:  ValidationResult{verified, status, method, reasons}
保存:    sources.source_verified / source_verification_method / verification_details
規則:    verified=false → 該來源整個 skipped，不寫任何 raw_documents（例：sloan.bot.com.tw 在 blocklist）
```

```text
Stage 2  Crawler（pages → fetch → parse → follow links）
Input:   sources.yaml 的 pages（HTML / PDF / CSV / JSON / XML）與 follow_links 設定
Process: crawler/generic/page_crawler.py（GenericPageCrawler）；v1 來源仍用各自的 crawler class
         - HTML：content_selectors → 主內容區；沒命中 → 啟發式（文字量 × (1 − 連結比例)）；split_selector 一頁多方案拆分
         - 一層（或設定深度）同網域連結追蹤，只追白名單網域、allow/deny regex
         - PDF → pypdf；CSV/JSON/XML → rows；skip: true → content_type=skipped + skip_reason
Output:  RawDocumentData{source_url, title, content_type, raw_html, raw_text, structured, attachments, published_date, meta{seed_category, depth, data_kind, ...}}
保存:    raw_documents（(source_id, source_url) 唯一；hash 相同只更新 last_seen_at）、data/raw/<source>/<hash>.html、crawl_jobs、crawl_logs
```

```text
Stage 3  關鍵字統計（可重跑）
Input:   raw_documents 全部語料（正例 = seed_category / v1 分類 + 種子分類器偽正例；負例 = 名單／統計資料集 + 結構性負例（網站結構頁、列表頁）+ 偽負例；中間地帶不參與）
Process: services/keyword_mining.py（字元 n-gram、log-odds ratio + Dirichlet 先驗、冗餘過濾；訊號詞 z ≥ 3 且 lift ≥ 3 且非補助頁出現率 ≤ 30% 且跨 ≥ 2 來源且非縣市名；
         類別詞 z ≥ 2 且其他類別出現率 ≤ 30% 且非補助頁出現率 ≤ 類別出現率一半；門檻用語料回測校正：非補助頁通過率 ≤ 5% 下 F1 最高）
Output:  補助訊號詞（附 pos_rate / neg_rate / lift）、負面詞、各類別關鍵字、條件句提示詞、屬性別名候選、門檻校正曲線
保存:    benefit_crawler/config/keyword_rules_v2.yaml、app/registry/attribute_aliases_mined.yaml、docs/generated/keyword-report.md、keyword_stats.latest
```

```text
Stage 4  分類
Input:   title + raw_text
Process: services/classifier_ensemble.py 三方投票：services/classifier.py 關鍵字（投是／否／棄權）× services/embeddings.py bge-m3（p_benefit：補助／非補助平均向量、最像的類別原型、kNN）× llm/fill.classify_document（完整類別清單＋page_kind）。
         先做結構性排除（services/admission.py page_kind：表單／附件／流程圖／進度查詢／標章／統計／問答／名單／行政公告／分頁片段／亂碼 → filtered_out 附原因；標題像方案但只有附件清單 → 保留為 uncertain）。
         兩方同意才放行；不一致交 LLM；LLM 說不是但有一方說是 → 保留為 uncertain（疑似補助，不進媒合）；LLM 不可用時同樣保留。
         例外（pipeline.keep_prior_classification）：本地 AI 這次不在線而先前 AI 已確認是補助 → 沿用先前判斷，不降級。
         2026-09-16 整站重爬時模型忙不過來，62 筆已確認的補助被降級成 uncertain 而整批從媒合消失（黃金集漏掉率一度從 0% 變 17.2%）。
         類別：兩方一致 high、LLM 與一方一致 medium、其餘 low + category_uncertain（主類別待確認，仍可媒合），候選存 categories_secondary。
         黃金集 150 筆留一法回測（docs/generated/classifier-eval.md、classifier-eval-llm.md）：不含 LLM 閘門 P .95 / R .98（漏抓 2 筆、誤放行 5 筆全標 uncertain），含 LLM P .93 / R 1.0（誤放行 7 筆中 6 筆已標 uncertain）；主類別正確率含 LLM .84（寬鬆 .91）
         seed_category 指定的頁面即使關鍵字沒過也保留（標記 method=seed_category）
Output:  ClassificationResult{is_benefit, category, domain, signal_score, category_scores, confidence, matched_*, reasons}
保存:    raw_documents.classification；不是補助 → processing_status=filtered_out；分頁片段 / 統計表 / 名單 → filtered_out / skipped / provider_data（附原因）
```

```text
Stage 5  抽取（原文 → benefit 文件）
Input:   通過 Stage 4 的 raw_document + source + classification
Process: services/extractor.py
         - core：provider（發布單位／機關單位名稱／轉知）、provider_type、provider_region、is_overview
         - benefit meta：benefit_form、amount（型態／週期／年化）、application_period（含隨到隨辦）、award_basis、quota、application（channel/effort/documents/requires_*）、obligations、exclusive_with、renewable、decision_lead_days
         - rules：結構化欄位（學制／成績／獎助身分／戶籍地限制）→ 高信心規則；標題身分 → 必要條件；
                  條件句（申請資格段落或含提示詞的句子）→ 子句 → 登錄表屬性 → operator/value（數值單位、否定、以上/以下、有序 enum、縣市推定、身分標籤 OR）
                  「符合下列條件之一：」條列 → 同一 OR 群組；「不得…」→ 排除；「但／惟／除…」與過長句 → unmapped（交給 AI）
         - conditions[]：每句的狀態（mapped / unmapped / procedural / complex）與候選屬性
Output:  ExtractionOutput{benefit, review_reasons, unmapped_conditions}
```

```text
Stage 6  本地 AI 補齊（Ollama；可離線跳過，之後 --llm-fill 補；預設只補 canonical 紀錄，--include-non-canonical 補重複紀錄）
Input:   Stage 5 的 benefit + 原文
Process: llm/fill.py
         - fill_benefit_meta：只填空缺欄位；每個值附摘錄；驗證（列舉值、數字在摘錄、摘錄在原文）
         - map_conditions：每個 unmapped 條件句 → 候選屬性中選一個 + operator/value/role；驗證；仍不合 → complex；提議新屬性 → review_items
         - extract_eligibility_sentences：規則式一句條件都沒抓到時，先請 AI 逐字列出資格句（逐段驗證在原文），再進 map_conditions
         - classify_document（完整類別清單）：關鍵字分類尚未經 AI 確認的方案一律確認類別與 page_kind
         - 思考型模型關閉 think；LLM_NUM_CTX 可調；換 32GB 主機用 qwen3:32b 並 --reset-llm 全部重做
Output:  benefit.llm{processed, model, tasks, accepted[], rejected[], errors[]}
```

```text
Stage 7  驗證
Input:   benefit（規則式或含 AI 補充）+ 原文
Process: services/schema_validator.py（title/source_url 必填；provider_type/category/benefit_form/award_basis/channel/exclusive_with 列舉；日期格式；金額正數；
         規則：attribute_id 在登錄表、operator 與型態相容、value 型態與 enum 值、數字在摘錄、摘錄在原文）
Output:  ValidationOutcome{ok, benefit, dropped, review_reasons}
保存:    被移除的規則記在 benefit.review.reasons；needs_review = 有東西被移除 或 沒有任何 simple 規則
狀態:    驗證後依最後的申請期間重算 status（本地 AI 可能補上或改寫截止日）；截止日已過或原文寫明停辦 → expired
```

### 日期與金額的兩個陷阱（2026-09-16 修正）

- **起始日不是截止日**：「自108年8月1日起受理申請迄今」的日期後面接「起」→ 視為起始日。當成截止日會讓還在辦的方案被標成已過期（育兒津貼、就學補助各一筆就是這樣消失的）。
- **月日範圍取最後一個**：「9月15日起至10月15日止」的截止日是 10/15。取第一個會讓還能申請的獎學金當天就過期。
- **資力門檻不是給付金額**：「不動產：115年度每戶不超過578萬元」是資格門檻。金額子句不從冒號切開（切開後數字那半看不出是門檻），並在門檻判斷加入資力審查用語（家庭總收入、全家人口、平均分配、最低生活費、動產、不動產、存款本金、有價證券…）。附件併入原文後這類句子變多，不處理會出現「補助 100 元～300,000 元」。

```text
Stage 8  去重 + 寫入
Input:   驗證通過的 benefit
Process: services/dedup.py（標題相似 ≥ 0.82 + 機關相容／截止日相同／相似 ≥ 0.95 → 同 canonical_id；短標題加限定詞視為不同方案；官方原始公告優先）；pipeline._upsert_benefit
Output:  benefits（含 index：attribute_ids、residence_cities、education_levels、tags_required、amount、application_end、simple/complex 規則數）
保存:    benefits；raw_documents.benefit_id；過期 → status=expired（不刪除）；文件不再是補助（分類器／AI 判定、被認定為重複網址而略過）→ 移除舊 benefit
```

```text
Stage 9  User Profile
Input:   完整填寫 / 逐步問答 / 快速輸入文字
Process: matching/profile.py（{attribute_id: {value, source, evidence, confirmed}} + need_type / dislikes / current_benefits）
         matching/profile_parser.py（規則式）；llm/fill.parse_profile（可選補充，摘錄必在使用者文字中）
Output:  Profile（未提供 = None；推導屬性與 identity.tags 即時計算）
保存:    user_profiles
```

```text
Stage 10 Matching
Input:   Profile + benefits（canonical、active）
Process: matching/engine.hard_filter_candidates（硬過濾屬性、信心 ≥ 0.8、非推定）→ rule_engine.evaluate_rule → engine.match_one（群組 OR/AND、bonus 不判資格、推定不拒絕、AI 複雜條件）
Output:  MatchItem{status, eligibility_score, matched/missing/failed/complex/bonus conditions, missing_attributes, explanation}
保存:    match_results（not_match 以外）
```

```text
Stage 11 追問 + 排序 + 呈現
Input:   MatchItem[] + Profile
Process: matching/planner.py（期望資訊增益）；matching/ranking.py（A 截止／互斥 → B 需求分流／排斥 → C 適合度 → D 互斥組合 → E 三張卡）
Output:  questions[]；ranking{recommended, bundle, cards, other, removed}
呈現:    前端「我的補助」：三張卡、建議組合、可申請清單（why / cautions / 條件）、其他、已排除、資料不足、目前不符合；每張卡回到 source_url
```
