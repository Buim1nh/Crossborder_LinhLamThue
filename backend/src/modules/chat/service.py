"""
MODULE 6 - Pipeline orchestrator.

Wires every step together in the order defined by the module flowchart:

    user message
        -> SAFETY FILTER      (blocked? -> polite decline, stop)
        -> BUILD CONTEXT      (from database)
        -> BUILD PROMPT       (system + user prompt)
        -> CALL LLM
        -> RECEIVE RESPONSE
        -> ADD DISCLAIMER     (appended if not already present)
        -> RETURN CHAT RESPONSE

The disclaimer is enforced here, on EVERY exit path — including blocked
requests and error fallbacks — so no response can escape without it.
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.chat.config import DISCLAIMER, DISCLAIMER_FINGERPRINT
from src.modules.chat.context_builder import build_user_context
from src.modules.chat.llm_client import LLMError, get_provider
from src.modules.chat.prompt_builder import build_prompt
from src.modules.chat.safety_filter import check_message
from src.modules.chat.schemas import ChatResponse, UserContext

logger = logging.getLogger(__name__)


ERROR_FALLBACK = (
    "Xin lỗi, hiện mình chưa thể xử lý câu hỏi này do sự cố kết nối tới trợ lý "
    "AI. Bạn vui lòng thử lại sau ít phút nhé."
)


def ensure_disclaimer(text: str) -> str:
    """
    Guarantee the mandatory disclaimer is present.

    Appends it only when missing, so responses where the model already
    followed instructions don't end up with a duplicate.
    """
    if DISCLAIMER_FINGERPRINT in text:
        return text.strip()
    return f"{text.strip()}\n\n{DISCLAIMER}"


def _context_digest(context: UserContext) -> dict:
    """Small, non-sensitive summary of what informed the answer (for the UI)."""
    return {
        "transaction_count": context.financial_summary.transaction_count,
        "recent_transactions": len(context.recent_transactions),
        "anomalies": len(context.anomalies),
        "subscriptions": len(context.subscriptions),
        "reconciliation": context.reconciliation_status.model_dump(),
    }


async def handle_chat(
    message: str,
    db: AsyncSession,
    user_id: Optional[int] = None,
) -> ChatResponse:
    """Run a user message through the full Module 6 pipeline."""

    # --- STEP 1: SAFETY FILTER -------------------------------------------
    # Runs first: blocked messages never reach the database or the LLM.
    verdict = check_message(message)
    if not verdict.allowed:
        logger.info("Chat message blocked (reason=%s)", verdict.reason)
        return ChatResponse(
            response=ensure_disclaimer(verdict.decline_message or ""),
            blocked=True,
            block_reason=verdict.reason,
            disclaimer=DISCLAIMER,
        )

    # --- STEP 2: BUILD CONTEXT -------------------------------------------
    context = await build_user_context(db, user_id=user_id)

    # --- STEP 3: BUILD PROMPT --------------------------------------------
    system_prompt, user_prompt = build_prompt(message, context)

    # --- STEP 4 & 5: CALL LLM / RECEIVE RESPONSE -------------------------
    provider = get_provider()
    try:
        result = await provider.complete(system_prompt, user_prompt)
        content, model = result.content, result.model
    except LLMError as exc:
        logger.error("LLM configuration error: %s", exc)
        content, model = ERROR_FALLBACK, None
    except Exception as exc:  # noqa: BLE001 - never leak provider errors to users
        logger.exception("LLM call failed: %s", exc)
        content, model = ERROR_FALLBACK, None

    # --- STEP 6 & 7: ADD DISCLAIMER / RETURN -----------------------------
    return ChatResponse(
        response=ensure_disclaimer(content),
        blocked=False,
        disclaimer=DISCLAIMER,
        model=model,
        context_used=_context_digest(context),
    )
