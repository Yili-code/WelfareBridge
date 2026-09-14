# 領域／類別樹與身分本體（實際載入內容）

來源：`backend/app/registry/taxonomy.yaml`（version 2）、`identity_ontology.yaml`

## 類別樹

- **教育**（`education`）：學生就學相關的獎學金、助學金、學雜費減免、住宿與就學補助
  - 獎學金（`scholarship`）— 依成績、身分或特定條件核發的獎學金／獎助學金；需求類型：cash_now、honor；預設給付形式：cash
  - 助學金（`student_aid`）— 弱勢學生助學金、生活助學金、安心就學等以經濟協助為主的補助；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 學雜費減免（`tuition_waiver`）— 學雜費減免、免學費、就學費用補助；需求類型：reduce_burden；預設給付形式：waiver
  - 就學補助（`education_subsidy`）— 就學補助金、教育代金、學習扶助、失業勞工子女就學補助等；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 住宿補助（`housing_support`）— 學生校內住宿補貼、宿舍補助；需求類型：reduce_burden；預設給付形式：cash
  - 學生急難救助（`emergency_aid_student`）— 學生或家庭遭遇變故的急難救助金；需求類型：cash_now；預設給付形式：cash
  - 就學貸款（`student_loan`）— 高級中等以上學校學生就學貸款、利息補貼；需求類型：reduce_burden；預設給付形式：loan
  - 留學獎助（`study_abroad`）— 留學獎學金、留學貸款、出國研習獎助；需求類型：cash_now、honor；預設給付形式：cash
- **青年**（`youth`）：青年就業、創業、壯遊與發展相關補助
  - 青年就業獎勵（`youth_employment`）— 青年就業獎勵津貼、初次尋職、跨域就業補助；需求類型：cash_now；預設給付形式：cash
  - 青年創業（`youth_entrepreneurship`）— 青年創業貸款、創業補助、育成；需求類型：reduce_burden；預設給付形式：loan
  - 青年發展（`youth_development`）— 壯遊、志工、國際參與等青年發展獎助；需求類型：honor；預設給付形式：cash
- **社會福利**（`social_welfare`）：低收入戶、中低收入戶、特殊境遇家庭、兒少、家庭與急難救助等社會救助與福利
  - 低收入戶生活補助（`low_income_allowance`）— 低收入戶／中低收入戶家庭生活扶助、就學生活補助；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 特殊境遇家庭扶助（`special_circumstances_aid`）— 特殊境遇家庭緊急生活扶助、子女生活津貼、傷病醫療補助；需求類型：cash_now；預設給付形式：cash
  - 生育獎勵金（`birth_incentive`）— 生育獎勵金、生育津貼、生育補助、生育給付（縣市政府或鄉鎮市區公所發給新生兒家庭的一次性給付）、產婦與新生兒營養補助、坐月子服務、好孕專車車資補貼；需求類型：cash_now；預設給付形式：cash
  - 保險費補助（`insurance_premium_subsidy`）— 全民健康保險保費補助、國民年金保險費補助（低收入戶、中低收入戶、老人、身心障礙者、所得未達一定標準者）；需求類型：reduce_burden；預設給付形式：cash
  - 育兒津貼（`child_allowance`）— 0 至未滿 5 歲育兒津貼、5 歲至入小學前就學補助；需求類型：reduce_burden；預設給付形式：cash
  - 托育補助（`childcare_subsidy`）— 托育補助、公共托育、準公共托育；需求類型：reduce_burden；預設給付形式：cash
  - 育嬰留停津貼（`parental_leave_allowance`）— 育嬰留職停薪津貼及薪資補助；需求類型：reduce_burden；預設給付形式：cash
  - 急難救助（`emergency_relief`）— 家庭遭遇急難變故的救助金、緊急紓困；需求類型：cash_now；預設給付形式：cash
  - 老人生活津貼（`elderly_allowance`）— 中低收入老人生活津貼、特別照顧津貼、老人收容安置補助；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 老人福利服務（`elderly_service`）— 老人營養餐飲、日間照顧、家庭托顧、機構安置等服務類福利；需求類型：service；預設給付形式：service
