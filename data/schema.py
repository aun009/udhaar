"""Label JSON schema for parser training and eval."""

from __future__ import annotations

import json
from typing import Any, Literal

EntryType = Literal["credit_given", "payment_received"]


def make_label(
    *,
    customer: str,
    amount: int | None,
    entry_type: EntryType,
    note: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "customer": customer,
        "amount": amount,
        "type": entry_type,
        "note": note,
        "error": error,
    }


def validate_label(obj: dict[str, Any]) -> tuple[bool, str | None]:
    required = {"customer", "amount", "type", "note", "error"}
    if set(obj.keys()) != required:
        return False, f"keys must be exactly {required}"
    if not isinstance(obj["customer"], str):
        return False, "customer must be str"
    if obj["amount"] is not None and not isinstance(obj["amount"], int):
        return False, "amount must be int or null"
    if obj["type"] not in ("credit_given", "payment_received"):
        return False, "invalid type"
    if obj["note"] is not None and not isinstance(obj["note"], str):
        return False, "note must be str or null"
    if obj["error"] is not None and not isinstance(obj["error"], str):
        return False, "error must be str or null"
    return True, None


def label_to_json(label: dict[str, Any]) -> str:
    return json.dumps(label, ensure_ascii=False, sort_keys=True)
