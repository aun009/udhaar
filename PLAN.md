# Udhaar — 40h execution plan

| Phase | Goal | Exit criteria |
|-------|------|----------------|
| **1** | Synthetic JSONL + number tests + real-audio kit | 4k/300/400 splits; pytest green; stats.json |
| **2** | `eval/run_eval.py` baselines (4B zero-shot, optional larger open / closed ref) | `eval/RESULTS.md` with real numbers |
| **3** | Tinker LoRA smoke → full → GGUF → Ollama flag | Fine-tuned weights load locally |
| **4** | Re-eval + 10 failure write-up | Updated RESULTS.md |
| **5** | Whisper + FastAPI + SQLite + single-page UI + pytest API | Demo path mock mode works |
| **6** | Docker, README mermaid, `POST_DRAFT.md` | One-command run documented |

**Now:** The locally runnable demo, evaluation baseline, API, UI, Docker setup,
and documentation are complete. Fine-tuning and real-audio evaluation are
optional operator-run tracks that require the external credentials, model
runtime, and labelled recordings described in `train/README.md` and
`data/real_test/README.md`.
