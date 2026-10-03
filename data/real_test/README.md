# Real shop audio — honest eval set

Record **20–30** short clips on a phone in the shop environment (fan noise, customers, Hindi/Marathi/Hinglish). Do **not** commit real customer names or phone numbers.

## Setup

1. Copy `labels_template.csv` to `labels.csv`.
2. Save WAV/MP3 files under `audio/` (e.g. `clip_01.wav`).
3. Fill `expected_json` with hand-written gold labels (same schema as synthetic data).

## Label schema

```json
{"customer": "Ramesh ji", "amount": 340, "type": "credit_given", "note": null, "error": null}
```

Use `"error": "missing_amount"` when no amount is spoken.

## Recording tips

- 3–8 seconds per clip; one ledger action per file.
- Include at least: 5 credit entries, 5 payments, 3 irregular amounts (dhai sau, pandrah sau), 3 noisy/failed cases.
- Note dialect (Hindi/Marathi) in the `dialect` column for reminder tuning later.

## Eval

After transcription (faster-whisper), run Phase 2 `eval/run_eval.py --real-audio data/real_test/labels.csv`.

**TODO(me):** Add shopkeeper name and hand-over quote in `POST_DRAFT.md` after field testing.
