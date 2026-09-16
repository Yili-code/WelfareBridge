"""文字正規化與基礎數值／日期解析（純規則，不做語意猜測）。

- 全形 → 半形、英文小寫、「台」→「臺」（只用於比對，不改原文）
- 民國年日期 → ISO（115/10/01 → 2026-10-01）
- 中文數字 → 整數（三萬二千 → 32000、七十 → 70、六個月 → 6）
- 22 縣市名稱標準化（台北／臺北／臺北市 → 臺北市）
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TAIPEI = ZoneInfo("Asia/Taipei")


def taiwan_today() -> date:
    """官方公告的申請期限以臺灣日期為準（容器多半是 UTC）。"""
    return datetime.now(TAIPEI).date()


def taiwan_day_start_utc() -> datetime:
    """臺灣今天 00:00 對應的 naive UTC 時間（資料庫一律存 naive UTC）。"""
    start = datetime.combine(taiwan_today(), datetime.min.time(), tzinfo=TAIPEI)
    return start.astimezone(timezone.utc).replace(tzinfo=None)


CITIES: tuple[str, ...] = (
    "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
    "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣",
    "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
    "臺東縣", "澎湖縣", "金門縣", "連江縣",
)

CITY_ALIASES: dict[str, str] = {}
for _city in CITIES:
    _base = _city[:-1]
    CITY_ALIASES[_city] = _city
    CITY_ALIASES[_base] = _city
    if "臺" in _city:
        CITY_ALIASES[_city.replace("臺", "台")] = _city
        CITY_ALIASES[_base.replace("臺", "台")] = _city
CITY_ALIASES.update({"北市": "臺北市", "中市": "臺中市", "南市": "臺南市", "高市": "高雄市", "馬祖": "連江縣"})

# 比對用：長的別名先比對（臺北市 > 臺北 > 北市），避免「新竹縣」被「新竹市」誤判
_CITY_PATTERN = re.compile("|".join(sorted((re.escape(k) for k in CITY_ALIASES), key=len, reverse=True)))

# 含公文常用的大寫與異體字：壹貳參肆伍陸柒捌玖、拾佰仟萬億（「新臺幣貳萬伍仟元整」「每名新台幣2仟元」）
CN_DIGITS = {
    "零": 0, "〇": 0, "０": 0,
    "一": 1, "壹": 1, "二": 2, "兩": 2, "貳": 2, "貮": 2, "三": 3, "參": 3, "叁": 3, "四": 4, "肆": 4,
    "五": 5, "伍": 5, "六": 6, "陸": 6, "七": 7, "柒": 7, "八": 8, "捌": 8, "九": 9, "玖": 9,
}
CN_UNITS = {"十": 10, "拾": 10, "百": 100, "佰": 100, "千": 1000, "仟": 1000, "萬": 10000, "万": 10000, "億": 100000000}


def fullwidth_to_halfwidth(text: str) -> str:
    out = []
    for char in text:
        code = ord(char)
        if code == 0x3000:
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:
            out.append(chr(code - 0xFEE0))
        else:
            out.append(char)
    return "".join(out)


def normalize_text(text: str) -> str:
    """比對用正規化：全形→半形、英文小寫、台→臺、壓縮空白。"""
    text = fullwidth_to_halfwidth(text or "")
    text = text.lower().replace("台", "臺").replace("ㄧ", "一")  # 注音「ㄧ」是公文常見錯字
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compact(text: str) -> str:
    """去掉所有空白（用於 source_excerpt 子字串驗證）。"""
    return re.sub(r"\s+", "", normalize_text(text))


def normalize_city(name: str | None) -> str | None:
    if not name:
        return None
    key = fullwidth_to_halfwidth(name).strip()
    if key in CITY_ALIASES:
        return CITY_ALIASES[key]
    match = _CITY_PATTERN.search(key)
    return CITY_ALIASES[match.group(0)] if match else None


def find_cities(text: str) -> list[str]:
    """依出現順序回傳文字中明確提到的縣市（標準名稱，去重）。"""
    found: list[str] = []
    for match in _CITY_PATTERN.finditer(fullwidth_to_halfwidth(text or "")):
        city = CITY_ALIASES[match.group(0)]
        if city not in found:
            found.append(city)
    return found


def chinese_to_int(text: str) -> int | None:
    """中文數字（含混合阿拉伯數字）→ 整數。無法解析回傳 None。"""
    text = fullwidth_to_halfwidth(text or "").replace(",", "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d+(\.\d+)?", text):
        return int(float(text))
    total = 0
    section = 0
    number = 0
    seen = False
    for char in text:
        if char.isdigit():
            number = number * 10 + int(char)
            seen = True
        elif char in CN_DIGITS:
            number = CN_DIGITS[char]
            seen = True
        elif char in CN_UNITS:
            unit = CN_UNITS[char]
            seen = True
            if unit >= 10000:
                total = (total + section + (number or 0)) * unit if (total + section + number) else unit
                section = 0
                number = 0
            else:
                section += (number if number else 1) * unit
                number = 0
        else:
            return None
    if not seen:
        return None
    return total + section + number


ROC_DATE_RE = re.compile(r"(?:民國)?\s*(\d{2,4})\s*[年/\-.]\s*(\d{1,2})\s*[月/\-.]\s*(\d{1,2})\s*日?")


def to_iso_date(text: str) -> str:
    """115/10/01、115-10-01、115年10月1日、2026/10/01 → 2026-10-01；無法解析回傳空字串。"""
    match = ROC_DATE_RE.search(fullwidth_to_halfwidth(text or ""))
    if not match:
        return ""
    year, month, day = (int(x) for x in match.groups())
    if year < 1911:
        year += 1911
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return ""
    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_date_range(text: str) -> tuple[str, str]:
    """回傳 (start_iso, end_iso)。只有一個日期時視為截止日；但日期後面緊接著「起」的是起始日
    （「自108年8月1日起受理申請迄今」不是截止日，當成截止日會讓還在辦的方案被標成已過期）。找不到年份的日期不猜。"""
    cleaned = fullwidth_to_halfwidth(text or "")
    found = [(match, to_iso_date(match.group(0))) for match in ROC_DATE_RE.finditer(cleaned)]
    found = [(match, date) for match, date in found if date]
    if not found:
        return "", ""
    if len(found) == 1:
        match, date = found[0]
        return (date, "") if re.match(r"\s*起", cleaned[match.end():]) else ("", date)
    return found[0][1], found[-1][1]


AMOUNT_RE = re.compile(
    # 「2仟元」「3萬5千元」這種數字接中文位數的寫法要當成一個數字（萬留在第二組，1.5萬元才不會被拆壞）。
    # 每個重複段都必須吃掉一個位數字（十百千），否則長串數字會讓正規表示式指數爆炸（見 docs 問題 #48）。
    r"(?:新臺幣|新台幣|NT\$|NTD|\$)?\s*("
    r"(?:[0-9０-９,，]+(?:\.\d+)?[十拾百佰千仟])*[0-9０-９,，]+(?:\.\d+)?[十拾百佰千仟]?"
    r"(?:[萬万](?:[0-9０-９,，]+[十拾百佰千仟])*[0-9０-９,，]*)?"
    r"|[一二兩三四五六七八九十百千萬零〇壹貳貮參叁肆伍陸柒捌玖拾佰仟万]+(?:\s{1,2}[一二兩三四五六七八九十百千萬零〇壹貳貮參叁肆伍陸柒捌玖拾佰仟万]+)*"
    r")\s*(萬|万|億)?\s*(元|圓)"
)


DIGIT_BREAK_RE = re.compile(r"(?<=[0-9０-９,，])\s+(?=[0-9０-９])")


def parse_amounts(text: str) -> list[int]:
    """抓出文字中所有金額（元）。「4,000元」「新臺幣三萬二千元」「1.5萬元」→ [4000, 32000, 15000]。"""
    values: list[int] = []
    text = DIGIT_BREAK_RE.sub("", text or "")  # 「1,\n500元」接回「1,500元」
    for match in AMOUNT_RE.finditer(text):
        raw, wan, _unit = match.groups()
        raw = fullwidth_to_halfwidth(raw).replace(",", "").replace("，", "")
        raw = re.sub(r"\s+", "", raw)  # PDF 斷行會在數字中間塞空白：「六 千元」
        value: float | None
        decimal_wan = re.fullmatch(r"(\d+(?:\.\d+)?)[萬万](.*)", raw)  # 「2萬7000」「1.5萬」
        if re.fullmatch(r"\d+(\.\d+)?", raw):
            value = float(raw)
        elif decimal_wan:  # 「1.5萬」「3萬5千」：整數部分乘一萬，再加上後面的零頭
            rest = chinese_to_int(decimal_wan.group(2)) if decimal_wan.group(2) else 0
            value = float(decimal_wan.group(1)) * 10000 + float(rest or 0)
        else:
            parsed = chinese_to_int(raw)
            value = float(parsed) if parsed is not None else None
        if value is None:
            continue
        if wan:
            value *= 100000000 if wan in {"億"} else 10000
        if value <= 0:
            continue
        values.append(int(round(value)))
    return values


DURATION_RE = re.compile(r"(?:滿|達|連續|居住|設籍)?\s*([0-9０-９]+|[一二兩三四五六七八九十]+)\s*(年|個月|月)\s*(以上|以上者)?")


YEAR_CONTEXT_RE = re.compile(r"(民國|中華民國)\s*$")
YEAR_SUFFIX_RE = re.compile(r"^(次|生|出生|度|日|[0-9０-９]{1,2}\s*月)")



# 「1副」「1份(箱/打)」「1,000點」「2,400cc」這種數量詞常被當成金額。
# 判準：這個數字在摘錄裡的每一次出現，後面緊接的都是非金錢量詞 → 不是錢。
NON_MONEY_COUNTER_RE = re.compile(r"^[ \t]*(?:副|份|箱|打|盒|包|件|張|台|臺|輛|point|點|歲|年|月|日|天|時|小時|次|人次|人|名|位|戶|班|床|坪|公斤|公升|倍|cc|c[.]c[.]|CC|C[.]C[.]|%|％|分|級|項|款|條|樣|種)")


def number_is_counted(value: float, excerpt: str) -> bool:
    """摘錄裡這個數字每次出現後面都接非金錢量詞（副、份、點、cc…）就回 True。"""
    text = normalize_text(excerpt or '')
    if not text:
        return False
    number = int(round(value))
    forms = {str(number), f'{number:,}'}
    seen = False
    for form in forms:
        start = 0
        while True:
            index = text.find(form, start)
            if index < 0:
                break
            start = index + len(form)
            following = text[start:start + 8]
            match = NON_MONEY_COUNTER_RE.match(following)
            if not match:
                return False
            if "元" in following[match.end():match.end() + 3] or "圓" in following[match.end():match.end() + 3]:
                return False  # 「1,000點(元)」這種等值於錢的寫法算金額
            seen = True
    return seen


def parse_duration_months(text: str) -> int | None:
    """「滿一年」「六個月以上」「設籍本市3年」→ 月數。「民國90年次」「90年1月1日」是年份不是期間，略過。"""
    source = text or ""
    for match in DURATION_RE.finditer(source):
        before = source[: match.start()]
        after = source[match.end():]
        if YEAR_CONTEXT_RE.search(before) or YEAR_SUFFIX_RE.match(after):
            continue
        if match.group(2) in {"年"} and (match.group(1) or "").isdigit() and 60 <= int(match.group(1)) <= 130:
            continue  # 「114年」這種數字在台灣文件裡幾乎都是民國年
        if match.group(2) in {"月", "個月"} and before.rstrip().endswith("年"):
            continue  # 「90年1月1日」的「1月」是日期的一部分
        number = chinese_to_int(match.group(1))
        if number is None:
            continue
        unit = match.group(2)
        return number * 12 if unit == "年" else number
    return None
