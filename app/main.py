"""Udhaar FastAPI application."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import asr, db
from app.config import DB_PATH, MOCK_MODE, REMINDER_OVERDUE_DAYS
from app.db import init_db
from app.parser_service import parse_transcript
from app.reminders import generate_reminder_message, whatsapp_link
from data.schema import validate_label

STATIC = Path(__file__).parent / "static"

app = FastAPI(title="Udhaar", version="1.0.0")


@app.on_event("startup")
def _startup() -> None:
    init_db(DB_PATH)


class ParseTextBody(BaseModel):
    transcript: str


class ConfirmBody(BaseModel):
    customer: str
    amount: int = Field(..., gt=0)
    type: str
    note: str | None = None
    raw_transcript: str | None = None


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mock_mode": MOCK_MODE,
        "whisper_installed": asr.transcribe_available(),
        "db": str(DB_PATH),
    }


@app.post("/entry/parse")
async def entry_parse_text(body: ParseTextBody) -> dict[str, Any]:
    return await parse_transcript(body.transcript)


@app.post("/entry/parse-audio")
async def entry_parse_audio(file: UploadFile = File(...)) -> dict[str, Any]:
    data = await file.read()
    if MOCK_MODE:
        raise HTTPException(
            400,
            "Audio parse disabled in mock mode; use text input or disable UDHAAR_MOCK.",
        )
    if not asr.transcribe_available():
        raise HTTPException(503, "faster-whisper not installed")
    try:
        transcript = asr.transcribe_audio_bytes(data)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"transcription failed: {exc}") from exc
    if not transcript:
        raise HTTPException(400, "empty transcription")
    result = await parse_transcript(transcript)
    result["transcript"] = transcript
    return result


@app.post("/entry/confirm")
async def entry_confirm(body: ConfirmBody) -> dict[str, Any]:
    if body.type not in ("credit_given", "payment_received"):
        raise HTTPException(400, "invalid type")
    label = {
        "customer": body.customer.strip(),
        "amount": body.amount,
        "type": body.type,
        "note": body.note,
        "error": None,
    }
    ok, msg = validate_label(label)
    if not ok:
        raise HTTPException(400, msg or "invalid label")
    with db.connect() as conn:
        cid = db.upsert_customer(conn, label["customer"])
        eid = db.insert_entry(
            conn,
            customer_id=cid,
            amount=label["amount"],
            entry_type=label["type"],
            note=label["note"],
            raw_transcript=body.raw_transcript,
        )
        balance = db.customer_balance(conn, cid)
    return {"entry_id": eid, "customer_id": cid, "balance": balance}


@app.get("/customers")
async def get_customers() -> list[dict[str, Any]]:
    with db.connect() as conn:
        return db.list_customers(conn)


@app.get("/reminders")
async def get_reminders() -> list[dict[str, Any]]:
    items = []
    with db.connect() as conn:
        for row in db.overdue_customers(conn, REMINDER_OVERDUE_DAYS):
            text = await generate_reminder_message(
                row["name"],
                row["balance"],
                row.get("dialect") or "hindi",
                row.get("oldest_credit"),
            )
            items.append(
                {
                    **row,
                    "message": text,
                    "whatsapp_url": whatsapp_link(row.get("phone"), text),
                }
            )
    return items


@app.get("/summary")
async def get_summary() -> dict[str, Any]:
    with db.connect() as conn:
        return db.monthly_summary(conn)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
