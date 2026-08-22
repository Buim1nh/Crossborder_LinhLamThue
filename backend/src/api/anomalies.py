"""Anomaly detection endpoints."""
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_active_user
from src.models.transaction import Transaction
from src.models.user import User
from src.services.anomaly_service import detect_anomalies

router = APIRouter()


class AnomalyResponse(BaseModel):
    id: str
    type: str
    severity: str
    description: str
    recommendation: str
    transaction_ids: List[int]
    dispute_deadline: str | None = None

    model_config = {"from_attributes": False}


@router.get("", response_model=List[AnomalyResponse])
async def get_anomalies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Detect and return all anomalies for the current user."""
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
    )
    transactions = result.scalars().all()
    return detect_anomalies(list(transactions))
