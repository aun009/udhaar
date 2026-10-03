# Udhaar — decisions log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-03 | Python FastAPI + SQLite for MVP backend | Fast ML glue; user prefers over Spring for this hackathon timeline |
| 2026-10-03 | Default parser model: Qwen2.5-3B-Instruct (GGUF Q4) via Ollama | Balance of quality vs CPU RAM; Qwen3-4B if Ollama tag available locally |
| 2026-10-03 | faster-whisper `small` int8 on CPU | Spec requirement; good Hindi coverage |
| 2026-10-03 | Parser label schema includes optional `"error"` | Hard negatives (no amount, ambiguous) need explicit flags for training/eval |
| 2026-10-03 | Phase 1 first: synthetic JSONL before any app wiring | End-to-end pipeline priority; eval table needs data |
| 2026-10-03 | `UDHAAR_MOCK=1` uses heuristic parser | Unblocks demo/tests without Ollama; LLM path when Ollama up |
| 2026-10-03 | Tinker train script uses async SDK pattern from docs | Adjust if SDK API differs; Unsloth fallback in train/README |
| 2026-10-03 | Reminders: template Hindi/Marathi (no auto WhatsApp) | Safety + spec; LLM polish optional later |
