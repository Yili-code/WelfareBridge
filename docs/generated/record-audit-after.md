# 紀錄稽核（規則式，867 筆）

- 乾淨（沒有任何旗標）：607（70.0%）

## 旗標統計

| 旗標 | 筆數 | 說明 |
| --- | ---: | --- |
| `cash_without_amount` | 177 | 現金給付但沒有金額 |
| `category_uncertain` | 63 | 類別三方不一致（待確認） |
| `no_simple_rules` | 47 | 沒有可判斷的資格規則 |
| `text_too_short` | 19 | 原文過短 |
| `gate_uncertain` | 11 | 是否補助三方不一致（待確認） |

## 各來源旗標數

| 來源 | 紀錄 | 旗標 |
| --- | ---: | ---: |
| kinmen_sw | 83 | 33 |
| taichung_sw | 59 | 11 |
| penghu_sw | 52 | 21 |
| chiayi_county_sw | 48 | 14 |
| helpdreams_private | 44 | 2 |
| chiayi_city_sw | 39 | 13 |
| changhua_sw | 38 | 9 |
| kaohsiung_sw | 37 | 17 |
| hsinchu_city_sw | 37 | 5 |
| tainan_sw | 35 | 10 |
| keelung_sw | 34 | 25 |
| miaoli_sw | 33 | 8 |
| yilan_sw | 32 | 16 |
| taoyuan_sw | 29 | 10 |
| nantou_sw | 29 | 6 |
| hualien_sw | 27 | 6 |
| ntpc_sw | 23 | 6 |
| helpdreams_gov | 19 | 2 |
| gov_tw_services | 19 | 8 |
| hsinchu_county_sw | 17 | 6 |
| wda_emps | 16 | 11 |
| tainan_east_office | 15 | 13 |
| moi_pip | 10 | 13 |
| bli_family | 10 | 6 |
| ltc_1966 | 9 | 13 |
| ntou_stu | 8 | 0 |
| taipei_dosw | 7 | 3 |
| mohw_social_assistance | 7 | 7 |
| ntpc_banqiao_office | 7 | 3 |
| sfaa_childcare | 6 | 1 |
| taipei_doe | 5 | 4 |
| mohw_gov | 5 | 5 |
| taipei_daan_office | 5 | 4 |
| taoyuan_zhongli_office | 5 | 1 |
| ece_moe | 5 | 0 |
| moe_programs | 3 | 1 |
| taipei_ws_files | 3 | 1 |
| mol_gov | 2 | 0 |
| taipei_opendata | 2 | 2 |
| cip_regulations | 1 | 0 |
| taipei_health | 1 | 1 |
| moe_law | 1 | 0 |

## 逐筆（只列有旗標的）

### 失業勞工子女生活扶助金
- id `f29c5ebd-066f-4d71-ac54-97dddc4fcade` ｜ 來源 helpdreams_gov ｜ 類別 low_income_allowance ｜ 機關 勞動部 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 衛生福利部社會及家庭署單親培力計畫
- id `9b76b98b-d2cd-4c30-ad44-161318eaa12b` ｜ 來源 helpdreams_gov ｜ 類別 student_aid ｜ 機關 衛生福利部社會及家庭署 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 行天宮急難濟助
- id `64c28b18-5e7d-4ca5-8960-4a4c1c11a272` ｜ 來源 helpdreams_private ｜ 類別 emergency_aid_student ｜ 機關 財團法人台北行天宮 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 欣榮圖書館急難學生助學金
- id `de541c00-9c9c-4a77-b340-ae3331d27ba3` ｜ 來源 helpdreams_private ｜ 類別 emergency_aid_student ｜ 機關 財團法人福田文教基金會 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 免學費方案
- id `2ef67a73-8958-43ba-9786-8bd18d5b0bfc` ｜ 來源 moe_programs ｜ 類別 tuition_waiver ｜ 機關 教育部 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 【轉知】僑務委員會115年度中等以上學校學行優良僑生獎學金相關資訊
- id `93832692-f005-4092-b323-03acb3f00065` ｜ 來源 taipei_doe ｜ 類別 scholarship ｜ 機關 僑務委員會 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 大專校院原住民學生獎助學金
- id `ca73c4db-4a0e-49db-aca6-706a9c272160` ｜ 來源 gov_tw_services ｜ 類別 scholarship ｜ 機關 原住民族委員會 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 就保職業訓練生活津貼
- id `19601da8-980b-447d-a77b-6771cc23e0d1` ｜ 來源 gov_tw_services ｜ 類別 training_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 勞動部-失業勞工子女就學補助線上申請
- id `0fcf4dec-e4ea-48d0-bdf0-c46d3e8dddb0` ｜ 來源 gov_tw_services ｜ 類別 education_subsidy ｜ 機關 勞動部 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣-就讀大專院校學生助學金 提供民眾線上申請，可免檢附戶籍謄本(查驗是否符合設籍澎湖縣的規定)，查驗是否為澎湖縣國、
- id `e22e1df1-1580-4f79-8c9c-9cc613e38e91` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 澎湖縣政府 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣-獎助就讀大專院校學生交通圖書券申請 提供民眾線上申請服務，可透過MyData完成身分驗證及同意後，提供「 現戶全
- id `4294b2f0-b6f4-4537-a693-1926f345ca57` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 澎湖縣政府 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺中市-低收入戶就學交通補助申請 未滿25歲之低收入戶者，就讀公私立大專以下國小以上學校，可申請就學交通補助，國小每學期
- id `2b35dc2a-0e7b-4c27-b828-c96ae8fbc9c5` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 臺中市政府 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 雲林縣-弱勢家庭幸福存款資產累積脫貧方案申請 民眾可透過MyData完成身分驗證及同意後，提供戶政國民身分證資料、現戶全
- id `a5f969f1-6f6a-45ca-a70d-323689af9714` ｜ 來源 gov_tw_services ｜ 類別 low_income_allowance ｜ 機關 雲林縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 長照服務的內容 — 居家服務
- id `c196ed6a-55d1-4914-8299-22f346d56285` ｜ 來源 taipei_health ｜ 類別 home_care ｜ 機關 臺北市政府衛生局 ｜ 等級 needs_review
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 老人機構收容安置補助(1100831更新)
- id `6d598eb5-7d1d-4b36-9f35-776fcabed3c6` ｜ 來源 taipei_ws_files ｜ 類別 institutional_care_subsidy ｜ 機關 臺北市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 勞工補助與就業促進措施
- id `63909417-d268-427a-9985-80951add9e28` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺北市如何申請長照服務
- id `32c957e3-4e6f-4cb3-aaba-83f54164e075` ｜ 來源 taipei_opendata ｜ 類別 ltc_general ｜ 機關 臺北市政府 ｜ 等級 needs_review
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 臺北市長期照顧十年計畫(一)-居家服務
- id `890d710e-e6f7-4bd9-9ae5-919ad0cf8736` ｜ 來源 taipei_opendata ｜ 類別 home_care ｜ 機關 臺北市政府 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 缺工就業獎勵
- id `009e8833-b5cb-4f68-a747-1cbccd2d4aae` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 臨時工作津貼
- id `58591588-4489-44b4-951b-c301c45a526f` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 僱用安定措施
- id `88119f35-3c69-4bcf-95a4-d776112ac6ea` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 青年職得好評計畫
- id `a9dab191-384b-4cb1-a8c2-4d47385aa522` ｜ 來源 wda_emps ｜ 類別 youth_employment ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 照顧服務就業獎勵
- id `af289eba-5c49-4e8f-ac15-db63728033c8` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 天災臨時工作津貼
- id `b67fbd85-7f66-4a48-9fd5-68b5c31d472a` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 4在臺「安居」更「安老」！ 衛福部公告外國專業人才及眷屬長照新制
- id `fdcfdaab-37d4-44e8-a2b0-800efd8262f0` ｜ 來源 ltc_1966 ｜ 類別 elderly_service ｜ 機關 衛生福利部長期照顧司 ｜ 等級 needs_review
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 16公告「衛生福利部建立住宿式長照機構與產學合作國際專班攬才留用試辦計畫」(1141016修正)
- id `869c3ab7-c125-4f68-b795-14a65c9e014f` ｜ 來源 ltc_1966 ｜ 類別 study_abroad ｜ 機關 衛生福利部長期照顧司 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 公益出租人
- id `a7458c65-d7a8-4972-bd00-b30f8bd64575` ｜ 來源 moi_pip ｜ 類別 rental_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 減班休息補貼
- id `44f855e9-749f-4172-bfda-7238d630d892` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 整合住宅補貼資源實施方案
- id `9c09f8ae-c131-404b-848a-911ca73f9b51` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 【已不再受理新申請案】內政部主辦4,000億元優惠購屋專案貸款
- id `06eeeeed-7879-4378-82ce-e4623812ec27` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 174 字，難以判斷

