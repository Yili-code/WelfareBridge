# 紀錄稽核（規則式，866 筆）

- 乾淨（沒有任何旗標）：214（24.7%）

## 旗標統計

| 旗標 | 筆數 | 說明 |
| --- | ---: | --- |
| `schema_dropped_fields` | 401 | 綱要驗證移除了欄位（值在原文找不到） |
| `cash_without_amount` | 189 | 現金給付但沒有金額 |
| `obligation_not_in_text` | 83 | 義務條款不在原文 |
| `rule_value_missing` | 62 | 規則缺值 |
| `category_uncertain` | 61 | 類別三方不一致（待確認） |
| `no_simple_rules` | 57 | 沒有可判斷的資格規則 |
| `provider_is_division` | 54 | 主辦機關是科室名 |
| `amount_not_in_text` | 48 | 金額數字不在原文 |
| `text_too_short` | 17 | 原文過短 |
| `region_missing` | 13 | 缺地區 |
| `category_title_conflict` | 10 | 標題與主類別衝突 |
| `provider_looks_like_contact` | 9 | 主辦機關像聯絡資訊 |
| `gate_uncertain` | 8 | 是否補助三方不一致（待確認） |
| `rule_city_conflict` | 5 | 規則城市與機關不符 |
| `amount_is_threshold` | 5 | 金額其實是收入／財產門檻 |
| `rolling_with_end_date` | 1 | 隨時受理卻有截止日 |
| `amount_older_version` | 1 | 金額是舊年度版本 |
| `derived_number_not_in_text` | 1 | AI 改寫的敘述裡有原文沒有的數字 |

## 各來源旗標數

| 來源 | 紀錄 | 旗標 |
| --- | ---: | ---: |
| kinmen_sw | 84 | 99 |
| taichung_sw | 59 | 55 |
| penghu_sw | 52 | 54 |
| chiayi_county_sw | 48 | 48 |
| helpdreams_private | 44 | 42 |
| chiayi_city_sw | 40 | 82 |
| changhua_sw | 38 | 50 |
| kaohsiung_sw | 37 | 39 |
| hsinchu_city_sw | 37 | 21 |
| tainan_sw | 35 | 33 |
| keelung_sw | 33 | 37 |
| miaoli_sw | 33 | 43 |
| yilan_sw | 32 | 55 |
| taoyuan_sw | 29 | 65 |
| nantou_sw | 29 | 19 |
| hualien_sw | 27 | 26 |
| ntpc_sw | 23 | 28 |
| helpdreams_gov | 19 | 18 |
| gov_tw_services | 19 | 22 |
| hsinchu_county_sw | 17 | 22 |
| wda_emps | 16 | 26 |
| tainan_east_office | 15 | 22 |
| moi_pip | 10 | 19 |
| bli_family | 10 | 11 |
| ltc_1966 | 9 | 13 |
| ntou_stu | 8 | 4 |
| mohw_social_assistance | 7 | 14 |
| ntpc_banqiao_office | 7 | 9 |
| taipei_dosw | 6 | 3 |
| sfaa_childcare | 6 | 5 |
| taipei_doe | 5 | 10 |
| taipei_daan_office | 5 | 8 |
| taoyuan_zhongli_office | 5 | 3 |
| ece_moe | 5 | 4 |
| mohw_gov | 4 | 2 |
| moe_programs | 3 | 3 |
| taipei_ws_files | 3 | 4 |
| mol_gov | 2 | 2 |
| taipei_opendata | 2 | 2 |
| cip_regulations | 1 | 1 |
| taipei_health | 1 | 1 |
| moe_law | 1 | 1 |

## 逐筆（只列有旗標的）

### 高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金
- id `ae25d97f-0ef5-4462-8b22-54c460d34c19` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 高雄市政府教育局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 大專以上學校清寒優秀學生愛心-安心就學獎學金
- id `4e6c8998-51d8-4158-ae3d-a5e9f93c1c48` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 臺東縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 失業勞工子女生活扶助金
- id `f29c5ebd-066f-4d71-ac54-97dddc4fcade` ｜ 來源 helpdreams_gov ｜ 類別 student_aid ｜ 機關 勞動部 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 雲林縣115學年度第1學期中等以上學校清寒優秀獎學金
- id `ebe6c3a0-bc79-4eaf-b69a-dcc484efa20c` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 雲林縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市中等以上學校清寒優秀學生獎學金
- id `962a26ef-d840-4f7b-9638-8a69e830b242` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 嘉義市政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市中等以上學校勤學優秀學生獎學金
- id `c6ac01cc-1999-4735-98c9-a10019f689d0` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 臺中市政府教育局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義縣清寒優秀學生獎學金
- id `4f4146ba-568b-411f-80ff-56bc68ee018d` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 嘉義縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 衛生福利部社會及家庭署單親培力計畫
- id `9b76b98b-d2cd-4c30-ad44-161318eaa12b` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 衛生福利部社會及家庭署 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣115學年度第1學期國民中學以上學校清寒優秀學生獎學金
- id `6c8719c7-82d7-460c-a730-a05259cb7e48` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 南投縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺東縣毛毅先生榮民子女獎助學金
- id `20e6b8fd-04e6-4464-a902-c2fdf0ed9ca5` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 臺東縣政府 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需提供清寒家庭證明

### 屏東縣中等以上學校清寒及優秀學生獎學金
- id `ca2237ea-0314-49d8-983d-0a910838dd56` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 屏東縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市高級中等以上學校原住民學生獎學金
- id `7886dcb3-0edd-42bd-bb47-5a6202f3657b` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 新北市政府教育局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 基隆市高級中等以上學校清寒優秀學生獎學金
- id `83dcd116-e090-4b6a-9ea9-5c2f41b56c5b` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 基隆市政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 宜蘭縣115年第2次中等以上學校優秀學生獎學金
- id `267d5bdc-ec54-467d-988f-87bb35104edd` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 宜蘭縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺南市115學年度第1學期清寒優秀學生獎學金
- id `831b758f-a2d6-4db0-a883-74d890a06347` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 臺南市政府教育局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新生代希望工程
- id `1791f6bf-9780-49ce-a3f3-864fb713eca5` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 社團法人高雄市社福慈善總會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 行天宮急難濟助
- id `64c28b18-5e7d-4ca5-8960-4a4c1c11a272` ｜ 來源 helpdreams_private ｜ 類別 emergency_aid_student ｜ 機關 財團法人台北行天宮 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中華開發文教基金會「技藝職能獎學金」
- id `bcbc970a-9186-4f6d-8e53-54c21ecf748e` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人中華開發文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 麗寶福容獎助學金
- id `4866c4ac-2452-43f8-8b01-2aba459a6c51` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人麗寶文化藝術基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 大學院校客家信仰文化研究生獎學金
- id `49bbcb3c-a6aa-4fe9-82ba-581ca9cd3e20` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人褒忠亭義民中學財團 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提交論文計畫書及指導教授推薦書
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 115 年永齡銘日希望獎助學金
- id `a5bfaeb3-ca4e-4032-be92-01c2ae3ffdf8` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人永齡教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年新光鋼添澄癲癇之友獎、助學金
- id `f14f3d93-3b62-477c-962c-d0552a33ae89` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 社團法人台灣癲癇之友協會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 高中職專、大學、碩士【誌善】清寒學生進步獎學金
- id `4c23585b-b8ce-4ee5-b6a9-26cb72669dee` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 社團法人中華佛教善緣慈善會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年(第十七屆)績優清寒孝親獎助學金
- id `1611c8e2-8dd8-4d0e-9356-92bc21f8f67b` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人邱創煥文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年度資訊人社會關懷獎學金
- id `009c7268-0657-4b7b-acd1-934b0ea81812` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 中華民國電腦學會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 財團法人趙自強教育基金會資助海外來台深造熱河省學生獎助金
- id `a8950f91-60ce-4898-aa2a-7f848290ee86` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人趙自齊教育基金會、台北市熱河同鄉會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 欣榮圖書館急難學生助學金
- id `de541c00-9c9c-4a77-b340-ae3331d27ba3` ｜ 來源 helpdreams_private ｜ 類別 emergency_aid_student ｜ 機關 財團法人福田文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 孝悌楷模獎學金
- id `5a874d8f-1eb9-4d82-a84e-3088a8f4b951` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人和諧孝悌文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 社團法人台灣松樑教育公益促進協會助學金
- id `5565042f-3110-44f1-988d-bdf9c9170651` ｜ 來源 helpdreams_private ｜ 類別 student_aid ｜ 機關 社團法人台灣松樑教育公益促進協會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 115學年度大專院校學生獎助學金
- id `cb8b45cc-5fb4-4541-8b92-26d93dd016a3` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人台中商業銀行文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 鄭豐喜研究所/大學獎學金、鄭豐喜肢障者家庭子女獎學金
- id `53cad9cf-fe0c-45b0-88c9-5ea4fdd3768c` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人鄭豐喜文化教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115 學年度第1學期資優學生獎學金
- id `7d4bc574-2f39-468a-abc7-f68d903bd638` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人奇鋐教育基金會 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供學業成績單
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 2026第十四屆崇友實業獎學金
- id `f73c0dbb-91d4-46ea-a082-4b5800ace89d` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人崇友文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 賑災基金會助學金
- id `9a2694c6-54a2-4bf1-a3dc-16594cf203ce` ｜ 來源 helpdreams_private ｜ 類別 emergency_aid_student ｜ 機關 財團法人賑災基金會 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供相關證明文件
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 桃園市利晉工程清寒助學金
- id `d0cb0f34-ec2a-42eb-a421-bedc5d8ca3e7` ｜ 來源 helpdreams_private ｜ 類別 student_aid ｜ 機關 財團法人桃園市利基工程社會福利慈善事業基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 文向獎學金（新生入學、優秀在學生、青少年向學築夢計畫）
- id `70f09290-73dd-425a-b37e-3a6c86b4d5fc` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人文向教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 心臟病童獎勵學金
- id `0183ff05-b448-4de9-847d-d5f8ed7cdca0` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人中華民國心臟病兒童基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 陽光獎學金、陽光獎、陽光電腦獎助學金、萬足燒傷勞工子女大專生獎助學金、
- id `ae9a867f-886a-40a6-a426-d14768546fa3` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 陽光社會福利基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登

