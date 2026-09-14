"""確定性驗證：對 candidates/ 裡的每個候選 YAML 重跑乾跑，數 program 頁、檢查官方網域與 getgrant，輸出摘要表。
用法：python verify_candidates.py <id1> <id2> ... | --all [--max-items 12]
"""
from __future__ import annotations

import io
import os
import re
import subprocess
from pathlib import Path
import sys

BACKEND = str(Path(__file__).resolve().parents[2])
PY = os.path.join(BACKEND, ".venv/Scripts/python.exe")
HERE = os.path.dirname(os.path.abspath(__file__))
CAND_DIR = os.path.join(HERE, "candidates")
DRY = os.path.join(HERE, "dry_run_candidate.py")


def main(argv: list[str]) -> int:
    max_items = "12"
    if "--max-items" in argv:
        max_items = argv[argv.index("--max-items") + 1]
    ids = [a for a in argv if not a.startswith("--") and a != max_items]
    if "--all" in argv:
        ids = [f[:-5] for f in sorted(os.listdir(CAND_DIR)) if f.endswith(".yaml") and not f.startswith("_")]
    rows = []
    for sid in ids:
        path = os.path.join(CAND_DIR, sid + ".yaml")
        text = io.open(path, encoding="utf-8").read()
        bad = "getgrant" in text.lower()
        proc = subprocess.run([PY, DRY, path, "--max-items", max_items], capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8"}, cwd=BACKEND)
        out = proc.stdout + proc.stderr
        official = "official=True" in out
        docs = re.findall(r"^\s+kind=(\w+) kw_benefit=(\w+) conf=([\d.]+) cats=.* text=(\d+) chars", out, re.M)
        program = sum(1 for k, _b, _c, n in docs if k == "program" and int(n) >= 300)
        program_kw = sum(1 for k, b, _c, n in docs if k == "program" and int(n) >= 300 and b == "True")
        kinds = {}
        for k, *_ in docs:
            kinds[k] = kinds.get(k, 0) + 1
        run = re.search(r"run: status=(\w+) discovered=(\d+) fetched=(\d+) failed=(\d+)", out)
        verdict = "reject" if (bad or not official) else ("ready" if program >= 3 else ("partial" if program else "reject"))
        rows.append((sid, verdict, official, program, program_kw, len(docs), kinds, run.groups() if run else None, bad))
        io.open(os.path.join(HERE, f"dryrun_{sid}.log"), "w", encoding="utf-8").write(out)
        print(f"{sid:<26} {verdict:<8} official={official} program≥300={program} (kw_yes {program_kw}) docs={len(docs)} kinds={kinds} run={run.groups() if run else 'n/a'}{'  !! getgrant' if bad else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
