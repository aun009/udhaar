#!/usr/bin/env python3
"""Convert train.jsonl to chat SFT format for Tinker / HF."""

from __future__ import annotations

import json
from pathlib import Path

from app.llm_client import training_system_prompt

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "data" / "out" / "train.jsonl"
OUT_PATH = ROOT / "train" / "sft_train.jsonl"


def main() -> None:
    system = training_system_prompt()
    count = 0
    with IN_PATH.open(encoding="utf-8") as fin, OUT_PATH.open("w", encoding="utf-8") as fout:
        for line in fin:
            row = json.loads(line)
            conv = {
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": row["transcript"]},
                    {
                        "role": "assistant",
                        "content": json.dumps(row["label"], ensure_ascii=False),
                    },
                ]
            }
            fout.write(json.dumps(conv, ensure_ascii=False) + "\n")
            count += 1
    print(f"Wrote {count} conversations to {OUT_PATH}")


if __name__ == "__main__":
    main()
