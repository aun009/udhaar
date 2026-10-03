"""Runtime configuration from environment."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "out"
DB_PATH = Path(os.environ.get("UDHAAR_DB", str(ROOT / "udhaar.db")))

MOCK_MODE = os.environ.get("UDHAAR_MOCK", "0") == "1"
USE_FINETUNED = os.environ.get("UDHAAR_USE_FINETUNED", "0") == "1"

OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL_BASE = os.environ.get(
    "UDHAAR_MODEL_BASE", "qwen2.5:3b-instruct"
)
OLLAMA_MODEL_FINETUNED = os.environ.get(
    "UDHAAR_MODEL_FINETUNED", "udhaar-parser"
)

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE = os.environ.get("WHISPER_COMPUTE", "int8")

REMINDER_OVERDUE_DAYS = int(os.environ.get("REMINDER_OVERDUE_DAYS", "30"))

PARSER_FEW_SHOT_PATH = ROOT / "eval" / "few_shot_examples.json"
