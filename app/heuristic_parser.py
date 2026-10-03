"""Regex/heuristic parser — mock mode and eval baseline (not production quality)."""

from __future__ import annotations

import re

from data.numbers import all_irregular_forms, normalize_spoken_amount
from data.schema import make_label, validate_label

PAYMENT_RE = re.compile(
    r"(chukta|payment|jama|clear|paid|pay kiya|dile\b|diye\b|ghetle|band\b|received)",
    re.I,
)
CREDIT_RE = re.compile(r"(udhaar|credit|likh do|badhao|khata)", re.I)
HONORIFIC_RE = re.compile(
    r"\b([A-Za-z][a-z]+(?:\s+(?:ji|bhai|bhau|tai|kaka|aaji|uncle|didi|ben|saheb|madam|sir))?)\b"
)
CORRECTION_RE = re.compile(
    r"nahi\s+(\d+)\s+nahi\s+(\d+)", re.I
)
DIGITS_RE = re.compile(r"(?:₹|rs\.?|rupaye?|rupees)?\s*(\d[\d,]*)", re.I)


def _extract_amounts(text: str) -> list[int]:
    amounts: list[int] = []
    t = text.lower()
    for m in CORRECTION_RE.finditer(t):
        amounts.append(int(m.group(2)))
    for m in DIGITS_RE.finditer(text):
        val = int(m.group(1).replace(",", ""))
        if val >= 10:
            amounts.append(val)
    for amount, forms in all_irregular_forms().items():
        for f in forms:
            if f in t:
                amounts.append(amount)
    if not amounts:
        one = normalize_spoken_amount(t)
        if one:
            amounts.append(one)
    # Drop obvious quantities ( lone 1-9 before kilo)
    filtered = []
    for a in amounts:
        if re.search(rf"\b{a}\s*kilo\b", t, re.I) and a <= 9:
            continue
        filtered.append(a)
    return filtered


def _guess_customer(text: str) -> str:
    # Prefer token before ko/ka/ne/la
    m = re.search(
        r"([A-Za-z][A-Za-z\s]{1,30}?(?:\s+(?:ji|bhai|bhau|tai|kaka|aaji|uncle|didi|ben|saheb))?)\s+(?:ko|ka|ne|la|se)\b",
        text,
        re.I,
    )
    if m:
        return " ".join(m.group(1).split())
    m2 = HONORIFIC_RE.search(text)
    if m2:
        return m2.group(1)
    return "Unknown"


def parse_transcript_heuristic(transcript: str) -> dict:
    t = transcript.strip()
    has_pay = bool(PAYMENT_RE.search(t))
    has_credit = bool(CREDIT_RE.search(t))
    if has_pay and not has_credit:
        entry_type = "payment_received"
    elif has_credit:
        entry_type = "credit_given"
    else:
        entry_type = "credit_given"

    amounts = _extract_amounts(t)
    amount: int | None = amounts[-1] if amounts else None
    error = None
    if amount is None and CREDIT_RE.search(t):
        error = "missing_amount"

    note = None
    item_m = re.search(
        r"(do kilo chawal|doodh ka packet|tel ki bottle|cheeni half kilo|sabun|biscuit ka dabba|masala|aata ek kilo|chai patti|namak)",
        t,
        re.I,
    )
    if item_m:
        note = item_m.group(1).lower()

    label = make_label(
        customer=_guess_customer(t),
        amount=amount,
        entry_type=entry_type,
        note=note,
        error=error,
    )
    ok, _ = validate_label(label)
    if not ok:
        label["error"] = label.get("error") or "invalid_label"
    return label
