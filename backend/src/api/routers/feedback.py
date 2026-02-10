"""Feedback API router for collecting user ratings on RAG responses."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["feedback"])

FEEDBACK_DIR = Path("data/feedback")
FEEDBACK_FILE = FEEDBACK_DIR / "feedback_log.jsonl"


class FeedbackRequest(BaseModel):
    """User feedback on a chat response."""
    message_index: int
    rating: str  # "up" or "down"
    reason: Optional[str] = None
    query: Optional[str] = None
    answer: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback on a chat response.

    Logs feedback to a JSONL file for future evaluation dataset building.
    """
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_index": feedback.message_index,
        "rating": feedback.rating,
        "reason": feedback.reason,
        "query": feedback.query,
        "answer": feedback.answer[:500] if feedback.answer else None,
    }

    def _write_feedback():
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    try:
        import asyncio
        await asyncio.to_thread(_write_feedback)
        logger.info(f"Feedback logged: {feedback.rating} (reason: {feedback.reason})")
        return {"status": "ok", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Failed to log feedback: {e}")
        return {"status": "error", "message": str(e)}
