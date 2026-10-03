"""Polite WhatsApp reminder text (template fallback + optional LLM)."""

from __future__ import annotations

import urllib.parse
from datetime import datetime

from app.config import MOCK_MODE


def template_reminder(
    name: str,
    balance: int,
    dialect: str = "hindi",
    oldest_credit: str | None = None,
) -> str:
    when = "pichhle mahine"
    if oldest_credit:
        try:
            dt = datetime.fromisoformat(oldest_credit.replace("Z", "+00:00"))
            when = dt.strftime("%d %b")
        except ValueError:
            pass
    if dialect == "marathi":
        return (
            f"{name}, {when} cha ₹{balance} udhaar urle aahe. "
            f"Suvidha zalyavar dyava. Dhanyawad."
        )
    return (
        f"{name}, {when} ka ₹{balance} baaki hai, jab suvidha ho to dijiye. Dhanyavaad."
    )


async def generate_reminder_message(
    name: str,
    balance: int,
    dialect: str = "hindi",
    oldest_credit: str | None = None,
) -> str:
    if MOCK_MODE:
        return template_reminder(name, balance, dialect, oldest_credit)
    # Optional LLM polish — keep template as safe default
    return template_reminder(name, balance, dialect, oldest_credit)


def whatsapp_link(phone: str | None, text: str) -> str | None:
    if not phone:
        return None
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10:
        digits = "91" + digits
    if not digits:
        return None
    return f"https://wa.me/{digits}?text={urllib.parse.quote(text)}"
