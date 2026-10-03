#!/usr/bin/env python3
"""
LoRA SFT on Tinker (Thinking Machines).

Requires: pip install tinker tinker-cookbook (see train/README.md)
Env: TINKER_API_KEY

Smoke test: python train/tinker_train.py --smoke
Full run:  python train/tinker_train.py --epochs 2 --rank 24
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SFT_PATH = ROOT / "train" / "sft_train.jsonl"


def ensure_sft() -> None:
    if not SFT_PATH.exists():
        os.system(f"{sys.executable} {ROOT / 'train' / 'prepare_sft_jsonl.py'}")


def load_conversations(limit: int | None) -> list[list[dict]]:
    rows = []
    with SFT_PATH.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line)["messages"])
            if limit and len(rows) >= limit:
                break
    return rows


async def run_smoke_or_full(smoke: bool, epochs: int, rank: int, model: str) -> None:
    if not os.environ.get("TINKER_API_KEY"):
        print("TINKER_API_KEY not set — aborting (see train/README.md for Unsloth fallback).")
        sys.exit(2)

    try:
        import tinker
    except ImportError as exc:
        print("Install tinker: uv pip install tinker tinker-cookbook")
        raise SystemExit(1) from exc

    ensure_sft()
    limit = 100 if smoke else None
    conversations = load_conversations(limit)
    print(f"Training on {len(conversations)} examples, model={model}, rank={rank}, epochs={epochs}")

    service = tinker.ServiceClient()
    training_client = await service.create_lora_training_client_async(
        base_model=model, rank=rank
    )
    tokenizer = training_client.get_tokenizer()

    # Minimal loop per Tinker tutorial 102 — forward_backward + optim_step per conversation
    lr = 2e-4
    for ep in range(epochs):
        loss_sum = 0.0
        for i, messages in enumerate(conversations):
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
            tokens = tokenizer.encode(text)
            # API shape may vary by SDK version — adjust per tinker-docs if this fails
            datum = tinker.Datum(tokens=tokens)
            result = await training_client.forward_backward_async([datum], loss_fn="cross_entropy")
            await training_client.optim_step_async(tinker.AdamParams(learning_rate=lr))
            loss_sum += float(getattr(result, "loss", 0) or 0)
            if smoke and i >= 5:
                break
        print(f"epoch {ep + 1}/{epochs} approx_loss={loss_sum / max(len(conversations), 1):.4f}")

    ckpt_path = ROOT / "train" / "checkpoints" / ("smoke" if smoke else "full")
    ckpt_path.mkdir(parents=True, exist_ok=True)
    await training_client.save_state_async(str(ckpt_path))
    print(f"Checkpoint saved to {ckpt_path}")
    print(
        "Export to GGUF: download weights from Tinker console / save_state, then "
        "llama.cpp convert + quantize Q4_K_M; register in Ollama as udhaar-parser."
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--rank", type=int, default=24)
    p.add_argument("--model", default="Qwen/Qwen3.5-4B")
    args = p.parse_args()
    asyncio.run(run_smoke_or_full(args.smoke, args.epochs, args.rank, args.model))


if __name__ == "__main__":
    main()
