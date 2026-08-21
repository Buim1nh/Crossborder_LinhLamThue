"""
MODULE 7 - Pydantic schemas & internal dataclasses for the ML inference pipeline.

These types are the module's public contract. Predictors and the service layer
speak only in these shapes, which is what lets the underlying model be swapped
(heuristic -> sklearn -> a remote endpoint) without touching callers.
"""
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from src.modules.ml.config import UNKNOWN_CATEGORY

# How a prediction was produced. Surfaced in every response so the caller can
# tell a real model apart from the zero-dependency fallback.
InferenceBackend = Literal["model", "heuristic", "disabled"]

# Column names matching `FeatureVector.to_numeric()`, in the same order.
# Module-level rather than a class attribute: an annotated attribute inside a
# Pydantic BaseModel would be interpreted as a *field*, not a constant.
NUMERIC_COLUMNS: tuple[str, ...] = (
    "abs_amount", "log_amount", "is_round_amount", "is_credit",
    "hour", "day_of_week", "day_of_month", "is_weekend", "is_odd_hour",
    "text_length", "token_count", "has_merchant",
)



# ============================================================================
# Inference input
# ============================================================================

class TransactionInput(BaseModel):
    """
    A single transaction to run inference on.

    Deliberately looser than `models.Transaction`: inference must work on rows
    that have not been persisted yet (e.g. straight out of a CSV/PDF parser).
    """
    amount: float
    description: str = ""
    merchant_name: Optional[str] = None
    currency: str = "USD"
    transaction_date: Optional[datetime] = None
    type: Optional[str] = None
    source_id: Optional[str] = None

    @field_validator("description", "merchant_name", mode="before")
    @classmethod
    def _blank_to_empty(cls, v: Any) -> Any:
        """Normalize None/whitespace so downstream text handling is total."""
        if v is None:
            return v
        return str(v).strip()


class PredictRequest(BaseModel):
    """Batch inference request."""
    transactions: list[TransactionInput] = Field(..., min_length=1)

    # Optional prior history used to calibrate the anomaly scorer. When empty,
    # `transactions` itself is used as its own reference distribution.
    history: list[TransactionInput] = Field(default_factory=list)


# ============================================================================
# Features
# ============================================================================

class FeatureVector(BaseModel):
    """
    Engineered features for one transaction.

    Kept as an explicit, named model rather than a bare list so that feature
    drift between training and serving is obvious in code review.
    """
    amount: float
    abs_amount: float
    log_amount: float
    is_round_amount: bool
    is_credit: bool

    hour: int = 0
    day_of_week: int = 0
    day_of_month: int = 1
    is_weekend: bool = False
    is_odd_hour: bool = False

    text: str = ""
    text_length: int = 0
    token_count: int = 0
    has_merchant: bool = False

    def to_numeric(self) -> list[float]:
        """Dense numeric view, in a fixed order, for array-based estimators."""
        return [
            self.abs_amount,
            self.log_amount,
            float(self.is_round_amount),
            float(self.is_credit),
            float(self.hour),
            float(self.day_of_week),
            float(self.day_of_month),
            float(self.is_weekend),
            float(self.is_odd_hour),
            float(self.text_length),
            float(self.token_count),
            float(self.has_merchant),
        ]



# ============================================================================
# Inference output
# ============================================================================

class CategoryPrediction(BaseModel):
    """Predicted spending category for one transaction."""
    category: str = UNKNOWN_CATEGORY
    confidence: float = 0.0
    backend: InferenceBackend = "heuristic"
    # Runner-up categories, highest first. Useful for "did you mean" UX.
    alternatives: list[tuple[str, float]] = Field(default_factory=list)


class AnomalySignal(BaseModel):
    """One contributing reason behind an anomaly score."""
    name: str
    weight: float
    value: float
    explanation: str


class AnomalyPrediction(BaseModel):
    """
    Anomaly assessment for one transaction.

    `score` is always 0..1. `is_anomaly` applies the configured threshold so
    every caller draws the line in the same place.
    """
    score: float = 0.0
    is_anomaly: bool = False
    backend: InferenceBackend = "heuristic"
    insufficient_data: bool = False
    signals: list[AnomalySignal] = Field(default_factory=list)

    @property
    def top_signal(self) -> Optional[AnomalySignal]:
        """Strongest contributor, for a one-line UI summary."""
        contributing = [s for s in self.signals if s.value > 0]
        if not contributing:
            return None
        return max(contributing, key=lambda s: s.weight * s.value)


class TransactionPrediction(BaseModel):
    """Combined per-transaction inference result."""
    source_id: Optional[str] = None
    description: str = ""
    amount: float = 0.0
    category: CategoryPrediction = Field(default_factory=CategoryPrediction)
    anomaly: AnomalyPrediction = Field(default_factory=AnomalyPrediction)


class PredictResponse(BaseModel):
    """Batch inference response."""
    predictions: list[TransactionPrediction] = Field(default_factory=list)
    count: int = 0
    anomaly_count: int = 0
    backend: dict[str, InferenceBackend] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelInfo(BaseModel):
    """Describes one loaded (or absent) model artifact."""
    name: str
    loaded: bool
    backend: InferenceBackend
    artifact_path: Optional[str] = None
    error: Optional[str] = None
