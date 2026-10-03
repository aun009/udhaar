# Fine-tuning Udhaar parser

## 1. Prepare SFT JSONL

```bash
PYTHONPATH=. python data/generate.py
PYTHONPATH=. python train/prepare_sft_jsonl.py
```

Output: `train/sft_train.jsonl` (chat format with system prompt + transcript → JSON label).

## 2. Tinker (preferred if you have credits)

```bash
export TINKER_API_KEY=...
uv pip install tinker tinker-cookbook

# Smoke (~100 examples, few steps)
PYTHONPATH=. python train/tinker_train.py --smoke

# Small budget full run
PYTHONPATH=. python train/tinker_train.py --epochs 2 --rank 24 --model Qwen/Qwen3.5-4B
```

Checkpoints: `train/checkpoints/`. Export merged weights via [Tinker docs](https://tinker-docs.thinkingmachines.ai/), convert to GGUF:

```bash
# After obtaining HF or gguf weights locally
ollama create udhaar-parser -f train/Modelfile
export UDHAAR_USE_FINETUNED=1
```

## 3. Fallback — Unsloth / Colab (if Tinker export blocked)

Document honestly in README if you use:

- HuggingFace `Qwen2.5-3B-Instruct` + Unsloth LoRA on `train/sft_train.jsonl`
- Merge adapters → GGUF Q4_K_M → Ollama

No fabricated metrics — re-run `eval/run_eval.py` after wiring the model.
