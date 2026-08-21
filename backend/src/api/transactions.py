from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.deps import get_current_active_user
from src.models.transaction import Transaction
from src.models.user import User

router = APIRouter()


@router.get("")
async def get_transactions(
    source: Optional[str] = Query(None, description="Filter by source (account, wallet, card)"),
    is_flagged: Optional[bool] = Query(None, description="Filter by flagged status"),
    is_subscription: Optional[bool] = Query(None, description="Filter by subscription status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get list of parsed transactions with filters and pagination."""
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    count_query = select(func.count(Transaction.id)).where(Transaction.user_id == current_user.id)

    if source:
        query = query.where(Transaction.source == source)
        count_query = count_query.where(Transaction.source == source)
    if is_flagged is not None:
        query = query.where(Transaction.is_flagged == is_flagged)
        count_query = count_query.where(Transaction.is_flagged == is_flagged)
    if is_subscription is not None:
        query = query.where(Transaction.is_subscription == is_subscription)
        count_query = count_query.where(Transaction.is_subscription == is_subscription)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    transactions = result.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "transactions": [
            {
                "id": t.id,
                "source": t.source,
                "source_id": t.source_id,
                "type": t.type.value if hasattr(t.type, "value") else str(t.type),
                "amount": t.amount,
                "currency": t.currency,
                "description": t.description,
                "merchant_name": t.merchant_name,
                "category": t.category,
                "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
                "is_flagged": t.is_flagged,
                "alert_level": t.alert_level.value if t.alert_level and hasattr(t.alert_level, "value") else None,
                "alert_reason": t.alert_reason,
                "is_subscription": t.is_subscription,
                "subscription_name": t.subscription_name,
                "next_charge_date": t.next_charge_date.isoformat() if t.next_charge_date else None,
                "masked_card": t.masked_card,
            }
            for t in transactions
        ],
    }
