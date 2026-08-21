"""
MODULE 7 - Step 4: ORCHESTRATION.

The single entry point callers should use. Wires preprocessing, the categorizer
and the anomaly scorer into one batch call.

Responsibilities kept here (and nowhere else):
  - enforcing the batch-size guardrail
  - choosing the reference history for anomaly scoring
  - honouring the ML_ENABLED master switch
  - guaranteeing one output row per input row, in order
"""
import logging
from typing import Optional

from src.modules.ml.config import UNKNOWN_CATEGORY, MLSettings, get_ml_settings
from src.modules.ml.predictors import AnomalyScorer, CategoryPredictor
from src.modules.ml.schemas import (
    AnomalyPrediction,
    CategoryPrediction,
    ModelInfo,
    PredictRequest,
    PredictResponse,
    TransactionInput,
    TransactionPrediction,
)

logger = logging.getLogger(__name__)


class MLService:
    """Facade over the inference pipeline."""

    def __init__(self, settings: Optional[MLSettings] = None):
        self.settings = settings or get_ml_settings()
        # Constructing these triggers a cached artifact load, so building the
        # service is cheap after the first time in the process.
        self.categorizer = CategoryPredictor(self.settings)
        self.anomaly_scorer = AnomalyScorer(self.settings)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, request: PredictRequest) -> PredictResponse:
        """
        Run categorization + anomaly scoring over a batch.

        Output is always the same length as `request.transactions` and in the
        same order, so callers can zip results back onto their own rows.
        """
        transactions = request.transactions[: self.settings.ML_MAX_BATCH_SIZE]
        if len(request.transactions) > self.settings.ML_MAX_BATCH_SIZE:
            logger.warning(
                "Batch truncated from %d to %d rows (ML_MAX_BATCH_SIZE)",
                len(request.transactions),
                self.settings.ML_MAX_BATCH_SIZE,
            )

        if not self.settings.ML_ENABLED:
            return self._disabled_response(transactions)

        # With no explicit history, the batch is its own reference distribution.
        # That is the common case for a one-off statement upload: "unusual"
        # then means "unusual within this statement".
        history = request.history or transactions
        stats = self.anomaly_scorer.build_stats(history)

        predictions: list[TransactionPrediction] = []
        for transaction in transactions:
            predictions.append(
                TransactionPrediction(
                    source_id=transaction.source_id,
                    description=transaction.description,
                    amount=transaction.amount,
                    category=self.categorizer.predict(transaction),
                    anomaly=self.anomaly_scorer.predict(transaction, stats),
                )
            )

        return PredictResponse(
            predictions=predictions,
            count=len(predictions),
            anomaly_count=sum(1 for p in predictions if p.anomaly.is_anomaly),
            backend={
                "categorizer": self.categorizer.info().backend,
                "anomaly_scorer": self.anomaly_scorer.info().backend,
            },
        )

    def predict_one(
        self,
        transaction: TransactionInput,
        history: Optional[list[TransactionInput]] = None,
    ) -> TransactionPrediction:
        """Convenience wrapper for scoring a single transaction."""
        response = self.predict(
            PredictRequest(transactions=[transaction], history=history or [])
        )
        return response.predictions[0]

    def model_info(self) -> list[ModelInfo]:
        """Artifact status for both models. Used by the health endpoint."""
        return [self.categorizer.info(), self.anomaly_scorer.info()]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _disabled_response(
        self, transactions: list[TransactionInput]
    ) -> PredictResponse:
        """
        Shape-compatible response when inference is switched off.

        Returning the same schema (rather than an error) means the caller does
        not need a separate code path for the disabled case.
        """
        return PredictResponse(
            predictions=[
                TransactionPrediction(
                    source_id=t.source_id,
                    description=t.description,
                    amount=t.amount,
                    category=CategoryPrediction(
                        category=UNKNOWN_CATEGORY, confidence=0.0, backend="disabled"
                    ),
                    anomaly=AnomalyPrediction(backend="disabled"),
                )
                for t in transactions
            ],
            count=len(transactions),
            anomaly_count=0,
            backend={"categorizer": "disabled", "anomaly_scorer": "disabled"},
        )


_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """FastAPI dependency: one shared service per process."""
    global _service
    if _service is None:
        _service = MLService()
    return _service