### 耐震弱層補強
- id `5eec16d5-9cb6-4d1a-ae2a-5c8f183b3737` ｜ 來源 moi_pip ｜ 類別 tuition_waiver ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 婦女再就業計畫
- id `2c2cf7a2-f13f-4072-af25-87cefd27d8e6` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 9長照自建資訊系統介接長照服務費用支付審核系統驗證作業，自即日起至114年7月25日截止
- id `95230a62-c062-479b-b50e-1b22c18be2ad` ｜ 來源 ltc_1966 ｜ 類別 ltc_general ｜ 機關 資訊處 ｜ 等級 needs_review
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；LLM 與另一方類別一致
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 育嬰留職停薪津貼及薪資補助
- id `71aa8fd1-b5c0-4ea1-9262-b14d6ebb726f` ｜ 來源 gov_tw_services ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 【轉知】綠色冀泉股份有限公司推動「校園都市林生態賦能」及「偏鄉弱勢學生 AI 循環筆電數位平權」雙軸支持計畫資訊
- id `483969c2-8724-4796-b7e8-1009c0ceca15` ｜ 來源 taipei_doe ｜ 類別 education_subsidy ｜ 機關 綠色冀泉股份有限公司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 商業型以房養老貸款
- id `29a562ae-7c50-4f83-8f90-6c35f0c06754` ｜ 來源 mohw_gov ｜ 類別 housing_loan_subsidy ｜ 機關 社會及家庭署 ｜ 等級 needs_review
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 房貸商品查詢
- id `0bf33603-069e-473f-b68b-f357fd8b6dab` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 住宅性能評估
- id `e6468991-4c83-4d53-8812-502d8b9322c2` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 無障礙住宅
- id `97baa19a-c7a7-4750-ac89-979b71eb2b32` ｜ 來源 moi_pip ｜ 類別 housing_support ｜ 機關 內政部國土管理署 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 高雄市輔具及居家無障礙環境改善代償墊付服務
- id `74f9de2f-3fd2-4f4a-8d82-f952783ab099` ｜ 來源 kaohsiung_sw ｜ 類別 assistive_device ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 低收入戶子女就學生活扶助
- id `d9367c5f-1ef7-4d54-8004-7a03f7175a5d` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `text_too_short` original_text：原文只有 139 字，難以判斷

