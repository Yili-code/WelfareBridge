# 分類器回測（黃金集 300 筆，留一法）

- 產生於 2026-09-13T15:30:13.008670+00:00；LLM 有參與三方投票；門檻 KW_YES_CONF=0.6 KW_NO_RATIO=0.5 EMB_YES=0.65 EMB_NO=0.35
- 黃金集：yes 215、portal 14、no 71（yes 與 portal 都算閘門正例；標 closed 的已停辦方案也算正例，由 status=expired 處理）

## 1. 閘門（是不是補助）

| 方法 | precision | recall | F1 | 漏抓 (FN) | 誤放行 (FP) |
| --- | ---: | ---: | ---: | ---: | ---: |
| keyword | 0.978 | 0.961 | 0.969 | 9 | 5 |
| embedding | 0.949 | 0.969 | 0.959 | 7 | 12 |
| ensemble | 0.935 | 1.0 | 0.966 | 0 | 16 |

- 三方投票放行中標「待人工確認」：9 筆；LLM 被呼叫：111 筆

## 2. 主類別（黃金集 yes 的方案）

| 方法 | 樣本 | 主類別正確 | 主或次類別命中 | 主類別正確率 | 寬鬆正確率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| keyword | 214 | 155 | 172 | 0.724 | 0.804 |
| embedding | 214 | 178 | 196 | 0.832 | 0.916 |
| ensemble | 214 | 176 | 193 | 0.822 | 0.902 |

- 三方投票主類別錯但黃金集主類別出現在其次類別：29 筆

## 3. 漏抓（黃金集是補助但三方投票沒放行）


## 4. 誤放行（黃金集不收但三方投票放行）

- 智慧共融照顧新模式 全國日間照顧服務單位齊聚交流（notice）：kw=False(0.0) emb=0.553 uncertain=True → 關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致
- 內政部社宅包租代管之長者換居政策（other）：kw=False(0.0) emb=0.5 uncertain=True → 關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- 住宿式機構服務（other）：kw=False(0.0) emb=0.446 uncertain=True → 關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致
- 長照自建資訊系統介接支付審核系統驗證作業（notice）：kw=True(0.583) emb=0.417 uncertain=False → 關鍵字與 embedding 都無明確意見，LLM 判定是補助；LLM 與另一方類別一致
- 112年度失智共同照護中心設置單位一覽表（directory）：kw=False(0.036) emb=0.445 uncertain=True → 關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有關鍵字的類別意見（類別待確認）
- 商業型以房養老貸款（other）：kw=False(0.143) emb=0.869 uncertain=False → 三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- 綠色冀泉雙軸支持計畫需求盤點（notice）：kw=False(0.179) emb=0.763 uncertain=False → 三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- 長照服務的內容 居家服務（衛生局）（attachment）：kw=False(0.0) emb=0.417 uncertain=True → 關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；LLM 與另一方類別一致
- 育有未滿2歲兒童育兒津貼總覽（other）：kw=False(0.107) emb=0.904 uncertain=False → 彙整頁：標題含「總覽」：彙整頁，保留供查閱但不進清單與媒合
- 托育人員、托嬰中心參與準公共化托育服務簽約相關規定（other）：kw=True(0.768) emb=0.961 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 極端氣候及年節時期加強關懷弱勢民眾計畫（other）：kw=True(0.714) emb=0.805 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 特殊境遇家庭扶助專區（directory）：kw=False(0.107) emb=0.729 uncertain=False → 彙整頁：標題含「專區」：彙整頁，保留供查閱但不進清單與媒合
- 育有未滿二歲兒童育兒津貼（faq）：kw=True(0.625) emb=0.964 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 特殊境遇家庭的相關福利（faq）：kw=True(0.732) emb=0.966 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 補助托嬰中心及居家式托育服務提供者收托身心障礙暨疑似發展遲緩幼兒實施計畫（attachment）：kw=False(0.196) emb=0.537 uncertain=False → 關鍵字與 embedding 都無明確意見，LLM 判定是補助；LLM 與另一方類別一致
- 115年0-6歲國家跟你一起養 資訊（other）：kw=False(0.196) emb=0.829 uncertain=False → 三方不一致，LLM 判定是補助；LLM 與另一方類別一致

