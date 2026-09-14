"""收錄政策（admission）：決定一份官方頁面能不能成為一筆「補助方案」紀錄。

標準參考 getgrant.tw 公開的《編輯與查核標準》（https://getgrant.tw/editorial-standards）——只借用它「收什麼、不收什麼、每筆要有哪些欄位」
的定義，不使用、不抓取它的任何資料；所有紀錄仍只來自官方來源。

收：對申請人有具體經濟價值的項目——補助、補貼、津貼、獎助／獎學金、減免、貸款（利息補貼）、有經濟價值的服務（長照、托育、交通接送…）。
不收（filtered_out，附原因）：
  form            申請書／申請表／切結書／同意書／委託書／範本／範例（表單本身不是方案）
  attachment      只有「檔案下載」沒有方案名稱的附件頁、只有附件清單沒有內文的頁面
  progress_query  申辦進度查詢、案件查詢（線上服務入口，不是方案）
  flowchart       流程圖
  logo            標章／LOGO／識別標誌
  statistics      統計表、統計年刊
  faq             問答集、常見問題
  directory       名單、名冊、一覽表、聯繫窗口
  notice          行政公告：修正條文、草案、廢止、公聽會、說明會、研習、徵求、招標、得獎名單、遴選、查核督導／稽核
  fragment        標題只是段落名（應備文件、相關檔案、洽辦資訊…）的分頁片段：沒有方案名稱，無法成為一筆紀錄
  garbled         PDF 文字擷取失敗的亂碼：幾乎沒有中文字、大半是不可讀符號，資格與給付內容無法判讀
  site_info       網站資訊頁：資料來源與更新頻率、隱私權、網站導覽、無障礙聲明、著作權、聯絡我們
  statute         法律本文：標題以「法／條例／施行細則」結尾且沒有補助方案名詞（長期照顧服務法、老人福利法…）；「…補助辦法／扶助條例」仍算方案
已停止受理（標題或原文標示「已不再受理／額度已用罄」）的方案仍收，但 status=expired：預設不列出、不進媒合（見 extractor）。
保留但不進清單／統計主數字／媒合（record_kind=portal）：總整理、懶人包、專區、福利地圖等彙整頁。
其餘為 record_kind=program，並依 getgrant 的必要欄位（名稱、主辦機關、資格、金額、期間、申請方式、來源網址）算完整度與品質等級。
"""

from __future__ import annotations

import re

WINDOW_RE = re.compile(r"^\s*[\[（(]\s*另開新視窗\s*[\]）)]\s*")
ATTACHMENT_PREFIX_RE = re.compile(r"^\s*[\(（\[]\s*(?:PDF|DOC|ODT|檔案)?\s*檔案?下載\s*[\)）\]]\s*", re.I)
FILE_SUFFIX_RE = re.compile(r"\s*[\(（]?\s*(?:pdf|docx?|odt|ods|xlsx?|csv)\s*檔?案?下載?\s*[\)）]?\s*$|\.(?:pdf|docx?|odt|ods|xlsx?|csv)\s*$", re.I)
FILE_TOKEN_RE = re.compile(r"\b(?:pdf|odt|docx?|ods|xlsx?)\b", re.I)
# 分頁片段：整個標題只是一個段落名（臺北市社會局 cp.aspx 的「申請說明／應備文件／洽辦資訊／相關檔案」分頁各成一份文件）
# 方案被站方拆成多頁時（勞保局：請領資格／給付標準／請領手續），只寫申辦流程的那頁不是方案本身
PROCEDURE_TAIL_RE = re.compile(r"(?:請領|申請|申辦)(?:手續|程序)\s*$")
FRAGMENT_TITLE_RE = re.compile(r"^(?:應備文件|應檢附文件|檢附文件|應附文件|相關檔案|相關連結|相關法規|法令依據|法規依據|洽辦資訊|申請說明|檔案下載|附件下載|附件|備註|注意事項|聯絡方式|聯絡資訊|服務內容|申請方式|申請資格|補助標準|補助內容|辦理單位|承辦單位|下載專區|表單下載|申請流程|作業流程)$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
READABLE_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffefA-Za-z0-9，。、：；！？（）()\[\]【】「」『』《》〈〉…—－\-_/\\.,:;!?'\"%$+=*#@&~‧·]")

# 方案名詞：標題含這些詞代表講的是一項方案（表單類字眼只在「沒有方案名詞」或「結尾就是表單」時才視為表單）
PROGRAM_NOUN_RE = re.compile(r"(計畫|辦法|要點|條例|規定|方案|措施|補助|補貼|津貼|給付|獎學金|獎助|助學|貸款|減免|救助|扶助|獎勵)")
FORM_WORD_RE = re.compile(r"(申請書|申請表|切結書|同意書|委託書|承諾書|聲明書|申報表|報名表|表單|表格|參考範例|範本|範例)")
FORM_TAIL_RE = re.compile(r"(申請書|申請表|切結書|同意書|委託書|承諾書|聲明書|申報表|報名表|範本|範例)\s*$")
STATUTE_TAIL_RE = re.compile(r"(?<![辦作方])(法|條例|施行細則)\s*$")  # 「辦法」「作法」「方法」不算法律本文
BENEFIT_NOUN_RE = re.compile(r"(補助|補貼|津貼|給付|獎學金|獎助|助學|貸款|減免|救助|扶助|獎勵)")  # 法律本文的例外：標題本身就講給付內容（扶助條例、補助辦法）

KIND_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("progress_query", re.compile(r"(進度查詢|申辦進度|查詢進度|案件查詢|核發進度|試算)")),
    ("site_info", re.compile(r"(資料來源與更新|更新頻率|隱私權|網站導覽|網站地圖|無障礙聲明|著作權聲明|使用條款|聯絡我們|意見信箱|歷史沿革|沿革$|開放資料宣告|資料開放宣告|網站安全|資訊安全政策)")),
    ("flowchart", re.compile(r"流程圖")),
    ("logo", re.compile(r"(LOGO|標章|標誌|識別標)", re.I)),
    ("statistics", re.compile(r"(統計表|統計年刊|統計資料|性別統計|統計$|預算書|決算書|預算決算|預算案|決算$|得標價|標售)")),
    ("faq", re.compile(r"(問答集|Q&A|常見問答|常見問題)", re.I)),
    ("directory", re.compile(r"(名單|名冊|一覽表|聯繫窗口|聯絡窗口|服務據點$)")),
    # 查核／督導／稽核要成詞才算行政公告：「審查核發作業規定」的「查核」是「審查核」的一部分、「督導員訓練」是人員訓練
    ("notice", re.compile(r"(修正條文|修正草案|草案|廢止|公聽會|說明會|研習|座談|徵才|招標|決標|徵求|遴選|入圍|得獎|(?<!審)查核(?:督導|作業|計畫|報告|要點|表|專區)?|督導(?!員)|稽核|修正發布|發布修正|修正案|條文對照表|調整公告)")),
]
# 內文首行：爬蟲給的標題可能是「…（來源頁）」或 PDF 檔名，真正的標題在內文第一行；首行短且含公告字眼時同樣視為行政公告
HEADLINE_MAX = 80
PORTAL_RE = re.compile(r"(總覽|總整理|有哪些|哪些.*方案|一覽$|懶人包|專區|彙整|福利地圖|服務地圖|報您知|全攻略|好安心|一次看|讓政府|整理[:：！!]?$)")
# 我的E政府「主題策展」頁（News_Content_26_*）：同一頁整理多項補助 → 一律彙整頁
PORTAL_URL_RE = re.compile(r"gov\.tw/News_Content_26_", re.I)