### 低收入戶乘車船補助
- id `37e86c2d-7e6b-48a2-a907-2e5530cae220` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 申請國民年金所得未達一定標準認定資格
- id `0868f3fa-efc4-4f27-8a6c-542bfe607994` ｜ 來源 kaohsiung_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 衛生福利部辦理兒童及少年未來教育與發展帳戶
- id `34687bf9-09db-43a0-9de3-1ac3238f7d76` ｜ 來源 kaohsiung_sw ｜ 類別 education_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 低收入戶子女升學補習費補助
- id `0dd789a4-6507-4227-9bc0-b3df63bbdb30` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 低收入戶就讀高中職以上在學子女之學習設備補助
- id `ef5e8710-8451-4cdb-92d3-d2718253579f` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 弱勢兒童及少年療育訓練費用補助
- id `feeaf339-9bec-4ce1-bbd0-7c26b9342970` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 輔導弱勢家庭青少年就業
- id `448d48e7-41fb-478f-a830-e65f32121ef0` ｜ 來源 kaohsiung_sw ｜ 類別 youth_employment ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 弱勢單親家庭子女教育補助
- id `e05bfc26-bdfb-4eba-a5a8-0ec1c66ff9ad` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 單親家庭服務
- id `d6c61f8b-7b74-4254-8121-c893e656392f` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 單親培力補助
- id `413f2811-f5b2-4824-b29e-caaefe67d56c` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 高中職以上子女學雜費減免認證
- id `65eb8f89-9e50-480b-ac80-c6064112faa5` ｜ 來源 kaohsiung_sw ｜ 類別 tuition_waiver ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 家庭暴力被害人法律訴訟補助
- id `f8780b84-7cdb-4d3f-90b3-ccdf9ef5ff77` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 現金給付之社會保險補助
- id `beaaed4d-1199-4872-a6a1-32e20e3d218d` ｜ 來源 kaohsiung_sw ｜ 類別 disability_other ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 衛生福利部急難救助金申請審核及撥款作業規定
- id `3cfec097-43d1-4731-a307-0e9c17ecd56e` ｜ 來源 mohw_social_assistance ｜ 類別 emergency_relief ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 急難救助作業流程（社會救助法第21條急難救助對象）
- id `5ab313e4-01d9-423d-866a-e9b66065846d` ｜ 來源 mohw_social_assistance ｜ 類別 emergency_relief ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 政府鼓勵脫貧自立3+1
- id `58442c6f-b5e1-4291-8957-e2b4f38db892` ｜ 來源 mohw_social_assistance ｜ 類別 low_income_allowance ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 極端氣候及年節時期加強關懷弱勢民眾計畫
- id `93f79aa3-f28e-40a9-bc90-7e200730857f` ｜ 來源 mohw_social_assistance ｜ 類別 special_circumstances_aid ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 低收入戶產婦生育及營養補助
- id `9a2cda9b-a9b8-47ac-845c-553aecb94f7e` ｜ 來源 ntpc_banqiao_office ｜ 類別 birth_incentive ｜ 機關 新北市板橋區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 好孕專車車資補貼
- id `30582ba4-bbc7-430f-add4-06ee5b7f14a6` ｜ 來源 ntpc_banqiao_office ｜ 類別 birth_incentive ｜ 機關 新北市板橋區公所 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 特殊境遇家庭的相關福利
- id `4d0d9eb7-89d6-4578-ac4c-de1481420ed2` ｜ 來源 ntpc_banqiao_office ｜ 類別 special_circumstances_aid ｜ 機關 新北市板橋區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新北市生育獎勵金
- id `f26b478b-4fe8-4dca-927d-fd99d86f1b10` ｜ 來源 ntpc_sw ｜ 類別 birth_incentive ｜ 機關 新北市政府民政局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新北市弱勢兒童少年生活扶助
- id `953170d8-ce98-4efe-a51e-0e47be12bea9` ｜ 來源 ntpc_sw ｜ 類別 low_income_allowance ｜ 機關 新北市各區公所 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 新北市市民意外事故致死救助
- id `3d38c96c-aecb-4bc8-b4a3-0c24f5c9f134` ｜ 來源 ntpc_sw ｜ 類別 emergency_relief ｜ 機關 新北市各區公所 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 新北市市民醫療補助
- id `da803ae9-f0a0-4e48-a23d-e788f6804fb4` ｜ 來源 ntpc_sw ｜ 類別 medical_subsidy ｜ 機關 新北市各區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新北市低收入戶及中低收入失能老人接受長期照顧機構安置補助
- id `ce32f817-382f-46f8-a08f-18d7605945bb` ｜ 來源 ntpc_sw ｜ 類別 institutional_care_subsidy ｜ 機關 新北市政府社會局老人福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新北市身心障礙者參加全民健康保險及社會保險自付保費補助
- id `80f39ea1-bd92-4e8e-b0f7-1bfec1d9a7f8` ｜ 來源 ntpc_sw ｜ 類別 disability_other ｜ 機關 新北市政府社會局身心障礙福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 未滿二歲兒童公共化及準公共托育補助（協助支付）金額表
- id `fbd85a26-bc76-452a-9adb-a4828654c6e7` ｜ 來源 sfaa_childcare ｜ 類別 childcare_subsidy ｜ 機關 衛生福利部社會及家庭署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺中市經濟弱勢兒童及少年生活扶助
- id `7ed864da-1318-429d-a750-c8f376b209bd` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 臺中市辦理中低收入家庭內未滿18歲兒童及少年健保費補助
- id `32e722aa-1a63-4511-a16f-a84bb947d290` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 行旅人返鄉車資補助(川資)
- id `20fb0e7f-bd07-48a4-b939-e94b37f226ae` ｜ 來源 taichung_sw ｜ 類別 emergency_relief ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 災害救助－安遷救助
- id `3a631ddf-0f1b-4410-96ed-760390212692` ｜ 來源 taichung_sw ｜ 類別 emergency_relief ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 災害救助－住屋淹水救助
- id `b1341534-6aa1-4818-ac0a-1c4392c68023` ｜ 來源 taichung_sw ｜ 類別 emergency_relief ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 災害救助－住屋土石流救助
- id `d6b5bc86-ac28-4f6d-bd46-c69975980bbf` ｜ 來源 taichung_sw ｜ 類別 emergency_relief ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 特殊境遇家庭扶助－緊急生活扶助
- id `d1b93e3f-b885-4279-97fa-826b15e30641` ｜ 來源 taichung_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺中市中低收入老人健保保費自付額補助
- id `976c6e5b-1bae-4489-a954-821857609340` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者參加健保費及社會保險補助
- id `a48d7d5f-b844-41a5-8436-416e3df3e094` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者國民年金保險費補助
- id `d7e0af12-554e-4932-b0cf-2d37b1def4f8` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 災害救助申請簡介
- id `4bc5a157-4eb1-4c48-bae9-63e16cb97b26` ｜ 來源 taipei_daan_office ｜ 類別 emergency_relief ｜ 機關 臺北市大安區公所 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 身心障礙者社會保險自付保險費現金補助
- id `9479ba5b-540a-498d-88ac-8bc883bc2633` ｜ 來源 taipei_daan_office ｜ 類別 disability_other ｜ 機關 臺北市大安區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 國民年金被保險人所得未達一定標準資格申請簡介
- id `ab7024d2-2b1a-4cd9-b4b4-2eca247090b6` ｜ 來源 taipei_daan_office ｜ 類別 insurance_premium_subsidy ｜ 機關 臺北市大安區公所 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 以工代賑臨時工申請須知
- id `231783a2-b819-4bd5-abd5-2d4cea95468c` ｜ 來源 taipei_daan_office ｜ 類別 low_income_allowance ｜ 機關 臺北市大安區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 桃園市急難救助
- id `729ad9f4-9da3-4e5d-84c2-fd5c7b93cf3d` ｜ 來源 taoyuan_sw ｜ 類別 emergency_relief ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 強化社會安全網—急難紓困
- id `8a3f5758-4832-4f42-9758-0b54020e1af7` ｜ 來源 taoyuan_sw ｜ 類別 emergency_relief ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 桃園市少年自立生活經濟扶助計畫
- id `2ba28fb5-3fea-4075-8321-5bec8df01d63` ｜ 來源 taoyuan_sw ｜ 類別 student_aid ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 中低收入老人裝置假牙補助
- id `c0ecffc1-7a8b-4c12-bc8f-e8a2005bd8ef` ｜ 來源 taoyuan_sw ｜ 類別 elderly_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者購買、租賃發電機或供電設備補助
- id `2f9869ee-7cd1-4b7d-8d2f-883670bc7dc4` ｜ 來源 taoyuan_sw ｜ 類別 disability_other ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身障者搭乘救護車費用補助
- id `79f407e8-88a6-40e2-b077-44ee71585083` ｜ 來源 taoyuan_sw ｜ 類別 disability_other ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者搭乘捷運半價補助
- id `233b350b-a75c-4768-8ffe-17b301250838` ｜ 來源 taoyuan_sw ｜ 類別 disability_other ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 老人保護
- id `ce7531ae-68da-492f-a58b-e1890e1a96d0` ｜ 來源 taoyuan_sw ｜ 類別 elderly_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `text_too_short` original_text：原文只有 198 字，難以判斷