- **長期照顧**（`long_term_care`）：長照 2.0 給付與支付：居家服務、日間照顧、家庭托顧、交通接送、輔具、喘息、機構補助
  - 居家服務（`home_care`）— 居家照顧服務、身體照顧與日常生活協助（照顧及專業服務給付）；需求類型：service；預設給付形式：service
  - 日間照顧（`day_care`）— 長照日間照顧中心服務；需求類型：service；預設給付形式：service
  - 家庭托顧（`family_care_home`）— 家庭托顧服務；需求類型：service；預設給付形式：service
  - 交通接送（`transport_service`）— 長期照顧交通接送服務給付；需求類型：service；預設給付形式：service
  - 輔具與無障礙（`assistive_device`）— 長照輔具服務、居家無障礙環境改善補助；需求類型：service、reduce_burden；預設給付形式：in_kind
  - 喘息服務（`respite_care`）— 喘息服務給付、照顧者支持；需求類型：service；預設給付形式：service
  - 營養餐飲（`meal_service`）— 失能者營養餐飲服務（送餐）；需求類型：service；預設給付形式：service
  - 機構住宿補助（`institutional_care_subsidy`）— 住宿式機構使用者補助、老人機構收容安置補助；需求類型：reduce_burden；預設給付形式：cash
  - 長照服務總覽（`ltc_general`）— 長照服務申請方式、給付及支付基準、服務項目總覽；需求類型：service；預設給付形式：service
- **身心障礙**（`disability`）：身心障礙者生活補助、輔具、照顧、就學與就業相關補助
  - 身心障礙者生活補助（`disability_living_allowance`）— 身心障礙者生活補助費；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 身心障礙輔具補助（`disability_assistive_device`）— 身心障礙者輔具費用補助；需求類型：reduce_burden、service；預設給付形式：cash
  - 身心障礙照顧補助（`disability_care_subsidy`）— 身心障礙者日間照顧、住宿式照顧費用補助、居家照顧、發展遲緩兒童早期療育費用補助、照顧者津貼；需求類型：service、reduce_burden；預設給付形式：cash
  - 身心障礙其他福利（`disability_other`）— 交通、稅賦、保險費補助等其他身心障礙福利；需求類型：reduce_burden；預設給付形式：cash
- **勞工就業**（`labor`）：失業給付、職業訓練生活津貼、就業促進津貼、僱用獎助等勞動部補助
  - 失業給付（`unemployment_benefit`）— 就業保險失業給付、提早就業獎助津貼；需求類型：cash_now；預設給付形式：cash
  - 職業訓練生活津貼（`training_allowance`）— 職業訓練期間生活津貼、職訓補助；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 就業促進津貼（`employment_incentive`）— 求職交通補助、跨域就業津貼、臨工津貼、缺工就業獎勵、僱用安定措施；需求類型：cash_now；預設給付形式：cash
  - 雇主補助（`employer_subsidy`）— 僱用獎助、減班休息補貼、雇主聘僱補助（申請者為雇主）；需求類型：reduce_burden；預設給付形式：cash
  - 勞工福利（`worker_welfare`）— 勞工子女就學補助、職工福利、勞工紓困；需求類型：cash_now、reduce_burden；預設給付形式：cash
- **住宅**（`housing`）：租金補貼、購置與修繕住宅貸款利息補貼、社會住宅
  - 租金補貼（`rental_subsidy`）— 中央擴大租金補貼、地方租金補貼；需求類型：reduce_burden；預設給付形式：cash
  - 住宅貸款利息補貼（`housing_loan_subsidy`）— 購置、修繕住宅貸款利息補貼；需求類型：reduce_burden；預設給付形式：cash
  - 社會住宅（`social_housing`）— 社會住宅承租、包租代管；需求類型：service、reduce_burden；預設給付形式：service
