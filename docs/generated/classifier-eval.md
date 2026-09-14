# 分類器回測（黃金集 300 筆，留一法）

- 產生於 2026-09-12T17:03:15.824990+00:00；LLM 未參與三方投票；門檻 KW_YES_CONF=0.6 KW_NO_RATIO=0.5 EMB_YES=0.65 EMB_NO=0.35
- 黃金集：yes 215、portal 14、no 71（yes 與 portal 都算閘門正例；標 closed 的已停辦方案也算正例，由 status=expired 處理）

## 1. 閘門（是不是補助）

| 方法 | precision | recall | F1 | 漏抓 (FN) | 誤放行 (FP) |
| --- | ---: | ---: | ---: | ---: | ---: |
| keyword | 0.956 | 0.948 | 0.952 | 12 | 10 |
| embedding | 0.929 | 0.969 | 0.949 | 7 | 17 |
| ensemble | 0.923 | 0.991 | 0.956 | 2 | 19 |

- 三方投票放行中標「待人工確認」：68 筆；LLM 被呼叫：0 筆

## 2. 主類別（黃金集 yes 的方案）

| 方法 | 樣本 | 主類別正確 | 主或次類別命中 | 主類別正確率 | 寬鬆正確率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| keyword | 214 | 151 | 171 | 0.706 | 0.799 |
| embedding | 214 | 178 | 196 | 0.832 | 0.916 |
| ensemble | 214 | 174 | 191 | 0.813 | 0.893 |

- 三方投票主類別錯但黃金集主類別出現在其次類別：29 筆

## 3. 漏抓（黃金集是補助但三方投票沒放行）

- 公告115年度日照中心導入科技輔具成效補助計畫（yes/assistive_device）：kw=False(0.17) emb=0.229 kind=program → 無訊號說是補助（本地 AI 不可用）
- 職場學習及再適應計畫（yes/employment_incentive）：kw=False(0.16) emb=0.123 kind=program → 無訊號說是補助（本地 AI 不可用）

## 4. 誤放行（黃金集不收但三方投票放行）

- 智慧共融照顧新模式 全國日間照顧服務單位齊聚交流（notice）：kw=False(0.0) emb=0.553 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別一致
- 內政部社宅包租代管之長者換居政策（other）：kw=False(0.0) emb=0.5 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；只有關鍵字的類別意見（類別待確認）
- 長照自建資訊系統介接支付審核系統驗證作業（notice）：kw=True(0.493) emb=0.417 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 商業型以房養老貸款（other）：kw=False(0.08) emb=0.869 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 標售得標價（statistics）：kw=False(0.05) emb=0.616 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 綠色冀泉雙軸支持計畫需求盤點（notice）：kw=False(0.1) emb=0.763 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 歷史沿革（other）：kw=True(0.363) emb=0.507 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 政府網站開放資料宣告（北市社會局）（other）：kw=True(0.643) emb=0.387 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；只有關鍵字的類別意見（類別待確認）
- 臺中市低收入戶三項生活補助費調整公告（notice）：kw=True(0.477) emb=0.958 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別一致
- 未參加相關社會保險之我國籍新生兒之生母生育補助 — 請領手續（fragment）：kw=True(0.898) emb=0.898 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 育有未滿2歲兒童育兒津貼總覽（other）：kw=False(0.06) emb=0.904 uncertain=False → 彙整頁：標題含「總覽」：彙整頁，保留供查閱但不進清單與媒合
- 托育人員、托嬰中心參與準公共化托育服務簽約相關規定（other）：kw=True(0.875) emb=0.961 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 極端氣候及年節時期加強關懷弱勢民眾計畫（other）：kw=True(0.582) emb=0.805 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- 國民年金生育給付暨加給補助 — 請領手續（fragment）：kw=True(0.975) emb=0.893 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 特殊境遇家庭扶助專區（directory）：kw=False(0.05) emb=0.729 uncertain=False → 彙整頁：標題含「專區」：彙整頁，保留供查閱但不進清單與媒合
- 育有未滿二歲兒童育兒津貼（faq）：kw=True(0.625) emb=0.964 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 特殊境遇家庭的相關福利（faq）：kw=True(0.786) emb=0.966 uncertain=False → 關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別一致
- 補助托嬰中心及居家式托育服務提供者收托身心障礙暨疑似發展遲緩幼兒實施計畫（attachment）：kw=False(0.09) emb=0.537 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；只有關鍵字的類別意見（類別待確認）
- 115年0-6歲國家跟你一起養 資訊（other）：kw=False(0.11) emb=0.829 uncertain=True → 三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

