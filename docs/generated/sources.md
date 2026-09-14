# 官方來源登錄與驗證結果

來源：`backend/benefit_crawler/config/sources.yaml` + `official_domains.yaml`；驗證方法為網域白名單／後綴 + HTTPS + 頁面標題關鍵字。

| id | 名稱 | 機關 | 類型 | 啟用 | 領域 | 頁面數（略過） | 追連結 | 網域驗證 | crawler |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| helpdreams_gov | 教育部圓夢助學網 — 政府機關獎助學金 | 教育部 | mixed | ✓ | education | 0（0） |  | ✅ manual_whitelist + https | `HelpDreamsGovernmentCrawler` |
| helpdreams_private | 教育部圓夢助學網 — 民間團體獎助學金 | 教育部 | private_organization | ✓ | education | 0（0） |  | ✅ manual_whitelist + https | `HelpDreamsPrivateCrawler` |
| moe_programs | 教育部圓夢助學網 — 教育部助學措施 | 教育部 | central_government | ✓ | education | 5（0） |  | ✅ manual_whitelist + https | `MoeAssistanceProgramCrawler` |
| cip_regulations | 原住民族委員會 — 獎助大專校院原住民學生實施要點 | 原住民族委員會 | central_government | ✓ | education | 1（0） |  | ✅ manual_whitelist + https | `CipRegulationCrawler` |
| yda_youth | 教育部青年發展署 | 教育部青年發展署 | central_government |  | youth | 0（0） |  | ✅ manual_whitelist + https | `YouthDevelopmentCrawler` |
| keelung_edu | 基隆市政府教育處 — 處務公告／最新消息 | 基隆市政府教育處 | local_government | ✓ | education | 0（0） |  | ✅ manual_whitelist + https | `KeelungEducationCrawler` |
| taipei_doe | 臺北市政府教育局 — 一般公告 | 臺北市政府教育局 | local_government | ✓ | education | 0（0） |  | ✅ manual_whitelist + https | `TaipeiEducationCrawler` |
| district_offices | 各區／鄉／鎮公所公告（設定檔驅動） | 地方行政機關 | township |  |  | 0（0） |  | ✅ manual_whitelist + https | `DistrictOfficeCrawler` |
| ntou_stu | 國立臺灣海洋大學 學務處生輔組 — 校外獎學金公告 | 國立臺灣海洋大學學生事務處 | school | ✓ | education | 0（0） |  | ✅ manual_whitelist + https | `NtouScholarshipCrawler` |
| gov_tw_services | 我的E政府 — 申辦服務與主題策展（補助總整理） | 國家發展委員會（我的E政府） | mixed | ✓ | education、social_welfare、labor、housing、long_term_care、disability | 9（0） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| taipei_dosw | 臺北市政府社會局 — 社會救助、老人福利、身心障礙、長期照顧 | 臺北市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 11（1） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| taipei_health | 臺北市政府衛生局 — 長照服務內容 | 臺北市政府衛生局 | local_government | ✓ | long_term_care | 1（0） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| taipei_ws_files | 臺北市政府 — 社會局／衛生局附件（PDF） | 臺北市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 12（0） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| mol_gov | 勞動部全球資訊網 — 業務專區 | 勞動部 | central_government | ✓ | labor | 2（0） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| wda_emps | 勞動部勞動力發展署（台灣就業通）— 勞工補助 | 勞動部勞動力發展署 | central_government | ✓ | labor、youth | 1（0） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| mol_opendata | 勞動部開放資料 — 職工福利概況 | 勞動部 | central_government | ✓ | labor | 2（2） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| mohw_gov | 衛生福利部 — 衛生福利e寶箱／長期照顧 | 衛生福利部 | central_government | ✓ | social_welfare、long_term_care、disability、health | 3（0） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| ltc_1966 | 衛福部長照專區（1966 專線）— 服務項目與給付 | 衛生福利部長期照顧司 | central_government | ✓ | long_term_care | 2（0） | 深度 2 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| mohw_opendata | 衛生福利部開放資料 — 老人長期照顧、安養機構 | 衛生福利部 | central_government | ✓ | long_term_care | 1（1） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| moi_pip | 內政部不動產資訊平台 — 租金補貼專區 | 內政部國土管理署 | central_government | ✓ | housing | 1（0） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| moe_law | 教育部主管法規查詢系統 — 補貼要點 | 教育部 | central_government | ✓ | education | 1（0） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| taipei_opendata | 臺北市資料大平臺 — 長照服務與機構名單 | 臺北市政府 | local_government | ✓ | long_term_care | 4（0） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| taichung_opendata | 臺中市資料開放平臺 — 老人福利機構 | 臺中市政府 | local_government | ✓ | social_welfare、long_term_care | 3（2） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| bot_student_loan | 臺灣銀行就學貸款入口（非官方公告來源） | 臺灣銀行 | unknown | ✓ | education | 1（1） |  | ⚠️ blocklist | `GenericPageCrawler` |
| kaohsiung_sw | 高雄市政府社會局 — 生育、育兒、社會救助、老人福利 | 高雄市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 41（1） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| mohw_social_assistance | 衛生福利部社會救助及社工司 — 低收入戶、中低收入戶、急難救助 | 衛生福利部社會救助及社工司 | central_government | ✓ | social_welfare | 15（5） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| ntpc_banqiao_office | 新北市板橋區公所 — 社會課受理的補助與救助 | 新北市板橋區公所 | township | ✓ | social_welfare、disability | 16（4） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| ntpc_sw | 新北市政府社會局 — 生育獎勵、育兒、社會救助、老人福利 | 新北市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 33（8） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| sfaa_childcare | 衛生福利部社會及家庭署 — 育兒津貼、托育補助、兒少福利 | 衛生福利部社會及家庭署 | central_government | ✓ | social_welfare | 16（5） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| taichung_sw | 臺中市政府社會局 — 生育、育兒、社會救助、老人福利 | 臺中市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 84（10） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| taipei_daan_office | 臺北市大安區公所 — 社會課受理的補助與救助 | 臺北市大安區公所 | township | ✓ | social_welfare、disability | 11（4） | 深度 1 | ✅ domain_suffix:gov.taipei + https | `GenericPageCrawler` |
| taoyuan_sw | 桃園市政府社會局 — 社會救助、兒少福利、老人福利、身心障礙 | 桃園市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 51（1） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| tainan_sw | 臺南市政府社會局 — 生育、育兒、社會救助、老人福利 | 臺南市政府社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 76（7） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| keelung_sw | 基隆市政府社會處 — 生育、育兒、社會救助、老人福利 | 基隆市政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 49（5） | 深度 1 | ✅ manual_whitelist + https | `GenericPageCrawler` |
| hsinchu_city_sw | 新竹市政府社會處 — 生育、育兒、社會救助、老人福利 | 新竹市政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 68（0） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| hsinchu_county_sw | 新竹縣政府社會處 — 生育、育兒、托育、社會救助、特殊境遇家庭 | 新竹縣政府社會處 | local_government | ✓ | social_welfare | 27（1） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| miaoli_sw | 苗栗縣政府社會處 — 生育、育兒、社會救助、老人福利 | 苗栗縣政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 59（18） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| changhua_sw | 彰化縣政府社會處 — 生育、育兒、社會救助、老人福利 | 彰化縣政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 62（1） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| nantou_sw | 南投縣政府社會及勞動局 — 生育、育兒、社會救助、老人福利 | 南投縣政府社會及勞動局 | local_government | ✓ | social_welfare、long_term_care、disability | 49（19） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| chiayi_city_sw | 嘉義市政府社會處 — 生育、育兒、社會救助、老人福利 | 嘉義市政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 67（13） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| bli_family | 勞動部勞工保險局 — 生育給付（勞保、國保、農保）、勞工生育補助、育嬰留職停薪津貼 | 勞動部勞工保險局 | central_government | ✓ | labor、social_welfare | 23（8） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| taoyuan_zhongli_office | 桃園市中壢區公所 — 社會課受理的補助與救助 | 桃園市中壢區公所 | township | ✓ | social_welfare、disability | 18（11） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| tainan_east_office | 臺南市東區區公所 — 社會課受理的補助與救助 | 臺南市東區區公所 | township | ✓ | social_welfare、disability | 26（6） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| ece_moe | 教育部國教署全國教保資訊網 — 幼兒園就學補助 | 教育部國民及學前教育署 | central_government | ✓ | education、social_welfare | 9（4） |  | ✅ manual_whitelist + https | `GenericPageCrawler` |
| chiayi_county_sw | 嘉義縣社會局 — 生育、育兒、社會救助、老人福利 | 嘉義縣社會局 | local_government | ✓ | social_welfare、long_term_care、disability | 70（9） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| hualien_sw | 花蓮縣政府社會處 — 生育、育兒、社會救助、老人福利 | 花蓮縣政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 48（6） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| kinmen_sw | 金門縣政府社會處 — 生育、育兒、社會救助、老人福利 | 金門縣政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 78（0） | 深度 1 | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| yilan_sw | 宜蘭縣政府社會處 — 生育、育兒、社會救助、老人福利 | 宜蘭縣政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 44（8） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |
| penghu_sw | 澎湖縣政府社會處 — 生育、育兒、社會救助、老人福利 | 澎湖縣政府社會處 | local_government | ✓ | social_welfare、long_term_care、disability | 57（4） |  | ✅ domain_suffix:gov.tw + https | `GenericPageCrawler` |

