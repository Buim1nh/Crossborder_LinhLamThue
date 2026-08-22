"""AI Financial Chat endpoint — tool-using agent (pre-computed insights as context)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_active_user
from src.models.transaction import Transaction
from src.models.user import User
from src.services.llm_service import get_llm_provider

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []


class ChatResponse(BaseModel):
    reply: str
    model: str


SYSTEM_PROMPT = """Bạn là Trợ lý Tài chính Wealify, trợ giúp bằng tiếng Việt.
Nếu không có dữ liệu, trả lời rằng bạn chưa có đủ thông tin.
Trả lời ngắn gọn, dễ hiểu, dựa trên dữ liệu được cung cấp."""


def _build_user_prompt(message: str, insights: dict) -> str:
    summary = insights.get("summary", {})
    subs = insights.get("top_subscriptions", [])
    anoms = insights.get("active_anomalies", [])

    parts = [
        f"Tóm tắt thu chi:",
        f"  Tổng thu: {summary.get('total_income_vnd', 0):,.0f}₫",
        f"  Tổng chi: {summary.get('total_expense_vnd', 0):,.0f}₫",
        f"  Tiết kiệm ròng: {summary.get('net_vnd', 0):,.0f}₫",
        f"  Chi tiêu định kỳ: {summary.get('subscription_burn_vnd', 0):,.0f}₫",
        f"  Số giao dịch: {summary.get('transaction_count', 0)}",
    ]

    if subs:
        parts.append("\nGói dịch vụ định kỳ:")
        for s in subs[:5]:
            parts.append(f"  - {s['merchant']}: ~{s['monthly_avg_vnd']:,.0f}₫/tháng ({s['occurrences']} lần)")

    if anoms:
        parts.append("\nCảnh báo:")
        for a in anoms[:3]:
            parts.append(f"  - [{a['type']}] {a['description']}")

    if not subs and not anoms:
        parts.append("\n(Không có gói định kỳ hay cảnh báo nào được phát hiện.)")

    parts.append(f"\nCâu hỏi người dùng: {message}")
    return "\n".join(parts)


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 1. Load user's transactions
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
    )
    transactions = list(result.scalars().all())

    # 2. Compute insights (inline import to avoid circular deps if Task 3 not done yet)
    try:
        from src.services.insights_service import compute_insights
        insights = compute_insights(transactions)
    except ImportError:
        insights = {
            "summary": {"total_income_vnd": 0, "total_expense_vnd": 0,
                        "net_vnd": 0, "subscription_burn_vnd": 0, "transaction_count": 0},
            "top_subscriptions": [],
            "active_anomalies": [],
        }

    # 3. Build LLM prompt
    user_prompt = _build_user_prompt(req.message, insights)

    # 4. Call LLM
    llm = get_llm_provider()
    try:
        resp = await llm.chat(user_prompt, system_prompt=SYSTEM_PROMPT)
        reply = resp.content
        model = resp.model
    except Exception:
        reply = "Xin lỗi, hệ thống đang bận. Bạn thử lại sau."
        model = "error"

    return ChatResponse(reply=reply, model=model)
