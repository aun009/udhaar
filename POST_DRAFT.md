# Udhaar: a private voice khata for a kirana shopkeeper

*Submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01).* 

## What I built

I built **Udhaar** for **[friend's name and relationship]**, who runs a neighbourhood kirana shop in **[city/neighbourhood]**. Their recurring problem was recording small customer debts quickly while serving the next person. Paper notes get lost, and a cloud app is a poor fit for sensitive customer names and balances.

Udhaar lets the shopkeeper speak or type a Hindi, Marathi, or Hinglish entry such as “Ramesh ji ko 340 ka samaan udhaar”. It proposes a structured entry, asks the shopkeeper to confirm it, and then updates a simple khata.

It also shows balances, a monthly summary, and polite WhatsApp reminder links. The links are always manually opened and sent; the app never messages a customer automatically.

## Demo

- Live demo or short video: **[add link]**
- Repository: https://github.com/aun009/udhaar
- Local demo: `UDHAAR_MOCK=1 uvicorn app.main:app --host 0.0.0.0 --port 8000`, then open `http://127.0.0.1:8000`.

The mock mode runs without a GPU, microphone, or network model service. The production path uses local Whisper and Ollama instead.

## How I built it

The system is a small FastAPI application with SQLite storage and a single mobile-friendly HTML page:

1. Audio is transcribed locally with `faster-whisper` when voice mode is enabled.
2. An open-weight Qwen instruct model served by Ollama converts the transcript into a strict JSON label.
3. The UI displays the proposed customer, amount, type, and note for confirmation.
4. Confirmed entries are stored locally in SQLite and used for balances and summaries.
5. A deterministic Hindi/Marathi reminder template produces a WhatsApp link for manual sending.

The repository also includes a synthetic Hindi/Marathi/Hinglish dataset generator, an evaluation runner, and a heuristic fallback so the core demo remains usable when Ollama is unavailable.

## Why open innovation mattered

Open models made the important parts adaptable instead of hiding them behind a remote API. Customer names and dues can remain on the shop laptop, amount-word examples can be added to the training set, and the parser model can be swapped or fine-tuned. Once the local runtime is installed, there is no per-entry API bill and the workflow can continue when the internet is unreliable.

That control has a cost: local model setup is more involved, and zero-shot parsing is less robust than a strong hosted model on messy speech. For this friend and this data, keeping the ledger private and editable was the better trade.

## Results and limitations

The reproducible heuristic baseline currently scores:

| Split | Examples | Exact JSON | Customer | Amount | Type | Valid JSON |
|---|---:|---:|---:|---:|---:|---:|
| Synthetic test | 400 | 16.00% | 47.50% | 48.00% | 94.00% | 100.00% |
| Unseen templates | 120 | 10.00% | 25.83% | 53.33% | 93.33% | 100.00% |

The second row should be read as 120 examples, 10.00% exact JSON, 25.83% customer, 53.33% amount, 93.33% type, and 100.00% valid JSON. These are baseline numbers, not a claim that the parser is solved. Ollama, fine-tuning, and real-audio rows are intentionally omitted until they are run locally.

## What my friend said

> **[Add a short quote after handing over the demo. Do not invent this.]**

## Open source and code

- Source: https://github.com/aun009/udhaar
- Evaluation details: `eval/RESULTS.md`
- Training notes: `train/README.md`

## My agent session

**[Optional: add the DevRelay agent-session link or remove this section.]**

## Partner categories

**[List only categories that actually apply, or remove this section.]**