- **醫療健康**（`health`）：醫療費用補助、健保費補助、重大傷病、心理健康支持
  - 醫療費用補助（`medical_subsidy`）— 醫療費用補助、住院看護費補助、重大傷病與弱勢兒少醫療補助；需求類型：cash_now、reduce_burden；預設給付形式：cash
  - 健康服務（`health_service`）— 心理諮商、健康檢查、預防保健等服務；需求類型：service；預設給付形式：service

## 身分本體

| id | 標籤 | 同義詞 | 對應屬性 | 隱含（具備即視為具備） | 依據 |
| --- | --- | --- | --- | --- | --- |
| `low_income` | 低收入戶 | 低收、低收入家庭、列冊低收入戶、低收入戶學生 | `identity.low_income` | economic_hardship、disadvantaged | — |
| `middle_low_income` | 中低收入戶 | 中低收、中低收入家庭、中低收入戶學生 | `identity.middle_low_income` | economic_hardship、disadvantaged | — |
| `economic_hardship` | 清寒 | 家境清寒、清寒家庭、清寒學生、家庭經濟困難、經濟困難 | `identity.economic_hardship` | disadvantaged | — |
| `special_circumstances` | 特殊境遇家庭 | 特殊境遇、特境家庭、特境 | `identity.special_circumstances` | disadvantaged | — |
| `disadvantaged` | 弱勢學生 | 弱勢、經濟弱勢、弱勢家庭、弱勢族群 | `` | — | 教育部大專校院弱勢學生助學計畫：低收入戶、中低收入戶、特殊境遇家庭、身心障礙、原住民等 |
| `indigenous` | 原住民 | 原住民族、原民、原住民學生、具原住民身分 | `identity.indigenous` | disadvantaged | — |
| `yami` | 雅美族 | 達悟族、雅美(達悟)族 | `identity.indigenous_tribe` | indigenous | — |
| `hakka` | 客家 | 客家子弟、客家籍、客家人 | `identity.hakka` | — | — |
| `disabled` | 身心障礙 | 身障、身心障礙者、身心障礙學生、領有身心障礙證明、身心障礙手冊、身心障礙證明 | `disability.has_certificate` | disadvantaged | — |
| `disabled_family` | 身心障礙人士子女 | 身心障礙者子女、身障子女、家中有身心障礙者 | `disability.family_member_has_certificate` | — | — |
| `new_immigrant` | 新住民 | 新移民、外籍配偶、新住民子女、新住民及其子女 | `identity.new_immigrant` | — | — |
| `single_parent` | 單親家庭 | 單親、單親家庭子女 | `identity.single_parent` | — | — |
| `grandparent_family` | 隔代教養 | 隔代教養家庭 | `identity.grandparent_family` | — | — |
| `orphan` | 失依兒少 | 孤兒、失依、失親、喪親、父母雙亡 | `identity.orphan` | disadvantaged | — |
| `veteran_family` | 榮民子女 | 榮眷、榮民遺眷、榮民或榮眷子女、榮民 | `identity.veteran_family` | — | — |
| `military_civil_bereaved` | 軍公教遺族 | 軍公教遺眷、遺族 | `identity.military_civil_bereaved` | — | — |
| `unemployed_worker_child` | 失業勞工子女 | 非自願離職勞工子女、失業勞工在學子女 | `identity.unemployed_worker_child` | — | — |
| `overseas_chinese` | 僑生 | 海外僑生、港澳生 | `identity.overseas_chinese` | — | — |
| `foreign_student` | 外籍生 | 國際學生、外國學生、外籍學生 | `identity.foreign_student` | — | — |
| `elderly` | 老人 | 長者、年滿65歲、65歲以上、高齡者、銀髮族 | `applicant.is_elderly` | — | — |
| `catastrophic_illness` | 重大傷病 | 重大傷病卡、領有重大傷病證明 | `health.catastrophic_illness` | — | — |
| `dementia` | 失智症 | 失智、失智者、認知功能障礙 | `care.dementia_diagnosis` | — | — |