### 補助托嬰中心及居家式托育服務提供者收托身心障礙暨疑似發展遲緩幼兒實施計畫
- id `027d467b-2b3c-48a4-b800-ee12eeaec907` ｜ 來源 tainan_sw ｜ 類別 childcare_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶學生就學費用減免
- id `72b1445a-9c95-4951-9681-224b13fec0c8` ｜ 來源 tainan_sw ｜ 類別 education_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `text_too_short` original_text：原文只有 193 字，難以判斷

### 低收入戶以工代賑
- id `0ed22337-5db6-46dc-9015-850daf2b9bb5` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺南市弱勢兒童及少年醫療費用補助
- id `a0a3a46c-8a4a-4f68-9072-0b4d759b178e` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入老人健保費自付額補助
- id `b89a3b5e-dce7-4e42-8509-db57028288ea` ｜ 來源 tainan_sw ｜ 類別 elderly_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 敬老優惠措施
- id `d15b6c70-f642-4c77-a44c-0dfeb45ef4aa` ｜ 來源 tainan_sw ｜ 類別 elderly_service ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 身心障礙者日間／住宿式照顧服務費用補助
- id `d1c3288c-b9c3-456a-a4a8-7f9b293d9d08` ｜ 來源 tainan_sw ｜ 類別 disability_care_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 六十五歲以上身心障礙者全民健康保險自付保險費補助
- id `8ea67ee9-e9f8-4eb3-b5ed-586d3ebf6635` ｜ 來源 tainan_sw ｜ 類別 disability_other ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童及少年療育訓練費用補助
- id `2dea4edf-094f-45d9-97e0-4e27dad3645b` ｜ 來源 tainan_sw ｜ 類別 childcare_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 基隆市特殊境遇家庭扶助
- id `1deb873f-4be4-4721-9961-7d8a81b699f7` ｜ 來源 keelung_sw ｜ 類別 special_circumstances_aid ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 基隆市市民亡故慰問金
- id `12bc2a6d-426c-4365-b310-199d47dc50fa` ｜ 來源 keelung_sw ｜ 類別 emergency_aid_student ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 基隆市「將士胸懷-翻轉未來」脫貧計畫
- id `257e06bc-de9a-4751-8ba6-b9b076bf002e` ｜ 來源 keelung_sw ｜ 類別 low_income_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者社會保險自付保險費補助
- id `cd29d69f-3212-4c8c-b105-ebd977b41f31` ｜ 來源 keelung_sw ｜ 類別 disability_other ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者居家維生器材用電優惠
- id `68b2cbe1-926a-4f24-99bc-5d36b386f16b` ｜ 來源 keelung_sw ｜ 類別 disability_other ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者三節慰問金
- id `5946606f-b74b-4c56-90d6-cc7b1f009893` ｜ 來源 keelung_sw ｜ 類別 disability_other ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 基隆市老人福利服務簡介
- id `cf1e0abe-199f-4546-b09b-3680a6e56753` ｜ 來源 keelung_sw ｜ 類別 elderly_service ｜ 機關 基隆市政府社會處長青及救助科 ｜ 等級 needs_review
- `text_too_short` original_text：原文只有 194 字，難以判斷

### 基隆市弱勢族群促進就業方案
- id `6115b439-31db-4263-8aea-70035d3e9a94` ｜ 來源 keelung_sw ｜ 類別 youth_employment ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 107年全國低收入戶及中低收入戶生活狀況調查報告
- id `a2e159d2-97d6-4e66-b16f-4315beb8f944` ｜ 來源 keelung_sw ｜ 類別 low_income_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `gate_uncertain` classification：有訊號說是補助但 LLM 說不是：依「不漏抓」原則保留為疑似補助，待人工確認；關鍵字與 embedding 類別一致
- `text_too_short` original_text：原文只有 152 字，難以判斷

### 申請使用牌照稅身心障礙者免稅（請逕洽基隆市稅務局）
- id `a63fb900-3f03-4306-a193-8eeedb572003` ｜ 來源 keelung_sw ｜ 類別 disability_living_allowance ｜ 機關 基隆市稅務局使用牌照稅科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 第5屆公益彩券經銷商
- id `426d7b49-8c79-45b8-9260-bb5a250f83da` ｜ 來源 keelung_sw ｜ 類別 disability_other ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者嚴重情緒行為正向支持整合模式試辦計畫
- id `2284e6e1-35ac-4b8c-97e2-5e993455123c` ｜ 來源 keelung_sw ｜ 類別 disability_care_subsidy ｜ 機關 社團法人中華民國愛加倍社會福利關懷協會 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者日間照顧及住宿式照顧服務(本市簽約機構)
- id `b4a50823-20eb-4a7a-8796-62df9be07035` ｜ 來源 keelung_sw ｜ 類別 disability_care_subsidy ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `text_too_short` original_text：原文只有 135 字，難以判斷

### 115年0-6歲國家跟你一起養 資訊
- id `7e29b32f-f92b-4321-b6e6-a137f287e578` ｜ 來源 keelung_sw ｜ 類別 child_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 182 字，難以判斷

### 衛生福利部公告直轄市、縣（市）政府辦理未滿二歲兒童托育準公共化服務與費用申報及支付作業要點(114年7月16日起)
- id `48980f9d-3751-4e1e-a033-1ba5b6929ca0` ｜ 來源 keelung_sw ｜ 類別 childcare_subsidy ｜ 機關 基隆市政府兒童及少年事務處福利服務科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 托育人員、托嬰中心參與準公共化托育服務簽約相關規定
- id `8e2e192b-3342-4f09-bda9-89cad20e0373` ｜ 來源 keelung_sw ｜ 類別 childcare_subsidy ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 重陽節敬老禮金
- id `333463f3-9ced-45ed-9710-4c3ada95ad93` ｜ 來源 hsinchu_city_sw ｜ 類別 elderly_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者健康保險及社會保險自付額保費補助
- id `97c7cb01-039d-4e7c-a2d0-f0d48bbb71cf` ｜ 來源 hsinchu_city_sw ｜ 類別 disability_other ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入傷病醫療補助
- id `1e711869-23b3-4f06-83ad-c4c9684b22a7` ｜ 來源 hsinchu_city_sw ｜ 類別 low_income_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶全民健康保險補助
- id `1789926d-ebdc-45f5-9156-bbe4ece6005f` ｜ 來源 hsinchu_city_sw ｜ 類別 low_income_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 189 字，難以判斷

