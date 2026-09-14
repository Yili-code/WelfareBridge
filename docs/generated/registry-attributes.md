# 屬性登錄表（實際載入內容）

來源：`backend/app/registry/attribute_registry.yaml`（version 2）＋ `attribute_aliases_mined.yaml`（語料統計別名，只在本地 AI 候選中使用）。

| 屬性 id | 型態 | 單位／允許值 | 領域 | 標籤 | 追問句 | 敏感度 | 硬過濾 | 推導 | 種子別名 | 統計別名（z≥3） | 規則使用次數 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `applicant.age` | number | years | all | 年齡 | 你今年幾歲？ | low | ✓ |  | 年滿、歲以上、歲以下、未滿、足歲、年齡 | 兒童、育兒津貼、原住民、實際、孫子女、際居住、實際居、設籍本市 | 826 |
| `applicant.is_elderly` | boolean |  | social_welfare、long_term_care、health | 年滿 65 歲 | 你（或受照顧者）是否年滿 65 歲？ | low |  | applicant.age >= 65 | 老人、長者、年滿65歲、65歲以上、高齡 | 活津貼、獨居、福利、照顧津貼、特別照顧、別照顧津、假牙、福利科 | 85 |
| `applicant.gender` | enum | male、female、other | all | 性別 | 你的性別？ | medium |  |  | 性別、男性、女性、婦女 | 分娩、未婚懷孕、生育、懷胎、孕婦、女生、生育補助、社會處婦 | 78 |
| `applicant.nationality` | enum | roc、foreign、stateless | all | 國籍 | 你的國籍？ | medium | ✓ |  | 國籍、本國籍、中華民國國民、外國人、外籍 | 居留、居留證、我國、人士、看護、籍人、護照、永久居留 | 87 |
| `applicant.marital_status` | enum | single、married、divorced、widowed | social_welfare、housing | 婚姻狀況 | 你的婚姻狀況？ | medium |  |  | 婚姻、已婚、未婚、離婚、喪偶、配偶 | 直系、親屬、扶養、懷孕、協議、父母、判決、直系血親 | 280 |
| `applicant.is_student` | boolean |  | all | 在學學生 | 你目前是否為在學學生？ | low | ✓ |  | 在學學生、在學之學生、目前在學、在校生、具學生身分、在學中 | 大學、學生證、高中職、空中大學、學生證影、校在學、就讀、夜間部 | 69 |
| `education.level` | enum（有序） | elementary、junior_high、senior_high、vocational_high、junior_college、university、master、doctoral | education、youth、social_welfare、labor | 教育階段 | 你目前的教育階段是？ | low | ✓ |  | 學制、就讀、大專校院、大專院校、大學、研究所、碩士班、博士班、高級中等學校、高中職、國中、國小、五專、專科 | 私立、每名、國內、年級、公私立、每名新臺、名新臺幣、就學 | 478 |
| `education.grade` | number |  | education | 年級 | 你目前是幾年級？ | low |  |  | 年級、大一、大二、大三、大四、一年級、二年級、三年級、新生 | 出生、出生登記、初設戶籍、登記、大學、設戶籍登、專科學校、成績 | 44 |
| `education.school` | text |  | education | 就讀學校 | 你就讀的學校是？ | low |  |  | 學校、就讀學校、校名 | 獎學金、高級、清寒、學期、優秀學生、生獎學金、私立、秀學生獎 | 0 |
| `education.school_type` | enum | public、private | education | 公私立 | 你的學校是公立還是私立？ | low |  |  | 限公立、限私立、僅限公立、僅限私立、公立學校為限、私立學校為限 | 國內公、私立大、私立高、寄養家庭、私立大專、就讀、教養機構、少年安置 | 10 |
| `education.school_city` | city |  | education | 學校所在縣市 | 你的學校在哪個縣市？ | low | ✓ |  | 就讀本市、本市學校、市立、縣立、設於本市 | 醫院、高雄市、山醫院、藝文場館、健身俱樂、身俱樂部、髮健身俱、銀髮健身 | 15 |
| `education.department` | text |  | education | 科系 | 你就讀的科系是？ | low |  |  | 科系、學系、系所、學門、主修 | 相關科、領域、工程、單位洽詢、依各校規、教務處、學士、校規定 | 0 |
| `education.program_type` | enum | day、night、continuing、in_service、open_university、credit_program、military_police | education | 就讀部別 | 你就讀的是日間部、夜間部、進修部還是在職專班？ | low | ✓ |  | 夜間部、進修部、進修學院、在職專班、空中大學、學分班、推廣教育、軍警學校、日間部、進修學校、補習學校、建教班 | 不含、國內、研究、不包、學學生、部學、博士班、不包括 | 84 |
| `education.extended_study` | boolean |  | education | 延長修業／重修 | 你目前是否延長修業年限、重修或補修？ | low |  |  | 延長修業、延畢、重修、補修、延長修業年限 | 學分班、公費生、間部、學士、推廣、學生不、修學分、間部學 | 10 |
| `education.years_in_program` | number | years | education | 本學制修業年數 | 你在目前學制已修業第幾年？ | low |  |  | 修業年限、修業第、修業年數 | 年限內、延長、每名每學、每學期最、內每、學分、學期最高、名每學期 | 5 |
| `education.is_freshman` | boolean |  | education | 新生 | 你是否為本學年新生？ | low |  |  | 新生、一年級新生、入學 | 出生、出生登記、登記、初設戶籍、設戶籍登、登記或初、記或初設、戶籍登記 | 40 |
| `academic.average_score` | number | score | education | 學業平均成績 | 你上一學期（或學年）的學業平均成績約幾分？ | low |  |  | 學業成績、學業平均、平均成績、成績平均、總平均、智育成績、學期成績 | 學年、操行、成績單、成績證明、分數、學年度、操行成績、學期學業 | 125 |
| `academic.gpa` | number | gpa | education | GPA | 你的 GPA 是多少？ | low |  |  | GPA、平均績點 | 分數、業平均成、學業平均、分數成績、相對應、對照、平均成績、百分 | 5 |
| `academic.ranking_percent` | number | percent | education | 班級排名百分比 | 你上一學期的班級排名大約在前百分之幾？ | low |  |  | 排名、名次、前百分之、班排、系排 | 學期學業、學業、成績、期學業成、業總成績、全校、學業成績、學業總成 | 20 |
| `academic.conduct_score` | number | score | education | 操行成績 | 你上一學期的操行（德育）成績約幾分？ | low |  |  | 操行、德育、操行成績、德育成績、品行 | 體育、不限、智育、成績平均、學業成績、懲處、業成績平、德行 | 40 |
| `academic.subject_min_score` | number | score | education | 最低單科成績 | 你上一學期最低的一科成績約幾分？ | low |  |  | 各科成績、每科、單科、各科目 | 總平均、成績符合、成績均、合下列標、績總平均、成績總平、學業成績、年學業成 | 8 |
| `academic.no_disciplinary_record` | boolean |  | education | 無懲處紀錄 | 你是否沒有警告以上的懲處紀錄？ | medium |  |  | 懲處、警告、記過、獎懲紀錄、未受懲處、操行不及格 | 操行成績、成績、評量、學業成績、德行、行評、學期、學期平均 | 29 |
| `academic.no_failed_subject` | boolean |  | education | 無不及格科目 | 你上一學期是否沒有不及格的科目？ | low |  |  | 不及格、及格、未達60分、未達六十分 | 學業成績、成績平均、業成績平、業成績總、且無任何、績總平均、成績總平、期學業成 | 16 |
| `residence.household_city` | city |  | all | 戶籍縣市 | 你的戶籍在哪個縣市？ | low | ✓ |  | 設籍、戶籍、戶籍地、籍設、本市、本縣、設籍本市、戶籍所在地 | 區公、實際居、際居住、戶口名簿、月內、年滿、出生、登記 | 985 |
| `residence.household_district` | text |  | all | 戶籍鄉鎮市區 | 你的戶籍在哪個鄉鎮市區？ | low |  |  | 本區、本鄉、本鎮、設籍本區、區公所 | 籍所在地、公所社、社會課、公所社會、戶籍地、公所提出、社會、向戶籍 | 0 |
| `residence.duration_months` | number | months | all | 設籍時間（月） | 你在戶籍地連續設籍多久了？（月） | low |  |  | 設籍滿、連續設籍、設籍達、設籍六個月、設籍一年、居住滿、連續居住 | 生兒出生、新生兒出、籍本縣滿、兒出生日、出生之日、往前推算、兒之父、母或父 | 139 |
| `residence.current_city` | city |  | all | 目前居住縣市 | 你目前實際居住在哪個縣市？ | low | ✓ |  | 實際居住、居住地、現居、居住於本市 | 且實際、居住國內、國內超過、住國內超、年居住國、居住本縣、最近一年、近一年居 | 272 |
| `residence.same_household_as_parent` | boolean |  | education、social_welfare | 與父母同戶籍 | 你是否與父母同一戶籍？ | medium |  |  | 同一戶籍、同戶、共同生活 | 直系血親、扶養、配偶、親屬、義務、納稅義務、稅義務人、扶養親屬 | 66 |
| `household.size` | number |  | all | 家庭人口數 | 你的家庭（同一戶）共有幾人？ | medium |  |  | 家庭人口、全家人口、家戶人口、人口數 | 家庭總、總收入、庭總收、人每月、最低生、每人每、未超、低生活 | 64 |
| `household.income_year` | number | TWD_year | all | 家庭年所得 | 你的家庭年所得大約是多少（新臺幣）？ | high |  |  | 家庭年所得、家庭所得、年所得、年收入、家庭總收入、所得總額、綜合所得、家戶所得 | 人每月、每人每、生活費、最低生、低生活、家人口、全家人、當年度 | 59 |
| `household.income_month` | number | TWD_month | all | 家庭月所得 | 你的家庭每月所得大約是多少？ | high |  | household.income_year / 12 | 每月所得、月收入、月所得 | 收入未、配全家人、均分配全、分配全家、入平均分 | 0 |
| `household.income_per_capita` | number | TWD_month | all | 家庭每人每月平均所得 | 你的家庭平均每人每月所得大約是多少？ | high |  | household.income_month / household.size | 平均每人每月、每人每月收入、每人每月所得、平均所得、家庭總收入平均分配全家人口 | 生活費、最低生、低生活、未超、當年度、每月最低、月最低生、人每月最 | 55 |
| `household.income_vs_poverty_line` | number | multiple | all | 每人所得為最低生活費的倍數 | 你的家庭每人每月所得約為當地最低生活費的幾倍？ | high |  | household.income_per_capita / poverty_line(residence.household_city) | 最低生活費、最低生活費標準、最低生活費1.5倍、最低生活費2倍、最低生活費2.5倍、倍 | 每人每、人每月、家庭總、庭總收、當年度、家人口、全家人、未超 | 88 |
| `household.assets` | number | TWD | education、social_welfare、housing、long_term_care | 家庭財產總額 | 你的家庭動產與不動產總額大約是多少？ | high |  |  | 動產、不動產、財產、存款、財產總額、土地及房屋價值 | 全家人、家人口、未超、合計、總收入、庭總收、家庭總、清單 | 161 |
| `household.dependents` | number |  | social_welfare | 扶養人數 | 你需要扶養幾位家人？ | medium |  |  | 扶養、扶養親屬、受扶養 | 義務、義務人、合所得稅、綜合所得、無力、能力、共同生活、離婚 | 53 |
| `financial.receiving_public_funding` | boolean |  | education | 公費生 | 你目前是否為公費生（享有公費待遇）？ | low |  |  | 公費、公費生、公費待遇、享有公費 | 安置、收容、收容安置、未接受、未經政府、政府、未接受公、政府其他 | 116 |
| `financial.receiving_other_benefit` | multi_enum | government_scholarship、tuition_waiver、student_aid、living_allowance、long_term_care、none | all | 目前領取中的政府補助 | 你目前已領取哪些政府補助或獎助？ | medium |  |  | 已領、已受領、已領取、領有其他、重複領取、不得重複、擇一、同性質補助、已享有 | 重複申請、返還、相同、追回已、請領、相同性質、同時符合、重複請領 | 166 |
| `financial.student_loan` | boolean |  | education | 就學貸款 | 你是否有申請就學貸款？ | medium |  |  | 就學貸款、助學貸款 | 通知書、加蓋印章、繳費單影、除須、費明細、辦理就學、學校加蓋、檢附銀行 | 2 |
| `financial.labor_insured` | boolean |  | labor | 有勞保／就業保險 | 你是否有勞工保險或就業保險？ | medium | ✓ |  | 就業保險、勞工保險、勞保、被保險人、投保 | 給付、失業、保局、國民年金、參加、生育給付、薪資、失業給付 | 141 |
| `identity.low_income` | boolean |  | all | 低收入戶 | 你是否具有低收入戶身分？ | high | ✓ |  | 低收入戶、低收 | 活津貼、活補助、生活補、老人生活、人生活津、看護、看護費、住院看護 | 133 |
| `identity.middle_low_income` | boolean |  | all | 中低收入戶 | 你是否具有中低收入戶身分？ | high | ✓ |  | 中低收入戶、中低收 | 活津貼、收入老人、低收入老、入戶證明、收入戶證、老人生活、列冊低收、冊低收入 | 229 |
| `identity.economic_hardship` | boolean |  | education | 清寒 | 你是否有清寒證明（村里長證明或學校認定）？ | high |  |  | 清寒、家境清寒 | 獎學金、優秀學生、生獎學金、秀學生獎、學生獎學、學校、獎助資格、學年度第 | 52 |
| `identity.special_circumstances` | boolean |  | all | 特殊境遇家庭 | 你是否為特殊境遇家庭？ | high |  |  | 特殊境遇家庭、特殊境遇 | 家庭扶助、家庭子女、條例第、遇家庭扶、歲之兒童、女生活津、符合特、庭扶助條 | 44 |
| `identity.indigenous` | boolean |  | all | 原住民 | 你是否具有原住民身分？ | high | ✓ |  | 原住民、原住民族 | 年滿、委員會、資料來源、市年滿、民身分、設籍本市、籍本市年、生助學金 | 10 |
| `identity.indigenous_tribe` | enum | 阿美族、泰雅族、排灣族、布農族、卑南族、魯凱族、鄒族、賽夏族… | education、social_welfare | 族別 | 你的族別是？ | high |  |  | 族別、雅美族、達悟族、阿美族、泰雅族、排灣族、布農族 | 設籍臺東、般助學金、籍臺東縣、蘭嶼鄉、族身分、申請一般、縣蘭、成績達 | 1 |
| `identity.hakka` | boolean |  | education | 客家 | 你是否為客家子弟？ | medium |  |  | 客家、客家子弟 |  | 0 |
| `identity.new_immigrant` | boolean |  | all | 新住民（含子女） | 你是否為新住民或新住民子女？ | high |  |  | 新住民、新移民、外籍配偶 | 居留證、遭逢特殊、逢特殊境、社會處婦、民遭、機票、培力、設籍前新 | 6 |
| `identity.single_parent` | boolean |  | all | 單親家庭 | 你是否來自單親家庭？ | high |  |  | 單親 | 培力、未成年、扶養、扶養事實、無扶養事、子女共同、家長、年子女權 | 12 |
| `identity.grandparent_family` | boolean |  | education、social_welfare | 隔代教養 | 你是否為隔代教養家庭？ | high |  |  | 隔代教養 |  | 0 |
| `identity.orphan` | boolean |  | education、social_welfare | 失依兒少 | 你是否為失依兒少（父母雙亡或無法扶養）？ | high |  |  | 失依、孤兒 | 依兒童、困苦、助要點、年生活扶、少年生活、湖縣政府、澎湖縣政 | 13 |
| `identity.veteran_family` | boolean |  | education | 榮民子女／榮眷 | 你是否為榮民或榮眷子女？ | medium |  |  | 榮民、榮眷 | 就養、子女獎、民就、入戶生活、收入戶生、服務處、外就、民之家 | 13 |
| `identity.military_civil_bereaved` | boolean |  | education | 軍公教遺族 | 你是否為軍公教遺族？ | medium |  |  | 軍公教遺族、遺族 | 優待、傷殘、族就、軍公教人、眷子女、公教人員、因公、用優 | 6 |
| `identity.unemployed_worker_child` | boolean |  | education、labor | 失業勞工子女 | 你的父母是否為非自願離職的失業勞工？ | high |  |  | 失業勞工子女、非自願離職 | 子女就學、女就學補、離職證明、合計滿、定期契約、未請領、老年給付、保險人因 | 15 |
| `identity.overseas_chinese` | boolean |  | education | 僑生 | 你是否為僑生？ | medium | ✓ |  | 僑生 | 行優、優良、僑務委員、務委員會、生獎學金、公告標題、學校學、慰問金 | 6 |
| `identity.foreign_student` | boolean |  | education | 外籍生 | 你是否為外籍學生？ | medium | ✓ |  | 外籍生、國際學生 |  | 0 |
| `identity.tags` | multi_enum | low_income、middle_low_income、economic_hardship、special_circumstances、disadvantaged、indigenous、yami、hakka… | all | 身分標籤 | 你是否具有下列任一身分？ | high |  | tags |  |  | 2065 |
| `disability.has_certificate` | boolean |  | disability、long_term_care、education、social_welfare、housing、labor | 身心障礙證明 | 你（或受照顧者）是否領有身心障礙證明？ | high | ✓ |  | 身心障礙證明、身心障礙手冊、身心障礙者、身障 | 活補助、生活補、用補助、費用補、日間照顧、有身心障、照顧費用、住宿式照 | 144 |
| `disability.certificate_level` | enum（有序） | 輕度、中度、重度、極重度 | disability、long_term_care、education、social_welfare | 身心障礙等級 | 身心障礙證明的等級是？ | high | ✓ |  | 障礙等級、輕度、中度、重度、極重度、中度以上、重度以上 | 失能、度身心障、每月補助、常生活活、生活活動、日常生活、人每月、活活動功 | 175 |
| `disability.category` | multi_enum | 第一類、第二類、第三類、第四類、第五類、第六類、第七類、第八類 | disability | 障礙類別 | 身心障礙證明的障礙類別是？ | high |  |  | 障礙類別、肢體障礙、視覺障礙、聽覺障礙、智能障礙、精神障礙、自閉症 | 訓練服務、精神病、障礙者個、個別化、失智症、視力、彈性、針對 | 9 |
| `disability.family_member_has_certificate` | boolean |  | education、social_welfare | 家中有身心障礙者 | 你的父母或家人是否領有身心障礙證明？ | high |  |  | 身心障礙人士子女、身心障礙者子女、家中有身心障礙者 | 障礙學生、心障礙學、費用減免、子女就學、學費用減、就學費用、女就學費、減免辦法 | 8 |
| `care.cms_level` | number | level | long_term_care | 長照需要等級（CMS） | 照顧管理專員評估的長照需要等級（CMS）是第幾級？ | high | ✓ |  | CMS、長照需要等級、照顧管理評估、失能等級、第2級以上、評估為第 | 經評估、期照顧管、管理中心、心評估、長期照顧、經長、要等級第、適用長照 | 43 |
| `care.needs_care` | boolean |  | long_term_care、social_welfare、disability | 失能／需照顧 | 你（或受照顧者）是否經評估為失能或需要他人照顧？ | high | ✓ |  | 失能、失能者、日常生活需他人協助、需照顧、生活無法自理、巴氏量表 | 重度、評估、長期照顧、生活活動、常生活活、活活動功、活動功能、期照顧管 | 66 |
| `care.adl_score` | number | score | long_term_care | 巴氏量表分數 | 巴氏量表（ADL）分數是多少？ | high |  |  | 巴氏量表、ADL、日常生活活動功能 | 失能、失能程度、估為重度、評估為重、作日、家人照顧、評估、能量 | 4 |
| `care.institutional_placement` | boolean |  | long_term_care、social_welfare、disability | 已入住機構 | 你（或受照顧者）目前是否已入住安養或住宿式機構？ | high | ✓ |  | 機構安置、入住機構、住宿式機構、安置於機構、全日型機構、護理之家 | 福利機構、住宿式服、宿式服務、精神、會福利機、長期照顧、實際入住、人福利機 | 66 |
| `care.has_foreign_caregiver` | boolean |  | long_term_care | 聘有外籍看護 | 家中是否聘有外籍看護工？ | medium |  |  | 外籍看護、外籍家庭看護工、聘僱外籍、外勞 | 業服務法、依就業、法相關規、工同、請假、籍看護工、無法協助、同住 | 33 |
| `care.is_primary_caregiver` | boolean |  | long_term_care | 主要照顧者 | 你是否為家中失能者的主要照顧者？ | medium |  |  | 照顧者、主要照顧者、家庭照顧者 | 實際照顧、受照顧、實際、應符合、合下列規、列規定、人照顧、失能程度 | 81 |
| `care.dementia_diagnosis` | boolean |  | long_term_care、health | 失智診斷 | 你（或受照顧者）是否有失智症診斷？ | high |  |  | 失智、失智症、認知功能 | 民之家、走失、精神、歲以上失、輔導會、養護、有走失、會所屬 | 5 |
| `health.catastrophic_illness` | boolean |  | health、social_welfare、education | 重大傷病 | 你是否持有重大傷病證明（卡）？ | high |  |  | 重大傷病、重大傷病卡、重大傷病證明 | 疾病、有工作能、父母、工作能力、遭遇重大、致不能工、不能工作、孫子女 | 34 |
| `health.specific_disease` | text |  | health、education | 特定疾病 | 你是否患有特定疾病（請說明）？ | high |  |  | 罕見疾病、癌症、洗腎、燒燙傷、病童、重症 | 重大傷病、符合衛生、利部公告、福利部公、合衛生福、大傷病證、傷病證明、康保險重 | 0 |
| `employment.status` | enum | employed、unemployed、student、retired、self_employed | labor、youth、housing、social_welfare | 就業狀態 | 你目前的就業狀態？ | medium | ✓ |  | 失業、非自願離職、待業、求職、在職、就業中、離職 | 勞工、就業服務、就業保險、公立就業、失蹤、業服務機、立就業服、服務機構 | 128 |
| `employment.unemployed_months` | number | months | labor | 失業月數 | 你已經失業多久了？（月） | medium |  |  | 失業期間、連續失業、離職滿、待業期間 | 連續達 | 19 |
| `employment.involuntary_separation` | boolean |  | labor | 非自願離職 | 你是否為非自願離職（被資遣、關廠等）？ | medium |  |  | 非自願離職、資遣、關廠、歇業、非自願性失業 | 失業給付、領失業給、就業保險、失業證明、業保險法、請領條件、件及相關、合就業 | 30 |
| `employment.insured_years` | number | years | labor | 就業保險年資 | 你的就業保險年資累計幾年？ | medium |  |  | 保險年資、投保年資、年資合計、累計年資 | 合計滿 | 5 |
| `employment.is_middle_aged` | boolean |  | labor | 中高齡（45 歲以上） | 你是否年滿 45 歲？ | low |  | applicant.age >= 45 | 中高齡、高齡者、45歲以上、65歲以上勞工 | 失業、就業保險、就業、住處所距、處所距離、原日常居、就業地點、地點與原 | 7 |
| `employment.in_training` | boolean |  | labor | 參加職業訓練 | 你是否正在或即將參加政府核定的職業訓練？ | low |  |  | 職業訓練、職訓、受訓、全日制訓練 | 活津貼、生活津、失業給付、核付、就業、業保險法、安排、就業保險 | 43 |
| `housing.tenure` | enum | own、rent、family、dorm、none | housing、education、social_welfare | 居住型態 | 你目前的居住型態？ | medium | ✓ |  | 租屋、租賃、承租、自有住宅、無自有住宅、住宿、宿舍 | 日間照顧、契約、照顧費用、心障礙、身心障、顧費用補、租金補、房屋租 | 337 |
| `housing.rent_month` | number | TWD_month | housing | 每月租金 | 你每月的租金是多少？ | medium |  |  | 租金、每月租金、房租 | 補貼、金補、房屋租、金補助、貸款利息、利息補貼、款利息補、租賃 | 73 |
| `housing.owns_property` | boolean |  | housing、social_welfare | 持有自有住宅 | 你或家庭成員是否持有自有住宅？ | high |  |  | 自有住宅、持有住宅、無自有住宅、房屋、名下 | 租賃、土地、價值、有權、租金補助、租賃契約、建物、補貼 | 148 |
| `family.children_count` | number |  | social_welfare、housing | 子女數 | 你有幾位子女？ | medium |  |  | 子女、子女數、未成年子女、第三名子女、第二名子女 | 扶養、離婚、父母、未婚、遭遇、義務、婚生子、懷孕 | 63 |
| `family.youngest_child_age` | number | years | social_welfare | 最小子女年齡 | 你最小的子女幾歲？ | medium | ✓ |  | 未滿2歲、未滿5歲、2歲以上、幼兒、學齡前、入國民小學前 | 育兒津貼、歲兒童、兒童育兒、歲兒童育、童育兒津、就學補助、育有未滿、監護人 | 138 |
| `family.pregnant` | boolean |  | social_welfare、health | 懷孕 | 你是否懷孕中？ | high |  |  | 懷孕、孕婦、妊娠 | 未婚、分娩、婦女、遭遇困境、生育、流產、生產、婚生子女 | 51 |
| `family.child_in_public_daycare` | boolean |  | social_welfare | 子女送托公共／準公共托育 | 你的子女是否送托公共托育或準公共托育單位？ | low |  |  | 公共托育、準公共、托嬰中心、送托、居家托育 | 托育服務、托育人員、服務、服務中心、歲兒童、兒童托育、公共化、服務費用 | 131 |
| `family.on_parental_leave` | boolean |  | social_welfare、labor | 育嬰留職停薪中 | 你是否正在育嬰留職停薪？ | medium |  |  | 育嬰留職停薪、育嬰留停、育嬰假 | 就保、薪資補、保育、資補助、被保險人、請領、得請領、請領育 | 20 |
