"""Thin service layer wrapping AnomalyDetector for the API."""
from datetime import datetime
from typing import List
from uuid import uuid4

from src.models.transaction import Transaction
from src.services.anomaly_detector import AnomalyDetector, Anomaly


def _to_response(anomaly: Anomaly) -> dict:
    return {
        "id": str(uuid4()),
        "type": anomaly.type,
        "severity": anomaly.severity.value,
        "description": anomaly.description,
        "recommendation": anomaly.recommendation,
        "transaction_ids": [t.id for t in anomaly.transactions],
        "dispute_deadline": anomaly.dispute_deadline.isoformat() if anomaly.dispute_deadline else None,
    }


def detect_anomalies(transactions: List[Transaction]) -> List[dict]:
    """Run all anomaly detectors and return a flat list of anomaly responses."""
    detector = AnomalyDetector()
    results: List[dict] = []

    # detect_duplicates and detect_subscriptions take a flat transaction list
    for method_name in ("detect_duplicates", "detect_subscriptions"):
        method = getattr(detector, method_name)
        for anomaly in method(transactions):
            results.append(_to_response(anomaly))

    # detect_discrepancies requires three separate source lists
    account_txns = [t for t in transactions if t.source == "account"]
    wallet_txns  = [t for t in transactions if t.source == "wallet"]
    card_txns    = [t for t in transactions if t.source == "card"]
    for anomaly in detector.detect_discrepancies(account_txns, wallet_txns, card_txns):
        results.append(_to_response(anomaly))

    return results