### 兒童早期療育費用補助
- id `64f87a9d-b0df-4189-ae12-30d01de13972` ｜ 來源 hsinchu_county_sw ｜ 類別 childcare_subsidy ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 新竹縣以工代賑實施計畫
- id `812a8352-5683-41d1-8bc2-a60a090cd249` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 川資（車資返鄉）救助
- id `acf38407-1842-4a05-85dd-92df43635847` ｜ 來源 hsinchu_county_sw ｜ 類別 emergency_relief ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新竹縣社勞政聯合促進低收入戶及中低收入戶 就業服務指引
- id `31618e40-5f64-41bf-b804-16274958979a` ｜ 來源 hsinchu_county_sw ｜ 類別 youth_employment ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 『役』起前進，『竹』夢踏實 新竹縣政府辦理低收入戶及中低收入戶自立脫貧計畫
- id `24c48b1d-dff6-46a0-b08f-d57a382c6e1a` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 急難紓困(原馬上關懷)、急難救助
- id `5b72299a-9598-4233-b190-606b1a1e553c` ｜ 來源 miaoli_sw ｜ 類別 emergency_relief ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 苗栗縣弱勢家庭兒童及少年緊急生活扶助補助
- id `0c1af7d6-568e-4d4b-8807-187e054caff5` ｜ 來源 miaoli_sw ｜ 類別 emergency_relief ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 苗栗縣辦理兒少生活扶助實施計畫
- id `ddbab147-0d3f-402c-904b-f163a02bc802` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 苗栗縣辦理低收入戶暨弱勢兒童及少年醫療補助審查及作業規定
- id `d855bd29-15d7-4220-88e7-6426265d875d` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 苗栗縣實(食)物銀行計畫
- id `491a020a-f47b-4c48-a6ea-3f7d1722649d` ｜ 來源 miaoli_sw ｜ 類別 emergency_relief ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 苗栗縣國民年金被保險人所得未達一定標準申請
- id `bf99499c-443d-4aa8-9c65-3760afb43de9` ｜ 來源 miaoli_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 115年苗栗縣兒童早期療育費用補助實施計畫
- id `82734490-490b-4af1-9c10-67d99e2b496e` ｜ 來源 miaoli_sw ｜ 類別 social_welfare ｜ 機關 苗栗縣政府(以下簡稱本府)。 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 設籍前新住民遭逢特殊境遇家庭扶助
- id `2b64948e-0ba8-4a13-bc80-67edc6bb5d0f` ｜ 來源 changhua_sw ｜ 類別 special_circumstances_aid ｜ 機關 社會處婦女及新住民福利科 吳辦事員 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者房屋租金補貼
- id `dead647e-c8f2-493b-bb88-3e8044dd428a` ｜ 來源 changhua_sw ｜ 類別 rental_subsidy ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶老人公費安養護補助
- id `5ecd15cc-8230-4e7e-baeb-940e63d83bec` ｜ 來源 changhua_sw ｜ 類別 institutional_care_subsidy ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶及中低收入老人裝置假牙補助
- id `4e50b62f-fc8d-46b6-af48-0b9f4a5991ff` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 65歲以上老人裝置全口活動假牙補助
- id `5896b4e9-477c-4f67-bab7-e33c08dd8dc4` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 油症患者喪葬補助
- id `4371052a-6f35-4c42-bdaa-4c6d70c2dfe5` ｜ 來源 changhua_sw ｜ 類別 special_circumstances_aid ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 國保生育給付加給補助至10萬元
- id `71f7e1d2-3ad2-4748-b00c-5e4926cdc1ab` ｜ 來源 changhua_sw ｜ 類別 birth_incentive ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 中低收入老人健保費補助
- id `b130ae23-d4c0-4713-a2f3-e03beb8c8992` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者監護及輔助宣告補助
- id `c5a359f2-fc7a-42fb-9b0d-c2ac14e37c19` ｜ 來源 changhua_sw ｜ 類別 disability_other ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣中低收入老人生活津貼審核作業辦法
- id `4083c39f-906f-491f-9a2e-ef2645994ffd` ｜ 來源 nantou_sw ｜ 類別 elderly_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣兒童及少年生活扶助審核作業規定
- id `50f2f1e9-a93b-4beb-a230-413ecb584c21` ｜ 來源 nantou_sw ｜ 類別 low_income_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣弱勢兒童及少年醫療補助作業規定
- id `9f49d68c-0a2d-4318-8f8d-0d02d8eca73b` ｜ 來源 nantou_sw ｜ 類別 medical_subsidy ｜ 機關 南投縣政府社會及勞動局(以下稱本局) ｜ 等級 verified
- `gate_uncertain` classification：三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別一致

### 南投縣政府社會及勞動局辦理發展遲緩兒童早期療育費用補助計畫
- id `da288cde-acc2-4e98-9b61-3a75f2e39517` ｜ 來源 nantou_sw ｜ 類別 medical_subsidy ｜ 機關 南投縣政府社會及勞動局（以下簡稱本局） 。 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 南投縣政府辦理身心障礙者參加社會保險保險費補助作業規定
- id `9ce26d22-a4c7-435c-88d8-80e5c82ed74a` ｜ 來源 nantou_sw ｜ 類別 disability_other ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣政府急難救助申請作業應備文件及程序
- id `46c64be1-ce17-4d2a-a5e5-54bfa264b408` ｜ 來源 nantou_sw ｜ 類別 emergency_relief ｜ 機關 社會及勞動局（ 社會救助科） ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 嘉義市急難救助
- id `3beec795-e520-4605-b0be-e43032ee8c65` ｜ 來源 chiayi_city_sw ｜ 類別 emergency_relief ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 115年度「中低收入老人」補助裝置假牙計畫
- id `5a6ca649-17d7-486d-b5aa-da51bab0c628` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 115年度「一般身分別老人」補助裝置假牙計畫
- id `00f1967e-0a43-43c8-ba73-6ea1b1a923e0` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入老人免費配戴老花眼鏡補助
- id `a31064e8-7cfe-481b-b322-88dce6ac32ce` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶老人助聽器補助
- id `73d2c4a3-3b8e-4d68-8b4e-47afd1913d6c` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 短缺川資補助
- id `e8853680-a8e9-4a5c-99e3-e1061a38cabb` ｜ 來源 chiayi_city_sw ｜ 類別 emergency_relief ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 187 字，難以判斷

