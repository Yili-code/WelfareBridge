"""比較兩次獨立標註（pass1 / pass2）：閘門與主類別一致率，列出不一致的案例；輸出合併用的 JSON。
合併規則：閘門一致 → 採用；閘門不一致 → 我（主流程）逐筆讀原文裁決，這裡先列出來；主類別不一致但閘門一致 → 主類別採 pass1，pass2 的主類別加入 secondary，confidence 降為 medium。
用法：python compare_labels.py <labels_dir> <batch_dir> → 寫 <labels_dir>/merged_auto.json 與 <labels_dir>/disagreements.txt
"""
from __future__ import annotations

import io
import json
import os
import re
import sys


def load(path):
    return {l["id"]: l for l in json.load(io.open(path, encoding="utf-8")).get("labels", [])}


def doc_text(batch_dir, batch, doc_id):
    text = io.open(os.path.join(batch_dir, batch + ".txt"), encoding="utf-8").read()
    m = re.search(r"##### " + re.escape(doc_id) + r"\n(.*?)(?=\n##### |\Z)", text, re.S)
    return m.group(1) if m else ""


def main(labels_dir, batch_dir):
    merged, disagreements = [], []
    gate_agree = cat_agree = total = 0
    for f in sorted(os.listdir(labels_dir)):
        if not f.endswith("_pass1.json"):
            continue
        batch = f.replace("_pass1.json", "")
        p1 = load(os.path.join(labels_dir, f))
        p2_path = os.path.join(labels_dir, batch + "_pass2.json")
        p2 = load(p2_path) if os.path.exists(p2_path) else {}
        for i, a in p1.items():
            total += 1
            b = p2.get(i)
            row = dict(a)
            if b is None:
                row["_note"] = "只有一次標註"
                merged.append(row)
                continue
            if a["is_benefit"] == b["is_benefit"]:
                gate_agree += 1
                if (a.get("category") or "") == (b.get("category") or ""):
                    cat_agree += 1
                else:
                    sec = list(dict.fromkeys((a.get("secondary") or []) + ([b["category"]] if b.get("category") else []) + (b.get("secondary") or [])))
                    row["secondary"] = [s for s in sec if s != a.get("category")]
                    row["confidence"] = "medium"
                    row["_note"] = f"主類別不一致：pass2={b.get('category')}"
                merged.append(row)
            else:
                disagreements.append((batch, i, a, b))
    print(f"total {total} | gate agree {gate_agree} ({gate_agree / max(total, 1):.2%}) | category agree {cat_agree} ({cat_agree / max(gate_agree, 1):.2%} of gate-agreed) | gate disagreements {len(disagreements)}")
    io.open(os.path.join(labels_dir, "merged_auto.json"), "w", encoding="utf-8").write(json.dumps({"labels": merged, "count": len(merged)}, ensure_ascii=False, indent=1))
    with io.open(os.path.join(labels_dir, "disagreements.txt"), "w", encoding="utf-8") as out:
        for batch, i, a, b in disagreements:
            out.write(f"##### {i} ({batch})\nPASS1: {a['is_benefit']}/{a.get('kind')}/{a.get('category')} — {a.get('reason')}\nPASS2: {b['is_benefit']}/{b.get('kind')}/{b.get('category')} — {b.get('reason')}\n")
            out.write(doc_text(batch_dir, batch, i)[:2500] + "\n\n")
    print("wrote merged_auto.json and disagreements.txt")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
