"""處理「摘錄裡沒有寫這個縣市」的戶籍縣市規則。

本地 AI 會把「設籍本市」補成某個具體縣市。兩種情形要分開：
  · 補成的就是這個方案的機關轄區 → 留著，但標成「依機關推定」並寫明依據（誠實標記，不是刪掉正確資料）。
  · 補成別的縣市，或把一句話展開成一長串縣市清單（戶籍謄本、火車票那種句子）→ 刪掉，沒有原文佐證。
加 --dry 只看不改。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, utcnow  # noqa: E402
from app.services.extractor import Extractor  # noqa: E402
from app.services.normalization import find_cities  # noqa: E402

ATTRIBUTE = "residence.household_city"


def main() -> int:
    dry = "--dry" in sys.argv
    db = get_db()
    dropped_records = dropped = marked = 0
    for row in db.benefits.find({"rules.attribute_id": ATTRIBUTE}, {"rules": 1, "title": 1, "benefit": 1, "provider": 1, "provider_region": 1}):
        rules = row.get("rules") or []
        jurisdiction = row.get("provider_region") or Extractor._jurisdiction(row.get("provider") or "", row.get("title") or "", {})
        kept: list[dict] = []
        changed = False
        for rule in rules:
            if rule.get("attribute_id") != ATTRIBUTE or rule.get("inferred"):
                kept.append(rule)
                continue
            value = rule.get("value")
            wanted = [c for c in dict.fromkeys(value if isinstance(value, list) else [value]) if c]
            excerpt = (rule.get("evidence") or {}).get("excerpt") or ""
            named = set(find_cities(excerpt))
            if all(city in named for city in wanted):
                kept.append(rule)
                continue
            if jurisdiction and wanted == [jurisdiction]:
                # 「設籍本市」＋機關轄區＝可接受的推定，但要標明白
                rule = {**rule, "inferred": True,
                        "inference_basis": f"摘錄只寫「本市／本縣」，依機關「{row.get('provider') or ''}」的轄區推定為{jurisdiction}",
                        "human_readable": (rule.get("human_readable") or "") + ("（依機關推定）" if "（依機關推定）" not in (rule.get("human_readable") or "") else "")}
                kept.append(rule)
                marked += 1
                changed = True
                continue
            print(f"- 刪：{(row.get('title') or '')[:32]}：{rule.get('operator')} {str(wanted)[:60]} ← 「{excerpt[:46]}」")
            dropped += 1
            changed = True
        if not changed:
            continue
        dropped_records += 1
        if dry:
            continue
        db.benefits.update_one(
            {"_id": row["_id"]},
            {"$set": {"rules": kept, "index": Extractor.build_index({**row, "rules": kept}), "updated_at": utcnow()}},
        )
    print(f"{'（試跑）' if dry else ''}{dropped_records} 筆紀錄：刪掉 {dropped} 條沒有佐證的戶籍規則、{marked} 條改標為依機關推定")
    return 0


if __name__ == "__main__":
    sys.exit(main())