EXCLUDED_KINDS = {"form", "attachment", "progress_query", "flowchart", "logo", "statistics", "faq", "directory", "notice", "fragment", "garbled", "site_info", "statute"}
KIND_LABELS = {
    "program": "補助方案", "portal": "彙整頁", "form": "申請書／表單", "attachment": "附件下載頁", "progress_query": "線上查詢／試算服務", "flowchart": "流程圖",
    "logo": "標章／識別標誌", "statistics": "統計／預算資料", "faq": "問答集", "directory": "名單／窗口", "notice": "行政公告",
    "fragment": "分頁片段（只有段落名）", "garbled": "亂碼（PDF 文字擷取失敗）", "site_info": "網站資訊頁", "statute": "法律本文",
}
REQUIRED_FIELDS = ["name", "agency", "eligibility", "amount", "period", "method", "source_url"]
FIELD_LABELS = {"name": "方案名稱", "agency": "主辦機關", "eligibility": "申請資格", "amount": "金額／給付內容", "period": "申請期間", "method": "申請方式", "source_url": "官方來源網址"}


def clean_title(title: str) -> str:
    text = WINDOW_RE.sub("", title or "")
    text = ATTACHMENT_PREFIX_RE.sub("", text)
    text = FILE_SUFFIX_RE.sub("", text)
    return text.strip()


def looks_garbled(text: str) -> bool:
    """PDF 文字擷取失敗的亂碼：去掉空白後幾乎沒有中文字（<5%），而且三成以上不是中英數與標點。純英文頁不算亂碼。"""
    body = "".join((text or "").split())
    if len(body) < 40:
        return False
    cjk = len(CJK_RE.findall(body))
    readable = len(READABLE_RE.findall(body))
    return cjk / len(body) < 0.05 and (len(body) - readable) / len(body) > 0.3


