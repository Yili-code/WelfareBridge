"""把程式實際使用的 LLM prompt（app/llm/prompts/*.md）同步到 docs/prompts/。

    python scripts/export_prompts.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.llm.prompts import PROMPT_DIR  # noqa: E402

TARGET = BACKEND.parent / "docs" / "prompts"


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for path in sorted(PROMPT_DIR.glob("*.md")):
        shutil.copyfile(path, TARGET / path.name)
        print(f"synced {path.name}")


if __name__ == "__main__":
    main()
