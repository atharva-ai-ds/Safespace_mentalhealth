"""FastAPI entry point for SafeSpace-RAG."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.ai_agent import ask_agent
from backend.config import LOG_DIR

logging.basicConfig(level=logging.INFO, handlers=[RotatingFileHandler(LOG_DIR / "safespace.log", maxBytes=1_000_000, backupCount=3), logging.StreamHandler()])
logger = logging.getLogger(__name__)
app = FastAPI(title="SafeSpace-RAG API", version="1.0.0")


class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=100)


class AskResponse(BaseModel):
    response: str
    sources: list[dict[str, object]]
    tool_called: str
    conversation_id: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(query: AskRequest) -> AskResponse:
    conversation_id = query.conversation_id or str(uuid4())
    logger.info("Question received for conversation %s", conversation_id)
    try:
        result = ask_agent(query.message.strip(), conversation_id)
        logger.info("Answer generated; tool=%s sources=%s", result["tool_called"], result["sources"])
        return AskResponse(**result, conversation_id=conversation_id)
    except Exception as exc:
        logger.exception("Unhandled API error")
        raise HTTPException(status_code=503, detail="SafeSpace is temporarily unavailable. Please try again.") from exc
