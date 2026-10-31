"""教育部開放資料（政府資料開放平臺）→ providers 集合，給前台「附近教育資源」使用。

資料集 CSV 從政府資料開放平臺下載後放在 data/opendata/moe/，啟動時若資料庫還沒有就匯入；
匯入的每筆資料保留原始欄位、資料集編號與授權，前台標示出處。授權皆為「政府資料開放授權條款－第1版」。
"""

from __future__ import annotations

import csv
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ..config import get_settings
from ..db import get_db
from .normalization import find_cities

log = logging.getLogger(__name__)
LICENSE = "政府資料開放授權條款－第1版"

# nid 是 data.gov.tw/dataset/{nid} 的編號；欄位名稱對應各資料集原本的 CSV 標題列
DATASETS = [
    {"nid": 163769, "file": "leling.csv", "kind": "樂齡學習中心", "agency": "教育部終身教育司", "title": "全國樂齡學習中心聯繫資料", "audience": "55 歲以上長者",
     "fields": {"name": "樂齡中心名稱", "city": "縣市", "district": "鄉鎮市區名稱", "address": "中心地址", "phone": "中心電話", "operator": "承辦單位"}},
    {"nid": 162867, "file": "newres.csv", "kind": "新住民學習中心", "agency": "教育部終身教育司", "title": "新住民學習中心據點資料", "audience": "新住民及其家人",
     "fields": {"name": "設置地點", "city": "縣市", "address": "地址", "phone": "聯絡電話"}},
    {"nid": 160225, "file": "afterschool.csv", "kind": "兒童課後照顧中心", "agency": "教育部終身教育司", "title": "全國立案兒童課後照顧服務中心基本資料", "audience": "國小學童家庭",
     "fields": {"name": "名稱", "city": "縣市", "address": "地址", "phone": "電話", "registered": "立案時間"}},
]


def dataset_url(nid: int) -> str:
    return f"https://data.gov.tw/dataset/{nid}"


def _folder() -> Path:
    return get_settings().data_path / "opendata" / "moe"


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def import_moe_opendata(force: bool = False) -> dict[str, int]:
    """匯入教育部開放資料；已匯入的資料集（以 source_id 判斷）略過，force=True 則重新寫入。回傳各資料集的筆數。"""
    db = get_db()
    now = datetime.now(timezone.utc)
    result: dict[str, int] = {}
    for dataset in DATASETS:
        source_id = f"moe_od_{dataset['nid']}"
        path = _folder() / dataset["file"]
        if not path.exists():
            log.info("moe open data file missing: %s", path)
            continue
        if not force and db.providers.count_documents({"source_id": source_id}) > 0:
            result[source_id] = db.providers.count_documents({"source_id": source_id})
            continue
        fields = dataset["fields"]
        count = 0
        for row in _read(path):
            name = (row.get(fields["name"]) or "").strip()
            if not name:
                continue
            address = (row.get(fields["address"]) or "").strip()
            city = (find_cities(row.get(fields["city"]) or "") or find_cities(address) or [""])[0]
            key = hashlib.sha1(f"{name}|{address}".encode("utf-8")).hexdigest()[:20]
            db.providers.update_one(
                {"source_id": source_id, "record_key": key},
                {"$set": {"name": name[:200], "service_kind": dataset["kind"], "city": city, "address": address[:200], "phone": (row.get(fields["phone"]) or "").strip()[:60],
                          "district": (row.get(fields.get("district", ""), "") or "").strip(), "operator": (row.get(fields.get("operator", ""), "") or "").strip(),
                          "record": row, "source_url": dataset_url(dataset["nid"]), "source_name": f"政府資料開放平臺：{dataset['title']}（{dataset['agency']}）",
                          "dataset": {"nid": dataset["nid"], "title": dataset["title"], "agency": dataset["agency"], "license": LICENSE, "audience": dataset["audience"]},
                          "crawl_time": now, "updated_at": now},
                 "$setOnInsert": {"_id": str(uuid.uuid4()), "created_at": now}},
                upsert=True,
            )
            count += 1
        result[source_id] = count
        log.info("moe open data %s: %d rows", dataset["title"], count)
    return result


def datasets_summary() -> list[dict]:
    """前台「資料來源」：每個資料集的名稱、機關、授權、網址與目前筆數。"""
    db = get_db()
    return [{"nid": d["nid"], "title": d["title"], "agency": d["agency"], "kind": d["kind"], "license": LICENSE, "audience": d["audience"], "url": dataset_url(d["nid"]),
             "count": db.providers.count_documents({"source_id": f"moe_od_{d['nid']}"})} for d in DATASETS]
