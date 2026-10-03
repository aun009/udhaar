"""Speech-to-text via faster-whisper (optional dependency)."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

from app.config import WHISPER_COMPUTE, WHISPER_DEVICE, WHISPER_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE,
        )
    return _model


def transcribe_audio_bytes(data: bytes, *, language: str | None = None) -> str:
    model = _get_model()
    suffix = ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        segments, _info = model.transcribe(
            path,
            language=language,
            vad_filter=True,
        )
        return " ".join(s.text.strip() for s in segments).strip()
    finally:
        Path(path).unlink(missing_ok=True)


def transcribe_available() -> bool:
    try:
        import faster_whisper  # noqa: F401

        return True
    except ImportError:
        return False