### 以工代賑實施計畫
- id `1960cd9f-a457-4a7b-b420-da9dabb9409b` ｜ 來源 chiayi_city_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童少年生活扶助
- id `7854fc8e-87e1-41fe-8cd5-dcf141926ee5` ｜ 來源 chiayi_city_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 嘉義市到宅坐月子服務
- id `43755afb-1691-4840-bd55-352ec8e22390` ｜ 來源 chiayi_city_sw ｜ 類別 home_care ｜ 機關 嘉義市政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 嘉義市育兒指導服務方案
- id `3b410edb-7b73-484c-ac90-bd167f668deb` ｜ 來源 chiayi_city_sw ｜ 類別 childcare_subsidy ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者輔助器具補助
- id `8b5e4dee-ed6e-4f0b-83d1-660fbd635921` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 勞保生育給付（含勞工生育補助）— 請領資格
- id `69c51a10-1276-4db2-90a7-0f6b1ac9cedb` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 勞保生育給付（含勞工生育補助）— 給付標準
- id `9c534850-3c2b-4a27-adc2-55bfba56cf38` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 196 字，難以判斷

### 就保育嬰留職停薪津貼 — 請領資格
- id `ea7cf67d-0bb0-4dec-8400-c3b74b271fc5` ｜ 來源 bli_family ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 育嬰留職停薪薪資補助（政府加發20%）— 補助方式
- id `28c504f7-074e-4821-9c78-b953ce86ee1f` ｜ 來源 bli_family ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 160 字，難以判斷

### 桃園市中壢區公所急難救助申請應備文件表
- id `5227e09b-f5cd-46c8-95f6-bf52d5c33f9b` ｜ 來源 taoyuan_zhongli_office ｜ 類別 emergency_relief ｜ 機關 桃園市中壢區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 災害救助
- id `cb248968-7803-4290-9bdf-04c79279b36b` ｜ 來源 tainan_east_office ｜ 類別 emergency_relief ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺南市育有未滿二歲兒童育兒津貼
- id `435f24bb-6230-43c6-ab4f-2ef5709ccfc0` ｜ 來源 tainan_east_office ｜ 類別 child_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺南市二歲以上未滿五歲幼兒育兒津貼
- id `0de9fdc4-437c-47f4-a016-7ea1f8c690e2` ｜ 來源 tainan_east_office ｜ 類別 child_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺南市5歲至入國民小學前幼兒就學補助
- id `8900222d-b539-4e76-a86f-78c8b4414b70` ｜ 來源 tainan_east_office ｜ 類別 education_subsidy ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 低收入戶家庭生活補助
- id `7b993d29-4856-4e49-9caf-71c4e40ef986` ｜ 來源 tainan_east_office ｜ 類別 low_income_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶收容
- id `64b6624c-1b84-4a2c-bf7f-38b52d971d73` ｜ 來源 tainan_east_office ｜ 類別 institutional_care_subsidy ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者托育養護補助
- id `0e46e07f-466e-47a3-93d5-df71a4e404db` ｜ 來源 tainan_east_office ｜ 類別 disability_care_subsidy ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 平民安葬救助金申請
- id `0d1a8294-d6c7-4801-b2ee-c034a7728c6c` ｜ 來源 tainan_east_office ｜ 類別 emergency_relief ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 原住民急難救助
- id `44b7fb89-e811-4861-bdd5-b4196f18f03d` ｜ 來源 tainan_east_office ｜ 類別 emergency_relief ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 原住民學生獎助學金
- id `26e47940-b251-495d-962b-bc7b6a4e8e92` ｜ 來源 tainan_east_office ｜ 類別 scholarship ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 各項業務查詢（第 3 頁）
- id `49a7efe7-213e-4376-94dc-13caae034daa` ｜ 來源 tainan_east_office ｜ 類別 emergency_aid_student ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 嘉義縣弱勢家庭坐月子到嘉（家）服務
- id `9fcb088f-f380-43f5-85eb-7a2cfb41097a` ｜ 來源 chiayi_county_sw ｜ 類別 birth_incentive ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 中低收入戶救助
- id `6763ae9d-0925-45c0-88bf-745cc07a6c87` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `text_too_short` original_text：原文只有 193 字，難以判斷

### 強化社會安全網-急難紓困方案
- id `3aa667c5-8f2e-4927-bf45-4f8234d944ee` ｜ 來源 chiayi_county_sw ｜ 類別 emergency_relief ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 社會救助醫療補助
- id `dea1fd29-c9d7-44bf-9b6f-edace9d0e971` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 嘉義縣弱勢家戶微型保險實施計畫
- id `96098af3-6245-4511-ab4e-e2c80ed13bf9` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 特殊境遇家庭緊急生活扶助
- id `ae2f0912-329a-412f-ab6d-dc906869cba3` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 特殊境遇家庭子女生活津貼
- id `9e4042ec-d566-423f-b05b-d106fd324506` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入老人全民健康保險費補助
- id `55b07c04-2b6b-46d6-808a-b51b2e58727a` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 嘉義縣敬老卡申辦及補助優待
- id `700e04bd-cb71-4e76-b883-b1f4ac5e47b1` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_service ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 營養餐飲服務
- id `7d591ca2-9157-4eba-8a40-1aa0d20c7efc` ｜ 來源 chiayi_county_sw ｜ 類別 meal_service ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `text_too_short` original_text：原文只有 187 字，難以判斷

