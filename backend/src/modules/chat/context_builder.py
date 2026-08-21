"""
MODULE 6 - Step 2: BUILD CONTEXT.

Pulls the user's financial picture out of the database and packs it into a
compact `UserContext`. Only this file knows about SQLAlchemy models; the
prompt builder and LLM client work purely with schemas, which keeps the
module easy to port to a different persistence layer.

What we gather (per the module spec):
  - user_id
  - recent_transactions (last N)
  - anomalies (flagged transactions)
  - subscriptions (active recurring charges)
  - reconciliation_status (email-match tallies)
  - financial_summary (spending / income / fees / net)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transaction import Transaction, TransactionType
from src.modules.chat.config import (
    ANOMALIES_LIMIT,
    RECENT_TRANSACTIONS_LIMIT,
    SUBSCRIPTIONS_LIMIT,
)
from src.modules.chat.schemas import (
    AnomalyBrief,
    FinancialSummary,
    ReconciliationStatus,
    SubscriptionBrief,
    TransactionBrief,
    UserContext,
)


def _fmt_date(value: Optional[datetime]) -> Optional[str]:
    """Render a datetime as YYYY-MM-DD, tolerating None."""
    return value.strftime("%Y-%m-%d") if value else None


def _scope_to_user(query, user_id: Optional[int]):
    """
    Restrict a query to a single user when the schema supports it.

    The current `Transaction` model has no `user_id` column (single-user
    deployment). We check dynamically so that adding the column later
    automatically enables per-user isolation with no change here.
    """
    if user_id is None:
        return query
    user_column = getattr(Transaction, "user_id", None)
    if user_column is None:
        return query
    return query.where(user_column == user_id)


async def build_user_context(
    db: AsyncSession,
    user_id: Optional[int] = None,
) -> UserContext:
    """
    Assemble the full financial context for a user.

    A single query fetches all transactions, then everything is derived
    in memory. Statement volumes are small (hundreds to low thousands of
    rows), so this avoids five separate round-trips.
    """
    query = _scope_to_user(
        select(Transaction).order_by(Transaction.transaction_date.desc()),
        user_id,
    )
    result = await db.execute(query)
    transactions: list[Transaction] = list(result.scalars().all())

    return UserContext(
        user_id=user_id,
        recent_transactions=_recent(transactions),
        anomalies=_anomalies(transactions),
        subscriptions=_subscriptions(transactions),
        reconciliation_status=_reconciliation(transactions),
        financial_summary=_summary(transactions),
    )


def _recent(transactions: list[Transaction]) -> list[TransactionBrief]:
    """Most recent N transactions (already sorted desc by the query)."""
    return [
        TransactionBrief(
            date=_fmt_date(t.transaction_date) or "unknown",
            amount=t.amount,
            currency=t.currency or "USD",
            description=t.description or "",
            merchant=t.merchant_name,
            category=t.category,
            type=t.type.value if t.type else None,
        )
        for t in transactions[:RECENT_TRANSACTIONS_LIMIT]
    ]


def _anomalies(transactions: list[Transaction]) -> list[AnomalyBrief]:
    """Flagged transactions, surfaced so the LLM can explain them."""
    flagged = [t for t in transactions if t.is_flagged]
    briefs: list[AnomalyBrief] = []

    for t in flagged[:ANOMALIES_LIMIT]:
        label = t.merchant_name or t.description or "giao dịch không rõ"
        briefs.append(
            AnomalyBrief(
                description=f"{label} - {t.amount} {t.currency or 'USD'}",
                level=t.alert_level.value if t.alert_level else None,
                reason=t.alert_reason,
                date=_fmt_date(t.transaction_date),
                dispute_deadline=_fmt_date(t.dispute_deadline),
            )
        )
    return briefs


def _subscriptions(transactions: list[Transaction]) -> list[SubscriptionBrief]:
    """
    Active recurring charges, de-duplicated by subscription name.

    Transactions arrive newest-first, so the first occurrence of each name
    is the latest charge — exactly what we want to report.
    """
    seen: dict[str, SubscriptionBrief] = {}

    for t in transactions:
        if not t.is_subscription:
            continue
        name = t.subscription_name or t.merchant_name or t.description or "unknown"
        if name in seen:
            continue
        seen[name] = SubscriptionBrief(
            name=name,
            amount=abs(t.amount),
            currency=t.currency or "USD",
            last_charge=_fmt_date(t.transaction_date),
            next_charge=_fmt_date(t.next_charge_date),
        )
        if len(seen) >= SUBSCRIPTIONS_LIMIT:
            break

    return list(seen.values())


def _reconciliation(transactions: list[Transaction]) -> ReconciliationStatus:
    """Tally how transactions line up against email receipts."""
    status = ReconciliationStatus()

    for t in transactions:
        match = t.email_match_status
        if match == "matched":
            status.matched += 1
        elif match == "no_email_found":
            status.no_email_found += 1
        elif match == "suspicious":
            status.suspicious += 1
        else:
            status.unchecked += 1

    return status


def _summary(transactions: list[Transaction]) -> FinancialSummary:
    """Aggregate money in/out plus a per-category spending breakdown."""
    if not transactions:
        return FinancialSummary()

    spending = sum(
        abs(t.amount) for t in transactions
        if t.type in (TransactionType.CARD_SPEND, TransactionType.PAYOUT)
    )
    income = sum(
        t.amount for t in transactions
        if t.type in (TransactionType.PAYIN, TransactionType.REFUND)
    )
    fees = sum(abs(t.amount) for t in transactions if t.type == TransactionType.FEE)

    by_category: dict[str, float] = {}
    for t in transactions:
        if t.type not in (TransactionType.CARD_SPEND, TransactionType.PAYOUT):
            continue
        key = t.category or "Uncategorized"
        by_category[key] = round(by_category.get(key, 0.0) + abs(t.amount), 2)

    dates = [t.transaction_date for t in transactions if t.transaction_date]

    return FinancialSummary(
        total_spending=round(spending, 2),
        total_income=round(income, 2),
        total_fees=round(fees, 2),
        net_flow=round(income - spending - fees, 2),
        currency=transactions[0].currency or "USD",
        transaction_count=len(transactions),
        period_start=_fmt_date(min(dates)) if dates else None,
        period_end=_fmt_date(max(dates)) if dates else None,
        by_category=by_category,
    )
