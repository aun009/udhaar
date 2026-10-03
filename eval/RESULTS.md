# Parser evaluation results

Metrics are computed on held-out synthetic splits unless noted.
Re-run: `PYTHONPATH=. python eval/run_eval.py --all`

| Model | Split | N | Exact JSON | Customer | Amount | Type | Valid JSON |
|-------|-------|---|------------|----------|--------|------|------------|
| heuristic_baseline | synthetic_test | 400 | 16.00% | 47.50% | 48.00% | 94.00% | 100.00% |
| heuristic_baseline | unseen_template_test | 120 | 10.00% | 25.83% | 53.33% | 93.33% | 100.00% |

## Notes

- Ollama not running — skipped LLM baseline. Start `ollama serve` and `ollama pull qwen2.5:3b-instruct`, then re-run with --use-ollama.
- Closed reference skipped (no OPENAI_API_KEY or --use-closed-ref).
- TINKER_API_KEY not set — fine-tuned row pending. See train/README.md.
- Real-audio eval empty — add clips to data/real_test/labels.csv (see README).

## Worst failures (sample)

- **Hanuman tai ko chaar sau rupees ka samaan diya on credit…**
  - gold: `{"customer": "Hanuman tai", "amount": 400, "type": "credit_given", "note": null, "error": null}`
  - pred: `{"customer": "Hanuman tai", "amount": null, "type": "credit_given", "note": null, "error": "missing_amount"}`
- **payment received Khanna tai dhai sau pachhattar…**
  - gold: `{"customer": "Khanna tai", "amount": 275, "type": "payment_received", "note": null, "error": null}`
  - pred: `{"customer": "payment", "amount": 275, "type": "payment_received", "note": null, "error": null}`
- **uh Laxman kaka ko teen sau pachaas udhaar diya haan…**
  - gold: `{"customer": "Laxman kaka", "amount": 350, "type": "credit_given", "note": null, "error": null}`
  - pred: `{"customer": "uh Laxman kaka", "amount": 350, "type": "credit_given", "note": null, "error": null}`
- **udhaar entry Priti ben do sau…**
  - gold: `{"customer": "Priti ben", "amount": 200, "type": "credit_given", "note": null, "error": null}`
  - pred: `{"customer": "udhaar", "amount": null, "type": "credit_given", "note": null, "error": "missing_amount"}`
- **pandhra ghetle Savitri ben kadun…**
  - gold: `{"customer": "Savitri ben", "amount": 15, "type": "payment_received", "note": null, "error": null}`
  - pred: `{"customer": "pandhra", "amount": null, "type": "payment_received", "note": null, "error": null}`
- **Chintu saheb cha paach hazaar udhaar liha…**
  - gold: `{"customer": "Chintu saheb", "amount": 5000, "type": "credit_given", "note": "namak", "error": null}`
  - pred: `{"customer": "Chintu saheb", "amount": null, "type": "credit_given", "note": null, "error": "missing_amount"}`
- **Vitthal bhau ne 150 rupaye ka payment kiya…**
  - gold: `{"customer": "Vitthal bhau", "amount": 150, "type": "payment_received", "note": "cheeni half kilo", "error": null}`
  - pred: `{"customer": "Vitthal bhau", "amount": 150, "type": "payment_received", "note": null, "error": null}`
- **saath paach ghetle Dattatray saheb kadun…**
  - gold: `{"customer": "Dattatray saheb", "amount": 65, "type": "payment_received", "note": null, "error": null}`
  - pred: `{"customer": "saath", "amount": null, "type": "payment_received", "note": null, "error": null}`
- **Beena aaji cha tees paach udhaar liha…**
  - gold: `{"customer": "Beena aaji", "amount": 35, "type": "credit_given", "note": "chai patti", "error": null}`
  - pred: `{"customer": "Beena aaji", "amount": null, "type": "credit_given", "note": null, "error": "missing_amount"}`
- **aaj cha hisaab Mahendra saheb ₹900…**
  - gold: `{"customer": "Mahendra saheb", "amount": 900, "type": "payment_received", "note": null, "error": null}`
  - pred: `{"customer": "aaj", "amount": 900, "type": "credit_given", "note": null, "error": null}`