### 身心障礙者參加社會保險自付保費補助
- id `3e9dbf40-dba4-4471-94de-e74be4fc84ff` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 本局身心障礙福利科05-3620900#1110。 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 補助就讀本縣私立幼托園所（機構）3-5歲身心障礙幼兒家長教育經費
- id `3ab6f841-3835-4670-b000-759695ba6803` ｜ 來源 chiayi_county_sw ｜ 類別 education_subsidy ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 失能身心障礙者補助使用居家照顧服務
- id `f1a55b44-acb6-470a-8c82-91f55c81eda1` ｜ 來源 chiayi_county_sw ｜ 類別 home_care ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 申請身心障礙者汽車牌照免稅
- id `b5abaacd-3945-41dd-af22-8981d6e20a4a` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 花蓮縣未滿2歲兒童托育補助（公共及準公共化特約托育補助）
- id `82cf76de-1ade-4599-8e11-d27c906c5b47` ｜ 來源 hualien_sw ｜ 類別 childcare_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 花蓮縣兒童及少年生活扶助
- id `44d558aa-c69d-4d6f-821a-e8c755062e5e` ｜ 來源 hualien_sw ｜ 類別 low_income_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 強化社會安全網－急難紓困實施方案
- id `e4d72a31-b64f-449d-86d4-9a85ea37c1d5` ｜ 來源 hualien_sw ｜ 類別 emergency_relief ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 國民年金所得未達一定標準保費補助
- id `748b4521-8719-4886-955d-e0cc82061738` ｜ 來源 hualien_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 短缺川資民眾返鄉乘車換票
- id `37de2121-f2c6-4557-9896-be252ecb56c5` ｜ 來源 hualien_sw ｜ 類別 emergency_relief ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣婦女生產補助
- id `1df2c525-9de9-4ca9-ac81-bc3d47e34ef4` ｜ 來源 kinmen_sw ｜ 類別 birth_incentive ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府生育贈禮
- id `f0b263a6-9129-48d1-9227-80244d9e9832` ｜ 來源 kinmen_sw ｜ 類別 birth_incentive ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 特殊境遇家庭扶助
- id `dec19bbb-37b6-421b-ba3f-0b56f52a3517` ｜ 來源 kinmen_sw ｜ 類別 special_circumstances_aid ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府友善托育補助
- id `e379dccc-7f39-41a1-b0c2-ed0cb588a3ef` ｜ 來源 kinmen_sw ｜ 類別 childcare_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童及少年生活扶助
- id `64018949-05b2-4762-88bd-b078fb20f5bc` ｜ 來源 kinmen_sw ｜ 類別 child_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入戶18歲以下兒童及少年健保費補助
- id `b0df7733-60b5-4ef3-b5e6-e07d639fe27e` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 143 字，難以判斷

### 低收入戶及中低收入戶參加健康保險費用補助
- id `016d2cba-8779-4d83-9f14-35b61756d556` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 161 字，難以判斷

### 金門縣低收入戶三節慰問金
- id `2bee620e-5b83-40fe-9fb1-36f31cecab2d` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `text_too_short` original_text：原文只有 140 字，難以判斷

