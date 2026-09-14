"""收錄政策：申請書／附件／流程圖／進度查詢等不是補助方案；彙整頁是 portal；方案完整度。"""

from app.services.admission import EXCLUDED_KINDS, admit, clean_title, completeness, looks_garbled, page_kind


def test_forms_and_attachments_are_excluded():
    assert page_kind("(檔案下載)長期照顧服務申請書.pdf")[0] == "form"
    assert page_kind("(PDF檔案下載)")[0] == "attachment"
    assert page_kind("受理家暴案件服務流程圖(doc檔案下載)")[0] == "flowchart"
    assert page_kind("國軍退除役官兵-就學獎助核發進度查詢 凡退除役官兵就讀…")[0] == "progress_query"
    assert page_kind("長照識別標誌(LOGO)及相關標章")[0] == "logo"
    assert page_kind("各縣市長期照顧管理中心聯繫窗口")[0] == "directory"
    assert page_kind("發布「長期照顧服務人員訓練認證繼續教育及登錄辦法」修正條文")[0] == "notice"
    assert page_kind("公告徵求辦理衛生福利部115至117年山地原住民及離島地區多元照顧服務模式發展計畫")[0] == "notice"
    assert page_kind("施用毒品者就業服務計畫", "更新日期：114/03/10 相關檔案 施用毒品者就業服務計畫 pdf odt 勞動部令 pdf")[0] == "attachment"
    for kind in ("form", "attachment", "flowchart", "progress_query", "logo", "directory", "notice"):
        assert kind in EXCLUDED_KINDS


def test_fragments_garbled_text_and_audit_pages_are_excluded():
    assert page_kind("應備文件", "申請說明 應備文件 洽辦資訊 應備文件1.申請書1份。2.申請人之身分證或戶籍資料影本1份。")[0] == "fragment"
    assert page_kind("相關檔案", "首頁 相關檔案 臺北市政府社會局辦理失能者生活輔助器具自辦補助計畫 pdf(119.27 KB)")[0] == "fragment"
    garbled = "ਕ ഃॴୋ ॴ˸ɪʹஷ ಂ j ๋˸ɪϼɛf f И͏f f ਕᇍఖjၽ̹̏eอ̹̏f ͋फԓf ֛ ࣨ f ͉̹ᒍਜf j ʘԓफf ʘԓफ ཞ඄˚ʘԓफ f ԓሿf ਕఊ ̣ԓf ਕఊ Зf ٫ ˴ f ሗʶʕ"
    assert looks_garbled(garbled)
    assert page_kind("長期照顧交通接送服務", garbled)[0] == "garbled"
    assert page_kind("長期照顧交通接送服務", "長期照顧交通接送服務：失能者往返醫療院所就醫或復健，每月最高補助 8 趟。")[0] == "program"
    assert not looks_garbled("Bike sharing subsidy for seniors: apply at the district office before 2026-12-31. Bring your ID card.")
    assert page_kind("整合住宅補貼資源實施方案查核督導專區")[0] == "notice"
    # 「審查核發」不是查核：作業規定寫的是給付資格與金額
    assert page_kind("澎湖縣弱勢兒童及少年醫療補助審查核發作業規定", "一、申請資格：設籍本縣之低收入戶兒童。二、補助金額：每人每次最高 5,000 元。")[0] == "program"
    # 勞保局把一項給付拆成三頁：只有申辦流程的那頁不是方案本身
    assert page_kind("國民年金生育給付暨加給補助 — 請領手續")[0] == "fragment"
    assert page_kind("勞保生育給付（含勞工生育補助）— 請領資格")[0] == "program"
    assert page_kind("就保育嬰留職停薪津貼 — 給付標準及期間")[0] == "program"
    assert page_kind("歷史沿革")[0] == "site_info"
    assert page_kind("臺中市低收入戶三項生活補助費調整公告")[0] == "notice"
    # 爬蟲標題是「…（來源頁）」或 PDF 檔名，真正的標題在內文首行
    assert page_kind("長期照顧服務申請及給付辦法（來源頁）", "衛福部修正發布長期照顧服務申請及給付辦法\n資料來源：長期照顧司\n衛生福利部於114年6月19日公告修正案…")[0] == "notice"
    assert page_kind("長期照顧服務申請及給付辦法", "長期照顧服務申請及給付辦法部分條文修正條文對照表\n修正條文 現行條文 說明\n第二條 …")[0] == "notice"
    assert page_kind("長期照顧服務申請及給付辦法", "長期照顧服務申請及給付辦法\n第二條 因身心失能，且符合下列資格之一者，得申請長期照顧服務：一、六十五歲以上。")[0] == "program"
    assert page_kind("預算決算書", "本局將於每年2月底前發布年度預算，並於5月底前發布前年度決算。116年度預算 單位預算 ‧預算案書")[0] == "statistics"
    assert page_kind("稅金試算")[0] == "progress_query"
    assert page_kind("資料來源與更新頻率")[0] == "site_info"
    assert page_kind("長期照顧服務法")[0] == "statute"
    assert page_kind("長期照顧服務機構法人條例")[0] == "statute"
    assert page_kind("老人福利法施行細則")[0] == "statute"
    assert page_kind("特殊境遇家庭扶助條例")[0] == "program"  # 含「扶助」：條例本身定義給付
    assert page_kind("身心障礙者生活補助費發給辦法")[0] == "program"
    for kind in ("fragment", "garbled", "site_info", "statute"):
        assert kind in EXCLUDED_KINDS


