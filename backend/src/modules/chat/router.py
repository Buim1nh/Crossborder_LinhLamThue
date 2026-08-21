"""
MODULE 6 - HTTP surface.

The module ships its own APIRouter so integrating it into the app is a
one-liner:

    from src.modules.chat import chat_router
    app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.chat.config import DISCLAIMER, get_chat_settings
from src.modules.chat.safety_filter import check_message
from src.modules.chat.schemas import ChatRequest, ChatResponse, SafetyVerdict
from src.modules.chat.service import handle_chat

router = APIRouter()


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Ask the financial assistant a question.

    Runs the full Module 6 pipeline: safety filter → context → prompt →
    LLM → disclaimer. Unsafe requests return HTTP 200 with `blocked=true`
    and a polite decline, since a refusal is a valid conversational turn
    rather than a client error.
    """
    return await handle_chat(payload.message, db, user_id=payload.user_id)


@router.post("/check", response_model=SafetyVerdict)
async def check_safety(payload: ChatRequest) -> SafetyVerdict:
    """
    Dry-run the safety filter without calling the LLM.

    Useful for the frontend to warn the user before they submit, and for
    debugging which pattern matched.
    """
    return check_message(payload.message)


@router.get("/info")
async def chat_info() -> dict:
    """Expose the active provider and the mandatory disclaimer text."""
    settings = get_chat_settings()
    return {
        "provider": settings.provider,
        "model": settings.model,
        "configured": bool(settings.api_key),
        "disclaimer": DISCLAIMER,
    }