### 金門縣政府補助低收入戶就學子女家戶購置電腦
- id `ae6400d1-c798-49c6-833f-fff76e43c8ec` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 急難紓困
- id `f1827110-0dbe-4f87-b399-bc7347b5dd30` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 金門縣緊急傷病及失能之縣民照顧服務補助
- id `0afaeabc-630e-4a00-b624-10d1bc155cdc` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣65歲以上老人全民健康保險補助
- id `ffaa39ce-31cf-4cd3-86ef-011ed899fc16` ｜ 來源 kinmen_sw ｜ 類別 elderly_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府補助中低收入獨居老人裝設有線電視費用
- id `bef1ebaa-300e-44b8-878c-e7404430a2a6` ｜ 來源 kinmen_sw ｜ 類別 elderly_service ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣身心障礙者日間及住宿式照顧費用部分負擔補助
- id `fafe6245-324e-480b-89e4-8b7bdba37b44` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者醫療及生活輔助器具費用補助
- id `daa7be8d-d13f-439a-8a40-68619ea19b0c` ｜ 來源 kinmen_sw ｜ 類別 assistive_device ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者參加社會保險費用補助
- id `9b60bbc3-050c-4fcd-aef0-4d121e2eaa02` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣紙尿褲看護墊補助
- id `639e0b6d-47f3-4833-b91c-b25c7f810e97` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣補助安置台灣教療養機構身心障礙者家屬探視交通費補助
- id `251f1ee0-f42b-45b5-baba-abd26aaf8dab` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣重度以上中低收入身心障礙者及身心障礙團體裝設有線電視補助
- id `906971bd-2ea6-48e7-92ce-93ca878734d0` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣民愛心卡
- id `38ece0a8-a9fe-4f7d-8d13-a7ba07512f29` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府辦理縣民經收出養機構媒合收養交通費補助
- id `dc411b50-e5bc-451d-ab7a-606af809ae57` ｜ 來源 kinmen_sw ｜ 類別 transport_service ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒少安置後續追蹤輔導與自立生活服務
- id `8cafd1a0-8e92-4c53-ac7b-06025df43614` ｜ 來源 kinmen_sw ｜ 類別 childcare_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣政府辦理團體微型首次罹患癌症健康保險
- id `11d9270d-b95b-4cfa-bfaf-3123f480d743` ｜ 來源 kinmen_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣身心障礙者自立生活支持服務
- id `cbcc8212-304e-4d81-bbd9-b3dfa2977ed7` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣視覺功能障礙者生活重建及生活訓練服務
- id `f4dac68e-fa9c-450d-a2ec-06fac16b0d70` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣多元身心障礙者社區居住與生活服務
- id `947409f2-746f-4f88-a771-8ac3a9890da9` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 社區居住名稱 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣精神障礙者協作模式服務
- id `d7bce029-e390-44f8-ac4f-0885b6687dd0` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 金門縣身心障礙者婚姻及生育輔導服務
- id `d34c6239-9f3d-452b-8477-1baf5366081f` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣政府辦理南山人壽團體微型傷害保險
- id `80024216-74ae-4783-b3d0-71d428fd8c9d` ｜ 來源 kinmen_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 弱勢兒童及少年醫療補助
- id `3739d1a5-b407-4bcf-a27f-4462de414492` ｜ 來源 yilan_sw ｜ 類別 medical_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童及少年未來教育與發展帳戶
- id `167af75c-c91e-4e49-b663-f2aec3b65b2d` ｜ 來源 yilan_sw ｜ 類別 education_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 發展遲緩兒童早期療育（含療育費及交通費補助）
- id `e074f8e8-243a-4fe2-8cee-196583f90de8` ｜ 來源 yilan_sw ｜ 類別 medical_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 宜蘭縣中低收入戶老人及低收入戶住宅設施設備修繕補助
- id `bfbc283d-3ade-4e11-abff-3a793812899f` ｜ 來源 yilan_sw ｜ 類別 low_income_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 川資(車資返鄉補助)
- id `5dadcc36-4548-4265-ba97-684a9e31c306` ｜ 來源 yilan_sw ｜ 類別 emergency_relief ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 物資銀行
- id `8d233365-49c5-4f56-880a-4e9509323e45` ｜ 來源 yilan_sw ｜ 類別 emergency_relief ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 弱勢民眾微型保險
- id `0f526d95-6e21-43b1-aebd-f4dcb1accac0` ｜ 來源 yilan_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 國民年金保險費補助（所得未達一定標準資格認定）
- id `b6c7ce14-d64e-4656-bf25-6631b26db93a` ｜ 來源 yilan_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入老人特別照顧津貼
- id `dad20af0-820c-482a-ac71-ffb693652812` ｜ 來源 yilan_sw ｜ 類別 elderly_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入戶老人假牙裝置補助
- id `02d0b57f-54cb-427b-8f15-e7fdfc59d012` ｜ 來源 yilan_sw ｜ 類別 elderly_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者（55至64歲）假牙裝置補助
- id `9c5dcdf0-22cc-4414-9d9d-2948a91fed55` ｜ 來源 yilan_sw ｜ 類別 disability_other ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者參加社會保險保險費補助
- id `65171db3-b004-4933-bf80-895990ad7fae` ｜ 來源 yilan_sw ｜ 類別 disability_other ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 高照顧負荷家庭創新服務方案
- id `ec06369c-4fe3-4d61-b95d-60cb3dbf3420` ｜ 來源 yilan_sw ｜ 類別 disability_care_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣辦理115年度弱勢兒童課後照顧服務實施計畫
- id `756c57b5-e1eb-44ea-9b7d-e23740667646` ｜ 來源 penghu_sw ｜ 類別 childcare_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 澎湖縣六歲以下幼童健保費自負額補助
- id `8c178de4-6a92-4b26-88af-83d1e3652943` ｜ 來源 penghu_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 澎湖縣六歲以下幼童參加全民健康保險保險費自負額補助實施要點
- id `78476371-ea0b-43f4-8ad9-03e5ab562d0a` ｜ 來源 penghu_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 澎湖縣政府低收入戶中低收入戶調查及生活扶助作業要點
- id `b8b1bf48-2e11-4e3a-8e9e-5a3d6a3d4fbd` ｜ 來源 penghu_sw ｜ 類別 low_income_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣民眾遭遇急難事件救助要點
- id `f9406a2d-5ba3-4dd3-8f13-1b43dd17df13` ｜ 來源 penghu_sw ｜ 類別 emergency_relief ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣災害救助金核發
- id `78192577-3510-4e0d-8011-02d1cc946a74` ｜ 來源 penghu_sw ｜ 類別 emergency_relief ｜ 機關 社會處 > 社會福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 澎湖縣政府低收入戶及中低收入戶簡易修繕住宅補助要點
- id `75f49793-f266-4728-a9a3-a38f2758be7a` ｜ 來源 penghu_sw ｜ 類別 housing_support ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 澎湖縣弱勢兒童及少年醫療補助作業規定
- id `20fd9479-1b90-4d86-a8b5-d1e5c65b51a6` ｜ 來源 penghu_sw ｜ 類別 medical_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 澎湖縣湖西鄉居民健保費定額補助
- id `3aa0a48f-489c-4071-8a0d-4fe694aa677d` ｜ 來源 penghu_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 中低收入老人生活津貼（白沙鄉公所受理）
- id `5b21b929-9f6b-4d61-9314-f2f5e8e84e4a` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣白沙鄉公所 > 社會課 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣中低收入老人特別照顧津貼補助
- id `b639bed4-ca42-4842-bf46-22c90e49d233` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 社會處 > 社會福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入老人假牙補助
- id `18a38127-5b6e-4396-a2fa-982556b2d8eb` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣中低收入老人重病住院看護補助實施要點
- id `c52ee14b-298d-4e55-b75e-90cd1b154052` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣政府辦理中、低收入失能老人機構照顧服務補助計畫
- id `de06e2f4-2453-4576-a1e0-36a85d5437f5` ｜ 來源 penghu_sw ｜ 類別 institutional_care_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者生活補助費
- id `4c692b32-26cf-4b74-9545-b7e5a579df89` ｜ 來源 penghu_sw ｜ 類別 disability_living_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者日間照顧及住宿式照顧費用補助
- id `27bb450b-cd90-4ad1-9046-4ef36fff6a1e` ｜ 來源 penghu_sw ｜ 類別 disability_care_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者社會保險費補助
- id `6d313373-3710-468b-9e44-6daeb53a19e8` ｜ 來源 penghu_sw ｜ 類別 disability_other ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 福利政策
- id `b9f316f3-256c-41a8-9da9-7f7a49808fa8` ｜ 來源 taipei_dosw ｜ 類別 elderly_service ｜ 機關 臺北市政府社會局 ｜ 等級 needs_review
- `category_uncertain` category：有訊號說是補助但 LLM 說不是：依「不漏抓」原則保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- `gate_uncertain` classification：有訊號說是補助但 LLM 說不是：依「不漏抓」原則保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 申請長期照顧服務流程
- id `4b97dc4e-975c-4f10-9e7f-c069b5ee7e19` ｜ 來源 mohw_gov ｜ 類別 ltc_general ｜ 機關 衛生福利部 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 職場學習及再適應計畫
- id `e389a723-58fd-4b7f-bb9a-9cc9aa4f5e3f` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### pdf
- id `0fae92dd-0bb4-4e9d-879c-22d1b2119e4f` ｜ 來源 mohw_gov ｜ 類別 ltc_general ｜ 機關 衛生福利部 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 住宿式機構服務
- id `40887302-4e90-4f56-9684-7ec5503d7273` ｜ 來源 ltc_1966 ｜ 類別 institutional_care_subsidy ｜ 機關 衛生福利部長期照顧司 ｜ 等級 verified
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 8公告本部「115年度日照中心導入科技輔具成效補助計畫」
- id `1a392080-14dd-4ccd-a3fe-e4b57b737891` ｜ 來源 ltc_1966 ｜ 類別 assistive_device ｜ 機關 衛生福利部長期照顧司 ｜ 等級 needs_review
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 10內政部社宅包租代管之長者換居政策
- id `d847f3af-45d2-4d78-a06e-418d3a1e0f20` ｜ 來源 ltc_1966 ｜ 類別 housing_support ｜ 機關 衛生福利部長期照顧司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `text_too_short` original_text：原文只有 167 字，難以判斷

### 14智慧共融照顧新模式 全國日間照顧服務單位齊聚交流
- id `131692d1-60a0-4567-9d36-01fe676a162b` ｜ 來源 ltc_1966 ｜ 類別 day_care ｜ 機關 衛生福利部長期照顧司 ｜ 等級 verified
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致

### 教保員證書補發／換發申請
- id `e79dbc1c-43fb-4ca5-9eab-63752641e5d3` ｜ 來源 keelung_sw ｜ 類別 childcare_subsidy ｜ 機關 基隆市政府社會處身心障礙福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `text_too_short` original_text：原文只有 192 字，難以判斷