def page_kind(title: str, text: str = "", url: str = "") -> tuple[str, str]:
    """回傳 (record_kind, 原因)。record_kind ∈ program | portal | EXCLUDED_KINDS。只看標題、網址與內文結構，不看關鍵字統計。"""
    name = clean_title(title)
    if not name:
        return "attachment", "附件下載頁沒有方案名稱，無法對應到任何補助方案"
    if looks_garbled(text):
        return "garbled", "文字擷取為亂碼（PDF 編碼失敗），資格與給付內容無法判讀"
    if FRAGMENT_TITLE_RE.match(name):
        return "fragment", f"標題只是段落名「{name}」：方案頁的分頁片段，沒有方案名稱"
    procedure = PROCEDURE_TAIL_RE.search(name)
    if procedure:
        return "fragment", f"標題以「{procedure.group(0).strip()}」結尾：同一方案被拆成多頁，這頁只有申辦流程（資格與給付內容在另一頁）"
    if url and PORTAL_URL_RE.search(url):
        return "portal", "我的E政府主題策展頁（同一頁整理多項補助），保留供查閱但不進清單與媒合"
    for kind, pattern in KIND_PATTERNS:
        match = pattern.search(name)
        if match:
            return kind, f"標題含「{match.group(0)}」：{KIND_LABELS[kind]}，不是補助方案內容"
    headline = next((line.strip() for line in (text or "").splitlines() if line.strip()), "")
    if headline and len(headline) <= HEADLINE_MAX:
        for kind, pattern in KIND_PATTERNS:
            match = pattern.search(headline)
            if match and kind == "notice":
                return kind, f"內文首行「{headline[:40]}」含「{match.group(0)}」：{KIND_LABELS[kind]}，不是補助方案內容"
    if FORM_TAIL_RE.search(name):
        return "form", f"標題以「{FORM_TAIL_RE.search(name).group(1)}」結尾：表單本身不是補助方案"
    form_word = FORM_WORD_RE.search(name)
    if form_word and not PROGRAM_NOUN_RE.search(name):
        return "form", f"標題含「{form_word.group(0)}」且沒有方案名詞：表單本身不是補助方案"
    statute = STATUTE_TAIL_RE.search(name)
    if statute and not BENEFIT_NOUN_RE.search(name):
        return "statute", f"標題以「{statute.group(1)}」結尾且沒有方案名詞：法律本文，不是補助方案"
    body = text or ""
    if len(body) < 400 and len(FILE_TOKEN_RE.findall(body)) >= 3:
        return "attachment", "頁面只有附件清單、沒有方案內文（資格與給付內容在附件裡，目前不抓附件）"
    if PORTAL_RE.search(name):
        return "portal", f"標題含「{PORTAL_RE.search(name).group(0)}」：彙整頁，保留供查閱但不進清單與媒合"
    return "program", ""


def completeness(benefit: dict) -> dict:
    """依 getgrant 的必要欄位算完整度：哪些有、哪些沒有。只看已抽出（含本地 AI 補齊並驗證過）的欄位，不猜。"""
    meta = benefit.get("benefit") or {}
    amount = meta.get("amount") or {}
    period = meta.get("application_period") or {}
    application = meta.get("application") or {}
    present: list[str] = []
    if (benefit.get("title") or "").strip():
        present.append("name")
    if (benefit.get("provider") or "").strip() and benefit.get("provider_type") not in {None, "", "unknown"}:
        present.append("agency")
    if benefit.get("rules") or benefit.get("conditions") or (meta.get("target_population_text") or "").strip():
        present.append("eligibility")
    if amount.get("value") is not None or amount.get("min") is not None or amount.get("max") is not None or (not meta.get("benefit_form_inferred") and meta.get("benefit_form") in {"service", "waiver", "in_kind", "voucher"}):
        present.append("amount")
    if period.get("end_date") or period.get("rolling") or period.get("start_date"):
        present.append("period")
    if application.get("channel") not in {None, "", "unknown"} or application.get("documents"):
        present.append("method")
    if ((benefit.get("source") or {}).get("source_url") or "").strip():
        present.append("source_url")
    missing = [f for f in REQUIRED_FIELDS if f not in present]
    return {"present": present, "missing": missing, "missing_labels": [FIELD_LABELS[f] for f in missing]}


def quality_tier(benefit: dict, kind: str, fields: dict) -> str:
    """verified：資格與給付內容都有、來源已驗證；needs_review：缺資格或金額／給付內容；portal：彙整頁。"""
    if kind == "portal":
        return "portal"
    source_ok = bool((benefit.get("source") or {}).get("source_verified"))
    missing = set(fields.get("missing") or [])
    if not source_ok or "eligibility" in missing or "amount" in missing or "name" in missing:
        return "needs_review"
    return "verified"


def admit(benefit: dict, *, title: str | None = None, text: str | None = None) -> dict:
    """給 pipeline 用：回傳要寫進 benefit 的 admission 區塊與 record_kind。"""
    kind, reason = page_kind(title if title is not None else benefit.get("title", ""), text if text is not None else benefit.get("original_text", ""), (benefit.get("source") or {}).get("source_url", ""))
    if kind in EXCLUDED_KINDS:
        return {"record_kind": kind, "admission": {"kind": kind, "kind_label": KIND_LABELS[kind], "reason": reason, "quality_tier": "reject", "completeness": None}}
    fields = completeness(benefit)
    tier = quality_tier(benefit, kind, fields)
    return {"record_kind": kind, "admission": {"kind": kind, "kind_label": KIND_LABELS[kind], "reason": reason, "quality_tier": tier, "completeness": fields}}