## 5. 主類別不同（三方投票 vs 黃金集）

- 高級中等學校各類學雜費減免及就學費用補助：gold=tuition_waiver ens=scholarship sec=['tuition_waiver', 'special_circumstances_aid', 'low_income_allowance'] kw=tuition_waiver emb=education_subsidy
- 失業給付申請：gold=unemployment_benefit ens=employment_incentive sec=['unemployment_benefit', 'training_allowance'] kw=employment_incentive emb=employment_incentive
- 衛生福利部社會及家庭署單親培力計畫：gold=education_subsidy ens=student_aid sec=['scholarship', 'childcare_subsidy', 'special_circumstances_aid'] kw=scholarship emb=education_subsidy
- 大鵬科技慈善基金會獎助學金：gold=student_aid ens=scholarship sec=['emergency_relief', 'student_aid'] kw=scholarship emb=scholarship
- 2026癌友家庭子女育秧獎助學金：gold=student_aid ens=scholarship sec=['student_aid'] kw=scholarship emb=scholarship
- 宋作楠先生紀念獎助學金：gold=student_aid ens=scholarship sec=['student_aid'] kw=scholarship emb=scholarship
- 住宿式長照機構與產學合作國際專班攬才留用試辦計畫：gold=employer_subsidy ens=study_abroad sec=['institutional_care_subsidy', 'disability_care_subsidy', 'disability_other'] kw=institutional_care_subsidy emb=ltc_general
- 外國專業人才及眷屬長照新制：gold=ltc_general ens=elderly_service sec=['transport_service', 'ltc_general', 'assistive_device'] kw=transport_service emb=ltc_general
- 急難救助（學產基金急難慰問金）：gold=emergency_aid_student ens=emergency_relief sec=[] kw=emergency_relief emb=emergency_relief
- 無障礙住宅：gold=housing_support ens=assistive_device sec=['employment_incentive', 'housing_support'] kw=assistive_device emb=assistive_device
- 【已不再受理新申請案】中產房貸支持專區：gold=housing_loan_subsidy ens=employment_incentive sec=[] kw=employment_incentive emb=low_income_allowance
- 公益出租人：gold=housing_support ens=rental_subsidy sec=['low_income_allowance', 'housing_support'] kw=low_income_allowance emb=rental_subsidy
- 失業勞工子女就學補助（在學子女生活扶助金）：gold=education_subsidy ens=student_aid sec=['employment_incentive', 'scholarship', 'education_subsidy'] kw=employment_incentive emb=education_subsidy
- 少年就業力準備計畫：gold=youth_employment ens=employment_incentive sec=[] kw=employment_incentive emb=employment_incentive
- 國民年金被保險人所得未達一定標準資格申請簡介：gold=low_income_allowance ens=insurance_premium_subsidy sec=['emergency_relief', 'low_income_allowance', 'disability_living_allowance'] kw=emergency_relief emb=disability_living_allowance
- 南投縣兒童及少年生活扶助審核作業規定：gold=special_circumstances_aid ens=low_income_allowance sec=['emergency_relief', 'child_allowance', 'special_circumstances_aid'] kw=low_income_allowance emb=low_income_allowance
- 申請使用牌照稅身心障礙者免稅（請逕洽基隆市稅務局）：gold=disability_other ens=disability_living_allowance sec=['disability_other'] kw=disability_living_allowance emb=disability_other
- 115年度弱勢兒童及少年生活扶助應備文件及規定：gold=special_circumstances_aid ens=low_income_allowance sec=['emergency_relief', 'special_circumstances_aid', 'child_allowance'] kw=emergency_relief emb=special_circumstances_aid
- 苗栗縣弱勢家庭兒童及少年緊急生活扶助補助：gold=emergency_relief ens=low_income_allowance sec=['emergency_relief', 'special_circumstances_aid'] kw=emergency_relief emb=special_circumstances_aid
- 兒童及少年未來教育與發展帳戶：gold=low_income_allowance ens=student_aid sec=['low_income_allowance', 'emergency_relief', 'elderly_allowance'] kw=low_income_allowance emb=child_allowance
- 失能老人接受長期照顧機構服務：gold=institutional_care_subsidy ens=elderly_service sec=['elderly_allowance', 'disability_care_subsidy', 'institutional_care_subsidy'] kw=elderly_allowance emb=institutional_care_subsidy
- 低收入戶未滿65歲生活無法自理者安置費用補助：gold=institutional_care_subsidy ens=low_income_allowance sec=['institutional_care_subsidy', 'emergency_relief', 'elderly_allowance'] kw=low_income_allowance emb=low_income_allowance
- 身心障礙者居家維生器材用電優惠：gold=disability_other ens=assistive_device sec=['disability_other', 'disability_living_allowance'] kw=assistive_device emb=assistive_device
- 苗栗縣辦理低收入戶與中低收入戶產婦及新生兒營養補助實施計畫(114修)：gold=birth_incentive ens=low_income_allowance sec=['birth_incentive'] kw=low_income_allowance emb=low_income_allowance
- 新竹縣社勞政聯合促進低收入戶及中低收入戶 就業服務指引：gold=employment_incentive ens=youth_employment sec=['low_income_allowance', 'childcare_subsidy', 'employment_incentive'] kw=low_income_allowance emb=employment_incentive
- 苗栗縣國民年金被保險人所得未達一定標準申請：gold=low_income_allowance ens=insurance_premium_subsidy sec=['emergency_relief', 'birth_incentive', 'unemployment_benefit'] kw=emergency_relief emb=low_income_allowance
- 低收入戶全民健康保險補助：gold=medical_subsidy ens=low_income_allowance sec=[] kw=low_income_allowance emb=low_income_allowance
- 兒童與少年未來教育及發展帳戶：gold=low_income_allowance ens=student_aid sec=['low_income_allowance', 'emergency_relief', 'elderly_allowance'] kw=low_income_allowance emb=child_allowance
- 南投縣低收入戶老人公費養護作業規定：gold=institutional_care_subsidy ens=elderly_allowance sec=['institutional_care_subsidy', 'low_income_allowance', 'emergency_relief'] kw=institutional_care_subsidy emb=elderly_allowance
- 高雄市發展遲緩兒童早期療育費用補助：gold=medical_subsidy ens=disability_care_subsidy sec=['disability_other', 'medical_subsidy', 'education_subsidy'] kw=disability_care_subsidy emb=medical_subsidy
- 國民年金保險費補助（所得未達一定標準）：gold=low_income_allowance ens=insurance_premium_subsidy sec=['special_circumstances_aid', 'emergency_relief', 'elderly_allowance'] kw=special_circumstances_aid emb=elderly_allowance
- 好孕專車車資補貼：gold=health_service ens=birth_incentive sec=['low_income_allowance', 'emergency_relief'] kw=low_income_allowance emb=birth_incentive
- 身心障礙者社會保險自付保險費補助：gold=disability_other ens=insurance_premium_subsidy sec=['disability_other'] kw=insurance_premium_subsidy emb=disability_other
- 身心障礙者社會保險自付保險費現金補助：gold=disability_other ens=insurance_premium_subsidy sec=['disability_living_allowance', 'disability_other'] kw=insurance_premium_subsidy emb=disability_other
- 衛生福利部辦理兒童及少年未來教育與發展帳戶：gold=low_income_allowance ens=education_subsidy sec=['low_income_allowance', 'child_allowance'] kw=low_income_allowance emb=child_allowance
- 身心障礙社區日間作業設施服務(小作所)：gold=disability_other ens=disability_care_subsidy sec=['disability_other'] kw=disability_other emb=disability_care_subsidy
- 老人營養送餐服務：gold=meal_service ens=elderly_service sec=['elderly_allowance', 'meal_service'] kw=elderly_allowance emb=meal_service
- 臺南市5歲至入國民小學前幼兒就學補助：gold=education_subsidy ens=child_allowance sec=['education_subsidy'] kw=education_subsidy emb=child_allowance
