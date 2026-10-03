# Hacktoberfest Weekend Challenge submission checklist

The project is technically demo-ready. Complete these human-owned items before publishing the DEV post:

## Required before publishing

- [ ] Replace the friend and location placeholders in `POST_DRAFT.md`.
- [ ] Hand the demo to that person and record one honest reaction or quote.
- [ ] Add a public GitHub repository URL.
- [ ] Add either a deployed URL or a short screen recording showing parse → confirm → balance.
- [ ] Run `source .venv/bin/activate && pytest -q` and confirm all tests pass.
- [ ] Run `PYTHONPATH=. python eval/run_eval.py --all` and copy any newly measured results.
- [ ] Remove unused placeholder sections or fill them with real links.

## Recommended demo capture

1. Start with `UDHAAR_MOCK=1 uvicorn app.main:app --host 0.0.0.0 --port 8000`.
2. Enter “Ramesh ji ko 340 ka samaan udhaar”.
3. Show the proposed label and edit/confirm it.
4. Show the customer balance and monthly summary.
5. Explain that WhatsApp reminders are links for manual sending only.

## Publish

Paste the completed `POST_DRAFT.md` into DEV, add the demo and repository links, select the Hacktoberfest Weekend Challenge, and submit before the deadline shown on the challenge page.
