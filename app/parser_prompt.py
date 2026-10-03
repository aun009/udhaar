"""Prompts for ledger entry parsing."""

from __future__ import annotations

import json
from pathlib import Path

SYSTEM_PROMPT = """You parse spoken Hindi/Marathi/Hinglish kirana shop ledger lines into strict JSON.
Output ONLY one JSON object with keys: customer (string), amount (integer or null), type ("credit_given" or "payment_received"), note (string or null), error (string or null).
Rules:
- credit_given = udhaar / samaan diya on credit; payment_received = payment diye / hisaab chukta / jama.
- Indian number words: dhai sau=250, derh sau=150, saade teen sau=350, sawa sau=125, pandrah sau=1500, derh hazaar=1500.
- Honorifics stay in customer: "Ramesh ji", "Sharma bhai".
- If speaker corrects amount ("nahi 240 nahi 340"), use the corrected final amount.
- If quantity and price both appear ("2 kilo chawal, 120 ka"), amount is the rupee price not kg.
- If no amount is stated, set amount null and error "missing_amount".
- note is optional item detail only when mentioned (e.g. doodh ka packet).
"""


def load_few_shot(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def build_messages(transcript: str, few_shot: list[dict]) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in few_shot:
        messages.append({"role": "user", "content": ex["transcript"]})
        messages.append(
            {"role": "assistant", "content": json.dumps(ex["label"], ensure_ascii=False)}
        )
    messages.append({"role": "user", "content": transcript})
    return messages
