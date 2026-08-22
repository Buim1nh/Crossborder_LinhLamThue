"""Pre-computed financial insights endpoint."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.deps import get_db, get_current_active_user
from src.models.transaction import Transaction
from src.models.user import User
from src.services.insights_service import compute_insights

router = APIRouter()


class InsightsResponse(BaseModel):
    period: dict
    summary: dict
    top_subscriptions: list
    active_anomalies: list
    by_source: dict
    computed_at: str

    model_config = {"from_attributes": False}


@router.get("", response_model=InsightsResponse)
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return pre-computed financial insights for the current user."""
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
    )
    transactions = list(result.scalars().all())
    return compute_insights(transactions)