## 5. 主類別不同（三方投票 vs 黃金集）

- 高級中等學校各類學雜費減免及就學費用補助：gold=tuition_waiver ens=education_subsidy sec=['special_circumstances_aid', 'tuition_waiver', 'low_income_allowance'] kw=special_circumstances_aid emb=education_subsidy
- 失業給付申請：gold=unemployment_benefit ens=employment_incentive sec=['unemployment_benefit', 'emergency_relief', 'training_allowance'] kw=unemployment_benefit emb=employment_incentive
- 大鵬科技慈善基金會獎助學金：gold=student_aid ens=scholarship sec=['emergency_relief', 'student_aid'] kw=scholarship emb=scholarship
- 2026癌友家庭子女育秧獎助學金：gold=student_aid ens=scholarship sec=['student_aid'] kw=scholarship emb=scholarship
- 台灣松樑教育公益促進協會助學金：gold=student_aid ens=scholarship sec=['student_aid'] kw=scholarship emb=student_aid
- 宋作楠先生紀念獎助學金：gold=student_aid ens=scholarship sec=['student_aid'] kw=scholarship emb=scholarship
- 昌益慈善基金會助學金：gold=student_aid ens=scholarship sec=['student_aid'] kw=scholarship emb=student_aid
- 住宿式長照機構與產學合作國際專班攬才留用試辦計畫：gold=employer_subsidy ens=ltc_general sec=['institutional_care_subsidy', 'disability_other'] kw=institutional_care_subsidy emb=ltc_general
- 急難救助（學產基金急難慰問金）：gold=emergency_aid_student ens=emergency_relief sec=[] kw=emergency_relief emb=emergency_relief
- 無障礙住宅：gold=housing_support ens=assistive_device sec=['emergency_relief', 'housing_support', 'employment_incentive'] kw=emergency_relief emb=assistive_device
- 【已不再受理新申請案】中產房貸支持專區：gold=housing_loan_subsidy ens=employment_incentive sec=[] kw=employment_incentive emb=low_income_allowance
- 公益出租人：gold=housing_support ens=rental_subsidy sec=['low_income_allowance'] kw=rental_subsidy emb=rental_subsidy
- 耐震弱層補強：gold=housing_support ens=scholarship sec=['assistive_device', 'housing_loan_subsidy', 'emergency_relief'] kw=scholarship emb=assistive_device
- 臺東縣大專以上學校清寒優秀學生愛心安心就學獎學金：gold=scholarship ens=student_aid sec=['scholarship'] kw=scholarship emb=student_aid
- 居家服務（PDF）：gold=home_care ens=ltc_general sec=['family_care_home', 'home_care', 'day_care'] kw=family_care_home emb=ltc_general
- 少年就業力準備計畫：gold=youth_employment ens=employment_incentive sec=[] kw=employment_incentive emb=employment_incentive
- 國民年金被保險人所得未達一定標準資格申請簡介：gold=low_income_allowance ens=emergency_relief sec=['low_income_allowance', 'elderly_allowance', 'disability_living_allowance'] kw=emergency_relief emb=disability_living_allowance
- 南投縣兒童及少年生活扶助審核作業規定：gold=special_circumstances_aid ens=low_income_allowance sec=['child_allowance', 'special_circumstances_aid'] kw=low_income_allowance emb=low_income_allowance
- 補助親屬接受委託照顧兒少費用計畫：gold=childcare_subsidy ens=emergency_relief sec=['employment_incentive', 'special_circumstances_aid', 'childcare_subsidy'] kw=emergency_relief emb=childcare_subsidy
- 苗栗縣政府老人聲請監護輔助宣告補助實施計畫：gold=elderly_allowance ens=elderly_service sec=['low_income_allowance', 'elderly_allowance', 'institutional_care_subsidy'] kw=elderly_service emb=elderly_allowance
- 苗栗縣弱勢家庭兒童及少年緊急生活扶助補助：gold=emergency_relief ens=special_circumstances_aid sec=['emergency_relief', 'low_income_allowance'] kw=emergency_relief emb=special_circumstances_aid
- 兒童及少年未來教育與發展帳戶：gold=low_income_allowance ens=child_allowance sec=['low_income_allowance', 'elderly_allowance', 'employment_incentive'] kw=low_income_allowance emb=child_allowance
- 低收入戶未滿65歲生活無法自理者安置費用補助：gold=institutional_care_subsidy ens=low_income_allowance sec=['institutional_care_subsidy', 'elderly_allowance'] kw=low_income_allowance emb=low_income_allowance
- 身心障礙者居家維生器材用電優惠：gold=disability_other ens=assistive_device sec=['disability_other', 'disability_living_allowance'] kw=assistive_device emb=assistive_device
- 低收入戶產婦生育及營養補助：gold=birth_incentive ens=low_income_allowance sec=['birth_incentive'] kw=low_income_allowance emb=birth_incentive
- 115年度「一般身分別老人」補助裝置假牙計畫：gold=elderly_allowance ens=assistive_device sec=['elderly_allowance', 'elderly_service'] kw=elderly_allowance emb=assistive_device
- 苗栗縣辦理低收入戶與中低收入戶產婦及新生兒營養補助實施計畫(114修)：gold=birth_incentive ens=low_income_allowance sec=['birth_incentive'] kw=low_income_allowance emb=low_income_allowance
- 苗栗縣國民年金被保險人所得未達一定標準申請：gold=low_income_allowance ens=emergency_relief sec=['unemployment_benefit', 'elderly_allowance', 'low_income_allowance'] kw=emergency_relief emb=low_income_allowance
- 低收入戶全民健康保險補助：gold=medical_subsidy ens=low_income_allowance sec=[] kw=low_income_allowance emb=low_income_allowance
- 兒童與少年未來教育及發展帳戶：gold=low_income_allowance ens=child_allowance sec=['low_income_allowance', 'elderly_allowance', 'emergency_relief'] kw=low_income_allowance emb=child_allowance
- 南投縣低收入戶老人公費養護作業規定：gold=institutional_care_subsidy ens=elderly_allowance sec=['institutional_care_subsidy', 'low_income_allowance', 'emergency_relief'] kw=institutional_care_subsidy emb=elderly_allowance
- 國民年金保險費補助（所得未達一定標準）：gold=low_income_allowance ens=elderly_allowance sec=['special_circumstances_aid', 'emergency_relief', 'insurance_premium_subsidy'] kw=special_circumstances_aid emb=elderly_allowance
- 好孕專車車資補貼：gold=health_service ens=birth_incentive sec=['low_income_allowance', 'emergency_relief', 'elderly_service'] kw=low_income_allowance emb=birth_incentive
- 身心障礙家庭托顧服務計畫：gold=family_care_home ens=disability_care_subsidy sec=['family_care_home'] kw=family_care_home emb=disability_care_subsidy
- 馬偕計畫（長期奉獻外籍人士比照老人優待及長照服務）：gold=elderly_service ens=ltc_general sec=['assistive_device', 'elderly_service', 'respite_care'] kw=assistive_device emb=ltc_general
- 衛生福利部辦理兒童及少年未來教育與發展帳戶：gold=low_income_allowance ens=child_allowance sec=['low_income_allowance'] kw=low_income_allowance emb=child_allowance
- 身心障礙社區日間作業設施服務(小作所)：gold=disability_other ens=disability_care_subsidy sec=['disability_other'] kw=disability_other emb=disability_care_subsidy
- 臺南市5歲至入國民小學前幼兒就學補助：gold=education_subsidy ens=child_allowance sec=['education_subsidy'] kw=education_subsidy emb=child_allowance
