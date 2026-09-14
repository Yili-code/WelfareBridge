"""把「矛盾規則鬆綁」誤併的身分擇一群組拆回必要條件。

鬆綁只有在條件互斥（低收／中低收）時才成立；先前的清單把「老人＋身心障礙」「老人＋原住民」
「單親＋特殊境遇」也當成互斥，於是把兩條各自必要的身分條件併成擇一，等於放寬資格。
這支腳本只動 `relax_contradictory_rules` 產生的群組（group_id 以 any_identity_tags 開頭），
原文真的寫「符合下列之一」而由抽取器產生的 alternative_／clause_any_ 群組不碰。加 --dry 只看不改。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, utcnow  # noqa: E402
from app.services.extractor import EXCLUSIVE_TAG_SETS, LIST_ITEM_RE, Extractor, _tag_of  # noqa: E402

PREFIX = "any_identity_tags"


def from_distinct_list_items(members: list[dict]) -> bool:
    """每條規則各自引用一個條列項（一、／二、／(1)）→ 原文本來就是條列，擇一有依據。"""
    excerpts = [((r.get("evidence") or {}).get("excerpt") or "").strip() for r in members]
    items = [e for e in excerpts if LIST_ITEM_RE.match(e)]
    return len(items) == len(members) and len(set(items)) == len(members) and len(members) > 1


def main() -> int:
    dry = "--dry" in sys.argv
    db = get_db()
    records = groups = demoted = 0
    for row in db.benefits.find({"rules.group_id": {"$regex": "^" + PREFIX}}, {"rules": 1, "title": 1, "benefit": 1}):
        rules = row.get("rules") or []
        by_group: dict[str, list[dict]] = {}
        for rule in rules:
            if str(rule.get("group_id") or "").startswith(PREFIX):
                by_group.setdefault(rule["group_id"], []).append(rule)
        touched = False
        for group, members in by_group.items():
            tags = {_tag_of(r.get("value")) for r in members} - {None}
            if any(tags <= exclusive for exclusive in EXCLUSIVE_TAG_SETS):
                continue  # 整組都是互斥身分，擇一是對的
            if from_distinct_list_items(members):
                continue  # 原文是條列（一、二、三…），擇一有原文依據
            # 只留下真的互斥的那一小群當擇一（低收／中低收），其餘各自回到必要條件
            cluster: set[str] = set()
            for exclusive in EXCLUSIVE_TAG_SETS:
                overlap = tags & exclusive
                if len(overlap) > 1 and len(overlap) > len(cluster):
                    cluster = overlap
            groups += 1
            touched = True
            print(f"- {(row.get('title') or '')[:32]}：{sorted(tags)} → 擇一 {sorted(cluster) or '無'}，其餘各自必要")
            index = 0
            title = (row.get("title") or "").strip()
            for rule in members:
                tag = _tag_of(rule.get("value"))
                if tag in cluster:
                    continue  # 留在原本的擇一群組
                index += 1
                rule["group_id"] = f"identity_tags_{index}"
                rule["human_readable"] = (rule.get("human_readable") or "").replace("（擇一）", "")
                excerpt = ((rule.get("evidence") or {}).get("excerpt") or "").strip()
                if excerpt != title:
                    # 條件來自內文的某一句，原文沒說這些身分是「同時」還是「擇一」→ 留著但標為需語意判斷，
                    # 媒合時不會直接判不符合（不製造假的不符合，也不假裝是擇一）
                    rule["complexity"] = "complex"
                    demoted += 1
        if not touched:
            continue
        records += 1
        if dry:
            continue
        db.benefits.update_one(
            {"_id": row["_id"]},
            {"$set": {"rules": rules, "index": Extractor.build_index({**row, "rules": rules}), "updated_at": utcnow()}},
        )
    print(f"{'（試跑）' if dry else ''}{records} 筆紀錄、{groups} 個群組拆回必要條件，其中 {demoted} 條改標為需語意判斷")
    return 0


if __name__ == "__main__":
    sys.exit(main())
