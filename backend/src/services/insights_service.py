"""Pre-computed financial insights service.

Called on every /api/insights request (no caching in v1 — sub-100ms for
2,500 rows, so the overhead of a cache is not worth the staleness risk).
"""
from datetime import datetime
from typing import Any

from src.models.transaction import Transaction

# Conversion rates
VND_RATE = 1.0
USD_RATE = 25_400.0
EUR_RATE = 27_500.0


def _rate(currency: str) -> float:
    c = currency.upper()
    if c == "USD":
        return USD_RATE
    if c == "EUR":
        return EUR_RATE
    return VND_RATE


def compute_insights(transactions: list[Transaction]) -> dict[str, Any]:
    """Compute income/expense/subscription/anomaly summary from a list of Transaction rows."""
    total_income_vnd = 0.0
    total_expense_vnd = 0.0
    subscription_burn_vnd = 0.0
    by_source: dict[str, dict[str, float]] = {
        "account": {"income": 0.0, "expense": 0.0},
        "wallet": {"income": 0.0, "expense": 0.0},
        "card": {"income": 0.0, "expense": 0.0},
    }

    all_dates = [t.transaction_date for t in transactions if t.transaction_date]
    period_from = min(all_dates) if all_dates else None
    period_to = max(all_dates) if all_dates else None

    for t in transactions:
        r = _rate(t.currency or "VND")
        amount_vnd = t.amount * r

        if t.amount > 0:
            total_income_vnd += amount_vnd
            if t.source in by_source:
                by_source[t.source]["income"] += amount_vnd
        else:
            total_expense_vnd += abs(amount_vnd)
            if t.source in by_source:
                by_source[t.source]["expense"] += abs(amount_vnd)

        if t.is_subscription:
            subscription_burn_vnd += abs(amount_vnd)

    # Top subscriptions (group by merchant_name, compute monthly avg)
    sub_by_merchant: dict[str, list[Transaction]] = {}
    for t in transactions:
        if t.is_subscription and t.merchant_name:
            sub_by_merchant.setdefault(t.merchant_name, []).append(t)

    top_subscriptions = []
    for merchant, tx_list in sub_by_merchant.items():
        amounts = [abs(tx.amount * _rate(tx.currency or "VND")) for tx in tx_list]
        monthly_avg = sum(amounts) / max(len(tx_list), 1)
        top_subscriptions.append(
            {
                "merchant": merchant,
                "monthly_avg_vnd": round(monthly_avg, 2),
                "occurrences": len(tx_list),
            }
        )
    top_subscriptions.sort(key=lambda x: x["monthly_avg_vnd"], reverse=True)
    top_subscriptions = top_subscriptions[:10]

    # Active anomalies — import here to avoid circular dependency with Task 2
    try:
        from src.services.anomaly_service import detect_anomalies

        active_anomalies = detect_anomalies(transactions)[:20]
    except ImportError:
        active_anomalies = []

    net_vnd = total_income_vnd - total_expense_vnd

    return {
        "period": {
            "from": period_from.isoformat() if period_from else None,
            "to": period_to.isoformat() if period_to else None,
        },
        "summary": {
            "total_income_vnd": round(total_income_vnd, 2),
            "total_expense_vnd": round(total_expense_vnd, 2),
            "net_vnd": round(net_vnd, 2),
            "subscription_burn_vnd": round(subscription_burn_vnd, 2),
            "transaction_count": len(transactions),
        },
        "top_subscriptions": top_subscriptions,
        "active_anomalies": active_anomalies,
        "by_source": {
            k: {"income_vnd": round(v["income"], 2), "expense_vnd": round(v["expense"], 2)}
            for k, v in by_source.items()
        },
        "computed_at": datetime.utcnow().isoformat(),
    }
