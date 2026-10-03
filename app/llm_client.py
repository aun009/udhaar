"""Ollama chat client for local open-weight models."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import OLLAMA_BASE, OLLAMA_MODEL_BASE, OLLAMA_MODEL_FINETUNED, USE_FINETUNED
from app.parser_prompt import build_messages, load_few_shot, SYSTEM_PROMPT
from app.config import PARSER_FEW_SHOT_PATH


def active_model() -> str:
    return OLLAMA_MODEL_FINETUNED if USE_FINETUNED else OLLAMA_MODEL_BASE


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            return None
    return None


async def ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            return r.status_code == 200
    except (httpx.HTTPError, OSError):
        return False


async def parse_with_llm(transcript: str) -> tuple[dict[str, Any] | None, str | None]:
    few_shot = load_few_shot(PARSER_FEW_SHOT_PATH)
    messages = build_messages(transcript, few_shot)
    payload = {
        "model": active_model(),
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_BASE}/api/chat", json=payload)
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
    parsed = _extract_json(content)
    if parsed is None:
        return None, "invalid_json_from_model"
    return parsed, None


def parse_with_llm_sync(transcript: str) -> tuple[dict[str, Any] | None, str | None]:
    import asyncio

    return asyncio.run(parse_with_llm(transcript))


def build_training_prompt_user(transcript: str) -> str:
    return transcript


def training_system_prompt() -> str:
    return SYSTEM_PROMPT