def test_programs_with_form_words_or_legal_pdfs_stay():
    assert page_kind("臺中市-低收入戶房屋租金補助申請書表 無自有住宅之低收入戶，且其他家庭成員均無自有住宅")[0] == "program"
    assert page_kind("(檔案下載)107年3月27日修正中低收入老人補助裝置假牙實施計畫(行政院核定本).pdf")[0] == "program"
    assert page_kind("【轉知】基隆市政府「基隆市高級中等以上學校清寒優秀學生獎學金給與辦法」及申請表相關資訊")[0] == "program"
    assert page_kind("300億元中央擴大租金補貼")[0] == "program"
    assert page_kind("公告本部「115年度日照中心導入科技輔具成效補助計畫」")[0] == "program"
    assert clean_title("[另開新視窗](PDF檔案下載)長期照顧服務申請書.pdf") == "長期照顧服務申請書"


def test_portals_are_kept_but_flagged():
    assert page_kind("中低收入戶的福利總整理：就學、就業、醫療及住宅補助！")[0] == "portal"
    assert page_kind("從求學到就業，身心障礙者的福利懶人包！")[0] == "portal"
    assert page_kind("社會住宅專區")[0] == "portal"
    assert page_kind("弱勢兒少福利報您知，給孩子一個明亮的未來！")[0] == "portal"


def test_completeness_and_quality_tier():
    benefit = {
        "title": "缺工就業獎勵", "provider": "勞動部勞動力發展署", "provider_type": "central_government",
        "rules": [{"attribute_id": "employment.status"}], "conditions": [],
        "benefit": {"amount": {"value": 5000, "unit": "month"}, "application_period": {"rolling": True}, "application": {"channel": "agency"}, "benefit_form": "cash", "benefit_form_inferred": False},
        "source": {"source_url": "https://emps.wda.gov.tw/x", "source_verified": True}, "original_text": "…",
    }
    fields = completeness(benefit)
    assert fields["missing"] == []
    assert admit(benefit)["admission"]["quality_tier"] == "verified"
    weak = {**benefit, "rules": [], "conditions": [], "benefit": {"amount": {}, "benefit_form": "cash", "benefit_form_inferred": True}}
    result = admit(weak)
    assert result["record_kind"] == "program"
    assert result["admission"]["quality_tier"] == "needs_review"
    assert "申請資格" in result["admission"]["completeness"]["missing_labels"]
    portal = {**benefit, "title": "中低收入戶的福利總整理"}
    assert admit(portal)["record_kind"] == "portal"


def test_gov_tw_theme_pages_are_portals():
    assert page_kind("家中遭逢變故，政府提供哪些急難紓困方案？", "", "https://www.gov.tw/News_Content_26_574274")[0] == "portal"
    assert page_kind("樂當銀髮族，讓政府助您享受樂齡生活！")[0] == "portal"
    assert page_kind("育嬰留職停薪津貼及薪資補助", "", "https://www.gov.tw/News_Content_2_559418")[0] == "program"