## 略過的頁面（記錄原因，資料不進正式資料表）

| 來源 | 頁面 | 網址 | 原因 |
| --- | --- | --- | --- |
| taipei_dosw | 臺北市老人照顧與失智服務地圖 | https://map.dosw.gov.taipei/taipeiWelfare_map/all_new/care_map.aspx | 互動式服務地圖（JavaScript 地圖應用），沒有可抽取的補助條文；服務據點請見 providers 資料 |
| mol_opendata | 職工福利概況（CSV） | https://apiservice.mol.gov.tw/OdService/download/A17000000J-020150-uE4 | 統計資料（職工福利事業概況統計表），不是可申請的補助條文 |
| mol_opendata | 職工福利概況（JSON） | https://apiservice.mol.gov.tw/OdService/download/A17000000J-020150-32X | 統計資料（同一資料集的 JSON 格式） |
| mohw_opendata | 老人長期照顧、安養機構所數及可供進住人數 | https://www.opendata.mohw.gov.tw/dataset/opendata/sfaa/161626/%E8%80%81%E4%BA%BA | 統計資料（各縣市機構所數與床位數），不是可申請的補助條文 |
| taichung_opendata | 臺中市老人福利機構（JSON） | https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a342f | 同一資料集的 JSON 格式（CSV 已匯入） |
| taichung_opendata | 臺中市老人福利機構（XML） | https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=dc448 | 同一資料集的 XML 格式（CSV 已匯入） |
| bot_student_loan | 高級中等以上學校學生就學貸款 | https://sloan.bot.com.tw/customer/login/SLoanLogin.action | 銀行登入頁（sloan.bot.com.tw 非 gov.tw／edu.tw 官方網域，且需登入），沒有公告條文可抽取；就學貸款規定請見教育部圓夢助學網 |
| kaohsiung_sw | 高雄市0-6歲育兒補助簡介 | https://socbu.kcg.gov.tw/index.php?prog=2&b_id=25&m_id=126&s_id=2819 | 頁面只有 PDF 附件（簡介與宣導單張），沒有可抽取的內文；各項補助已分別列於 s_id=760/626/526/2341/770 |
| mohw_social_assistance | 低收入戶、中低收入戶常見問答 | https://dep.mohw.gov.tw/DOSAASW/cp-572-5035-103.html | 問答集（FAQ）依收錄政策排除；申請條件內容已由資格審核標準 PDF 涵蓋 |
| mohw_social_assistance | 衛生福利部辦理災害救濟捐款專戶慰問金發放要點 | https://dep.mohw.gov.tw/DOSAASW/cp-576-44095-103.html | 頁面只有 docx／odt 附件與申請表單，爬蟲不解析 docx；要點本文沒有 HTML 或 PDF 版本 |
| mohw_social_assistance | 115年度低收入戶類別條件一覽表 | https://www.mohw.gov.tw/dl-97290-0b65921d-b09a-426b-996e-3346f5b61e9d.html | 標題為一覽表（依收錄政策視為名單／窗口類排除）；各款類別條件屬資格審核標準的補充 |
| mohw_social_assistance | 兒童及少年未來教育與發展帳戶宣導摺頁 | https://www.mohw.gov.tw/dl-58806-bdcafdda-cb96-4daa-852f-50b4a26be59b.html | PDF 使用自訂字型編碼，pypdf 抽出來是亂碼；方案條文只存在於條例本文（法律本文依政策排除） |
| mohw_social_assistance | 生活扶助法令解釋 | https://dep.mohw.gov.tw/DOSAASW/cp-571-5013-103.html | 歷年函釋彙編（14 萬字），不是方案內容頁 |
| ntpc_banqiao_office | 弱勢兒童及少年生活扶助 | https://www.banqiao.ntpc.gov.tw/uploaddowndoc?file=banqiao02/202304251640020.pdf | PDF 只有兩題問答（健保費、其他福利），沒有完整申請資格（410 字） |
| ntpc_banqiao_office | 強化社會安全網-急難紓困實施方案 | https://www.banqiao.ntpc.gov.tw/uploaddowndoc?dis=banqiao02&file=banqiao02/20230 | PDF 只有服務對象與申請程序、沒有給付金額（433 字），內容不足以成為一筆方案 |
| ntpc_banqiao_office | 社會福利業務（常見問題清單） | https://www.banqiao.ntpc.gov.tw/home.jsp?id=cde22cf69925c531&pagesize=100&page=1 | 目錄頁：17 筆社福業務清單，各項目直接連到 PDF，方案內容已分別列在 pages |
| ntpc_banqiao_office | 板橋區社會福利表格下載區 | https://www.banqiao.ntpc.gov.tw/home.jsp?id=a1889b4d7b31ee0e | 只有申請表單下載，沒有方案內文 |
| ntpc_sw | 0~2歲擴大育兒津貼及準公共化托育專區 | https://www.sw.ntpc.gov.tw/home.jsp?id=5867b2cfdc1aad19&act=be4f48068b2b0031&dat | 只有法令依據、名冊與申請表的附件連結清單，資格與金額都在附件裡 |
| ntpc_sw | 弱勢家庭兒童夜間暨臨時托育補助 | https://www.sw.ntpc.gov.tw/home.jsp?id=b2dfefc09cf046f2&act=be4f48068b2b0031&dat | 頁面只有實施計畫與申請表附件清單，沒有方案內文 |
| ntpc_sw | 新北市政府臨時托育服務 | https://www.sw.ntpc.gov.tw/home.jsp?id=b2dfefc09cf046f2&act=be4f48068b2b0031&dat | 頁面只有服務計畫附件，沒有方案內文 |
| ntpc_sw | 新北育兒資訊網 | https://lovebaby.sw.ntpc.gov.tw/ | Angular 單頁應用（#/ 路由），福利內容由 JavaScript 動態載入，伺服器端只有空殼 |
| ntpc_sw | 社會救助業務總覽 | https://www.sw.ntpc.gov.tw/home.jsp?id=dff618d9d6f956fa | 只是分類目錄頁（各方案連到 service.ntpc.gov.tw 申辦 E 服務，跨主機無法用 follow_links 追） |
| ntpc_sw | 新北市獨居老人照顧關懷服務計畫 | https://www.sw.ntpc.gov.tw/home.jsp?id=bd3ac04bd17eafde&act=be4f48068b2b0031&dat | 機關間的實施計畫（依據、目的、執行單位分工），沒有民眾申請資格與申請方式 |
| ntpc_sw | 老人福利業務總覽 | https://www.sw.ntpc.gov.tw/home.jsp?id=bd3ac04bd17eafde | 只是分類目錄頁（分頁靠 POST 表單，方案多連到 service.ntpc.gov.tw） |
| ntpc_sw | 身心障礙者日間照顧及住宿式照顧費用補助 | https://www.sw.ntpc.gov.tw/home.jsp?id=d4abdaae79035953&act=be4f48068b2b0031&dat | 頁面只有申請規定與補助標準一覽表的附件連結，沒有方案內文 |
| sfaa_childcare | 弱勢兒童及少年醫療補助 | https://www.sfaa.gov.tw/sfaa/list/detail/5i3/5BH | 內文只有一段 188 字摘要且無金額；資格與給付內容在「弱勢兒童及少年生活扶助與托育及醫療費用補助辦法」PDF（已另收） |
| sfaa_childcare | 育兒津貼及托育準公共專區 | https://www.sfaa.gov.tw/sfaa/list/5d3 | 專區目錄頁，只有各公告的連結 |
| sfaa_childcare | 0~6歲國家跟你一起養2.0 | https://www.sfaa.gov.tw/sfaa/list/detail/5d3/5Ur | 只有宣導圖片，沒有可抽取的文字 |
| sfaa_childcare | 未滿2歲兒童托育補助問答集 | https://www.sfaa.gov.tw/sfaa/list/detail/5d3/5KG | 問答集（FAQ）附件頁，收錄政策排除 |
| sfaa_childcare | 原住民兒童零至二歲托育服務補助要點 | https://www.sfaa.gov.tw/sfaa/list/detail/5eK/5XX | 補助對象為試辦單位（地方政府／民間團體）的開辦與營運經費，不是民眾可申請的給付 |
| taichung_sw | 臺中市平價托育及準公共服務實施計畫（網頁） | https://www.society.taichung.gov.tw/134479/post | 網頁內文只有依據、目的與各區承辦人分機，實施對象與托育費用／補助規定在附件計畫 PDF（已另列為 pdf 頁面） |
| taichung_sw | 臺中市獨居老人服務計畫 | https://www.society.taichung.gov.tw/461592/post | 內文是計畫目標、執行單位與四區委託單位電話，沒有個人申請資格與給付內容 |
| taichung_sw | 中低收入戶健保費減免 | https://www.society.taichung.gov.tw/135817/post | 內文只有一句（補助全民健保費二分之一＋洽詢電話，47 字），資格與申請方式在附件裡 |
| taichung_sw | 低收入戶及中低收入戶核列與福利一覽表 | https://www.society.taichung.gov.tw/135811/post | 各行政區承辦人聯絡表＋福利項目一覽，屬名單／一覽表，不是單一方案頁 |
| taichung_sw | 準公共化托育服務 | https://www.society.taichung.gov.tw/2286918/normalURL | 育兒資訊專區的外部轉址項目，頁面沒有內文（0 字） |
| taichung_sw | 社會救助－低收及中低收入戶（目錄） | https://www.society.taichung.gov.tw/13862/Lpsimplelist | 分類目錄頁，方案內容頁已逐一列入 |
| taichung_sw | 社會救助－災害、急難救助（目錄） | https://www.society.taichung.gov.tw/13865/Lpsimplelist | 分類目錄頁，方案內容頁已逐一列入 |
| taichung_sw | 老人福利（目錄） | https://www.society.taichung.gov.tw/13783/Lpsimplelist | 分類目錄頁（兩頁、共 36 筆），方案內容頁已逐一列入 |
| taichung_sw | 身心障礙者福利（目錄） | https://www.society.taichung.gov.tw/13798/Lpsimplelist | 分類目錄頁（兩頁、共 58 筆），方案內容頁已逐一列入 |
| taichung_sw | 兒少－育兒資訊專區（目錄） | https://www.society.taichung.gov.tw/2285652/Lpsimplelist | 分類目錄頁，方案內容頁已逐一列入 |
| taipei_daan_office | 社會課服務項目 | https://dado.gov.taipei/News_Content.aspx?n=0783D7E57EDE1FB4&sms=4A389A5CC11718C | 只是業務目錄頁，連結多半指向社會局 dosw.gov.taipei（已由 taipei_dosw 收錄） |
| taipei_daan_office | 身心障礙證明申請 | https://dado.gov.taipei/News_Content.aspx?n=0783D7E57EDE1FB4&sms=4A389A5CC11718C | 只有鑑定流程與應備文件，沒有給付內容 |
| taipei_daan_office | 好便利櫃檯受理項目一覽表 | https://dado.gov.taipei/cp.aspx?n=B97F40B7B1A09872 | 只是受理項目名稱清單，沒有資格與給付 |
| taipei_daan_office | 重陽專區 | https://dado.gov.taipei/News.aspx?n=3B6B49D14C7D84A7&sms=D36FF802DE9B88C4 | 只有匯款同意書下載與社會局線上申請外部連結，沒有方案內文 |
| taoyuan_sw | 社會救助業務總覽 | https://sab.tycg.gov.tw/cl.aspx?n=7354 | 只是分類目錄頁（子項已逐一列在 pages） |
| tainan_sw | 一般戶老人假牙補助 | https://sab.tainan.gov.tw/News_Content.aspx?n=21370&s=4378301 | 內文只有「洽辦單位：衛生局」與電話，資格與補助金額在衛生局網站 |
| tainan_sw | 國民年金老年基本保證年金（原敬老福利生活津貼） | https://sab.tainan.gov.tw/News_Content.aspx?n=21369&s=4378298 | 只有一段說明改由勞保局依國民年金法發給，資格與金額請見勞保局（mol_gov／勞保局來源） |
| tainan_sw | 關懷獨居老人服務計畫 | https://sab.tainan.gov.tw/News_Content.aspx?n=21372&s=4888858 | 網頁只有承辦人與附件（服務計畫 PDF），沒有服務對象與內容條文 |
| tainan_sw | 居家身心障礙者維生器材及必要生活輔具用電優惠 | https://sab.tainan.gov.tw/News_Content.aspx?n=21384&s=4378401 | 內文只有承辦人與「服務內容、服務對象同經濟部、衛福部公告」一句，沒有資格與優惠內容 |
| tainan_sw | 不列入媒體資料交換之身心障礙者社會保險費補助 | https://sab.tainan.gov.tw/News_Content.aspx?n=21384&s=7670425 | 網頁只有附件清單（作業要點令與表單 PDF），沒有方案內文 |
| tainan_sw | 身心障礙者購買或承租商店攤販低利貸款或租金補貼（網頁） | https://sab.tainan.gov.tw/News_Content.aspx?n=21384&s=4378400 | 網頁只有附件清單（令、實施計畫、申請表），資格與補貼標準在實施計畫 PDF（已另列為 pdf 頁面） |
| tainan_sw | 0-6歲國家一起養 | https://sab.tainan.gov.tw/News_Content.aspx?n=21444&s=7755541 | 政策宣導頁，只有一段政策說明與圖片，資格與金額在育兒津貼／托育補助頁 |
| keelung_sw | 115年度擴大獨居老人服務實施計畫 | https://www.klcg.gov.tw/tw/social/2754-315781.html | 頁面主內容區沒有文字（計畫內容只在附件） |
| keelung_sw | 基隆市輔具服務資源簡介 | https://www.klcg.gov.tw/tw/social/2807-297391.html | 頁面主內容區沒有文字（只有圖片） |
| keelung_sw | 基隆市身心障礙者輔具費用補助相關規定 | https://www.klcg.gov.tw/tw/social/2696-112613.html | 頁面只有一個外部連結，沒有資格與補助內容 |
| keelung_sw | 基隆市低收入戶特殊救助項目補助辦法 | https://www.klcg.gov.tw/tw/social/2810-113164.html | 頁面只有一句話，辦法內容與申請表都在附件 |
| keelung_sw | 0-未滿2歲擴大育兒津貼（社會處舊頁） | https://www.klcg.gov.tw/tw/social/2770-112911.html | 頁面回傳空殼（沒有主內容區），育兒津貼已改由兒少處少子女化專區頁面提供 |
| hsinchu_county_sw | 0-6歲國家一起養2.0 | https://social.hsinchu.gov.tw/News_Content.aspx?n=2783&s=264093 | 頁面只有一張圖片（#CCMS_Content 只有標題 12 字），沒有可抽取的文字 |
| miaoli_sw | 苗栗縣兒童及少年生活扶助實施計畫（網頁） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=938214 | 網頁內文只有目的與法令依據（141 字），扶助對象與金額在附件實施計畫 PDF（已另列為 pdf 頁面） |
| miaoli_sw | 弱勢兒童及少年醫療補助審查及作業規定（網頁） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=938219 | 網頁內文只有目的與法令依據（179 字），補助對象與標準在附件作業規定 PDF（已另列為 pdf 頁面） |
| miaoli_sw | 苗栗縣中低收入老人未滿七十歲者補助全民健康保險費基準（申請表） | https://webws.miaoli.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDEwL3JlbGZpbGUvOTQ2 | 申辦須知的「老人健保費補助基準」項目只附申請表 PDF（405 字、全是表格欄位），沒有寫資格與補助標準的文件 |
| miaoli_sw | 苗栗縣低收入戶中低收入戶調查及發放 | https://webws.miaoli.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDEwL3JlbGZpbGUvOTYw | 申辦須知清單直接連到 .doc 檔（沒有網頁與 PDF 版本），crawler 不支援 doc 格式 |
| miaoli_sw | 修正苗栗縣辦理低收入戶與中低收入戶產婦及新生兒營養補助實施計畫（網頁） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=147156 | 網頁只有標題與 3 個附件連結（237 字），計畫內文在附件 PDF（已另列為 pdf 頁面） |
| miaoli_sw | 中低收入老人生活津貼發給辦法（網頁） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=938209 | 網頁只有標題與附件連結（186 字），辦法內文在附件 PDF（已另列為 pdf 頁面） |
| miaoli_sw | 中低收入老人特別照顧津貼發給辦法（網頁） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=938213 | 網頁只有標題與附件連結（186 字），辦法內文在附件 PDF（已另列為 pdf 頁面） |
| miaoli_sw | 苗栗縣特殊境遇家庭扶助計畫（網頁） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=40630 | 網頁只有 11 個附件連結（申請表、切結書、流程圖、實施計畫），資格與給付內文在主站 n=5615&s=260665 與附件 PDF（已另列） |
| miaoli_sw | 未滿二歲兒童托育準公共化服務費用申報（主站轉載） | https://www.miaoli.gov.tw/News_Content.aspx?n=5615&s=260692 | 與社會處 n=682&s=533082 內容相同（同一方案的主站轉載） |
| miaoli_sw | 苗栗縣中低收入老人住宅設施修繕設備補助辦法 | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=825667 | 網頁只有標題與 doc/odt 附件（164 字），沒有 PDF 可抽取 |
| miaoli_sw | 苗栗縣政府推展老人福利服務補助作業要點 | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=868067 | 對象是團體／機構的補助作業要點，網頁只有 doc 附件（146 字） |
| miaoli_sw | 苗栗縣政府辦理身心障礙者社會保險費補助異動書 | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=712683 | 純表單下載頁 |
| miaoli_sw | 權益一覽表 | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=682&s=993601 | 只有一個 4.5MB 的權益一覽表 PDF（多方案彙整表），不是單一方案頁 |
| miaoli_sw | 未滿2歲兒童育兒津貼托育費用補助（家長專區） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=11024&s=981256 | 頁面只有圖片與問答集／作業要點 PDF（152 字），育兒津貼內文請見主站 n=5615&s=260695 |
| miaoli_sw | 未滿2歲兒童托育公共化及準公共補助（家長專區） | https://www.miaoli.gov.tw/social_affairs/News_Content.aspx?n=11024&s=981258 | 頁面只有圖片（82 字），沒有可抽取內文 |
| miaoli_sw | 113年度辦理原住民族長者裝置假牙執行計畫（原住民族事務中心） | https://www.miaoli.gov.tw/News_Content2.aspx?n=295&s=723875 | 113 年度舊公告，網頁只有 doc/pdf/odt 附件（359 字） |
| miaoli_sw | 苗栗縣政府婦女福利服務資訊（目錄） | https://www.miaoli.gov.tw/News.aspx?n=5615&sms=13027 | 主站婦女福利服務資源整合平台的目錄頁，方案內容頁已逐一列入 |
| miaoli_sw | 托育服務專區－家長專區－補助資訊（目錄） | https://www.miaoli.gov.tw/social_affairs/News.aspx?n=11024&sms=15349 | 目錄頁，兩個項目都只有圖片 |
| changhua_sw | 社會救助專區目錄 | https://www.chcg.gov.tw/DTO/social/07other/other01_list.aspx?topsn=714 | 只是分類目錄頁（子項已逐一列在 pages） |
| nantou_sw | 南投縣特殊境遇家庭扶助申請及審核作業要點 | https://welfare.nantou.gov.tw/ViewService/FileDownload.ashx?id=476b3f60-61c5-4b9 | 掃描影像 PDF，pdf_to_text 抽不到文字（乾跑 0 字）；需要 OCR |
| nantou_sw | 中低收入老人生活津貼 | https://welfare.nantou.gov.tw/1486/1002 | 靜態 HTML 只有標題（14 字）；內文（補助對象、申請資格、補助標準每月 8 |
| nantou_sw | 中低收入老人特別照顧津貼 | https://welfare.nantou.gov.tw/1486/1001 | 同上，內文為 POST 載入的 P_Word partial（約 890 字） |
| nantou_sw | 中低收入老人醫療補助 | https://welfare.nantou.gov.tw/1486/1005 | 同上，內文為 POST 載入的 P_Word partial；規定內容已改列附件 PDF |
| nantou_sw | 低收入戶老人公費安養 | https://welfare.nantou.gov.tw/1486/1020 | 同上，內文為 POST 載入的 P_Word partial（約 535 字）；作業要點已改列附件 PDF |
| nantou_sw | 低收入戶老人公費養護 | https://welfare.nantou.gov.tw/1486/1021 | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| nantou_sw | 身心障礙生活補助 | https://welfare.nantou.gov.tw/1486/3007 | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| nantou_sw | 低收入戶生活補助（低收入戶申請） | https://welfare.nantou.gov.tw/1486/3041 | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| nantou_sw | 中低收入戶申請 | https://welfare.nantou.gov.tw/1486/3042 | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| nantou_sw | 低收入戶喪葬補助 | https://welfare.nantou.gov.tw/1486/3043 | 同上，內文為 POST 載入的 P_Word partial（約 320 字）；沒有附件 |
| nantou_sw | 低收入戶婦嬰營養補助 | https://welfare.nantou.gov.tw/1486/3044 | 同上，內文為 POST 載入的 P_Word partial（約 340 字）；附件只有領款收據 |
| nantou_sw | 低收入戶及中低收入戶傷病醫療補助 | https://welfare.nantou.gov.tw/1486/4001 | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| nantou_sw | 低收入戶及中低收入戶傷病住院看護補助 | https://welfare.nantou.gov.tw/1486/4002 | 同上，內文為 POST 載入的 P_Word partial（約 810 字）；實施計劃已改列附件 PDF |
| nantou_sw | 急難紓困實施方案 | https://welfare.nantou.gov.tw/1486/reliefsubsidy | 同上，內文為 POST 載入的 P_Word partial（約 3 |
| nantou_sw | 三節慰問金（春節、端午、中秋） | https://welfare.nantou.gov.tw/1486/326 | 同上，內文為 POST 載入的 P_Word partial（約 350 字）；附件只有清冊、名冊、領據 |
| nantou_sw | 微型保險 | https://welfare.nantou.gov.tw/1486/microinsurance | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| nantou_sw | 國民年金保費補助 | https://welfare.nantou.gov.tw/1486/1731 | 同上，內文為 POST 載入的 P_Word partial（約 580 字）；沒有附件 |
| nantou_sw | 國民年金生育給付 | https://welfare.nantou.gov.tw/1486/baby | 同上，內文為 POST 載入的 P_Word partial（約 820 字，含申請資格與給付標準）；沒有附件。縣府「南投縣生育獎勵金」不在本站（由民政處／各戶政事務所受理，縣府官網只有失效的新聞頁與法規系統條文） |
| nantou_sw | 兒童及少年未來教育與發展帳戶申請 | https://welfare.nantou.gov.tw/1486/18 | 同上，內文為 POST 載入的 P_Word partial（約 1 |
| chiayi_city_sw | 嘉義市政府重陽節敬老禮金發放實施要點（網頁） | https://social.chiayi.gov.tw/News_Content.aspx?n=1101&s=404399 | 網頁只有附件清單（doc/pdf/odt）沒有內文；要點 PDF 已另列為 pdf 頁面 |
| chiayi_city_sw | 嘉義市政府重陽節敬老禮金發放作業要點（舊版網頁） | https://social.chiayi.gov.tw/News_Content.aspx?n=1101&s=560020 | 2020 年舊版，只有附件 PDF 沒有內文；以 2021 年上版的實施要點 PDF 為準 |
| chiayi_city_sw | 嘉義市重陽節敬老禮金發放實施要點（2018 舊版網頁） | https://social.chiayi.gov.tw/News_Content.aspx?n=1101&s=293578 | 2018 年舊版，只有 doc 附件沒有內文 |
| chiayi_city_sw | 嘉義市百歲人瑞營養禮金發放（網頁） | https://social.chiayi.gov.tw/News_Content.aspx?n=1101&s=404398 | 網頁只有附件清單沒有內文；作業要點 PDF 已另列為 pdf 頁面 |
| chiayi_city_sw | 嘉義市兒童及少年津貼補助一覽表 | https://social.chiayi.gov.tw/News_Content.aspx?n=401&s=293560 | 一覽表，網頁本身沒有內文（0 字）只有附件 |
| chiayi_city_sw | 弱勢兒童及少年生活扶助與托育及醫療費用補助辦法 | https://social.chiayi.gov.tw/News_Content.aspx?n=401&s=293357 | 轉載衛福部中央法規全文（3 |
| chiayi_city_sw | 嘉義市發展遲緩兒童早期療育服務 | https://social.chiayi.gov.tw/News_Content.aspx?n=401&s=293362 | 內文是通報轉介中心的服務業務說明，沒有個人申請資格與給付內容 |
| chiayi_city_sw | 社會救助（目錄） | https://social.chiayi.gov.tw/News.aspx?n=397&sms=9377 | 分類目錄頁，方案內容頁已逐一列入 |
| chiayi_city_sw | 老人福利（目錄） | https://social.chiayi.gov.tw/News.aspx?n=1101&sms=9555 | 分類目錄頁（兩頁、共 36 筆，夾雜課程招生與活動公告），方案內容頁已逐一列入 |
| chiayi_city_sw | 兒童少年福利（目錄） | https://social.chiayi.gov.tw/News.aspx?n=401&sms=9380 | 分類目錄頁，方案內容頁已逐一列入 |
| chiayi_city_sw | 身心障礙福利（目錄） | https://social.chiayi.gov.tw/News.aspx?n=393&sms=9376 | 分類目錄頁（約 50 筆），方案內容頁已逐一列入 |
| chiayi_city_sw | 家庭福利（目錄） | https://social.chiayi.gov.tw/cl.aspx?n=3833 | 分類目錄頁（含婦女福利、生育津貼），方案內容頁已逐一列入 |
| chiayi_city_sw | 育兒專區 | https://social.chiayi.gov.tw/infant.htm | 育兒專區入口頁（連到生育津貼、育兒津貼、托育補助等），方案內容頁已逐一列入 |
| bli_family | 勞保生育給付（含勞工生育補助） | https://www.bli.gov.tw/0004836.html | 方案目錄頁：只有分頁連結、書表下載與常見問答清單，內文在 0004844／0004845／0004846 |
| bli_family | 就保育嬰留職停薪津貼 | https://www.bli.gov.tw/0015003.html | 方案目錄頁：只有分頁連結、書表下載與常見問答清單，內文在 0015726／0015727／0015728 |
| bli_family | 國民年金生育給付 | https://www.bli.gov.tw/0016965.html | 目錄頁：只列兩項方案的分頁連結 |
| bli_family | 農保生育給付及加給補助 | https://www.bli.gov.tw/0006758.html | 目錄頁：只有兩個分頁連結，內文在 0109674／0109675 |
| bli_family | 寶貝誕生（分眾導覽） | https://www.bli.gov.tw/0100086.html | 分眾導覽目錄頁：只列各項給付的連結，沒有資格與金額內文 |
| bli_family | 勞工生育補助 — 補助方式 | https://www.bli.gov.tw/0109620.html | 只有一句話（加計至10萬元、無須另行申請），內容已含在 0004845 給付標準與 0109619 要點 |
| bli_family | 育嬰留職停薪薪資補助 — 補助依據 | https://www.bli.gov.tw/0105470.html | 只有一個法規連結，沒有內文 |
| bli_family | 國民年金生育給付金額試算 | https://www.bli.gov.tw/0100409.html | 線上試算頁（收錄政策排除），相關規定內容已由 0016966 涵蓋 |
| taoyuan_zhongli_office | 113年特殊境遇家庭扶助 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6431&s=1212736 | 舊年度版本（113 年），內容與 115 年度頁重複，只收最新年度 |
| taoyuan_zhongli_office | 108年特殊境遇家庭扶助 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6431&s=651667 | 舊年度版本（108 年），金額標準已過期 |
| taoyuan_zhongli_office | 育有未滿2歲兒童育兒津貼申請表 | https://ws.tycg.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNzkvcmVsZmlsZS8xMTM5My8xN | 純申請表（2382 字都是欄位、應備文件與切結），沒有給付金額；育兒津貼為中央方案，由 sfaa_childcare 收錄 |
| taoyuan_zhongli_office | 2歲以上未滿5歲幼兒育兒津貼及5歲至入國民小學前幼兒就學補助申復申請表 | https://ws.tycg.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNzkvcmVsZmlsZS8xMTM5My84N | 純申復申請表（2209 字），沒有資格與金額 |
| taoyuan_zhongli_office | 民眾常用檔案下載 | https://www.zhongli.tycg.gov.tw/News.aspx?n=6379&sms=11393 | 目錄頁：社會課各項業務只以附件 PDF 提供，方案 PDF 已分別列在 pages |
| taoyuan_zhongli_office | 特殊境遇家庭扶助業務 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6379&s=1601099 | 頁面只有「請參照附件」一句（67 字），內容在附件 PDF |
| taoyuan_zhongli_office | 弱勢家庭兒童及少年生活扶助業務 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6379&s=1601098 | 頁面只有「請參照附件」一句（77 字），內容在附件 PDF |
| taoyuan_zhongli_office | 低收入戶及中低收入戶申請相關表單 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6379&s=847679 | 頁面只有「請參考附件」一句（63 字），內容在附件 PDF |
| taoyuan_zhongli_office | 桃園市急難救助業務相關表單 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6379&s=847789 | 頁面只有「規定如附件」一句（54 字），內容在附件 PDF |
| taoyuan_zhongli_office | 國民年金所得未達一定標準業務 | https://www.zhongli.tycg.gov.tw/News_Content.aspx?n=6379&s=847832 | 頁面只有一句（67 字），附件只有申請書與流程圖，沒有給付內容 |
| taoyuan_zhongli_office | 業務職掌 | https://www.zhongli.tycg.gov.tw/cp.aspx?n=6366 | 只有各課室職掌一句話（社會課：社會福利、社會救助…），沒有方案 |
| tainan_east_office | 身心障礙者健康保險費補助 | https://www.tneast.gov.tw/News_Content_Table.aspx?n=21123&s=4360957 | 只有一句「不須至本所申請，由市府轉檔健保局」，沒有資格與補助內容 |
| tainan_east_office | 子女就學教育補助 | https://www.tneast.gov.tw/News_Content_Table.aspx?n=21123&s=4360966 | 只有「核列低收入戶高中職以上學生，區公所主動造冊」一句，沒有給付內容 |
| tainan_east_office | 兒童家庭生活補助 | https://www.tneast.gov.tw/News_Content_Table.aspx?n=21123&s=4360967 | 只有「核列低收入戶國中小兒童，區公所主動造冊」一句，沒有給付內容 |
| tainan_east_office | 國中、小營養午餐補助 | https://www.tneast.gov.tw/News_Content_Table.aspx?n=21123&s=4360965 | 只有兩句（低收入戶學生、由公所核發證明後向學校申請），沒有給付內容 |
| tainan_east_office | 住宅補貼申請 | https://www.tneast.gov.tw/News_Content_Table.aspx?n=21123&s=4360978 | 經建課頁面，只有應附文件清單，沒有資格與補貼金額（方案本文在內政部／都發局） |
| tainan_east_office | 役男家屬生活扶助 | https://www.tneast.gov.tw/News_Content_Table.aspx?n=21123&s=4360932 | 兵役業務，只有「由區公所調查填寫家狀表經市府核定」與文件清單，沒有資格與給付 |
| ece_moe | 關於公共化教保服務 | https://www.ece.moe.edu.tw/ch/ggh/public/about-ggh/ | 收費表與「公立、非營利幼兒園」頁完全相同，避免重複 |
| ece_moe | 育兒津貼及就學補助申請表下載 | https://www.ece.moe.edu.tw/ch/subsidy/allowance-1/apply_0001/ | 只有 22 縣市申請表 PDF 連結（表單），收錄政策排除 |
| ece_moe | 各縣市育兒津貼／就學補助諮詢窗口 | https://www.ece.moe.edu.tw/ch/subsidy/allowance-1/county-contact/ | 只有各縣市聯絡電話表，沒有資格與給付內容 |
| ece_moe | 幼兒就學補助相關法規 | https://www.ece.moe.edu.tw/ch/law/category07/ | 法規目錄，各法規頁只有連到 law.moj.gov.tw 的連結；法律本文被收錄政策排除 |
| chiayi_county_sw | 業務專區總覽 | https://sabcc.cyhg.gov.tw/Content_List.aspx?n=0043A8CF0BB98E08 | 業務專區目錄頁（左側選單列出所有分類），方案內容頁已逐一列入 |
| chiayi_county_sw | 老人福利津貼（目錄） | https://sabcc.cyhg.gov.tw/News.aspx?n=7787&sms=19854 | 分類列表頁，方案內容頁已逐一列入 |
| chiayi_county_sw | 老人生活照顧（目錄） | https://sabcc.cyhg.gov.tw/News.aspx?n=7788&sms=19855 | 分類列表頁，方案內容頁已逐一列入 |
| chiayi_county_sw | 老人健康維護（目錄） | https://sabcc.cyhg.gov.tw/News.aspx?n=7789&sms=19856 | 分類列表頁，方案內容頁已逐一列入 |
| chiayi_county_sw | 特殊境遇家庭（目錄） | https://sabcc.cyhg.gov.tw/News.aspx?n=7776&sms=19847 | 分類列表頁，方案內容頁已逐一列入 |
| chiayi_county_sw | 身心障礙經濟扶助（目錄） | https://sabcc.cyhg.gov.tw/News.aspx?n=7800&sms=19863 | 分類列表頁，方案內容頁已逐一列入 |
| chiayi_county_sw | 身心障礙個人照顧服務（目錄） | https://sabcc.cyhg.gov.tw/News.aspx?n=7798&sms=19861 | 分類列表頁，方案內容頁已逐一列入 |
| chiayi_county_sw | 嘉義縣政府辦理特殊境遇家庭扶助標準作業流程 | https://sabcc.cyhg.gov.tw/News_Content.aspx?n=7776&s=96769 | 作業流程頁（只有 SOP 連結，276 字），各項特境扶助的方案頁已逐一列入 |
| chiayi_county_sw | 嘉義縣設籍前新住民遭逢特殊境遇相關福利及扶助計畫（網頁） | https://sabcc.cyhg.gov.tw/News_Content.aspx?state=F5D336F102ACBC68&n=5BE589B23FF | 網頁只有附件清單沒有內文；計畫 PDF 在 nextws.cyhg.gov.tw/Download.ashx，該主機 TLS 的 DH 金鑰太小（OpenSSL DH_KEY_TOO_SMALL），專案 HTTP 客戶端抓不到，curl 可以；待客戶端放寬 SECLEVEL 後再登錄 PDF |
| hualien_sw | 花蓮縣公共化及準公共化托育服務價格上限 | https://sa.hl.gov.tw/Detail_sp/8fa4681a2f1c46d0be1924fab8164637 | 內文只有圖片（抽出 0 字） |
| hualien_sw | 花蓮縣坐月子到宅服務 | https://sa.hl.gov.tw/Detail_sp/9e48aee2f7d840a884ac24476a4d096f | 內文只有外部網站連結（56 字），沒有資格與給付 |
| hualien_sw | 定點臨時托育服務 | https://sa.hl.gov.tw/Detail_sp/54afc740c3ff4cff908bf8dceff5cb6d | 社福中心臨托服務時段說明，沒有補助資格與給付內容 |
| hualien_sw | 中低收入老人生活津貼（社會救助分類） | https://sa.hl.gov.tw/Detail_sp/a5f00ac066a8472299c7d37b47175e70 | 與老人福利分類下的 dc1acc8d… 同一方案、內容相同 |
| hualien_sw | 身心障礙者生活補助（身心障礙福利分類） | https://sa.hl.gov.tw/Detail_sp/11fd53f5764b48d792acb7a6bec111e5 | 與社會救助分類下的 919c84e1… 同一方案，此頁仍是 113 年度門檻數字 |
| hualien_sw | 身障生活輔具代償墊付民眾專區 | https://sa.hl.gov.tw/Detail_sp/012d480232f7468ea021e6f3251924b3 | 只有申請流程與購買應附資料（243 字），資格與給付在 662fed91… 輔具費用補助頁 |
| yilan_sw | 嬰幼兒照顧服務總覽 | https://sntroot.e-land.gov.tw/News.aspx?n=11276&sms=12833 | 分類目錄頁 |
| yilan_sw | 銀髮族服務總覽 | https://sntroot.e-land.gov.tw/News.aspx?n=11277&sms=12834 | 分類目錄頁 |
| yilan_sw | 社會救助總覽 | https://sntroot.e-land.gov.tw/News.aspx?n=11278&sms=12835 | 分類目錄頁 |
| yilan_sw | 身心障礙者服務總覽 | https://sntroot.e-land.gov.tw/News.aspx?n=11280&sms=12837 | 分類目錄頁 |
| yilan_sw | 宜蘭縣重陽節敬老禮金實施要點 | https://sntroot.e-land.gov.tw/News_Content.aspx?n=10124&s=130420 | 頁面只有 PDF 附件（20 字），已改登錄附件 PDF |
| yilan_sw | 宜蘭縣低收入戶產婦及嬰兒營養補助 | https://sntroot.e-land.gov.tw/News_Content.aspx?n=11278&s=133571 | 頁面只有聯絡人（51 字），沒有資格與給付內容 |
| yilan_sw | 災害救助及災害收容所 | https://sntroot.e-land.gov.tw/News_Content.aspx?n=11278&s=133534 | 頁面只有聯絡人（64 字），沒有資格與給付內容；災害救助金標準只在法規列表 |
| yilan_sw | 身心障礙福利（個人及家庭照顧服務）總覽 | https://sntroot.e-land.gov.tw/cp.aspx?n=10414 | 一頁彙整 11 項身障服務（家庭關懷訪視、社區居住、自立生活等，7 |
| penghu_sw | 未滿2歲暨延長3歲兒童托育公共化及準公共服務補助（附件頁） | https://www.penghu.gov.tw/society/home.jsp?id=316&act=view&dataserno=20210803000 | 頁面只有附件清單沒有內文；方案內容以上面的「申請須知」PDF 收錄 |
| penghu_sw | 特殊境遇家庭補助（附件頁） | https://www.penghu.gov.tw/society/home.jsp?id=169&act=view&dataserno=20130906000 | 頁面只有附件清單（條例、申請表、問答）沒有內文；方案內容以「實施作業要點」PDF 收錄 |
| penghu_sw | 重陽節敬老禮金實施要點（附件頁） | https://www.penghu.gov.tw/society/home.jsp?id=317&act=view&dataserno=20200615000 | 頁面只有附件沒有內文；方案內容以 PDF 收錄 |
| penghu_sw | 離島地區六十五歲以上老人全民健康保險應自付保險費補助 | https://www.penghu.gov.tw/society/home.jsp?id=317&act=view&dataserno=20180528000 | 內文只有一句補助對象，其餘說明都在圖片裡（無文字可抽取） |
