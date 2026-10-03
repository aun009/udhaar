"""Unified parse pipeline with mock/heuristic/LLM backends."""

from __future__ import annotations

from typing import Any

from app.config import MOCK_MODE
from app.heuristic_parser import parse_transcript_heuristic
from app.llm_client import ollama_available, parse_with_llm
from data.schema import validate_label


async def parse_transcript(transcript: str) -> dict[str, Any]:
    transcript = transcript.strip()
    if not transcript:
        return {
            "customer": "",
            "amount": None,
            "type": "credit_given",
            "note": None,
            "error": "empty_transcript",
        }

    if MOCK_MODE:
        label = parse_transcript_heuristic(transcript)
        return {"label": label, "backend": "heuristic", "transcript": transcript}

    if await ollama_available():
        label, err = await parse_with_llm(transcript)
        if label is not None:
            ok, msg = validate_label(label)
            if ok:
                return {"label": label, "backend": "ollama", "transcript": transcript}
            label = label or {}
            label["error"] = label.get("error") or msg
            return {"label": label, "backend": "ollama", "transcript": transcript}
        # fall through
        fallback = parse_transcript_heuristic(transcript)
        fallback["error"] = fallback.get("error") or err
        return {"label": fallback, "backend": "heuristic_fallback", "transcript": transcript}

    label = parse_transcript_heuristic(transcript)
    label["error"] = label.get("error") or "ollama_unavailable"
    return {"label": label, "backend": "heuristic", "transcript": transcript}