### 昌益慈善基金會助學金
- id `18b9e498-c448-4db0-abdd-a799b0fd9a46` ｜ 來源 helpdreams_private ｜ 類別 student_aid ｜ 機關 昌益慈善基金會(昌益事業群) ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請文件不全、成績未符標準、或有其他資格不符情形者，將不予審核。
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 行天宮資優學生長期獎助學金
- id `081d2ce7-2504-4909-8b14-f187510b3bf3` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人行天宮文教發展促進基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 2026年「青力親為●千萬祝福」服務學習獎勵計畫
- id `749f8fdb-68db-471e-8fa4-0cbbd7c54031` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人天河教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 祥和文教基金會優秀清寒獎學金
- id `4d879d43-6da6-496b-97ec-18e63049ceb8` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人祥和文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 耀登炳南創新研究獎、大專校院優秀人才獎學金
- id `a21d6138-28cf-4435-8a71-0a4b7fa5deaa` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人耀登炳南教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 宋作楠先生紀念獎助學金
- id `b6513573-fa73-4086-a6be-8e7f2313696f` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人宋作楠先生紀念教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 台新青少年志工菁英獎獎助學金
- id `b2dcdb3e-3321-4130-ac06-9ff91a184490` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人台新青少年基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 鴻海獎學鯨
- id `772c99ed-a497-4b46-93e4-142d25b36a86` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人鴻海教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 印順文教基金會「115年度論文獎學金」
- id `3d6987c4-6312-4564-918a-7a95b2efa324` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人印順文教基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 2026癌友家庭子女—育秧獎助學金
- id `c39d34b5-cd02-4973-98cc-7ba6ce0b20e8` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人育田社會福利慈善基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 財團法人得力教育基金會-清寒獎助學金
- id `3086a45b-1480-4e2b-8483-5cd8067e732f` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人得力教育基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 115學年度第1學期「韌世代」獎助學金
- id `3ce8569c-053e-4ae3-8d0d-f3c2c6db4b95` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人台灣兒童暨家庭扶助基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 羅慧夫顱顏基金會115年「得福獎助學金」
- id `72833481-52b7-45b3-b54c-6deec232d075` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人羅慧夫顱顏基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 大鵬科技慈善基金會獎助學金
- id `cd95b700-366f-4926-b6cd-a45aff0d51fb` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人大鵬科技慈善基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 正德基金會115年秋季獎學金
- id `8f68ab88-dae8-4fb2-988e-56d737c3cd33` ｜ 來源 helpdreams_private ｜ 類別 scholarship ｜ 機關 財團法人正德社會福利慈善基金會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 弱勢助學（大專校院弱勢學生助學計畫）
- id `a1368320-ee58-4d5d-9670-37235ba62220` ｜ 來源 moe_programs ｜ 類別 student_aid ｜ 機關 教育部 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：5000 不在原文可解析的金額中（原文金額：[1200, 3000, 6000, 15000, 20000, 35000, 1000000, 6500000]）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 學雜費減免
- id `b167099d-26f0-471d-8644-368682736435` ｜ 來源 moe_programs ｜ 類別 tuition_waiver ｜ 機關 教育部 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 原住民族委員會獎助大專校院原住民學生實施要點
- id `b6e83971-f992-4c8b-a6fb-5c4df111b7d2` ｜ 來源 cip_regulations ｜ 類別 scholarship ｜ 機關 原住民族委員會 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 【轉知】臺東縣政府115學年度第1學期「大專以上學校清寒優秀學生愛心安心就學獎學金」自115年10月1日起至115年10
- id `3760dfd5-e483-4d6b-b40b-db7c4564c56a` ｜ 來源 taipei_doe ｜ 類別 scholarship ｜ 機關 臺東縣政府 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[6000, 12000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[6000, 12000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[6000, 12000]）

### 【轉知】臺東縣政府「毛毅先生榮民子女獎助學金實施要點」及申請相關資訊
- id `cac2375e-de08-4fc8-b17d-e3c978474b8b` ｜ 來源 taipei_doe ｜ 類別 scholarship ｜ 機關 臺東縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 【轉知】僑務委員會115年度中等以上學校學行優良僑生獎學金相關資訊
- id `93832692-f005-4092-b323-03acb3f00065` ｜ 來源 taipei_doe ｜ 類別 scholarship ｜ 機關 僑務委員會 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 2026年崇友實業獎學金
- id `a9cec2ab-8b4f-4358-8fa9-ff6013107b8f` ｜ 來源 ntou_stu ｜ 類別 scholarship ｜ 機關 民間團體（公告未載明名稱） ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 宋映潭先生獎學金
- id `1ef5f201-e13e-4049-accc-d1c8213f107b` ｜ 來源 ntou_stu ｜ 類別 scholarship ｜ 機關 民間團體（公告未載明名稱） ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 大專校院原住民學生獎助學金
- id `ca73c4db-4a0e-49db-aca6-706a9c272160` ｜ 來源 gov_tw_services ｜ 類別 scholarship ｜ 機關 原住民族委員會 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 就保職業訓練生活津貼
- id `19601da8-980b-447d-a77b-6771cc23e0d1` ｜ 來源 gov_tw_services ｜ 類別 training_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：申請人應於離職退保後2年內，備具相關書件，親自向公立就業服務機構辦理求職登記，經公立就業服務機構安排參加全日制職業訓練。
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 高級中等學校各類學雜費減免及就學費用補助
- id `e8f77cba-a4f2-4732-8a53-897bbee7274b` ｜ 來源 gov_tw_services ｜ 類別 tuition_waiver ｜ 機關 教育部國民及學前教育署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 計程車駕駛及子女獎學金
- id `d665d35a-378b-4dfc-b031-1b1085841433` ｜ 來源 gov_tw_services ｜ 類別 scholarship ｜ 機關 交通部公路局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣-就讀大專院校學生助學金 提供民眾線上申請，可免檢附戶籍謄本(查驗是否符合設籍澎湖縣的規定)，查驗是否為澎湖縣國、
- id `e22e1df1-1580-4f79-8c9c-9cc613e38e91` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 澎湖縣政府 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣-獎助就讀大專院校學生交通圖書券申請 提供民眾線上申請服務，可透過MyData完成身分驗證及同意後，提供「 現戶全
- id `4294b2f0-b6f4-4537-a693-1926f345ca57` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 澎湖縣政府 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 國民中小學清寒原住民學生助學金 為協助國民中小學清寒原住民學生順利完成學業，激發向上精神，補助國民中學學生新臺幣4千元，
- id `f8839461-e2ed-48ab-86d0-858f50b1e56d` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 原住民族委員會 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[2000, 4000, 400000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[2000, 4000, 400000]）

### 臺中市-低收入戶就學交通補助申請 未滿25歲之低收入戶者，就讀公私立大專以下國小以上學校，可申請就學交通補助，國小每學期
- id `2b35dc2a-0e7b-4c27-b828-c96ae8fbc9c5` ｜ 來源 gov_tw_services ｜ 類別 education_subsidy ｜ 機關 臺中市政府 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 宜蘭縣-國民教育階段身心障礙學生獎助學金 就讀宜蘭縣公私立國民中小學之各類身心障礙學生，且在三年內未曾領取本獎助金者，可
- id `237d0f5e-a291-4946-a4fe-76403713c28f` ｜ 來源 gov_tw_services ｜ 類別 student_aid ｜ 機關 宜蘭縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市-低收入戶生活補助 為臺中市列冊之低收入戶者，可申請生活費補助，包含16歲以下兒童或少年生活補助、高中(職)以上就
- id `bd735766-da2e-4f2c-8963-f148c23a3826` ｜ 來源 gov_tw_services ｜ 類別 low_income_allowance ｜ 機關 臺中市政府 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需提交相关证明文件

### 臺中市-低收入戶房屋租金補助申請書表 無自有住宅之低收入戶，且其他家庭成員均無自有、借住、配住及居於三親等以內親屬之房舍
- id `b58238f6-3b9e-43d3-ac32-cab75053f712` ｜ 來源 gov_tw_services ｜ 類別 rental_subsidy ｜ 機關 臺中市政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新竹縣-(中)低收入戶租賃房屋租金補助 為新竹縣列冊之(中)低收入戶，符合無自有住宅之要件，每戶每月可申請補助新臺幣2千
- id `0fe32a12-f528-42c2-945b-6248dc13e401` ｜ 來源 gov_tw_services ｜ 類別 rental_subsidy ｜ 機關 新竹縣政府 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：100 不在原文可解析的金額中（原文金額：[500, 2500]）
- `amount_not_in_text` benefit.amount：100 不在原文可解析的金額中（原文金額：[500, 2500]）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新竹縣-(中)低收入戶房屋修繕補助新竹縣列冊之(中)低收入戶，其住宅符合所規定之要件，可申請房屋修繕補助。
- id `ed9cbd3c-e7d3-4b99-9b5b-c9fffdc309d3` ｜ 來源 gov_tw_services ｜ 類別 housing_support ｜ 機關 新竹縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 雲林縣-弱勢家庭幸福存款資產累積脫貧方案申請 民眾可透過MyData完成身分驗證及同意後，提供戶政國民身分證資料、現戶全
- id `a5f969f1-6f6a-45ca-a70d-323689af9714` ｜ 來源 gov_tw_services ｜ 類別 low_income_allowance ｜ 機關 雲林縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺北市中低收入老人特別照顧津貼
- id `3e56f73b-71ac-4e38-8dfd-274a329781d7` ｜ 來源 taipei_dosw ｜ 類別 elderly_allowance ｜ 機關 臺北市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺北市急難救助
- id `3514a40c-3ff8-436f-83ac-ad22188b9733` ｜ 來源 taipei_dosw ｜ 類別 emergency_relief ｜ 機關 臺北市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 長期照顧輔具服務
- id `e4c51f4c-9672-49c8-a70c-437ccb6636ab` ｜ 來源 taipei_dosw ｜ 類別 assistive_device ｜ 機關 臺北市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 長照服務的內容 — 居家服務
- id `c196ed6a-55d1-4914-8299-22f346d56285` ｜ 來源 taipei_health ｜ 類別 home_care ｜ 機關 臺北市政府衛生局 ｜ 等級 needs_review
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 老人機構收容安置補助(1100831更新)
- id `6d598eb5-7d1d-4b36-9f35-776fcabed3c6` ｜ 來源 taipei_ws_files ｜ 類別 institutional_care_subsidy ｜ 機關 臺北市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_city_conflict` residence.household_city：規則城市 ['宜蘭縣'] 與機關／標題 ['臺北市'] 不同
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 居家無障礙環境改善補助注意事項
- id `dc99f6dc-32a4-4c12-84a9-fac7072d0689` ｜ 來源 taipei_ws_files ｜ 類別 assistive_device ｜ 機關 臺北市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 我想要參加職業訓練
- id `026bdb76-43f9-4c13-ab02-7c104eb4a717` ｜ 來源 mol_gov ｜ 類別 training_allowance ｜ 機關 勞動部 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 失業勞工子女就學補助
- id `8913df54-b6f9-40b3-b167-1332ccbf7de2` ｜ 來源 mol_gov ｜ 類別 worker_welfare ｜ 機關 勞動福祉退休司 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 勞工補助與就業促進措施
- id `63909417-d268-427a-9985-80951add9e28` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 教育部辦理大專校院學生校內住宿補貼要點
- id `d207d0a8-fbe4-4ecc-8936-252c4fe6ca62` ｜ 來源 moe_law ｜ 類別 housing_support ｜ 機關 教育部 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺北市如何申請長照服務
- id `32c957e3-4e6f-4cb3-aaba-83f54164e075` ｜ 來源 taipei_opendata ｜ 類別 ltc_general ｜ 機關 臺北市政府 ｜ 等級 needs_review
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 臺北市長期照顧十年計畫(一)-居家服務
- id `890d710e-e6f7-4bd9-9ae5-919ad0cf8736` ｜ 來源 taipei_opendata ｜ 類別 home_care ｜ 機關 臺北市政府 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 300億元中央擴大租金補貼
- id `74b594ed-72d4-41c1-82f5-fcccb31ed2a6` ｜ 來源 moi_pip ｜ 類別 rental_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 verified
- `rolling_with_end_date` benefit.application_period：rolling=True 但有截止日 2026-12-31

### 缺工就業獎勵
- id `009e8833-b5cb-4f68-a747-1cbccd2d4aae` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 求職交通補助金
- id `9a6e8085-7717-454a-9003-2d16a74b4355` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臨時工作津貼
- id `58591588-4489-44b4-951b-c301c45a526f` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 僱用安定措施
- id `88119f35-3c69-4bcf-95a4-d776112ac6ea` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 青年職得好評計畫
- id `a9dab191-384b-4cb1-a8c2-4d47385aa522` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 照顧服務就業獎勵
- id `af289eba-5c49-4e8f-ac15-db63728033c8` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：受僱於居家式、社區式及照顧機構等長照單位連續達30日以上，且每月薪資不低於中央主管機關公告之每月基本工資
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 專案缺工就業獎勵
- id `19113c11-1dbc-47e5-a3d6-33c3487d89d1` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 青年跨域就業促進補助
- id `d9f8160e-84cb-413e-b0a7-d607c052a0f4` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 跨域就業津貼
- id `9ac943aa-9599-4213-a604-7b63411e8caa` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 天災臨時工作津貼
- id `b67fbd85-7f66-4a48-9fd5-68b5c31d472a` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 支援青年就業計畫
- id `8694f208-120e-45f6-bad4-432afcb51b5a` ｜ 來源 wda_emps ｜ 類別 youth_employment ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：同一期間已領取政府其他相似計畫之獎勵金或津貼
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 長照3.0中重度照顧支持升級 機構住民補助每年最高18萬
- id `990ee559-04a6-40b7-81a2-ae4fb201f602` ｜ 來源 ltc_1966 ｜ 類別 institutional_care_subsidy ｜ 機關 長期照顧司 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需入住住宿式機構的中、重度失能者

### 在臺「安居」更「安老」！ 衛福部公告外國專業人才及眷屬長照新制
- id `fdcfdaab-37d4-44e8-a2b0-800efd8262f0` ｜ 來源 ltc_1966 ｜ 類別 ltc_general ｜ 機關 長期照顧司 ｜ 等級 needs_review
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 公告「衛生福利部建立住宿式長照機構與產學合作國際專班攬才留用試辦計畫」(1141016修正)
- id `869c3ab7-c125-4f68-b795-14a65c9e014f` ｜ 來源 ltc_1966 ｜ 類別 study_abroad ｜ 機關 長期照顧司 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 低收入戶及中低收入戶住宅補貼
- id `baa9abec-dbd7-4be9-ac71-7f42cc70bcb2` ｜ 來源 moi_pip ｜ 類別 rental_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 失業給付
- id `5837163a-e489-4417-9cca-3498cb03f225` ｜ 來源 wda_emps ｜ 類別 unemployment_benefit ｜ 機關 勞動部勞動力發展署 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：每月未親自至公立就業服務機構辦理失業再認定，或於辦理失業再認定時，未提供至少2次以上的求職紀錄。
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 充電再出發訓練計畫
- id `44f855e9-749f-4172-bfda-7238d630d892` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 職場學習及再適應計畫
- id `7fbfdbb0-6678-491b-a760-ded6a069b9b4` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 公告本部「115年度日照中心導入科技輔具成效補助計畫」
- id `941a666c-814b-4384-8272-c049502b9d4a` ｜ 來源 ltc_1966 ｜ 類別 assistive_device ｜ 機關 長期照顧司 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 整合住宅補貼資源實施方案
- id `9c09f8ae-c131-404b-848a-911ca73f9b51` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 【已不再受理新申請案】內政部主辦4,000億元優惠購屋專案貸款
- id `06eeeeed-7879-4378-82ce-e4623812ec27` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `amount_not_in_text` benefit.amount：4000 不在原文可解析的金額中（原文金額：[4606]）
- `amount_not_in_text` benefit.amount：4000 不在原文可解析的金額中（原文金額：[4606]）
- `amount_not_in_text` benefit.amount：4000 不在原文可解析的金額中（原文金額：[4606]）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 174 字，難以判斷

### 耐震弱層補強
- id `5eec16d5-9cb6-4d1a-ae2a-5c8f183b3737` ｜ 來源 moi_pip ｜ 類別 housing_support ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 婦女再就業計畫
- id `2c2cf7a2-f13f-4072-af25-87cefd27d8e6` ｜ 來源 wda_emps ｜ 類別 employment_incentive ｜ 機關 勞動部勞動力發展署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府獎學金
- id `3ee97ace-6751-4c0f-b904-d4a0af69a3d2` ｜ 來源 helpdreams_gov ｜ 類別 scholarship ｜ 機關 金門縣政府 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 裕民航運獎學金
- id `329c16ad-06a5-4692-a064-a2daaea50668` ｜ 來源 ntou_stu ｜ 類別 scholarship ｜ 機關 民間團體（公告未載明名稱） ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 裕民航運培育金
- id `31572785-aea2-42dc-8c9b-6ba0f558d90f` ｜ 來源 ntou_stu ｜ 類別 scholarship ｜ 機關 民間團體（公告未載明名稱） ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 長照自建資訊系統介接長照服務費用支付審核系統驗證作業，自即日起至114年7月25日截止
- id `95230a62-c062-479b-b50e-1b22c18be2ad` ｜ 來源 ltc_1966 ｜ 類別 ltc_general ｜ 機關 資訊處 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 衛生福利部「長照交通接送公版預約整合服務」研發成果授權公告
- id `c775e61b-66d0-4311-bb8f-f465d962e594` ｜ 來源 ltc_1966 ｜ 類別 transport_service ｜ 機關 長期照顧司 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 育嬰留職停薪津貼及薪資補助
- id `71aa8fd1-b5c0-4ea1-9262-b14d6ebb726f` ｜ 來源 gov_tw_services ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 【轉知】綠色冀泉股份有限公司推動「校園都市林生態賦能」及「偏鄉弱勢學生 AI 循環筆電數位平權」雙軸支持計畫資訊
- id `483969c2-8724-4796-b7e8-1009c0ceca15` ｜ 來源 taipei_doe ｜ 類別 education_subsidy ｜ 機關 綠色冀泉股份有限公司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：有訊號說是補助但 LLM 說不是：依「不漏抓」原則保留為疑似補助，待人工確認；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：有訊號說是補助但 LLM 說不是：依「不漏抓」原則保留為疑似補助，待人工確認；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 商業型以房養老貸款
- id `29a562ae-7c50-4f83-8f90-6c35f0c06754` ｜ 來源 mohw_gov ｜ 類別 housing_loan_subsidy ｜ 機關 社會及家庭署 ｜ 等級 needs_review
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### (檔案下載)107年3月27日修正中低收入老人補助裝置假牙實施計畫(行政院核定本).pdf
- id `4dd7aa67-45a6-4e33-8eff-b5298e6237a9` ｜ 來源 mohw_gov ｜ 類別 elderly_allowance ｜ 機關 衛生福利部 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 智慧共融照顧新模式 全國日間照顧服務單位齊聚交流
- id `467e1a8d-6424-4c7b-aef1-a3cef1355afe` ｜ 來源 ltc_1966 ｜ 類別 day_care ｜ 機關 長期照顧司 ｜ 等級 verified
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致

### 長照十年計畫2.0
- id `64f4dd5d-6315-477e-bee9-edfeb8e7fc28` ｜ 來源 ltc_1966 ｜ 類別 ltc_general ｜ 機關 長期照顧司 ｜ 等級 needs_review
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；關鍵字與 embedding 類別一致
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 身心障礙者房屋租金及購屋貸款利息補貼
- id `15da8949-7f2b-4b5b-8e38-d19991ffae7a` ｜ 來源 moi_pip ｜ 類別 rental_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 房貸商品查詢
- id `0bf33603-069e-473f-b68b-f357fd8b6dab` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 住宅性能評估
- id `e6468991-4c83-4d53-8812-502d8b9322c2` ｜ 來源 moi_pip ｜ 類別 housing_loan_subsidy ｜ 機關 內政部國土管理署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 無障礙住宅
- id `97baa19a-c7a7-4750-ac89-979b71eb2b32` ｜ 來源 moi_pip ｜ 類別 housing_support ｜ 機關 內政部國土管理署 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 高雄市生育津貼
- id `76673583-61b8-450c-b7ae-6f174e268e2a` ｜ 來源 kaohsiung_sw ｜ 類別 birth_incentive ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `amount_older_version` benefit.amount：金額摘錄是民國 [112] 年的版本，資格／標題提到民國 [114] 年

### 低收入戶生活補助
- id `bd55dd19-c027-4ef2-bddb-899b1cbb12c1` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 低收入戶孕產婦及嬰幼兒營養補助
- id `6a96073c-5f12-49e1-8313-59541dc481ff` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 高雄市經濟弱勢市民醫療補助(含看護費補助)
- id `e1eb331a-9290-49b8-96be-4b9680d8c973` ｜ 來源 kaohsiung_sw ｜ 類別 medical_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：應於出院或医疗行为发生后3个月内提出申请。

### 敬老卡優惠
- id `1b85aecc-4672-423b-b6a0-5538d1dcf5d5` ｜ 來源 kaohsiung_sw ｜ 類別 elderly_service ｜ 機關 本市各區公所社會(經)課 ｜ 等級 needs_review
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 老人修繕住屋補助
- id `9f2fd396-a9db-4fd4-af28-4c34160d87a0` ｜ 來源 kaohsiung_sw ｜ 類別 elderly_service ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_title_conflict` category：標題含「修繕」，預期 ['disability_other', 'housing_loan_subsidy', 'housing_support', 'social_housing']，實際 elderly_service

### 單親家庭子女托育補助
- id `acb8eb4b-0c74-48ec-878f-35c1f0973ff1` ｜ 來源 kaohsiung_sw ｜ 類別 childcare_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1500 不在原文可解析的金額中（原文金額：[3000, 180000, 1200000, 6500000]）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 高雄市輔具及居家無障礙環境改善代償墊付服務
- id `74f9de2f-3fd2-4f4a-8d82-f952783ab099` ｜ 來源 kaohsiung_sw ｜ 類別 assistive_device ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請時需提交身心障礙證明影本、國民身分證影本或戶口名簿影本、輔具補助基準表所定各補助項目之診斷書及輔具評估報告書等文件。
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 身心障礙照顧者津貼
- id `f7309cf3-dd38-4937-a007-4b96d58eab5b` ｜ 來源 kaohsiung_sw ｜ 類別 disability_care_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶子女就學生活扶助
- id `d9367c5f-1ef7-4d54-8004-7a03f7175a5d` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `text_too_short` original_text：原文只有 139 字，難以判斷

### 低收入戶乘車船補助
- id `37e86c2d-7e6b-48a2-a907-2e5530cae220` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 衛生福利部辦理兒童及少年未來教育與發展帳戶
- id `34687bf9-09db-43a0-9de3-1ac3238f7d76` ｜ 來源 kaohsiung_sw ｜ 類別 education_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 低收入戶子女升學補習費補助
- id `0dd789a4-6507-4227-9bc0-b3df63bbdb30` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 低收入戶就讀高中職以上在學子女之學習設備補助
- id `ef5e8710-8451-4cdb-92d3-d2718253579f` ｜ 來源 kaohsiung_sw ｜ 類別 education_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 弱勢兒童及少年療育訓練費用補助
- id `feeaf339-9bec-4ce1-bbd0-7c26b9342970` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 輔導弱勢家庭青少年就業
- id `448d48e7-41fb-478f-a830-e65f32121ef0` ｜ 來源 kaohsiung_sw ｜ 類別 youth_employment ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 弱勢單親家庭子女教育補助
- id `e05bfc26-bdfb-4eba-a5a8-0ec1c66ff9ad` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 高雄市發展遲緩兒童早期療育費用補助
- id `10f55807-c26b-426a-937e-b015d10e69e3` ｜ 來源 kaohsiung_sw ｜ 類別 childcare_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 單親家庭服務
- id `d6c61f8b-7b74-4254-8121-c893e656392f` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 單親培力補助
- id `413f2811-f5b2-4824-b29e-caaefe67d56c` ｜ 來源 kaohsiung_sw ｜ 類別 student_aid ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 單親家園租屋服務
- id `bb472a05-d05b-4df4-bf64-6135651d73d6` ｜ 來源 kaohsiung_sw ｜ 類別 rental_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 緊急生活扶助
- id `a24c471e-8043-4650-a9ad-26ca75ad6ead` ｜ 來源 kaohsiung_sw ｜ 類別 low_income_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需設籍及實際居住本市
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 高中職以上子女學雜費減免認證
- id `65eb8f89-9e50-480b-ac80-c6064112faa5` ｜ 來源 kaohsiung_sw ｜ 類別 tuition_waiver ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 家庭暴力被害人法律訴訟補助
- id `f8780b84-7cdb-4d3f-90b3-ccdf9ef5ff77` ｜ 來源 kaohsiung_sw ｜ 類別 emergency_aid_student ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需提交身份證明、律師費用收據及相關證明文件
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 全民健康保險保費自付額補助
- id `1dc24cb5-9113-4bf1-acb7-ede8d8efbae9` ｜ 來源 kaohsiung_sw ｜ 類別 medical_subsidy ｜ 機關 高雄市政府社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 現金給付之社會保險補助
- id `beaaed4d-1199-4872-a6a1-32e20e3d218d` ｜ 來源 kaohsiung_sw ｜ 類別 disability_living_allowance ｜ 機關 高雄市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 衛生福利部急難救助金申請審核及撥款作業規定
- id `3cfec097-43d1-4731-a307-0e9c17ecd56e` ｜ 來源 mohw_social_assistance ｜ 類別 emergency_relief ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 急難救助作業流程（社會救助法第21條急難救助對象）
- id `5ab313e4-01d9-423d-866a-e9b66065846d` ｜ 來源 mohw_social_assistance ｜ 類別 emergency_relief ｜ 機關 社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺灣省及福建省低收入戶生活扶助金額表（113年1月1日起適用）
- id `84577e8b-9c9d-4d7e-be4c-44e1051b9c7d` ｜ 來源 mohw_social_assistance ｜ 類別 low_income_allowance ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：11850 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：11850 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：11850 不在原文可解析的金額中（原文金額：[]）

### 政府鼓勵脫貧自立3+1
- id `58442c6f-b5e1-4291-8957-e2b4f38db892` ｜ 來源 mohw_social_assistance ｜ 類別 low_income_allowance ｜ 機關 社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶及中低收入戶（衛生福利e寶箱）
- id `ddf46923-618d-442d-9876-d0bfbf371a4d` ｜ 來源 mohw_social_assistance ｜ 類別 low_income_allowance ｜ 機關 社會救助及社工司 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 極端氣候及年節時期加強關懷弱勢民眾計畫
- id `93f79aa3-f28e-40a9-bc90-7e200730857f` ｜ 來源 mohw_social_assistance ｜ 類別 low_income_allowance ｜ 機關 衛生福利部社會救助及社工司 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有關鍵字的類別意見（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登

### 低收入戶產婦生育及營養補助
- id `9a2cda9b-a9b8-47ac-845c-553aecb94f7e` ｜ 來源 ntpc_banqiao_office ｜ 類別 birth_incentive ｜ 機關 新北市板橋區公所 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：提供申請表、戶籍謄本、領款收據等文件
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 好孕專車車資補貼
- id `30582ba4-bbc7-430f-add4-06ee5b7f14a6` ｜ 來源 ntpc_banqiao_office ｜ 類別 childcare_subsidy ｜ 機關 新北市板橋區公所 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶申請資格與補助
- id `0b5b8854-723c-4e23-9453-d7d6bdc13de5` ｜ 來源 ntpc_banqiao_office ｜ 類別 low_income_allowance ｜ 機關 新北市板橋區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 特殊境遇家庭的相關福利
- id `4d0d9eb7-89d6-4578-ac4c-de1481420ed2` ｜ 來源 ntpc_banqiao_office ｜ 類別 special_circumstances_aid ｜ 機關 新北市板橋區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 市民意外救助
- id `35c1132b-2ddc-4bde-8b42-dc42235c1602` ｜ 來源 ntpc_banqiao_office ｜ 類別 emergency_relief ｜ 機關 新北市板橋區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者生活補助及走失手鍊
- id `a11f71cd-9dce-40eb-8bd0-b3a0616c1278` ｜ 來源 ntpc_banqiao_office ｜ 類別 disability_living_allowance ｜ 機關 新北市板橋區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市生育獎勵金
- id `f26b478b-4fe8-4dca-927d-fd99d86f1b10` ｜ 來源 ntpc_sw ｜ 類別 birth_incentive ｜ 機關 新北市政府民政局 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：申請人須在新生兒出生之次日起1年內提出申請
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_city_conflict` residence.household_city：規則城市 ['基隆市', '臺北市', '桃園市'] 與機關／標題 ['新北市', '新北市'] 不同
- `rule_city_conflict` residence.household_city：規則城市 ['臺北市', '桃園市', '基隆市'] 與機關／標題 ['新北市', '新北市'] 不同

### 新北市低收入戶產婦生育及營養補助
- id `08a99d09-5a3b-4061-b7fe-3507aa4e99a0` ｜ 來源 ntpc_sw ｜ 類別 birth_incentive ｜ 機關 新北市政府社會局社會救助科 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供申請表、戶籍謄本、領款收據等文件
- `amount_not_in_text` benefit.amount：400 不在原文可解析的金額中（原文金額：[20400]）
- `amount_not_in_text` benefit.amount：400 不在原文可解析的金額中（原文金額：[20400]）
- `amount_not_in_text` benefit.amount：400 不在原文可解析的金額中（原文金額：[20400]）

### 新北市弱勢兒童少年生活扶助
- id `953170d8-ce98-4efe-a51e-0e47be12bea9` ｜ 來源 ntpc_sw ｜ 類別 low_income_allowance ｜ 機關 新北市各區公所 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市中低收入戶資格申請
- id `c756c90f-8072-479f-bd95-97b6480a699d` ｜ 來源 ntpc_sw ｜ 類別 low_income_allowance ｜ 機關 新北市政府社會局社會救助科 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市急難救助
- id `6e83173b-997b-4c90-aaee-89de74179d43` ｜ 來源 ntpc_sw ｜ 類別 emergency_relief ｜ 機關 新北市各區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市政府委任區公所辦理強化社會安全網急難紓困實施方案
- id `069b779f-73c8-4153-a393-e231e3acba6f` ｜ 來源 ntpc_sw ｜ 類別 emergency_relief ｜ 機關 新北市政府社會局社會救助科 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需檢具申請書或通報表
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市市民意外事故致死救助
- id `3d38c96c-aecb-4bc8-b4a3-0c24f5c9f134` ｜ 來源 ntpc_sw ｜ 類別 emergency_relief ｜ 機關 新北市各區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 新北市低收入戶及中低收入戶傷病住院看護費用補助
- id `2a6d4eca-e02b-47f6-bbc0-8ae7a4c18593` ｜ 來源 ntpc_sw ｜ 類別 low_income_allowance ｜ 機關 新北市各區公所 ｜ 等級 verified
- `amount_is_threshold` benefit.amount.description：（二）本市列冊之中低收入戶，單月自行負擔看護費用累計超過新臺幣（以下同）三萬元或最近三個月累計超過五萬元以上者。
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市市民醫療補助
- id `da803ae9-f0a0-4e48-a23d-e788f6804fb4` ｜ 來源 ntpc_sw ｜ 類別 medical_subsidy ｜ 機關 新北市各區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市中低收入老人生活津貼
- id `723e17b9-2a03-4aab-9984-0a83b9810092` ｜ 來源 ntpc_sw ｜ 類別 elderly_allowance ｜ 機關 新北市政府社會局老人福利科 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市中低收入老人裝置假牙補助
- id `c90703a5-7d2f-4e6a-9d95-ed234f3b5af9` ｜ 來源 ntpc_sw ｜ 類別 elderly_allowance ｜ 機關 新北市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新北市中低收入老人重病住院看護補助
- id `6cc91a11-2612-4d3e-8257-3f8501a2af47` ｜ 來源 ntpc_sw ｜ 類別 elderly_allowance ｜ 機關 新北市政府社會局老人福利科 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 新北市低收入戶及中低收入失能老人接受長期照顧機構安置補助
- id `ce32f817-382f-46f8-a08f-18d7605945bb` ｜ 來源 ntpc_sw ｜ 類別 institutional_care_subsidy ｜ 機關 新北市政府社會局老人福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新北市敬老、愛心及愛心陪伴悠遊卡
- id `c158bce7-fdc7-4cea-be17-8edb1c6eb8c1` ｜ 來源 ntpc_sw ｜ 類別 elderly_service ｜ 機關 新北市各區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 新北市身心障礙者生活補助
- id `d9ffcb2b-d9c1-437e-bca6-dd7b61ca22ee` ｜ 來源 ntpc_sw ｜ 類別 disability_living_allowance ｜ 機關 新北市政府社會局身心障礙福利科 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 新北市身心障礙者參加全民健康保險及社會保險自付保費補助
- id `80f39ea1-bd92-4e8e-b0f7-1bfec1d9a7f8` ｜ 來源 ntpc_sw ｜ 類別 disability_other ｜ 機關 新北市政府社會局身心障礙福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新北市身心障礙者租賃房屋租金補助
- id `9398be25-6a5a-4bf4-af67-7ec578f2f353` ｜ 來源 ntpc_sw ｜ 類別 rental_subsidy ｜ 機關 新北市政府社會局身心障礙福利科 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 直轄市、縣(市)政府辦理未滿二歲兒童托育公共化及準公共服務作業要點
- id `ec468665-c62c-461d-a48b-ff393cc04bfd` ｜ 來源 sfaa_childcare ｜ 類別 childcare_subsidy ｜ 機關 衛生福利部社會及家庭署 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登

### 未滿二歲兒童公共化及準公共托育補助（協助支付）金額表
- id `fbd85a26-bc76-452a-9adb-a4828654c6e7` ｜ 來源 sfaa_childcare ｜ 類別 childcare_subsidy ｜ 機關 衛生福利部社會及家庭署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 補助親屬接受委託照顧兒少費用計畫
- id `d1de6969-235b-4028-8523-7f16f921ae7f` ｜ 來源 sfaa_childcare ｜ 類別 childcare_subsidy ｜ 機關 衛生福利部社會及家庭署 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺中市生育津貼
- id `1c538796-da82-4b8d-ae4b-57f4a6b628bf` ｜ 來源 taichung_sw ｜ 類別 birth_incentive ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 未滿二歲兒童育兒津貼
- id `0c558b31-65c6-44dd-9edd-6799133787c5` ｜ 來源 taichung_sw ｜ 類別 child_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市平價托育及準公共服務實施計畫
- id `a700cac4-a555-400a-811f-410fbd459a20` ｜ 來源 taichung_sw ｜ 類別 childcare_subsidy ｜ 機關 臺中市政府社會局（以下稱本局） ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登

### 臺中市政府社會局弱勢家庭兒童臨時托育服務補助計畫
- id `d94cc651-d46c-4655-9989-3abea747b100` ｜ 來源 taichung_sw ｜ 類別 childcare_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市到宅坐月子服務(含弱勢對象)
- id `c53f853d-7e4e-4ed9-9944-c96402b3001a` ｜ 來源 taichung_sw ｜ 類別 home_care ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺中市政府社會局辦理發展遲緩兒童早期療育補助執行計畫
- id `36a11cc6-1b41-4a21-9144-ee056f4d9adf` ｜ 來源 taichung_sw ｜ 類別 childcare_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 臺中市低收入戶三節慰問金補助計畫
- id `5bcae46b-a89b-4719-b93d-24f0f6cc5501` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺中市政府社會局低收入戶房屋租金補助及房屋稅減免
- id `a177ca4a-4d4d-4f0b-a729-224a819c45f9` ｜ 來源 taichung_sw ｜ 類別 rental_subsidy ｜ 機關 臺中市政府地方稅務局(電話 ｜ 等級 verified
- `provider_looks_like_contact` provider：臺中市政府地方稅務局(電話
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市低收入戶、中低收入戶住院看護費用補助
- id `27c8edfb-3a56-4286-855c-3f5c3f6dd63a` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人應於看護行為結束日起三個月內提出申請，逾期不予受理。
- `amount_is_threshold` benefit.amount.description：(二)未滿六十五歲之中低收入戶傷、病者，須符合單月自行負擔看護費用累計新臺幣三萬元以上或最近三個月內累計新臺幣五萬元以上。

### 臺中市市民醫療補助
- id `de9d48ea-77e8-40ec-96ff-be376f7f5454` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市辦理低收入戶及中低收入戶微型保險
- id `6d764704-15ab-44bd-96ce-4a79c5fe7d4a` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市經濟弱勢兒童及少年生活扶助
- id `7ed864da-1318-429d-a750-c8f376b209bd` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市辦理中低收入家庭內未滿18歲兒童及少年健保費補助
- id `32e722aa-1a63-4511-a16f-a84bb947d290` ｜ 來源 taichung_sw ｜ 類別 low_income_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺中市急難救助
- id `89f57f06-25a1-48d4-909e-900c900fea06` ｜ 來源 taichung_sw ｜ 類別 emergency_relief ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

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
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 特殊境遇家庭扶助－子女生活津貼
- id `a6d19795-c72a-438d-a113-f3d0914edcec` ｜ 來源 taichung_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 特殊境遇家庭扶助－傷病醫療補助
- id `26a61abf-e83c-4edc-a116-66d530f598bd` ｜ 來源 taichung_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 特殊境遇家庭扶助－兒童托育津貼
- id `b297c18c-dc27-48e2-a108-b4058aeacde2` ｜ 來源 taichung_sw ｜ 類別 childcare_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 特殊境遇家庭扶助－法律訴訟補助
- id `0aba7cfa-7a41-4f70-aaac-2c5faced5c91` ｜ 來源 taichung_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：檢附委任狀及起訴狀影本
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 特殊境遇家庭扶助－設籍前新住民返鄉機票費
- id `2509ca24-222f-4fdf-8539-606dcec1fe5b` ｜ 來源 taichung_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：應於返國20日內持機票存根聯或搭機證明及護照出、入境查驗章頁影本辦理核銷、撥款
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市單親及弱勢家庭短期租屋津貼計畫
- id `49090a16-86bc-42bb-b431-32f9334a446b` ｜ 來源 taichung_sw ｜ 類別 rental_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市重陽節敬老禮金
- id `bfa878b3-0a92-4705-8116-bcabc59e3b04` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 百歲人瑞敬老禮金
- id `10fa1f5b-39d6-4f00-944c-310e788d2f84` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 65歲以上老人健保補助
- id `e41a4598-9e98-457e-b006-7c8b2413ae18` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市中低收入老人健保保費自付額補助
- id `976c6e5b-1bae-4489-a954-821857609340` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 空間行善者－獨居銀髮族暨弱勢民眾住屋愛心修繕補助
- id `3e8b0f15-3b05-4b13-aaf0-e77aba2a0e22` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 老人聲請監護輔助宣告費用補助
- id `2aa8e22f-c11b-46c0-8a52-507f2d8621f9` ｜ 來源 taichung_sw ｜ 類別 elderly_allowance ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：於法院指定醫院鑑定後6個月內檢附申請文件

### 低收入戶孤苦無依老人收容照顧補助
- id `2b1de74a-a072-49f3-91df-1a450e027722` ｜ 來源 taichung_sw ｜ 類別 institutional_care_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市政府社會局低收入戶老人補助配戴助聽器實施計畫
- id `3b7f1397-242b-4511-8814-391a6ec4be49` ｜ 來源 taichung_sw ｜ 類別 assistive_device ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需檢附6個月內經健保合約醫療院所開立之診斷證明書及聽力圖正本

### 臺中市敬老眼鏡補助暨視力檢查服務實施計畫
- id `479ba913-8f82-40d4-8020-81664b0f52b8` ｜ 來源 taichung_sw ｜ 類別 assistive_device ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺中市中低收入獨居老人營養餐飲服務
- id `ba88cce1-a1e8-4894-befe-bf83aadd396c` ｜ 來源 taichung_sw ｜ 類別 meal_service ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺中市政府社會局身心障礙照顧者津貼
- id `a67358c9-5522-4a67-8dd7-6b59de4fe599` ｜ 來源 taichung_sw ｜ 類別 disability_care_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者參加健保費及社會保險補助
- id `a48d7d5f-b844-41a5-8436-416e3df3e094` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者國民年金保險費補助
- id `d7e0af12-554e-4932-b0cf-2d37b1def4f8` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 臺中市身心障礙者房屋租金補貼
- id `e9194b4e-ab59-4122-9cde-4d38aa849382` ｜ 來源 taichung_sw ｜ 類別 rental_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者裝置假牙補助計畫
- id `cd90b0a2-09b9-4e13-a5f5-8afb0af47748` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `category_title_conflict` category：標題含「假牙」，預期 ['assistive_device', 'disability_assistive_device', 'elderly_allowance', 'elderly_service', 'medical_subsidy']，實際 disability_other
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者傷病住院看護費用補助
- id `14b276da-1799-4f05-adcb-2907aba9c061` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 視覺障礙者搭乘計程車費用補助
- id `6bc00914-acf7-4d93-a6dc-7b3f22836d01` ｜ 來源 taichung_sw ｜ 類別 transport_service ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 補助身心障礙者住屋愛心修繕計畫
- id `93d13d14-6f00-4f34-b936-4c1ba13af75f` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者聲請監護(輔助)宣告費用補助
- id `ec63f159-dc84-4417-a437-ef0391e93c19` ｜ 來源 taichung_sw ｜ 類別 disability_other ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺中市遊民醫療及看護補助計畫
- id `6d02acb5-558b-4f71-8c22-7dff21e0f4fc` ｜ 來源 taichung_sw ｜ 類別 medical_subsidy ｜ 機關 臺中市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 災害救助申請簡介
- id `4bc5a157-4eb1-4c48-bae9-63e16cb97b26` ｜ 來源 taipei_daan_office ｜ 類別 emergency_relief ｜ 機關 臺北市大安區公所 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者社會保險自付保險費現金補助
- id `9479ba5b-540a-498d-88ac-8bc883bc2633` ｜ 來源 taipei_daan_office ｜ 類別 disability_other ｜ 機關 臺北市大安區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 國民年金被保險人所得未達一定標準資格申請簡介
- id `ab7024d2-2b1a-4cd9-b4b4-2eca247090b6` ｜ 來源 taipei_daan_office ｜ 類別 low_income_allowance ｜ 機關 臺北市大安區公所 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 以工代賑臨時工申請須知
- id `231783a2-b819-4bd5-abd5-2d4cea95468c` ｜ 來源 taipei_daan_office ｜ 類別 low_income_allowance ｜ 機關 臺北市大安區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 育兒津貼申請簡介
- id `4b6789d3-4f23-4780-8828-f7a57740eb61` ｜ 來源 taipei_daan_office ｜ 類別 child_allowance ｜ 機關 臺北市大安區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 低收、中低收入戶申請資格
- id `90f7c1be-0fcd-4b57-8523-2896f04d09d7` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 低收入戶就學生活扶助
- id `6761ddf7-f8e4-4ea2-ad40-82ff61509ccd` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region

### 桃園市低收入戶及中低收入戶傷病看護費用補助
- id `5b7b0a89-100a-426d-8c1e-e5dfec7cd41f` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人需提供看護費用收據正本、診斷證明書等文件
- `amount_is_threshold` benefit.amount.description：本市列冊未滿六十五歲之中低收入戶之傷、病患，於住院期間經醫師診斷證明需專人看護，而無親屬或親屬無法看護，且自付看護費用單月累計達新臺幣三萬元以上，或最近三個月內累計達新臺幣五萬元以上。

### 低收入戶孕產婦及嬰兒營養品代金補助
- id `7e90d2c8-87a4-4787-9122-6ff7a35e0450` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 低收入戶三節慰問金
- id `65318f3d-ee93-409c-bb46-7ab29954cef4` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 桃園市市民醫療補助
- id `9c80bf9a-d51f-4118-9d55-a143cf316d32` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 桃園市急難救助
- id `729ad9f4-9da3-4e5d-84c2-fd5c7b93cf3d` ｜ 來源 taoyuan_sw ｜ 類別 emergency_relief ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 強化社會安全網—急難紓困
- id `8a3f5758-4832-4f42-9758-0b54020e1af7` ｜ 來源 taoyuan_sw ｜ 類別 emergency_relief ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 桃園市少年自立生活經濟扶助計畫
- id `2ba28fb5-3fea-4075-8321-5bec8df01d63` ｜ 來源 taoyuan_sw ｜ 類別 student_aid ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 65歲以上老人健保自付額補助
- id `a6531eed-d35d-4078-a48b-4840a16f0625` ｜ 來源 taoyuan_sw ｜ 類別 elderly_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 桃園市重陽敬老禮金
- id `be71dc8c-605a-4f69-a6d5-f7196521cba6` ｜ 來源 taoyuan_sw ｜ 類別 elderly_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人裝置假牙補助
- id `c0ecffc1-7a8b-4c12-bc8f-e8a2005bd8ef` ｜ 來源 taoyuan_sw ｜ 類別 elderly_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人住屋修繕補助
- id `e9a5bc19-009f-4ad6-8c5c-9fead718faaf` ｜ 來源 taoyuan_sw ｜ 類別 elderly_service ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 失能老人接受長期照顧機構服務
- id `f6ad368d-c183-4eae-b77d-25c2fef3dfa3` ｜ 來源 taoyuan_sw ｜ 類別 institutional_care_subsidy ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 住宿式服務機構使用者專案補助
- id `c7c1ea7a-4c32-481d-b4ed-ba9e233d55f6` ｜ 來源 taoyuan_sw ｜ 類別 institutional_care_subsidy ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 獨居老人服務
- id `1fb7cc4c-238e-4eaf-bfc8-bfb5d37c2217` ｜ 來源 taoyuan_sw ｜ 類別 elderly_service ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 老人緊急救援服務
- id `98d6be67-1d3c-4029-b02a-5115cfb606a3` ｜ 來源 taoyuan_sw ｜ 類別 elderly_service ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 老人營養送餐服務
- id `85bbfe3b-d44b-4a6e-bd36-0d8e9f31ac1e` ｜ 來源 taoyuan_sw ｜ 類別 meal_service ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收及中低收促進就業服務
- id `168a7162-f5dd-4703-a0c8-c9dd9f8187c3` ｜ 來源 taoyuan_sw ｜ 類別 low_income_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 外籍人士（持永久居留證）敬老卡
- id `fe677b9b-1af9-49ef-a4b0-03f5f20f6174` ｜ 來源 taoyuan_sw ｜ 類別 elderly_service ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 社區照顧關懷據點及巷弄長照站
- id `65b31cbd-f16a-47e9-b302-d82c2f7de78a` ｜ 來源 taoyuan_sw ｜ 類別 elderly_service ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region

### 預防走失愛的手鍊
- id `3da99b92-d52d-48fd-9c00-027c1ea74420` ｜ 來源 taoyuan_sw ｜ 類別 elderly_service ｜ 機關 桃園市政府社會局 ｜ 等級 verified
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 身心障礙者購買、租賃發電機或供電設備補助
- id `2f9869ee-7cd1-4b7d-8d2f-883670bc7dc4` ｜ 來源 taoyuan_sw ｜ 類別 disability_other ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 身障者搭乘救護車費用補助
- id `79f407e8-88a6-40e2-b077-44ee71585083` ｜ 來源 taoyuan_sw ｜ 類別 disability_other ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：於搭乘救護車之日起三個月內提出申請
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 身心障礙者搭乘捷運半價補助
- id `233b350b-a75c-4768-8ffe-17b301250838` ｜ 來源 taoyuan_sw ｜ 類別 disability_other ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：需持身分證正本或身心障礙證明正本
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 桃園至台北榮民總醫院就診專車
- id `3870d3f2-704c-4bf3-90b6-d6100adda968` ｜ 來源 taoyuan_sw ｜ 類別 transport_service ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；LLM 與另一方類別一致

### 老人保護
- id `ce7531ae-68da-492f-a58b-e1890e1a96d0` ｜ 來源 taoyuan_sw ｜ 類別 elderly_allowance ｜ 機關 桃園市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `region_missing` provider_region：機關是 桃園市政府社會局 但沒有 provider_region
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表
- `text_too_short` original_text：原文只有 198 字，難以判斷

### 重陽敬老金
- id `59080a97-d090-49b2-a204-9ae9f88398da` ｜ 來源 tainan_sw ｜ 類別 elderly_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺南市政府中低收入老人補助裝置假牙實施計畫
- id `3fc48ebe-19ae-4ce8-b626-4e0e31437043` ｜ 來源 tainan_sw ｜ 類別 elderly_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[6600, 7000, 9000, 22000, 33000, 44000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[6600, 7000, 9000, 22000, 33000, 44000]）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺南市政府居家安胎服務補助
- id `fca3fcd9-95a3-41d8-b657-ed393f1a5692` ｜ 來源 tainan_sw ｜ 類別 birth_incentive ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 臺南市危機家庭兒童托育費用補助
- id `2d2c616d-40ba-449b-a67d-ded417914524` ｜ 來源 tainan_sw ｜ 類別 childcare_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 補助托嬰中心及居家式托育服務提供者收托身心障礙暨疑似發展遲緩幼兒實施計畫
- id `027d467b-2b3c-48a4-b800-ee12eeaec907` ｜ 來源 tainan_sw ｜ 類別 childcare_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶高中職以上就學生活補助
- id `a8d31c5b-77b9-4e40-b08b-75aca34ae0d6` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶傷病住院看護費用補助
- id `584443e4-73e5-41ea-9650-faa8c1ef2da4` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶學生就學費用減免
- id `72b1445a-9c95-4951-9681-224b13fec0c8` ｜ 來源 tainan_sw ｜ 類別 education_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表
- `text_too_short` original_text：原文只有 193 字，難以判斷

### 低收入戶以工代賑
- id `0ed22337-5db6-46dc-9015-850daf2b9bb5` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 醫療補助（低收入戶及中低收入戶）
- id `be639a85-b885-44f9-8ab2-097fe747cd89` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入戶內兒童及少年健保費自付額全額補助
- id `fd21c58d-e861-4897-941d-a173e49587d9` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺南市弱勢兒童及少年醫療費用補助
- id `a0a3a46c-8a4a-4f68-9072-0b4d759b178e` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：於醫療行為或申請事項結束日起六個月內提出申請
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺南市經濟弱勢家庭兒童及少年生活扶助
- id `9d26c884-1c43-4870-aeef-93c27d6508de` ｜ 來源 tainan_sw ｜ 類別 low_income_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 特殊境遇家庭法律訴訟補助
- id `abe4afa1-3835-4e2e-816b-07736c5a8279` ｜ 來源 tainan_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：10000 不在原文可解析的金額中（原文金額：[38788, 50000, 465450, 6500000]）
- `amount_not_in_text` benefit.amount：10000 不在原文可解析的金額中（原文金額：[38788, 50000, 465450, 6500000]）

### 特殊境遇家庭子女教育補助
- id `97cd4533-f41d-416c-833e-cd4b884c3397` ｜ 來源 tainan_sw ｜ 類別 special_circumstances_aid ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人健保費自付額補助
- id `b89a3b5e-dce7-4e42-8509-db57028288ea` ｜ 來源 tainan_sw ｜ 類別 elderly_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人醫療補助
- id `76fe4138-d983-4d3c-a4bc-6612be89bf84` ｜ 來源 tainan_sw ｜ 類別 elderly_allowance ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供相關證明文件

### 敬老優惠措施
- id `d15b6c70-f642-4c77-a44c-0dfeb45ef4aa` ｜ 來源 tainan_sw ｜ 類別 elderly_service ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 永久居留外籍人士乘車敬老優惠
- id `73b9da28-71e8-4a4f-854c-6b6009a6b2ba` ｜ 來源 tainan_sw ｜ 類別 elderly_service ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 獨居老人在宅緊急救援服務
- id `da9be0c6-8be4-4229-a374-41f0874b7794` ｜ 來源 tainan_sw ｜ 類別 elderly_service ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者日間／住宿式照顧服務費用補助
- id `d1c3288c-b9c3-456a-a4a8-7f9b293d9d08` ｜ 來源 tainan_sw ｜ 類別 disability_care_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者房屋租金補貼及購屋貸款利息補貼
- id `6dc33b4e-25b0-49b3-9af8-69d006314f2b` ｜ 來源 tainan_sw ｜ 類別 rental_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 六十五歲以上身心障礙者全民健康保險自付保險費補助
- id `8ea67ee9-e9f8-4eb3-b5ed-586d3ebf6635` ｜ 來源 tainan_sw ｜ 類別 disability_other ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童及少年療育訓練費用補助
- id `2dea4edf-094f-45d9-97e0-4e27dad3645b` ｜ 來源 tainan_sw ｜ 類別 childcare_subsidy ｜ 機關 臺南市政府社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 基隆市生育獎勵金
- id `1a7a6727-33ae-4398-84ba-035efe8017ef` ｜ 來源 keelung_sw ｜ 類別 birth_incentive ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人須於新生兒出生後60日內提出申請

### 申請低收入戶、中低收入戶
- id `9e1aad13-c6d5-4792-a09e-4f75f4d3e0ab` ｜ 來源 keelung_sw ｜ 類別 low_income_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供相關文件

### 基隆市民眾急難救助
- id `f209f557-2ada-49d5-b1a6-1223427a9ef1` ｜ 來源 keelung_sw ｜ 類別 emergency_relief ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供急難事由證明文件

### 基隆市特殊境遇家庭扶助
- id `1deb873f-4be4-4721-9961-7d8a81b699f7` ｜ 來源 keelung_sw ｜ 類別 special_circumstances_aid ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人補助裝置假牙實施計畫
- id `527b83d1-b8d3-45ee-af8e-9821d0b6c277` ｜ 來源 keelung_sw ｜ 類別 elderly_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 老人參加全民健康保險保險費自付額補助
- id `ac5d1816-32bc-43a8-b04d-efcae6ebb43b` ｜ 來源 keelung_sw ｜ 類別 elderly_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 敬老三節慰問金
- id `a23e79d3-33b3-47ce-b583-ea18aaa7c7f2` ｜ 來源 keelung_sw ｜ 類別 elderly_allowance ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `category_title_conflict` category：標題含「慰問金」，預期 ['emergency_relief', 'low_income_allowance', 'medical_subsidy', 'special_circumstances_aid']，實際 elderly_allowance
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 基隆市115年低收入戶老人配戴助聽器計畫
- id `c89ea1fd-729d-4f6e-ac6d-3db28150ab89` ｜ 來源 keelung_sw ｜ 類別 assistive_device ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

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
- `obligation_not_in_text` benefit.obligations：需經醫師診斷並使用相關維生器材或生活輔具
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者三節慰問金
- id `5946606f-b74b-4c56-90d6-cc7b1f009893` ｜ 來源 keelung_sw ｜ 類別 disability_other ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_title_conflict` category：標題含「慰問金」，預期 ['emergency_relief', 'low_income_allowance', 'medical_subsidy', 'special_circumstances_aid']，實際 disability_other

### 身心障礙房屋租賃補助
- id `f24764cd-a76a-4ece-98b7-774b3e672a6b` ｜ 來源 keelung_sw ｜ 類別 rental_subsidy ｜ 機關 基隆市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙家庭照顧者支持服務
- id `a2600ea7-1238-4b7d-8f4a-02f17871f507` ｜ 來源 keelung_sw ｜ 類別 disability_other ｜ 機關 林社工為您服務。 ｜ 等級 verified
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 基隆市老人福利服務簡介
- id `cf1e0abe-199f-4546-b09b-3680a6e56753` ｜ 來源 keelung_sw ｜ 類別 elderly_service ｜ 機關 基隆市政府社會處長青及救助科 ｜ 等級 needs_review
- `text_too_short` original_text：原文只有 194 字，難以判斷

### 基隆市弱勢族群促進就業方案
- id `6115b439-31db-4263-8aea-70035d3e9a94` ｜ 來源 keelung_sw ｜ 類別 youth_employment ｜ 機關 基隆市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

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

### 新竹市育兒津貼加碼
- id `40764763-ad33-4234-bb26-d661a2f0df2f` ｜ 來源 hsinchu_city_sw ｜ 類別 child_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 兒童臨時托育費用補助
- id `5dbec2bd-333a-4028-a80c-a9be1de1f6cd` ｜ 來源 hsinchu_city_sw ｜ 類別 childcare_subsidy ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 兒童及少年醫療費用補助
- id `791cc33d-0c27-4bf0-9201-774bc264514a` ｜ 來源 hsinchu_city_sw ｜ 類別 medical_subsidy ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 新竹市115年度設籍前新住民社會救助計畫
- id `60d8bf40-3e50-4099-9063-2f360832c9e6` ｜ 來源 hsinchu_city_sw ｜ 類別 low_income_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `amount_is_threshold` benefit.amount.description：2.中低收入戶 ： 自行負擔費用超過新台幣2 萬元整者 ， 補
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 愛老津貼
- id `d81577a8-62f6-4598-a31d-3d53bcead6e1` ｜ 來源 hsinchu_city_sw ｜ 類別 elderly_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 安老津貼
- id `472fc7c2-8ddd-4d3d-ad44-e080933b7ef5` ｜ 來源 hsinchu_city_sw ｜ 類別 elderly_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人租賃房屋租金補助
- id `2641cb0d-9622-4102-94dc-fdd16fe68407` ｜ 來源 hsinchu_city_sw ｜ 類別 rental_subsidy ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請者應於期滿一個月內重新申請。補助期間內租賃房屋如有變更時，受補助人應於變更後一個月內，檢附新租賃契約重新申請。
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 重陽節敬老禮金
- id `333463f3-9ced-45ed-9710-4c3ada95ad93` ｜ 來源 hsinchu_city_sw ｜ 類別 elderly_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者租賃房屋租金及購屋貸款利息補貼
- id `15e00929-8b35-4908-97b6-40e371514c08` ｜ 來源 hsinchu_city_sw ｜ 類別 rental_subsidy ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者健康保險及社會保險自付額保費補助
- id `97c7cb01-039d-4e7c-a2d0-f0d48bbb71cf` ｜ 來源 hsinchu_city_sw ｜ 類別 disability_other ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者社區居住服務
- id `b738fc5a-368f-455f-bf3e-550b64f04c8c` ｜ 來源 hsinchu_city_sw ｜ 類別 disability_other ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者緊急救援服務
- id `1f0dfc86-a9a7-4b55-986a-2cf689a49a42` ｜ 來源 hsinchu_city_sw ｜ 類別 disability_other ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者婚姻、生育輔導及心理重建服務
- id `dfce115c-5d32-4114-9a28-ed858224bfe5` ｜ 來源 hsinchu_city_sw ｜ 類別 disability_other ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 社區日間作業設施服務
- id `80246a73-9173-47ea-a8cf-acde6d493bbd` ｜ 來源 hsinchu_city_sw ｜ 類別 disability_other ｜ 機關 財團法人福榮融合教育推廣基金會 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 低收入戶喪葬費補助
- id `36138961-c151-4f77-957c-a994a196c203` ｜ 來源 hsinchu_city_sw ｜ 類別 low_income_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請者不得重覆申領其他喪葬費用補助。

### 低收入戶全民健康保險補助
- id `1789926d-ebdc-45f5-9156-bbe4ece6005f` ｜ 來源 hsinchu_city_sw ｜ 類別 low_income_allowance ｜ 機關 新竹市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 189 字，難以判斷

### 新竹市生育津貼
- id `c78bdae8-5ded-4eb0-b197-590bd0af47f5` ｜ 來源 hsinchu_city_sw ｜ 類別 birth_incentive ｜ 機關 新竹市政府民政處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 新竹縣新生兒營養補助
- id `1078d239-20eb-4366-87d5-3f75d2d21737` ｜ 來源 hsinchu_county_sw ｜ 類別 birth_incentive ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 未滿二歲(延長二至三歲)兒童托育費用補助
- id `39188fc1-466c-4d2f-9d5e-7f157c29d481` ｜ 來源 hsinchu_county_sw ｜ 類別 childcare_subsidy ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：提供相關證明文件
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童早期療育費用補助
- id `64f87a9d-b0df-4189-ae12-30d01de13972` ｜ 來源 hsinchu_county_sw ｜ 類別 childcare_subsidy ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 新竹縣政府低/中低收入戶就業獎勵補助計畫
- id `5c5ccdac-592d-4d43-be15-f16b44a8d1f5` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需配合社工員訪視
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年度低收入戶及中低收入戶電腦設備購置補助計畫
- id `e6bb3b95-0d7b-44b9-af10-77b5a1cbd3c1` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 所要求之資料。 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低/中低收入戶微型火災不便費用保險
- id `e334cfa2-0cd8-407c-8334-27e89d6e2a12` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 低收入戶及中低收入戶家庭自立脫貧-希望存摺投資方案
- id `a9541512-e9df-40da-b63b-6c37cc8d718b` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 兒童與少年未來教育及發展帳戶
- id `cc19cd12-355d-45a7-8a6b-bfe903c62468` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 新竹縣以工代賑實施計畫
- id `812a8352-5683-41d1-8bc2-a60a090cd249` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：需具工作能力及意願，能勝任招募單位派任工作
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 川資（車資返鄉）救助
- id `acf38407-1842-4a05-85dd-92df43635847` ｜ 來源 hsinchu_county_sw ｜ 類別 emergency_relief ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 新竹縣社勞政聯合促進低收入戶及中低收入戶 就業服務指引
- id `31618e40-5f64-41bf-b804-16274958979a` ｜ 來源 hsinchu_county_sw ｜ 類別 youth_employment ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 『役』起前進，『竹』夢踏實 新竹縣政府辦理低收入戶及中低收入戶自立脫貧計畫
- id `24c48b1d-dff6-46a0-b08f-d57a382c6e1a` ｜ 來源 hsinchu_county_sw ｜ 類別 low_income_allowance ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 財團法人達成慈善基金會-施棺專案
- id `70a04949-c61b-4178-bc5d-d2184b3f688a` ｜ 來源 hsinchu_county_sw ｜ 類別 emergency_relief ｜ 機關 新竹縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 實物銀行
- id `adaef226-2265-4a53-b9b1-772b866b87c6` ｜ 來源 hsinchu_county_sw ｜ 類別 emergency_relief ｜ 機關 新竹縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 苗栗縣113年生育津貼（民政處）
- id `485bf518-d13a-4fb2-a70b-bd01e3f7619d` ｜ 來源 miaoli_sw ｜ 類別 birth_incentive ｜ 機關 民政處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 未滿二歲兒童托育準公共化服務費用申報
- id `d5d3cf44-0827-43ca-91d8-aa588c5b8a34` ｜ 來源 miaoli_sw ｜ 類別 childcare_subsidy ｜ 機關 婦幼發展及平權科 ｜ 等級 verified
- `provider_is_division` provider：婦幼發展及平權科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 苗栗縣低收入戶及中低收入戶傷病住院看護費用補助
- id `1f1e6306-6db7-4c18-8d8e-fc32bd0fbda1` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 救助及專業發展科 ｜ 等級 verified
- `provider_is_division` provider：救助及專業發展科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 苗栗縣低收及中低收入戶傷病醫療費用補助（醫療補助審核作業規定）
- id `dbf5e47a-5d2f-47b1-89b2-dc3860de2229` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 救助及專業發展科 ｜ 等級 verified
- `provider_is_division` provider：救助及專業發展科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 急難紓困(原馬上關懷)、急難救助
- id `5b72299a-9598-4233-b190-606b1a1e553c` ｜ 來源 miaoli_sw ｜ 類別 emergency_relief ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 苗栗縣弱勢家庭兒童及少年緊急生活扶助補助
- id `0c1af7d6-568e-4d4b-8807-187e054caff5` ｜ 來源 miaoli_sw ｜ 類別 emergency_relief ｜ 機關 救助及專業發展科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：救助及專業發展科

### 115年苗栗縣敬老禮金
- id `501fd6f7-2677-40f4-b178-606627b6c579` ｜ 來源 miaoli_sw ｜ 類別 elderly_allowance ｜ 機關 老人福利科 ｜ 等級 verified
- `provider_is_division` provider：老人福利科

### 苗栗縣政府老人聲請監護輔助宣告補助實施計畫
- id `347d3c03-a42a-48bc-ad66-7a88f9ffa245` ｜ 來源 miaoli_sw ｜ 類別 elderly_allowance ｜ 機關 老人福利科 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需檢附相關申請文件
- `provider_is_division` provider：老人福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 苗栗縣敬老愛心卡
- id `b596e4bd-869d-462d-8eae-b84f60e2a915` ｜ 來源 miaoli_sw ｜ 類別 elderly_service ｜ 機關 老人及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：老人及身障福利科

### 苗栗縣愛心手鍊預防走失服務計畫
- id `c6a19735-cca5-4dcd-9c6b-1e098a7799e2` ｜ 來源 miaoli_sw ｜ 類別 elderly_service ｜ 機關 老人福利科 ｜ 等級 verified
- `provider_is_division` provider：老人福利科
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 苗栗縣低(中)低收入戶住屋災害保險申請須知
- id `69c32a1c-633d-4a26-a667-48aeca933428` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 救助及專業發展科 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人需為列冊低收入戶或中低收入戶，且需提供相關證明文件。
- `provider_is_division` provider：救助及專業發展科

### 苗栗縣辦理兒少生活扶助實施計畫
- id `ddbab147-0d3f-402c-904b-f163a02bc802` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 苗栗縣辦理低收入戶暨弱勢兒童及少年醫療補助審查及作業規定
- id `d855bd29-15d7-4220-88e7-6426265d875d` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 苗栗縣實(食)物銀行計畫
- id `491a020a-f47b-4c48-a6ea-3f7d1722649d` ｜ 來源 miaoli_sw ｜ 類別 emergency_relief ｜ 機關 救助及專業發展科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：救助及專業發展科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 苗栗縣未滿20歲懷孕青少女產檢暨產後就醫車資補助計畫
- id `d0afbdda-60c2-4cb4-86f9-ff90ea5ada07` ｜ 來源 miaoli_sw ｜ 類別 birth_incentive ｜ 機關 婦幼發展及平權科 ｜ 等級 verified
- `provider_is_division` provider：婦幼發展及平權科

### 苗栗縣國民年金被保險人所得未達一定標準申請
- id `bf99499c-443d-4aa8-9c65-3760afb43de9` ｜ 來源 miaoli_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 老人福利科 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `provider_is_division` provider：老人福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 苗栗縣身心障礙者微型傷害保險
- id `e2d64a3f-39f2-47e3-bfe5-a79e1c2bec3a` ｜ 來源 miaoli_sw ｜ 類別 disability_other ｜ 機關 救助及專業發展科 ｜ 等級 verified
- `provider_is_division` provider：救助及專業發展科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 視覺障礙者生活重建及生活訓練服務
- id `8729a01f-e6f7-426b-b4f2-03a7237e228a` ｜ 來源 miaoli_sw ｜ 類別 disability_other ｜ 機關 老人及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：老人及身障福利科

### 苗栗縣辦理低收入戶與中低收入戶產婦及新生兒營養補助實施計畫(114修)
- id `2646c7db-460c-4e8d-92e7-bc9f668590c8` ｜ 來源 miaoli_sw ｜ 類別 low_income_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供相關證明文件
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人生活津貼發給辦法
- id `7f13f66c-910d-40be-86e2-7756a8b3ddaa` ｜ 來源 miaoli_sw ｜ 類別 elderly_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人特別照顧津貼發給辦法
- id `8452b08f-75ee-4cd1-9f1c-921ad21a4a35` ｜ 來源 miaoli_sw ｜ 類別 elderly_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 苗栗縣中低收入老人重病住院看護費用補助計畫
- id `8b15b055-8af2-4daf-8a0a-c546dcce8b16` ｜ 來源 miaoli_sw ｜ 類別 elderly_allowance ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 苗栗縣低收入戶老人配戴助聽器補助計畫
- id `d00e9fb5-c092-4a07-baab-87c16d5def94` ｜ 來源 miaoli_sw ｜ 類別 assistive_device ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 苗栗縣政府辦理身心障礙者房屋租金補貼作業要點
- id `c8c72532-ada9-430d-9afa-6d0c16c830d6` ｜ 來源 miaoli_sw ｜ 類別 rental_subsidy ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 苗栗縣身心障礙者消耗性用品補助要點
- id `a26b8b0a-1edd-4795-a074-78a89412f52b` ｜ 來源 miaoli_sw ｜ 類別 disability_other ｜ 機關 苗栗縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年苗栗縣兒童早期療育費用補助實施計畫
- id `82734490-490b-4af1-9c10-67d99e2b496e` ｜ 來源 miaoli_sw ｜ 類別 social_welfare ｜ 機關 苗栗縣政府(以下簡稱本府)。 ｜ 等級 needs_review
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 彰化縣政府生育補助
- id `19dd0fba-4a57-4742-9e92-1c335b30de6c` ｜ 來源 changhua_sw ｜ 類別 birth_incentive ｜ 機關 社會處婦女及新住民福利科 吳辦事員 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人應於新生兒出生之日起3個月內提出申請

### 設籍前新住民遭逢特殊境遇家庭扶助
- id `2b64948e-0ba8-4a13-bc80-67edc6bb5d0f` ｜ 來源 changhua_sw ｜ 類別 special_circumstances_aid ｜ 機關 社會處婦女及新住民福利科 吳辦事員 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 低收入戶暨寄養家庭兒童托育津貼
- id `3b4c4d5b-880a-4498-a3fe-77db778bc3cf` ｜ 來源 changhua_sw ｜ 類別 childcare_subsidy ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 發展遲緩兒童早期療育費用補助
- id `15d3ba67-1f4f-427a-950d-57f4d2c48d07` ｜ 來源 changhua_sw ｜ 類別 disability_care_subsidy ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者房屋租金補貼
- id `dead647e-c8f2-493b-bb88-3e8044dd428a` ｜ 來源 changhua_sw ｜ 類別 rental_subsidy ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者(中)低收入戶裝置假牙費用補助
- id `2be7e1a6-4af9-4243-8876-4c4bdee974ae` ｜ 來源 changhua_sw ｜ 類別 disability_other ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者購置停車位貸款利息補貼或承租停車位補助
- id `1660c2b4-8ba6-4da6-b075-d360b013617d` ｜ 來源 changhua_sw ｜ 類別 disability_other ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 彰化縣長青幸福卡申辦暨補助項目
- id `6ee8b9dc-31fa-4e9a-8c2f-badd194adbee` ｜ 來源 changhua_sw ｜ 類別 elderly_service ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[79]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[79]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[79]）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人住宅設施設備補助
- id `6dff71b5-3568-4f6f-acf3-6d13f7eb89ca` ｜ 來源 changhua_sw ｜ 類別 elderly_service ｜ 機關 受理申請單位 ｜ 等級 verified
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 低收入戶老人公費安養護補助
- id `5ecd15cc-8230-4e7e-baeb-940e63d83bec` ｜ 來源 changhua_sw ｜ 類別 institutional_care_subsidy ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶及中低收入老人裝置假牙補助
- id `4e50b62f-fc8d-46b6-af48-0b9f4a5991ff` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 65歲以上老人裝置全口活動假牙補助
- id `5896b4e9-477c-4f67-bab7-e33c08dd8dc4` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 本縣各鄉鎮市公所、本府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶補助
- id `5c819b9c-a89f-4cf9-88d7-06f19b5d12f7` ｜ 來源 changhua_sw ｜ 類別 low_income_allowance ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：5000 不在原文可解析的金額中（原文金額：[15515, 95000, 3730000]）
- `amount_not_in_text` benefit.amount：5000 不在原文可解析的金額中（原文金額：[15515, 95000, 3730000]）

### 彰化縣敬老眼鏡
- id `cb69848a-02ff-4df3-a454-6cea21a5583c` ｜ 來源 changhua_sw ｜ 類別 elderly_service ｜ 機關 受理申請單位 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 防走失愛心手鍊
- id `c3d68ecb-486b-4e33-a18f-6c010ac853ea` ｜ 來源 changhua_sw ｜ 類別 elderly_service ｜ 機關 社會處長青福利科 黃社工員 ｜ 等級 needs_review
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 獨居老人關懷訪視及電話問安服務
- id `2cbb70db-bfcc-4ac2-abf8-2cedce6610a3` ｜ 來源 changhua_sw ｜ 類別 elderly_service ｜ 機關 各鄉鎮市公所社會課或民政課、本府社會處 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臨時托育服務
- id `3b733012-3043-4490-8df6-66b43beff2c9` ｜ 來源 changhua_sw ｜ 類別 childcare_subsidy ｜ 機關 社會處兒少科 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 改善低收入戶住宅設施設備補助
- id `391ff950-c12e-4739-b75a-54223ccb40ab` ｜ 來源 changhua_sw ｜ 類別 low_income_allowance ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需提交全戶戶籍謄本、低收入戶證明書等文件

### 油症患者喪葬補助
- id `4371052a-6f35-4c42-bdaa-4c6d70c2dfe5` ｜ 來源 changhua_sw ｜ 類別 special_circumstances_aid ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請書及領款收據需正本，其他文件可提供影本。
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 國保生育給付加給補助至10萬元
- id `71f7e1d2-3ad2-4748-b00c-5e4926cdc1ab` ｜ 來源 changhua_sw ｜ 類別 birth_incentive ｜ 機關 彰化縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 「資產累積、築夢心希望」家庭發展帳戶脫貧計畫
- id `89611856-1f53-4256-b7dc-e64ff2f330cb` ｜ 來源 changhua_sw ｜ 類別 low_income_allowance ｜ 機關 彰化縣政府 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人健保費補助
- id `b130ae23-d4c0-4713-a2f3-e03beb8c8992` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：中低收入老人生活津貼申領資格消失時，本項健保費自付額補助亦隨停止發放，如有溢領者應即追繳。
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 彰化縣重陽敬老禮金
- id `bf77f49f-200f-4b3a-95b3-3ef1f115db13` ｜ 來源 changhua_sw ｜ 類別 elderly_allowance ｜ 機關 (一)社會處長青福利科 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶老人配戴助聽器補助
- id `352c305b-0287-4d39-8ade-17564fd10dab` ｜ 來源 changhua_sw ｜ 類別 assistive_device ｜ 機關 (一)社會處長青福利科 黃社工師 電話(04)753-2337 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需檢附6個月內經健保合約醫療院所開立之診斷證明書及聽力圖正本
- `provider_looks_like_contact` provider：(一)社會處長青福利科 黃社工師 電話(04)753-2337
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 身心障礙者監護及輔助宣告補助
- id `c5a359f2-fc7a-42fb-9b0d-c2ac14e37c19` ｜ 來源 changhua_sw ｜ 類別 disability_other ｜ 機關 彰化縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣生育獎勵金發放作業要點
- id `516bf5fd-e005-44cf-9f2d-8193e4ec704c` ｜ 來源 nantou_sw ｜ 類別 birth_incentive ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣中低收入老人生活津貼審核作業辦法
- id `4083c39f-906f-491f-9a2e-ef2645994ffd` ｜ 來源 nantou_sw ｜ 類別 elderly_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣重陽節敬老禮金發放作業規定
- id `cad9e0c6-89eb-495d-8adc-98f27698c827` ｜ 來源 nantou_sw ｜ 類別 elderly_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣辦理重陽節敬老禮金禮券發放實施要點
- id `61e784f3-95b8-403c-8f5e-bad1ca4e2ba6` ｜ 來源 nantou_sw ｜ 類別 elderly_allowance ｜ 機關 為本府，協辦單位為本縣各鄉（鎮、市）公所(以 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣弱勢家庭老人住宅修繕補助辦法
- id `6e38bc74-0e0a-4220-b40d-f1d55a08d9ca` ｜ 來源 nantou_sw ｜ 類別 elderly_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣低收入戶老人公費安養補助作業要點
- id `9a2bcb0b-a4b5-4116-99ee-eb2b0272ac42` ｜ 來源 nantou_sw ｜ 類別 institutional_care_subsidy ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣低收入戶老人公費養護作業規定
- id `b9c05665-6056-4c33-ad98-5622cdf54e10` ｜ 來源 nantou_sw ｜ 類別 institutional_care_subsidy ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣營養餐飲服務補助計畫
- id `357ef3ff-bb46-4600-bdfb-5f591b7c32f7` ｜ 來源 nantou_sw ｜ 類別 meal_service ｜ 機關 以電話或傳真通知於7日內補齊，逾期未補或補正不 ｜ 等級 verified
- `provider_looks_like_contact` provider：以電話或傳真通知於7日內補齊，逾期未補或補正不

### 南投縣兒童及少年生活扶助審核作業規定
- id `50f2f1e9-a93b-4beb-a230-413ecb584c21` ｜ 來源 nantou_sw ｜ 類別 low_income_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣政府弱勢家庭兒童少年緊急生活扶助補助及核發作業規定
- id `31722b77-d542-4267-9426-043a2a5cd5b3` ｜ 來源 nantou_sw ｜ 類別 emergency_relief ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣政府社會及勞動局辦理發展遲緩兒童早期療育費用補助計畫
- id `da288cde-acc2-4e98-9b61-3a75f2e39517` ｜ 來源 nantou_sw ｜ 類別 medical_subsidy ｜ 機關 南投縣政府社會及勞動局（以下簡稱本局） 。 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 南投縣特殊境遇家庭扶助補助標準及應備文件
- id `1c13604f-8971-4b4b-bf23-246ec24de3af` ｜ 來源 nantou_sw ｜ 類別 special_circumstances_aid ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣身心障礙者房屋租金補貼作業要點
- id `952c4515-ec79-4466-8050-56ec428bf88c` ｜ 來源 nantou_sw ｜ 類別 rental_subsidy ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣政府辦理身心障礙者參加社會保險保險費補助作業規定
- id `9ce26d22-a4c7-435c-88d8-80e5c82ed74a` ｜ 來源 nantou_sw ｜ 類別 disability_other ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣身心障礙者臨時及短期照顧服務補助計畫
- id `f8ce93d8-af74-48fc-a7b5-005b0a0c7629` ｜ 來源 nantou_sw ｜ 類別 respite_care ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣政府急難救助申請作業應備文件及程序
- id `46c64be1-ce17-4d2a-a5e5-54bfa264b408` ｜ 來源 nantou_sw ｜ 類別 emergency_relief ｜ 機關 社會及勞動局（ 社會救助科） ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 南投縣政府醫療補助審核作業規定（低收入戶及中低收入戶傷病醫療補助）
- id `b10978fe-b901-42d9-865e-8188340cee5d` ｜ 來源 nantou_sw ｜ 類別 low_income_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 南投縣辦理傷病看護費用補助實施計劃（低收入戶及中低收入戶）
- id `43ded9f6-f5bc-4af6-9524-15f1c3b87497` ｜ 來源 nantou_sw ｜ 類別 low_income_allowance ｜ 機關 南投縣政府社會及勞動局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市生育津貼
- id `d0ba2cb9-89c7-4456-b0b6-fba27bce9d37` ｜ 來源 chiayi_city_sw ｜ 類別 birth_incentive ｜ 機關 兒少及婦女福利科 ｜ 等級 verified
- `provider_is_division` provider：兒少及婦女福利科

### 未滿二歲兒童托育公共化及準公共托育費用補助
- id `1ae31273-bf5a-44d4-8101-e9fff7bfe2b1` ｜ 來源 chiayi_city_sw ｜ 類別 childcare_subsidy ｜ 機關 兒少及婦女福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：兒少及婦女福利科

### 嘉義市中低收入戶
- id `7262aa53-999f-44f2-99f4-8432ed5d7cfb` ｜ 來源 chiayi_city_sw ｜ 類別 low_income_allowance ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科

### 嘉義市急難救助
- id `3beec795-e520-4605-b0be-e43032ee8c65` ｜ 來源 chiayi_city_sw ｜ 類別 emergency_relief ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 65-69歲中低收入老人健保補助
- id `de1b159c-c9f5-4acf-8586-9d1c11a5d7de` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市政府80歲以上老人全民健康保險自付保險費補助試辦計畫
- id `f5d08b1f-950c-42c8-83a2-1685b87580aa` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科

### 115年度「中低收入老人」補助裝置假牙計畫
- id `5a6ca649-17d7-486d-b5aa-da51bab0c628` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 長青及社會行政科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：長青及社會行政科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年度「一般身分別老人」補助裝置假牙計畫
- id `00f1967e-0a43-43c8-ba73-6ea1b1a923e0` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 長青及社會行政科 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：需攜帶申請人身分證及戶籍謄本至本府社會處申請
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：長青及社會行政科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市百歲人瑞營養禮金發放作業要點
- id `82c21d9e-de62-4b1c-a6cf-7a35eacffb10` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義市政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人修繕住屋補助
- id `4500ae98-54ae-426a-a2fd-d43876e255c8` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_allowance ｜ 機關 長青及社會行政科 ｜ 等級 verified
- `category_title_conflict` category：標題含「修繕」，預期 ['disability_other', 'housing_loan_subsidy', 'housing_support', 'social_housing']，實際 elderly_allowance
- `provider_is_division` provider：長青及社會行政科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人免費配戴老花眼鏡補助
- id `a31064e8-7cfe-481b-b322-88dce6ac32ce` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 長青及社會行政科 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：1 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：1 不在原文可解析的金額中（原文金額：[]）
- `provider_is_division` provider：長青及社會行政科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 低收入戶老人助聽器補助
- id `73d2c4a3-3b8e-4d68-8b4e-47afd1913d6c` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 長青及社會行政科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：長青及社會行政科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中、低收入戶失能老人機構公費安置
- id `02be8f71-657a-44c4-a7d4-8c2098f30325` ｜ 來源 chiayi_city_sw ｜ 類別 institutional_care_subsidy ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科

### 老人暨身心障礙者免費乘車補助（敬老、愛心悠遊卡）
- id `bc57f8f1-bc8a-4124-9e37-29b115e73372` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_service ｜ 機關 長青及社會行政科 ｜ 等級 verified
- `provider_is_division` provider：長青及社會行政科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 關懷獨居老人服務
- id `76787833-7b37-491b-94ab-6390979dd669` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_service ｜ 機關 長青及社會行政科 ｜ 等級 verified
- `provider_is_division` provider：長青及社會行政科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市115年獨居老人居家安全設備裝置計畫
- id `bd1fef3a-bf6e-4773-9f72-0e6e49df15d0` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_service ｜ 機關 長青及社會行政科 ｜ 等級 verified
- `provider_is_division` provider：長青及社會行政科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市115年獨居老人居家用電安全檢測及照明修繕汰換計畫
- id `1a3a10cd-c5bc-4f08-b117-bc4b70b6023f` ｜ 來源 chiayi_city_sw ｜ 類別 elderly_service ｜ 機關 長青及社會行政科 ｜ 等級 verified
- `category_title_conflict` category：標題含「修繕」，預期 ['disability_other', 'housing_loan_subsidy', 'housing_support', 'social_housing']，實際 elderly_service
- `provider_is_division` provider：長青及社會行政科

### 短缺川資補助
- id `e8853680-a8e9-4a5c-99e3-e1061a38cabb` ｜ 來源 chiayi_city_sw ｜ 類別 emergency_relief ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 187 字，難以判斷

### 低收入戶微型火災保險（微型住宅綠能保險）
- id `0ab2f645-3131-4c4a-9592-2359b782e215` ｜ 來源 chiayi_city_sw ｜ 類別 low_income_allowance ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 弱勢家庭微型團體傷害保險
- id `0da5af1b-12e6-4285-87bb-148f36196106` ｜ 來源 chiayi_city_sw ｜ 類別 low_income_allowance ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 嘉義市實物銀行
- id `68bdc16b-51bd-4965-8686-825f520ef0d0` ｜ 來源 chiayi_city_sw ｜ 類別 emergency_relief ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 以工代賑實施計畫
- id `1960cd9f-a457-4a7b-b420-da9dabb9409b` ｜ 來源 chiayi_city_sw ｜ 類別 low_income_allowance ｜ 機關 救助及身障福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：救助及身障福利科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 兒童少年生活扶助
- id `7854fc8e-87e1-41fe-8cd5-dcf141926ee5` ｜ 來源 chiayi_city_sw ｜ 類別 special_circumstances_aid ｜ 機關 兒少及婦女福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：兒少及婦女福利科

### 嘉義市115年度「嘉有好孕」乘車補助計畫
- id `540425df-60d1-473a-b6ee-2ae8ca4613f0` ｜ 來源 chiayi_city_sw ｜ 類別 birth_incentive ｜ 機關 兒少及婦女福利科 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人須為設籍本市之孕婦，並實際居住於本市。
- `provider_is_division` provider：兒少及婦女福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義市到宅坐月子服務
- id `43755afb-1691-4840-bd55-352ec8e22390` ｜ 來源 chiayi_city_sw ｜ 類別 home_care ｜ 機關 兒少及婦女福利科 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `provider_is_division` provider：兒少及婦女福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 嘉義市育兒照顧喘息服務
- id `953c01af-c237-44fc-883d-9cc90aa52090` ｜ 來源 chiayi_city_sw ｜ 類別 childcare_subsidy ｜ 機關 兒少及婦女福利科 ｜ 等級 verified
- `provider_is_division` provider：兒少及婦女福利科

### 嘉義市育兒指導服務方案
- id `3b410edb-7b73-484c-ac90-bd167f668deb` ｜ 來源 chiayi_city_sw ｜ 類別 childcare_subsidy ｜ 機關 兒少及婦女福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：兒少及婦女福利科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者輔助器具補助
- id `8b5e4dee-ed6e-4f0b-83d1-660fbd635921` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 嘉義市政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 輔助器具免費借用、回收及維修
- id `7a6505fa-1de2-4b79-91fa-03b98747e36f` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 救助及身障福利科 ｜ 等級 needs_review
- `provider_is_division` provider：救助及身障福利科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 嘉義市115年身心障礙者育兒輔具費用補助
- id `b579e0e3-511c-4ece-8d32-7853ad260c2e` ｜ 來源 chiayi_city_sw ｜ 類別 assistive_device ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：收到核定函6個月內檢附文件申請核銷撥款
- `provider_is_division` provider：救助及身障福利科

### 身心障礙者臨時暨短期照顧服務
- id `93803e3d-44b7-48bf-8b92-092a536d4b87` ｜ 來源 chiayi_city_sw ｜ 類別 respite_care ｜ 機關 網路事業部 ｜ 等級 verified
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 嘉義市身心障礙者復康巴士交通服務
- id `850fae5c-9868-4c3d-a8b8-bf0dc3cea513` ｜ 來源 chiayi_city_sw ｜ 類別 transport_service ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科

### 身心障礙者在宅緊急救援服務
- id `161f2688-80c3-42af-a279-d0c939686dd2` ｜ 來源 chiayi_city_sw ｜ 類別 disability_other ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者自立生活支持服務
- id `8333b6f0-1471-4851-aa56-6666c720d819` ｜ 來源 chiayi_city_sw ｜ 類別 disability_other ｜ 機關 救助及身障福利科 ｜ 等級 verified
- `provider_is_division` provider：救助及身障福利科
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙學生、身心障礙人士及低收入戶子女就學減免、補助學雜費
- id `1573bc6b-129d-4c00-948d-5a01d026541d` ｜ 來源 chiayi_city_sw ｜ 類別 education_subsidy ｜ 機關 嘉義市政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需提交身心障礙手冊(證明)影本、戶口名簿影本、低收入戶證明（無則免附）

### 勞保生育給付（含勞工生育補助）— 請領資格
- id `69c51a10-1276-4db2-90a7-0f6b1ac9cedb` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 勞保生育給付（含勞工生育補助）— 給付標準
- id `9c534850-3c2b-4a27-adc2-55bfba56cf38` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表
- `text_too_short` original_text：原文只有 196 字，難以判斷

### 勞工生育補助要點（勞保生育給付加計補助至10萬元）
- id `9d9babbb-9db0-46a6-a6b4-5f2eec07fc4c` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 就保育嬰留職停薪津貼 — 請領資格
- id `ea7cf67d-0bb0-4dec-8400-c3b74b271fc5` ｜ 來源 bli_family ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 就保育嬰留職停薪津貼 — 給付標準及期間
- id `b45893ad-d330-432d-88dc-a55964e2da01` ｜ 來源 bli_family ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提前復職或離職需通知停發

### 育嬰留職停薪薪資補助（政府加發20%）— 補助方式
- id `28c504f7-074e-4821-9c78-b953ce86ee1f` ｜ 來源 bli_family ｜ 類別 parental_leave_allowance ｜ 機關 勞動部勞工保險局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 160 字，難以判斷

### 農保生育給付
- id `84897059-547e-45b6-a114-50e088e6d265` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：須在分娩或早產之日起5年內提出申請

### 農民健康保險生育給付加給補助要點
- id `96ce60c9-8bc5-47ad-94fb-e7f161004d94` ｜ 來源 bli_family ｜ 類別 birth_incentive ｜ 機關 勞動部勞工保險局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 桃園市中壢區公所急難救助申請應備文件表
- id `5227e09b-f5cd-46c8-95f6-bf52d5c33f9b` ｜ 來源 taoyuan_zhongli_office ｜ 類別 emergency_relief ｜ 機關 桃園市中壢區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 桃園市生育津貼發放作業要點申請說明（含申請表）
- id `6d3f5139-4fd2-4893-9fea-a1bfb69fb8f2` ｜ 來源 taoyuan_zhongli_office ｜ 類別 birth_incentive ｜ 機關 桃園市中壢區公所 ｜ 等級 verified
- `rule_city_conflict` residence.household_city：規則城市 ['臺北市', '新北市', '基隆市'] 與機關／標題 ['桃園市', '桃園市'] 不同
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 災害救助
- id `cb248968-7803-4290-9bdf-04c79279b36b` ｜ 來源 tainan_east_office ｜ 類別 emergency_relief ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 臺南市育有未滿二歲兒童育兒津貼
- id `435f24bb-6230-43c6-ab4f-2ef5709ccfc0` ｜ 來源 tainan_east_office ｜ 類別 child_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺南市二歲以上未滿五歲幼兒育兒津貼
- id `0de9fdc4-437c-47f4-a016-7ea1f8c690e2` ｜ 來源 tainan_east_office ｜ 類別 child_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 臺南市5歲至入國民小學前幼兒就學補助
- id `8900222d-b539-4e76-a86f-78c8b4414b70` ｜ 來源 tainan_east_office ｜ 類別 education_subsidy ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 低收入戶家庭生活補助
- id `7b993d29-4856-4e49-9caf-71c4e40ef986` ｜ 來源 tainan_east_office ｜ 類別 low_income_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 傷病醫療補助
- id `9fae8991-0c84-48db-a562-e47a39c07e34` ｜ 來源 tainan_east_office ｜ 類別 low_income_allowance ｜ 機關 臺南市東區區公所 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 低收入戶收容
- id `64b6624c-1b84-4a2c-bf7f-38b52d971d73` ｜ 來源 tainan_east_office ｜ 類別 institutional_care_subsidy ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者托育養護補助
- id `0e46e07f-466e-47a3-93d5-df71a4e404db` ｜ 來源 tainan_east_office ｜ 類別 disability_care_subsidy ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_title_conflict` category：標題含「托育」，預期 ['child_allowance', 'childcare_subsidy']，實際 disability_care_subsidy
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 平民安葬救助金申請
- id `0d1a8294-d6c7-4801-b2ee-c034a7728c6c` ｜ 來源 tainan_east_office ｜ 類別 emergency_relief ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 原住民急難救助
- id `44b7fb89-e811-4861-bdd5-b4196f18f03d` ｜ 來源 tainan_east_office ｜ 類別 emergency_relief ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 原住民學生獎助學金
- id `26e47940-b251-495d-962b-bc7b6a4e8e92` ｜ 來源 tainan_east_office ｜ 類別 scholarship ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 原住民建構及修繕住宅補助
- id `f1e71ad2-96ff-4130-ae2d-429cdb771911` ｜ 來源 tainan_east_office ｜ 類別 housing_support ｜ 機關 臺南市東區區公所 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 各項業務查詢（第 3 頁）
- id `49a7efe7-213e-4376-94dc-13caae034daa` ｜ 來源 tainan_east_office ｜ 類別 emergency_aid_student ｜ 機關 臺南市東區區公所 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 5歲至入國民小學前幼兒就學補助（未就讀平價教保服務機構）
- id `54218a66-2362-4251-9962-772604e04bbd` ｜ 來源 ece_moe ｜ 類別 education_subsidy ｜ 機關 教育部國民及學前教育署 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需就讀一般私立教保服務機構
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 公立及非營利幼兒園幼兒就學補助（家長每月繳費上限、政府協助支付差額、低收與中低收入家庭子女免費）
- id `49ab5908-dccf-4827-9011-533c378a817d` ｜ 來源 ece_moe ｜ 類別 education_subsidy ｜ 機關 教育部國民及學前教育署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 準公共幼兒園幼兒就學補助（家長每月繳費上限、政府協助支付差額、低收與中低收入家庭子女免費）
- id `aee11f67-437b-4bf2-9eab-4fa5d00a1f8a` ｜ 來源 ece_moe ｜ 類別 education_subsidy ｜ 機關 教育部國民及學前教育署 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 嘉義縣婦女生育補助
- id `7619f22a-50f6-4e9e-8b2f-2f322e6480c9` ｜ 來源 chiayi_county_sw ｜ 類別 birth_incentive ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請時需提供產婦私章、出生證明

### 嘉義縣新生兒大禮包
- id `4ba091f8-3e98-4d10-b8ce-c3549112dbdb` ｜ 來源 chiayi_county_sw ｜ 類別 birth_incentive ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 嘉義縣弱勢家庭坐月子到嘉（家）服務
- id `9fcb088f-f380-43f5-85eb-7a2cfb41097a` ｜ 來源 chiayi_county_sw ｜ 類別 birth_incentive ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 弱勢兒童及少年生活扶助
- id `406ed406-787b-42ab-b951-20be6e77b36d` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入戶救助
- id `6763ae9d-0925-45c0-88bf-745cc07a6c87` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `text_too_short` original_text：原文只有 193 字，難以判斷

### 強化社會安全網-急難紓困方案
- id `3aa667c5-8f2e-4927-bf45-4f8234d944ee` ｜ 來源 chiayi_county_sw ｜ 類別 emergency_relief ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 社會救助醫療補助
- id `dea1fd29-c9d7-44bf-9b6f-edace9d0e971` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶住院看護補助
- id `06def07c-c332-4c92-91b5-71ba85dcb721` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：於看護行為終止之日起3個月內提出申請

### 嘉義縣弱勢家戶微型保險實施計畫
- id `96098af3-6245-4511-ab4e-e2c80ed13bf9` ｜ 來源 chiayi_county_sw ｜ 類別 low_income_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 特殊境遇家庭緊急生活扶助
- id `ae2f0912-329a-412f-ab6d-dc906869cba3` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 特殊境遇家庭子女生活津貼
- id `9e4042ec-d566-423f-b05b-d106fd324506` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 特殊境遇家庭訴訟律師諮詢補助
- id `ca09888b-4fea-4e49-ad4a-13fcd59b63c6` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 特殊境遇家庭兒童托育津貼
- id `bd2b049f-8337-4cdf-9543-b28df8fe06b0` ｜ 來源 chiayi_county_sw ｜ 類別 special_circumstances_aid ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：應於事實發生6個月內提出申請

### 中低收入老人生活津貼補助
- id `a6d32d1c-89de-4cc3-97c8-8dec3aa5c126` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 重陽節敬老禮金發放補助
- id `8b55e4c0-c6ab-4950-9843-5811a3c243c1` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需於重陽節前一個月仍持續在籍
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人全民健康保險費補助
- id `55b07c04-2b6b-46d6-808a-b51b2e58727a` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 中低收入老人重病住院看護補助
- id `7dfc4e45-e5d0-4b6d-8fe9-4989af5cefa0` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：應備文件：申請表、醫療院所診斷證明書正本、看護費用收據正本、照顧服務員技術士證或照顧服務員訓練結業證明書及身分證正反面影本各1份、低收入戶、符合中低收入老人生活津貼或家庭總收入每人每月平均在最低生活費用標準2.5倍以下之證明書。

### 改善中低收入老人住宅設施、設備補助
- id `df0fba4e-bb31-492d-afbc-cb263588971f` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_allowance ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入老人進住機構及聘僱長期看護工補助
- id `abff56c7-4732-4446-b94c-7add05b4fbbe` ｜ 來源 chiayi_county_sw ｜ 類別 institutional_care_subsidy ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：被照顧者年滿65歲，領有(中)低收入老人生活津貼且設籍本縣達六個月以上者；機構提供照顧達一年以上，目前仍持續照顧者；實際聘僱長期看護工達一年以上，目前仍聘雇中者。
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 114年度住宿式服務機構使用者補助方案
- id `c53453ca-e7ab-4c84-8404-95c37604991e` ｜ 來源 chiayi_county_sw ｜ 類別 institutional_care_subsidy ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 嘉義縣敬老卡申辦及補助優待
- id `700e04bd-cb71-4e76-b883-b1f4ac5e47b1` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_service ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[85]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[85]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[85]）

### 長期照顧-輔具服務及居家無障礙環境改善服務
- id `cf8dc6fd-b097-4def-b1d3-1bb3134f79f7` ｜ 來源 chiayi_county_sw ｜ 類別 assistive_device ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人須自付負擔比例10%或30%
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 營養餐飲服務
- id `7d591ca2-9157-4eba-8a40-1aa0d20c7efc` ｜ 來源 chiayi_county_sw ｜ 類別 meal_service ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `text_too_short` original_text：原文只有 187 字，難以判斷

### 身心障礙者及老人預防走失服務
- id `1692bd29-fc99-410e-815b-c105c773dfa4` ｜ 來源 chiayi_county_sw ｜ 類別 elderly_service ｜ 機關 電話 ｜ 等級 verified
- `provider_is_division` provider：電話
- `provider_looks_like_contact` provider：電話
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 身心障礙者參加社會保險自付保費補助
- id `3e9dbf40-dba4-4471-94de-e74be4fc84ff` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 本局身心障礙福利科05-3620900#1110。 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 補助就讀本縣私立幼托園所（機構）3-5歲身心障礙幼兒家長教育經費
- id `3ab6f841-3835-4670-b000-759695ba6803` ｜ 來源 chiayi_county_sw ｜ 類別 education_subsidy ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者購買或承租商店攤販低利貸款或租金補貼
- id `33e10a97-8742-4645-9354-69900cf66398` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 嘉義縣居家身心障礙者使用維生器材及必要生活輔具用電優惠申請
- id `2aeaf2a1-832b-4f11-a0e0-5ea42b579f2d` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 失能身心障礙者補助使用居家照顧服務
- id `f1a55b44-acb6-470a-8c82-91f55c81eda1` ｜ 來源 chiayi_county_sw ｜ 類別 home_care ｜ 機關 嘉義縣社會局 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者送餐服務
- id `6f46e58f-a88c-4230-892c-ab85cf5ae870` ｜ 來源 chiayi_county_sw ｜ 類別 meal_service ｜ 機關 本局老人福利科05-3620900#3230吳小姐。 ｜ 等級 verified
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 獨居身心障礙者緊急救援服務計畫
- id `a8723739-52a1-4db4-a24e-e6f12dd440c2` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 申請身心障礙者汽車牌照免稅
- id `b5abaacd-3945-41dd-af22-8981d6e20a4a` ｜ 來源 chiayi_county_sw ｜ 類別 disability_other ｜ 機關 嘉義縣社會局 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：備件
- `amount_not_in_text` benefit.amount：2400 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：2400 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：2400 不在原文可解析的金額中（原文金額：[]）

### 花蓮縣婦女生育補助
- id `c6375659-bc28-49ba-b1cf-dfc5e646a79e` ｜ 來源 hualien_sw ｜ 類別 birth_incentive ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 花蓮縣未滿2歲兒童托育補助（公共及準公共化特約托育補助）
- id `82cf76de-1ade-4599-8e11-d27c906c5b47` ｜ 來源 hualien_sw ｜ 類別 childcare_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 花蓮縣弱勢家庭臨時托育服務計畫
- id `ea83db43-0c07-4986-a9e6-9e2698a9f574` ｜ 來源 hualien_sw ｜ 類別 childcare_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 花蓮縣準公共友善托育獎勵措施實施計畫
- id `a36438d4-ebf8-46cc-89f2-411452947f75` ｜ 來源 hualien_sw ｜ 類別 childcare_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 花蓮縣兒童及少年生活扶助
- id `44d558aa-c69d-4d6f-821a-e8c755062e5e` ｜ 來源 hualien_sw ｜ 類別 low_income_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 花蓮縣弱勢兒童及少年醫療費用補助
- id `fed0c690-a46a-4c00-8d28-f529b3b2d926` ｜ 來源 hualien_sw ｜ 類別 medical_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 花蓮縣急難救助
- id `b65599a9-4f4e-4cff-aa79-df421b2f0719` ｜ 來源 hualien_sw ｜ 類別 emergency_relief ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 強化社會安全網－急難紓困實施方案
- id `e4d72a31-b64f-449d-86d4-9a85ea37c1d5` ｜ 來源 hualien_sw ｜ 類別 emergency_relief ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需提供申請書暨通報表、認定表、戶籍謄本、診斷書、死亡證明書、相關證明文件、醫療費用收據、印章及其他證明文件（依實際需要提供財產所得與稅籍證明）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶住宅修繕補助
- id `dbe3c5ca-113f-4f99-a889-2c815d2b8791` ｜ 來源 hualien_sw ｜ 類別 low_income_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 花蓮縣低(中低)收入戶及弱勢族群醫療及住院照顧費用補助
- id `35a278b7-add2-460c-be4d-60d713c31ad2` ｜ 來源 hualien_sw ｜ 類別 low_income_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 115年衛生福利部關懷弱勢加發生活補助（花蓮縣）
- id `48459321-3413-4aab-abc1-3c3cc3e13356` ｜ 來源 hualien_sw ｜ 類別 low_income_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 國民年金所得未達一定標準保費補助
- id `748b4521-8719-4886-955d-e0cc82061738` ｜ 來源 hualien_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：申請人需自付30%的保險費
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 短缺川資民眾返鄉乘車換票
- id `37de2121-f2c6-4557-9896-be252ecb56c5` ｜ 來源 hualien_sw ｜ 類別 emergency_relief ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 花蓮縣65歲以上老人全民健康保險自付保險費補助
- id `fe5943c9-d3cf-42c9-87e4-d7455a05daeb` ｜ 來源 hualien_sw ｜ 類別 elderly_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 花蓮縣65歲以上長者假牙補助
- id `74ce1de8-4e77-476e-8226-e19d4583731a` ｜ 來源 hualien_sw ｜ 類別 elderly_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 花蓮縣政府重陽節敬老禮金
- id `6555f343-185a-43c3-989a-c8e0323df330` ｜ 來源 hualien_sw ｜ 類別 elderly_allowance ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 住宿式機構服務使用者補助方案
- id `33b6933c-e155-497a-a6ee-cb968f28bb69` ｜ 來源 hualien_sw ｜ 類別 institutional_care_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者生活輔具費用補助
- id `b9be561d-82cb-46b3-af8e-a7a19bd38e81` ｜ 來源 hualien_sw ｜ 類別 assistive_device ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請輔具前須先申請並收到核定函

### 身心障礙者房屋租金補助
- id `b57928ae-e0b2-4244-911f-54796e057eb2` ｜ 來源 hualien_sw ｜ 類別 rental_subsidy ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者首次購屋貸款利息補貼
- id `b0ccca28-a57e-405d-bd6e-be5dd7fb5732` ｜ 來源 hualien_sw ｜ 類別 disability_other ｜ 機關 花蓮縣政府社會處 ｜ 等級 needs_review
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者家庭托顧服務
- id `86cff572-10fc-475d-9ac1-7d6613139beb` ｜ 來源 hualien_sw ｜ 類別 family_care_home ｜ 機關 花蓮縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣婦女生產補助
- id `1df2c525-9de9-4ca9-ac81-bc3d47e34ef4` ｜ 來源 kinmen_sw ｜ 類別 birth_incentive ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府生育贈禮
- id `f0b263a6-9129-48d1-9227-80244d9e9832` ｜ 來源 kinmen_sw ｜ 類別 birth_incentive ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1 不在原文可解析的金額中（原文金額：[]）
- `amount_not_in_text` benefit.amount：3 不在原文可解析的金額中（原文金額：[]）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣政府支持生育加碼補助
- id `b0ee1f9d-1c42-4920-baf0-e9c75d8e70a7` ｜ 來源 kinmen_sw ｜ 類別 birth_incentive ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 特殊境遇家庭扶助
- id `dec19bbb-37b6-421b-ba3f-0b56f52a3517` ｜ 來源 kinmen_sw ｜ 類別 special_circumstances_aid ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：檢附申請調查表、全戶戶籍資料、特殊境遇原因相關證明文件、領據及申請人本人郵局存摺封面影本
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 育有未滿二歲兒童育兒津貼
- id `d3cf3bad-1b06-47d0-807f-35c3ee836efe` ｜ 來源 kinmen_sw ｜ 類別 child_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：於兒童未滿2歲前申請
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府友善托育補助
- id `e379dccc-7f39-41a1-b0c2-ed0cb588a3ef` ｜ 來源 kinmen_sw ｜ 類別 childcare_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣父母照顧子女津貼
- id `521e6533-d0f2-4b63-a787-f31be004c55c` ｜ 來源 kinmen_sw ｜ 類別 child_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `derived_number_not_in_text` benefit.target_population_text：benefit.target_population_text：「父母雙方同時符合設籍條件且照顧未滿12歲子女的父母」中的 12 不在原文
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 兒童及少年生活扶助
- id `64018949-05b2-4762-88bd-b078fb20f5bc` ｜ 來源 kinmen_sw ｜ 類別 child_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 弱勢家庭兒童及少年緊急生活扶助
- id `cc2d8710-9e60-46b5-9121-708cafeabd85` ｜ 來源 kinmen_sw ｜ 類別 child_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 中低收入戶18歲以下兒童及少年健保費補助
- id `b0df7733-60b5-4ef3-b5e6-e07d639fe27e` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 143 字，難以判斷

### 金門縣弱勢兒童及少年醫療費用補助
- id `0b23c02f-bfdf-42c2-a4d6-bf3abd013a87` ｜ 來源 kinmen_sw ｜ 類別 medical_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶家庭生活扶助
- id `94075813-bd45-410a-9a52-b8d11f2d09f2` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入戶扶助
- id `269d06dc-f357-4539-8e37-8426b1653826` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 低收入戶子女就學生活補助
- id `98245d57-d3fc-4c29-93fd-e0c037997c48` ｜ 來源 kinmen_sw ｜ 類別 student_aid ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 低收入戶及中低收入戶參加健康保險費用補助
- id `016d2cba-8779-4d83-9f14-35b61756d556` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `text_too_short` original_text：原文只有 161 字，難以判斷

### 低收入戶及中低收入戶傷病醫療看護費用補助
- id `2bc0c226-2726-4265-af47-59d104073355` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣低收入戶三節慰問金
- id `2bee620e-5b83-40fe-9fb1-36f31cecab2d` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `text_too_short` original_text：原文只有 140 字，難以判斷

### 金門縣政府補助低收入戶網路服務費
- id `ecbbb888-39d1-4b50-bc32-62a248368272` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：檢附申請書、支出原始憑證及領據、金融機構存摺影本、主管機關同意核備函

### 金門縣政府補助低收入戶就學子女家戶購置電腦
- id `ae6400d1-c798-49c6-833f-fff76e43c8ec` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府辦理低收入戶及弱勢家庭就學子女自立脫貧補助
- id `66520b5e-eb4b-4769-a49e-64b16be66602` ｜ 來源 kinmen_sw ｜ 類別 student_aid ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：100 不在原文可解析的金額中（原文金額：[500, 2000, 18000, 24000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[500, 2000, 18000, 24000]）
- `amount_not_in_text` benefit.amount：100 不在原文可解析的金額中（原文金額：[500, 2000, 18000, 24000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[500, 2000, 18000, 24000]）

### 以工代賑輔導
- id `7e07961f-bac0-429a-be8a-73a2dd526c6a` ｜ 來源 kinmen_sw ｜ 類別 low_income_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 急難救助
- id `0ae7b42d-252a-4427-b970-83905be05aee` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：申請人應自事故發生日起3個月內提出申請
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 急難紓困
- id `f1827110-0dbe-4f87-b399-bc7347b5dd30` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣災害救助金
- id `fe8b1175-3175-4406-94ec-a904eaf75591` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[5000, 10000, 20000, 100000, 200000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[5000, 10000, 20000, 100000, 200000]）

### 縣民遭受意外傷害濟助
- id `d55e01a0-364a-467e-aae7-bcce4c2ddb31` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供相關證明文件

### 縣民非因意外致死亡身心障礙濟助
- id `0033df41-524c-4ccd-9c1a-f75e30f1c064` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：須於事實發生之日起6個月內提出申請

### 金門縣緊急傷病及失能之縣民照顧服務補助
- id `0afaeabc-630e-4a00-b624-10d1bc155cdc` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣實（食）物銀行
- id `860842cb-15f1-4477-8586-3c03bb38b7a4` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣65歲以上老人全民健康保險補助
- id `ffaa39ce-31cf-4cd3-86ef-011ed899fc16` ｜ 來源 kinmen_sw ｜ 類別 elderly_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣歷經戰地軍管時期老人慰助金
- id `077680fa-ecdb-427c-836c-ae91b387d447` ｜ 來源 kinmen_sw ｜ 類別 elderly_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府辦理老人收容安置補助
- id `26e0e363-4d72-4566-bf45-448eeeca8e0c` ｜ 來源 kinmen_sw ｜ 類別 institutional_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣中低收入老人住宅改善補助
- id `f3e667f7-fc3d-425b-8a70-814669c540c9` ｜ 來源 kinmen_sw ｜ 類別 elderly_service ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 老人在宅緊急救援連線服務
- id `d920a67c-3b06-4210-99a8-90989c982a93` ｜ 來源 kinmen_sw ｜ 類別 elderly_service ｜ 機關 提供服務，由本府提供每月連線服務費。 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需填具申請書表

### 金門縣政府預防走失智慧防護網絡服務
- id `80ba71f0-cf72-40ee-ad5c-71085eaa75f4` ｜ 來源 kinmen_sw ｜ 類別 elderly_service ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣政府補助中低收入獨居老人裝設有線電視費用
- id `bef1ebaa-300e-44b8-878c-e7404430a2a6` ｜ 來源 kinmen_sw ｜ 類別 elderly_service ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙生活補助
- id `8cb702db-10f9-4359-868b-d36a87ff5783` ｜ 來源 kinmen_sw ｜ 類別 disability_living_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `amount_is_threshold` benefit.amount.description：3.家庭總收入應計算人口之所有存款本金及有價證券價值合計未超過一人時為新臺幣200萬元，每增加1人，增加新臺幣25萬元。

### 金門縣身心障礙者居家生活津貼
- id `ab36cc0c-a005-4498-abd7-8759969b8a39` ｜ 來源 kinmen_sw ｜ 類別 disability_living_allowance ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣身心障礙照顧者津貼
- id `50beb943-6b06-4c43-9ace-e113caa0c4f3` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣身心障礙者日間及住宿式照顧費用部分負擔補助
- id `fafe6245-324e-480b-89e4-8b7bdba37b44` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者醫療及生活輔助器具費用補助
- id `daa7be8d-d13f-439a-8a40-68619ea19b0c` ｜ 來源 kinmen_sw ｜ 類別 assistive_device ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者參加社會保險費用補助
- id `9b60bbc3-050c-4fcd-aef0-4d121e2eaa02` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 居家身心障礙者使用維生器材及必要生活輔具用電優惠
- id `7efa815e-a8fe-4232-9266-9c5066eff31d` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣身心障礙者租賃房屋租金補助
- id `3774b04f-e216-4efe-8f82-3b57d57dc610` ｜ 來源 kinmen_sw ｜ 類別 rental_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣身心障礙者臨時及短期照顧服務費用補助
- id `8cb9c821-8cb5-4ed9-b030-3429fc12694f` ｜ 來源 kinmen_sw ｜ 類別 respite_care ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣身心障礙者家庭托顧服務
- id `26aa3767-5ed0-46b8-91b1-04f2f3a69f54` ｜ 來源 kinmen_sw ｜ 類別 family_care_home ｜ 機關 地址 ｜ 等級 verified
- `provider_is_division` provider：地址
- `provider_looks_like_contact` provider：地址

### 金門縣身心障礙者社區式日間照顧服務
- id `e4fccb5f-d887-4266-a8ce-bb33383a1b26` ｜ 來源 kinmen_sw ｜ 類別 day_care ｜ 機關 據點名稱 ｜ 等級 verified
- `provider_is_division` provider：據點名稱
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣身心障礙者復康巴士
- id `61c5703e-94ec-4d05-a82b-cd9bd92a360d` ｜ 來源 kinmen_sw ｜ 類別 transport_service ｜ 機關 承辦單位 ｜ 等級 verified
- `provider_is_division` provider：承辦單位
- `provider_looks_like_contact` provider：承辦單位
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣精神障礙者住院期間伙食費用補助
- id `8c206bdf-01da-4927-b1e8-56c65534e34f` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣紙尿褲看護墊補助
- id `639e0b6d-47f3-4833-b91c-b25c7f810e97` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣政府辦理極重度長期失能身心障礙者三節慰問金
- id `2f8b7c1a-6201-41f2-99c2-4cb263fa7827` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_title_conflict` category：標題含「慰問金」，預期 ['emergency_relief', 'low_income_allowance', 'medical_subsidy', 'special_circumstances_aid']，實際 disability_other

### 金門縣補助安置台灣教療養機構身心障礙者家屬探視交通費補助
- id `251f1ee0-f42b-45b5-baba-abd26aaf8dab` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣重度以上中低收入身心障礙者及身心障礙團體裝設有線電視補助
- id `906971bd-2ea6-48e7-92ce-93ca878734d0` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：提供相關文件
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣民愛心卡
- id `38ece0a8-a9fe-4f7d-8d13-a7ba07512f29` ｜ 來源 kinmen_sw ｜ 類別 disability_other ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：需提供身分證、身心障礙證明及照片
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 金門縣設籍前新住民社會救助計畫
- id `94e62b5e-69ea-4005-b4b0-acc02ebff52c` ｜ 來源 kinmen_sw ｜ 類別 emergency_relief ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣設籍前新住民遭逢特殊境遇家庭扶助計畫
- id `36274c51-7798-471b-b4f0-680ed974eb1f` ｜ 來源 kinmen_sw ｜ 類別 special_circumstances_aid ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 金門縣政府辦理縣民經收出養機構媒合收養交通費補助
- id `dc411b50-e5bc-451d-ab7a-606af809ae57` ｜ 來源 kinmen_sw ｜ 類別 transport_service ｜ 機關 金門縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：提供相關文件
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒少安置後續追蹤輔導與自立生活服務
- id `8cafd1a0-8e92-4c53-ac7b-06025df43614` ｜ 來源 kinmen_sw ｜ 類別 childcare_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣政府辦理團體微型首次罹患癌症健康保險
- id `11d9270d-b95b-4cfa-bfaf-3123f480d743` ｜ 來源 kinmen_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣政府辦理境內外縣籍身心障礙安置個案及機構三節慰問
- id `e35a18ed-f935-4e72-8bf5-d900e9293934` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 金門縣身心障礙者自立生活支持服務
- id `cbcc8212-304e-4d81-bbd9-b3dfa2977ed7` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣視覺功能障礙者生活重建及生活訓練服務
- id `f4dac68e-fa9c-450d-a2ec-06fac16b0d70` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣身心障礙者社區日間作業設施服務
- id `03b5184d-0043-4f05-a815-d6a2dfb46a31` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 據點名稱 ｜ 等級 verified
- `provider_is_division` provider：據點名稱

### 金門縣多元身心障礙者社區居住與生活服務
- id `947409f2-746f-4f88-a771-8ac3a9890da9` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 社區居住名稱 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 金門縣身心障礙者家庭支持服務
- id `ad131389-fbae-421f-a853-6f8e91305a0c` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 服務據點 ｜ 等級 verified
- `provider_is_division` provider：服務據點

### 金門縣精神障礙者協作模式服務
- id `d7bce029-e390-44f8-ac4f-0885b6687dd0` ｜ 來源 kinmen_sw ｜ 類別 disability_care_subsidy ｜ 機關 據點地址 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `gate_uncertain` classification：關鍵字與 embedding 都無明確意見，LLM 判定是補助（僅 LLM 一方，待人工確認）；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `provider_is_division` provider：據點地址
- `provider_looks_like_contact` provider：據點地址
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）

### 金門縣政府辦理南山人壽團體微型傷害保險
- id `80024216-74ae-4783-b3d0-71d428fd8c9d` ｜ 來源 kinmen_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 金門縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 宜蘭縣婦女生育津貼
- id `c91b8347-d2fd-4950-822d-5b7394ef0ae8` ｜ 來源 yilan_sw ｜ 類別 birth_incentive ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 未滿二歲兒童托育準公共化服務
- id `58e92ff1-83a1-43f3-a4cf-b1cbc1330880` ｜ 來源 yilan_sw ｜ 類別 childcare_subsidy ｜ 機關 財團法人宜蘭縣私立蘭馨婦幼中心 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：每月托育滿16日，則補助以1個月計，未滿16日則以半個月計。
- `provider_is_division` provider：財團法人宜蘭縣私立蘭馨婦幼中心

### 宜蘭縣特殊境遇家庭與兒童及少年生活扶助（含弱勢兒少緊急生活扶助）
- id `3394c482-70dd-4e28-954a-815c6517cbae` ｜ 來源 yilan_sw ｜ 類別 special_circumstances_aid ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 弱勢兒童及少年醫療補助
- id `3739d1a5-b407-4bcf-a27f-4462de414492` ｜ 來源 yilan_sw ｜ 類別 medical_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 兒童及少年未來教育與發展帳戶
- id `167af75c-c91e-4e49-b663-f2aec3b65b2d` ｜ 來源 yilan_sw ｜ 類別 education_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 發展遲緩兒童早期療育（含療育費及交通費補助）
- id `e074f8e8-243a-4fe2-8cee-196583f90de8` ｜ 來源 yilan_sw ｜ 類別 medical_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 低收入戶生活扶助
- id `9559f3e0-ba12-4453-a244-dbdeefc3eba5` ｜ 來源 yilan_sw ｜ 類別 low_income_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 民眾急難救助
- id `c1f3ce92-0dc6-49a0-bf5e-f81134cf3b90` ｜ 來源 yilan_sw ｜ 類別 emergency_relief ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[2000, 10000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[2000, 10000]）

### 低收入戶及中低收入傷病醫療、照顧服務費用補助
- id `dc00acfb-87cd-4387-996b-473de89b7512` ｜ 來源 yilan_sw ｜ 類別 low_income_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：應備文件：身分證明文件、診斷書、醫療費收據、照顧服務費收據、照顧服務員證照、非低(中低)收入戶者申請醫療補助須附財稅證明、郵局存款簿封面影本、申請人印章。

### 低收入戶喪葬補助
- id `f9c9fef8-9010-4860-bde8-80926739a240` ｜ 來源 yilan_sw ｜ 類別 low_income_allowance ｜ 機關 社會救助科 聯絡資訊 ｜ 等級 verified
- `provider_looks_like_contact` provider：社會救助科 聯絡資訊

### 宜蘭縣中低收入戶老人及低收入戶住宅設施設備修繕補助
- id `bfbc283d-3ade-4e11-abff-3a793812899f` ｜ 來源 yilan_sw ｜ 類別 low_income_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 115年-117年宜蘭縣展翼飛揚脫貧計畫
- id `7332fbb7-3a3e-4afb-8273-4031c4400755` ｜ 來源 yilan_sw ｜ 類別 student_aid ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 川資(車資返鄉補助)
- id `5dadcc36-4548-4265-ba97-684a9e31c306` ｜ 來源 yilan_sw ｜ 類別 emergency_relief ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 物資銀行
- id `8d233365-49c5-4f56-880a-4e9509323e45` ｜ 來源 yilan_sw ｜ 類別 emergency_relief ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 弱勢民眾微型保險
- id `0f526d95-6e21-43b1-aebd-f4dcb1accac0` ｜ 來源 yilan_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 國民年金保險費補助（所得未達一定標準資格認定）
- id `b6c7ce14-d64e-4656-bf25-6631b26db93a` ｜ 來源 yilan_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 社會救助科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：社會救助科
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 中低收入老人特別照顧津貼
- id `dad20af0-820c-482a-ac71-ffb693652812` ｜ 來源 yilan_sw ｜ 類別 elderly_allowance ｜ 機關 社會救助科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `provider_is_division` provider：社會救助科
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 65歲以上未滿70歲中低收入老人全民健康保險自付保險費補助
- id `a2fa1a69-ac91-48c7-b169-fbd5b626bd01` ｜ 來源 yilan_sw ｜ 類別 elderly_allowance ｜ 機關 社會救助科 聯絡資訊 ｜ 等級 verified
- `provider_looks_like_contact` provider：社會救助科 聯絡資訊
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值

### 中低收入戶老人假牙裝置補助
- id `02d0b57f-54cb-427b-8f15-e7fdfc59d012` ｜ 來源 yilan_sw ｜ 類別 elderly_allowance ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：5年內同一顎或同一牙位已受本府社會處假牙補助者，不得再次申請補助
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 獨居老人關懷服務
- id `61554184-b68d-4aaf-9890-71c7264c8a17` ｜ 來源 yilan_sw ｜ 類別 elderly_service ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 獨居老人緊急救援通報系統服務
- id `c20a33a0-bae1-4362-aa3f-70fe0a34695a` ｜ 來源 yilan_sw ｜ 類別 elderly_service ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需備齊相關文件
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 宜蘭縣社會福利智慧卡（敬老卡、愛心卡）
- id `02d223d4-eb38-4170-b2b3-2d6ca615e660` ｜ 來源 yilan_sw ｜ 類別 elderly_service ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者生活補助
- id `c9a772eb-eaef-4bdc-beb7-9868034e95fb` ｜ 來源 yilan_sw ｜ 類別 disability_living_allowance ｜ 機關 社會救助科 ｜ 等級 verified
- `provider_is_division` provider：社會救助科
- `rule_value_missing` residence.current_city：residence.current_city = 沒有值
- `rule_value_missing` residence.household_city：residence.household_city = 沒有值
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者（55至64歲）假牙裝置補助
- id `9c5dcdf0-22cc-4414-9d9d-2948a91fed55` ｜ 來源 yilan_sw ｜ 類別 disability_other ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：5年內同一顎或同一牙位已受本府社會處假牙補助者，不得再次申請補助。
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_title_conflict` category：標題含「假牙」，預期 ['assistive_device', 'disability_assistive_device', 'elderly_allowance', 'elderly_service', 'medical_subsidy']，實際 disability_other
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者租賃房屋租金補助
- id `a4d75f95-4bb5-4640-927a-edfeacfbf440` ｜ 來源 yilan_sw ｜ 類別 rental_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者購屋貸款利息補貼
- id `b757433e-d419-40d8-97e9-0c165122660d` ｜ 來源 yilan_sw ｜ 類別 disability_other ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者參加社會保險保險費補助
- id `65171db3-b004-4933-bf80-895990ad7fae` ｜ 來源 yilan_sw ｜ 類別 disability_other ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身心障礙者交通服務（復康巴士）
- id `d2bf447d-f410-4a5a-9334-20fbebf0dc8c` ｜ 來源 yilan_sw ｜ 類別 transport_service ｜ 機關 宜蘭縣政府社會處 ｜ 等級 verified
- `rule_city_conflict` residence.household_city：規則城市 ['臺北市', '新北市', '基隆市'] 與機關／標題 ['宜蘭縣'] 不同
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登

### 高照顧負荷家庭創新服務方案
- id `ec06369c-4fe3-4d61-b95d-60cb3dbf3420` ｜ 來源 yilan_sw ｜ 類別 disability_care_subsidy ｜ 機關 宜蘭縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 馬公市新生嬰兒營養代金
- id `caf8507e-672c-4a2e-9fd2-43a20654d9d9` ｜ 來源 penghu_sw ｜ 類別 birth_incentive ｜ 機關 澎湖縣馬公市公所 > 社會課 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需在新生兒出生日起3個月內提出申請

### 澎湖縣家庭安全提升補助（未滿2歲嬰幼兒每月3千元）
- id `d4e726fd-1406-4488-8a0b-5b8621179bdc` ｜ 來源 penghu_sw ｜ 類別 child_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[2000, 3000, 9000]）
- `amount_not_in_text` benefit.amount：1000 不在原文可解析的金額中（原文金額：[2000, 3000, 9000]）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣辦理未滿二歲暨延長三歲兒童托育公共化及準公共服務費用申請須知
- id `de24d83f-d22b-4621-b563-d3778c2e9f4f` ｜ 來源 penghu_sw ｜ 類別 childcare_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣辦理115年度弱勢兒童課後照顧服務實施計畫
- id `756c57b5-e1eb-44ea-9b7d-e23740667646` ｜ 來源 penghu_sw ｜ 類別 childcare_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣六歲以下幼童健保費自負額補助
- id `8c178de4-6a92-4b26-88af-83d1e3652943` ｜ 來源 penghu_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣六歲以下幼童參加全民健康保險保險費自負額補助實施要點
- id `78476371-ea0b-43f4-8ad9-03e5ab562d0a` ｜ 來源 penghu_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣政府低收入戶中低收入戶調查及生活扶助作業要點
- id `b8b1bf48-2e11-4e3a-8e9e-5a3d6a3d4fbd` ｜ 來源 penghu_sw ｜ 類別 low_income_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣民眾遭遇急難事件救助要點
- id `f9406a2d-5ba3-4dd3-8f13-1b43dd17df13` ｜ 來源 penghu_sw ｜ 類別 emergency_relief ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `obligation_not_in_text` benefit.obligations：需檢具相關證明文件
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣災害救助金核發
- id `78192577-3510-4e0d-8011-02d1cc946a74` ｜ 來源 penghu_sw ｜ 類別 emergency_relief ｜ 機關 社會處 > 社會福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `no_simple_rules` rules：沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣政府低收入戶及中低收入戶簡易修繕住宅補助要點
- id `75f49793-f266-4728-a9a3-a38f2758be7a` ｜ 來源 penghu_sw ｜ 類別 housing_support ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣政府辦理重大傷病婦女生活補助費實施要點
- id `10bb3b68-a3f7-406b-9b7c-4e307afb38dd` ｜ 來源 penghu_sw ｜ 類別 special_circumstances_aid ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣政府困苦失依兒童及少年生活扶助要點
- id `dfe3598f-0feb-4b63-8f56-61cf2ee3f974` ｜ 來源 penghu_sw ｜ 類別 low_income_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣弱勢兒童及少年醫療補助作業規定
- id `20fd9479-1b90-4d86-a8b5-d1e5c65b51a6` ｜ 來源 penghu_sw ｜ 類別 medical_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）

### 澎湖縣政府辦理弱勢家庭兒童及少年緊急生活扶助補助及核發作業規定
- id `dfdbbe41-e473-4a11-877f-5df3386b5630` ｜ 來源 penghu_sw ｜ 類別 emergency_relief ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣湖西鄉居民健保費定額補助
- id `3aa0a48f-489c-4071-8a0d-4fe694aa677d` ｜ 來源 penghu_sw ｜ 類別 insurance_premium_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：關鍵字與 embedding 都判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 中低收入老人生活津貼（白沙鄉公所受理）
- id `5b21b929-9f6b-4d61-9314-f2f5e8e84e4a` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣白沙鄉公所 > 社會課 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 澎湖縣中低收入老人特別照顧津貼補助
- id `b639bed4-ca42-4842-bf46-22c90e49d233` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 社會處 > 社會福利科 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 中低收入老人假牙補助
- id `18a38127-5b6e-4396-a2fa-982556b2d8eb` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣長輩補助裝假牙
- id `c12fbdcb-86ee-4b35-bd7a-95579d5b708d` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣政府衛生局 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣政府發放重陽節敬老禮金實施要點
- id `63653156-7108-46e7-94ac-a4c028648893` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 澎湖縣中低收入老人重病住院看護補助實施要點
- id `c52ee14b-298d-4e55-b75e-90cd1b154052` ｜ 來源 penghu_sw ｜ 類別 elderly_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 澎湖縣中低老人住宅修繕補助實施辦法
- id `322373b2-098c-4922-91d7-3e52c203bbda` ｜ 來源 penghu_sw ｜ 類別 housing_support ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `category_uncertain` category：三方不一致，LLM 判定是補助；只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）

### 澎湖縣政府辦理中、低收入失能老人機構照顧服務補助計畫
- id `de06e2f4-2453-4576-a1e0-36a85d5437f5` ｜ 來源 penghu_sw ｜ 類別 institutional_care_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 獨居老人緊急救援連線系統
- id `dc2c4c7f-423f-4ec1-a1fe-cb32248aa068` ｜ 來源 penghu_sw ｜ 類別 elderly_service ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 居家服務（長照）
- id `ec9c6d95-8289-4704-b8fa-e3d8a739f130` ｜ 來源 penghu_sw ｜ 類別 home_care ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者生活補助費
- id `4c692b32-26cf-4b74-9545-b7e5a579df89` ｜ 來源 penghu_sw ｜ 類別 disability_living_allowance ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者日間照顧及住宿式照顧費用補助
- id `27bb450b-cd90-4ad1-9046-4ef36fff6a1e` ｜ 來源 penghu_sw ｜ 類別 disability_care_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身心障礙者三節慰問金發放作業要點
- id `ef9e9607-f8fd-4bf9-a050-65ae23744fe3` ｜ 來源 penghu_sw ｜ 類別 disability_other ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：提供身心障礙證明正反面影本、金融機構帳戶封面影本及領據
- `category_title_conflict` category：標題含「慰問金」，預期 ['emergency_relief', 'low_income_allowance', 'medical_subsidy', 'special_circumstances_aid']，實際 disability_other

### 身心障礙者社會保險費補助
- id `6d313373-3710-468b-9e44-6daeb53a19e8` ｜ 來源 penghu_sw ｜ 類別 disability_other ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額

### 身障房屋租金補助
- id `04f33862-f2e9-45c3-a392-140d75a5b6b4` ｜ 來源 penghu_sw ｜ 類別 rental_subsidy ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `cash_without_amount` benefit.amount：給付形式是現金但沒有任何金額
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表; rule[] 不在屬性登錄表

### 身障房屋貸款補助
- id `1afecd19-507c-4f3c-99bd-d56f48ac01c8` ｜ 來源 penghu_sw ｜ 類別 disability_other ｜ 機關 澎湖縣政府社會處 ｜ 等級 needs_review
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者輔具費用補助
- id `7d382ddd-3c85-4fda-9951-6b9c1d466059` ｜ 來源 penghu_sw ｜ 類別 assistive_device ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `schema_dropped_fields` schema：驗證時移除：rule[] 不在屬性登錄表

### 身心障礙者育兒輔具服務
- id `cceb91b3-38a1-4935-ba43-ecab760d8cfc` ｜ 來源 penghu_sw ｜ 類別 assistive_device ｜ 機關 澎湖縣政府社會處 ｜ 等級 verified
- `obligation_not_in_text` benefit.obligations：需經輔具中心評估後核定

