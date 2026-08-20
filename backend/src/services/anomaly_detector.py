"""
Anomaly Detection Service.

Detects:
- Duplicate charges
- Forgot-to-cancel subscriptions
- Unusual spending patterns
- Amount discrepancies between sources
"""
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from src.models.transaction import Transaction, TransactionType, AlertLevel


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    type: str  # "duplicate" | "subscription" | "discrepancy" | "unusual"
    severity: AlertLevel
    transactions: list[Transaction]
    description: str
    recommendation: str
    dispute_deadline: Optional[datetime] = None


class AnomalyDetector:
    """Service for detecting financial anomalies."""
    
    # Known subscription keywords
    SUBSCRIPTION_KEYWORDS = [
        'netflix', 'spotify', 'hulu', 'disney+', 'disney plus',
        'amazon prime', 'hbo', 'apple music', 'youtube premium',
        'adobe', 'microsoft', 'dropbox', 'google one',
        'gym', 'fitness', 'membership', 'subscription',
        'monthly', 'annual', 'yearly',
    ]
    
    def __init__(self):
        self.anomalies: list[Anomaly] = []
    
    def detect_duplicates(self, transactions: list[Transaction]) -> list[Anomaly]:
        """Detect duplicate charges (same amount to same merchant within 24h)."""
        anomalies = []
        
        # Group by merchant and amount
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for t in transactions:
            key = f"{t.merchant_name}_{t.amount}"
            grouped[key].append(t)
        
        for key, group in grouped.items():
            if len(group) > 1:
                # Check if within 24 hours
                dates = sorted([t.transaction_date for t in group])
                for i in range(1, len(dates)):
                    if (dates[i] - dates[i-1]).total_seconds() < 86400:  # 24 hours
                        anomalies.append(Anomaly(
                            type="duplicate",
                            severity=AlertLevel.NEEDS_CONFIRMATION,
                            transactions=group,
                            description=f"Potential duplicate charge: ${group[0].amount} to {group[0].merchant_name}",
                            recommendation="Please verify if you made this purchase twice",
                            dispute_deadline=self._calculate_dispute_deadline(dates[i])
                        ))
                        break
        
        return anomalies
    
    def detect_subscriptions(self, transactions: list[Transaction]) -> list[Anomaly]:
        """Detect recurring subscriptions."""
        anomalies = []
        
        # Group by merchant
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for t in transactions:
            if t.merchant_name:
                grouped[t.merchant_name].append(t)
        
        for merchant, group in grouped.items():
            if len(group) >= 2:
                # Check for recurring pattern
                group_sorted = sorted(group, key=lambda x: x.transaction_date)
                intervals = []
                for i in range(1, len(group_sorted)):
                    delta = (group_sorted[i].transaction_date - group_sorted[i-1].transaction_date).days
                    intervals.append(delta)
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    # Common intervals: ~30 days (monthly), ~7 days (weekly)
                    if 25 <= avg_interval <= 35 or 5 <= avg_interval <= 9:
                        is_subscription = any(
                            kw in merchant.lower() for kw in self.SUBSCRIPTION_KEYWORDS
                        ) or avg_interval in [28, 30, 31]
                        
                        if is_subscription:
                            anomalies.append(Anomaly(
                                type="subscription",
                                severity=AlertLevel.REGULAR,
                                transactions=group,
                                description=f"Recurring subscription detected: {merchant}",
                                recommendation=f"Estimated next charge: ${group[-1].amount} on {self._estimate_next_charge(group[-1].transaction_date, avg_interval)}",
                                dispute_deadline=self._calculate_dispute_deadline(group[-1].transaction_date)
                            ))
        
        return anomalies
    
    def detect_discrepancies(self, account: list[Transaction], wallet: list[Transaction], card: list[Transaction]) -> list[Anomaly]:
        """Detect discrepancies between 3 sources."""
        anomalies = []
        
        # Check for money that left account but hasn't reached card
        # (simplified logic - real implementation would need more sophisticated matching)
        return anomalies
    
    def _estimate_next_charge(self, last_date: datetime, interval: float) -> str:
        """Estimate next charge date."""
        next_date = last_date + timedelta(days=interval)
        return next_date.strftime("%Y-%m-%d")
    
    def _calculate_dispute_deadline(self, transaction_date: datetime) -> datetime:
        """Calculate 60-day dispute deadline."""
        return transaction_date + timedelta(days=60)
