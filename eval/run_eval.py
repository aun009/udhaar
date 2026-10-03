#!/usr/bin/env python3
"""Evaluate parser on synthetic and real-audio splits."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.heuristic_parser import parse_transcript_heuristic
from app.llm_client import ollama_available, parse_with_llm
from data.schema import label_to_json

DATA_OUT = ROOT / "data" / "out"
RESULTS_JSON = ROOT / "eval" / "results.json"
RESULTS_MD = ROOT / "eval" / "RESULTS.md"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def normalize_label(label: dict) -> dict:
    return {
        "customer": (label.get("customer") or "").strip(),
        "amount": label.get("amount"),
        "type": label.get("type"),
        "note": label.get("note"),
        "error": label.get("error"),
    }


def field_acc(golds: list[dict], preds: list[dict], field: str) -> float:
    if not golds:
        return 0.0
    ok = sum(1 for g, p in zip(golds, preds) if g.get(field) == p.get(field))
    return ok / len(golds)


def exact_json_acc(golds: list[dict], preds: list[dict]) -> float:
    if not golds:
        return 0.0
    ok = 0
    for g, p in zip(golds, preds):
        if label_to_json(normalize_label(g)) == label_to_json(normalize_label(p)):
            ok += 1
    return ok / len(golds)


def valid_json_rate(preds: list[dict]) -> float:
    if not preds:
        return 0.0
    from data.schema import validate_label

    ok = sum(1 for p in preds if validate_label(normalize_label(p))[0])
    return ok / len(preds)


async def run_model_on_rows(
    rows: list[dict],
    parser: Callable[[str], Any],
) -> list[dict]:
    preds = []
    for row in rows:
        transcript = row["transcript"]
        if asyncio.iscoroutinefunction(parser):
            pred, _ = await parser(transcript)
        else:
            pred = parser(transcript)
        if isinstance(pred, tuple):
            pred = pred[0]
        preds.append(normalize_label(pred or {}))
    return preds


def evaluate_split(name: str, rows: list[dict], preds: list[dict]) -> dict:
    golds = [normalize_label(r["label"]) for r in rows]
    return {
        "split": name,
        "n": len(rows),
        "exact_json": round(exact_json_acc(golds, preds), 4),
        "customer_acc": round(field_acc(golds, preds, "customer"), 4),
        "amount_acc": round(field_acc(golds, preds, "amount"), 4),
        "type_acc": round(field_acc(golds, preds, "type"), 4),
        "valid_json_rate": round(valid_json_rate(preds), 4),
    }


def worst_failures(rows: list[dict], preds: list[dict], k: int = 10) -> list[dict]:
    golds = [normalize_label(r["label"]) for r in rows]
    bad = []
    for row, g, p in zip(rows, golds, preds):
        if label_to_json(g) != label_to_json(p):
            bad.append(
                {
                    "transcript": row["transcript"][:120],
                    "gold": g,
                    "pred": p,
                }
            )
    return bad[:k]


async def llm_parser(transcript: str):
    return await parse_with_llm(transcript)


def heuristic_parser(transcript: str) -> dict:
    return parse_transcript_heuristic(transcript)


def load_real_rows(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    rows = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("audio_file", "").startswith("clip_") and "expected_json" in r:
                label = json.loads(r["expected_json"])
                rows.append(
                    {
                        "transcript": r.get("transcript") or "",
                        "label": label,
                        "audio_file": r["audio_file"],
                    }
                )
    return rows


def render_md(all_results: dict) -> str:
    lines = [
        "# Parser evaluation results",
        "",
        "Metrics are computed on held-out synthetic splits unless noted.",
        "Re-run: `PYTHONPATH=. python eval/run_eval.py --all`",
        "",
        "| Model | Split | N | Exact JSON | Customer | Amount | Type | Valid JSON |",
        "|-------|-------|---|------------|----------|--------|------|------------|",
    ]
    for model_name, splits in all_results.get("models", {}).items():
        for s in splits:
            lines.append(
                f"| {model_name} | {s['split']} | {s['n']} | {s['exact_json']:.2%} | "
                f"{s['customer_acc']:.2%} | {s['amount_acc']:.2%} | {s['type_acc']:.2%} | "
                f"{s['valid_json_rate']:.2%} |"
            )
    lines.extend(["", "## Notes", ""])
    for note in all_results.get("notes", []):
        lines.append(f"- {note}")
    if all_results.get("worst_failures"):
        lines.extend(["", "## Worst failures (sample)", ""])
        for w in all_results["worst_failures"]:
            lines.append(f"- **{w['transcript']}…**")
            lines.append(f"  - gold: `{json.dumps(w['gold'], ensure_ascii=False)}`")
            lines.append(f"  - pred: `{json.dumps(w['pred'], ensure_ascii=False)}`")
    return "\n".join(lines) + "\n"


async def main_async(args: argparse.Namespace) -> None:
    notes: list[str] = []
    models: dict[str, list[dict]] = {}

    test_path = DATA_OUT / "test.jsonl"
    unseen_path = DATA_OUT / "test_unseen.jsonl"
    if not test_path.exists():
        print("Missing data/out — run: PYTHONPATH=. python data/generate.py")
        sys.exit(1)

    test_rows = load_jsonl(test_path)
    unseen_rows = load_jsonl(unseen_path) if unseen_path.exists() else []

    parsers: list[tuple[str, Callable]] = [("heuristic_baseline", heuristic_parser)]

    if args.use_ollama and await ollama_available():
        parsers.append(("qwen_base_ollama", llm_parser))
        notes.append("Ollama base model eval included.")
    else:
        notes.append(
            "Ollama not running — skipped LLM baseline. Start `ollama serve` and "
            "`ollama pull qwen2.5:3b-instruct`, then re-run with --use-ollama."
        )

    if os.environ.get("OPENAI_API_KEY") and args.use_closed_ref:
        notes.append("Closed reference eval: TODO(me) — optional OpenAI call not wired in CI.")
    else:
        notes.append("Closed reference skipped (no OPENAI_API_KEY or --use-closed-ref).")

    if os.environ.get("TINKER_API_KEY"):
        notes.append(
            "Fine-tuned model: run train/tinker_train.py then export to Ollama; "
            "set UDHAAR_USE_FINETUNED=1 and re-run eval."
        )
    else:
        notes.append(
            "TINKER_API_KEY not set — fine-tuned row pending. See train/README.md."
        )

    worst: list[dict] = []
    for model_name, parser in parsers:
        split_results = []
        for split_name, rows in [
            ("synthetic_test", test_rows),
            ("unseen_template_test", unseen_rows),
        ]:
            if not rows:
                continue
            preds = await run_model_on_rows(rows, parser)
            split_results.append(evaluate_split(split_name, rows, preds))
            if model_name == parsers[0][0] and split_name == "synthetic_test":
                worst = worst_failures(rows, preds, 10)
        models[model_name] = split_results

    real_csv = Path(args.real_audio)
    real_rows = load_real_rows(real_csv)
    if real_rows:
        preds = await run_model_on_rows(real_rows, heuristic_parser)
        models.setdefault("heuristic_baseline", []).append(
            evaluate_split("real_audio", real_rows, preds)
        )
        notes.append(f"Real-audio CSV: {len(real_rows)} labeled clips.")
    else:
        notes.append(
            "Real-audio eval empty — add clips to data/real_test/labels.csv (see README)."
        )

    payload = {"models": models, "notes": notes, "worst_failures": worst}
    RESULTS_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    RESULTS_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="Run all available baselines")
    p.add_argument("--use-ollama", action="store_true", default=True)
    p.add_argument("--use-closed-ref", action="store_true")
    p.add_argument(
        "--real-audio",
        default=str(ROOT / "data" / "real_test" / "labels.csv"),
    )
    asyncio.run(main_async(p.parse_args()))


if __name__ == "__main__":
    main()
