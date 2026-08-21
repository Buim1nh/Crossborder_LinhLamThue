"""
MODULE 6: LLM Chat Interface.

A self-contained chat module. Everything it needs — config, safety rules,
prompts, provider clients, HTTP routes and tests — lives in this folder.

Pipeline:
    message → safety filter → context → prompt → LLM → disclaimer → response

Typical integration:

    from src.modules.chat import chat_router
    app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
"""
from src.modules.chat.config import DISCLAIMER, get_chat_settings
from src.modules.chat.router import router as chat_router
from src.modules.chat.safety_filter import check_message, is_blocked
from src.modules.chat.schemas import ChatRequest, ChatResponse, UserContext
from src.modules.chat.service import ensure_disclaimer, handle_chat

__all__ = [
    "DISCLAIMER",
    "ChatRequest",
    "ChatResponse",
    "UserContext",
    "chat_router",
    "check_message",
    "ensure_disclaimer",
    "get_chat_settings",
    "handle_chat",
    "is_blocked",
]
