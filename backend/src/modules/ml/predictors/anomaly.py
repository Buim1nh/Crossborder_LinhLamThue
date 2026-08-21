"""
MODULE 7 - Step 3b: ANOMALY INFERENCE.

Scores how unusual a transaction is relative to the user's own history.

Backends:

- "model":     a serialized estimator with `score_samples` (e.g. IsolationForest)
               over the dense numeric feature vector.
- "heuristic": a transparent weighted sum of five interpretable signals.

The heuristic is the default for a deliberate reason: an anomaly flag is shown
directly to the user, so it must be EXPLAINABLE. "Flagged because this is 8x
your typical spend at a merchant you've never used" is actionable; a bare
IsolationForest score is not. Every result therefore carries its `signals`.
"""
import logging
import statistics
from collections import Counter
from typing import Any, Optional

from src.modules.ml.config import (
    AMOUNT_ZSCORE_CAP,
    ANOMALY_SIGNAL_WEIGHTS,
    MIN_HISTORY_FOR_STATS,
    RAPID_REPEAT_WINDOW_SECONDS,
    MLSettings,
    get_ml_settings,
)
from src.modules.ml.preprocessor import build_features, merchant_key
from src.modules.ml.registry import get_registry
from src.modules.ml.schemas import (
    AnomalyPrediction,
    AnomalySignal,
    ModelInfo,
    TransactionInput,
)

logger = logging.getLogger(__name__)

# Scale factor making MAD a consistent estimator of stddev for normal data.
_MAD_TO_STD = 1.4826

# Fallback when MAD is exactly 0 (i.e. >50% of history is one identical amount),
# which would otherwise make the z-score divide by zero.
_MIN_SPREAD = 1e-6


class HistoryStats:
    """
    Reference distribution built from a user's prior transactions.

    Computed once per batch and reused for every row, so scoring a 500-row
    upload stays O(n) rather than O(n^2).
    """

    def __init__(self, history: list[TransactionInput]):
        self.count = len(history)

        amounts = [abs(float(t.amount)) for t in history]
        self.median_amount = statistics.median(amounts) if amounts else 0.0

        # Median Absolute Deviation, not stddev: the mean and stddev are
        # themselves dragged upward by the very outliers we are hunting for,
        # which masks them. MAD is robust to that.
        if amounts:
            deviations = [abs(a - self.median_amount) for a in amounts]
            self.mad = statistics.median(deviations)
        else:
            self.mad = 0.0

        self.merchant_counts: Counter[str] = Counter(
            merchant_key(t) for t in history if merchant_key(t)
        )

        # (merchant, rounded amount) -> sorted timestamps, for repeat detection.
        self._occurrences: dict[tuple[str, float], list[float]] = {}
        for t in history:
            if t.transaction_date is None:
                continue
            key = (merchant_key(t), round(abs(float(t.amount)), 2))
            self._occurrences.setdefault(key, []).append(
                t.transaction_date.timestamp()
            )
        for timestamps in self._occurrences.values():
            timestamps.sort()

    @property
    def is_sufficient(self) -> bool:
        return self.count >= MIN_HISTORY_FOR_STATS

    def amount_zscore(self, amount: float) -> float:
        """Robust z-score of `amount` against the historical distribution."""
        spread = max(self.mad * _MAD_TO_STD, _MIN_SPREAD)
        return abs(abs(amount) - self.median_amount) / spread

    def merchant_frequency(self, key: str) -> int:
        return self.merchant_counts.get(key, 0)

    def has_recent_duplicate(
        self, key: str, amount: float, timestamp: Optional[float]
    ) -> bool:
        """True if an identical charge occurred within the repeat window."""
        if timestamp is None:
            return False
        occurrences = self._occurrences.get((key, round(abs(amount), 2)))
        if not occurrences:
            return False
        return any(
            0 < abs(timestamp - prior) <= RAPID_REPEAT_WINDOW_SECONDS
            for prior in occurrences
        )


class AnomalyScorer:
    """Scores transactions for unusualness, with explanations."""

    name = "anomaly_scorer"

    def __init__(self, settings: Optional[MLSettings] = None):
        self.settings = settings or get_ml_settings()
        self._model = get_registry().load(self.name, self.settings.anomaly_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_stats(self, history: list[TransactionInput]) -> HistoryStats:
        """Precompute the reference distribution for a batch."""
        return HistoryStats(history)

    def predict(
        self, transaction: TransactionInput, stats: HistoryStats
    ) -> AnomalyPrediction:
        """Score one transaction against `stats`. Never raises."""
        if not stats.is_sufficient:
            # Refuse to guess: with 2 transactions, everything looks like an
            # outlier, and false alarms erode trust fast.
            return AnomalyPrediction(
                score=0.0,
                is_anomaly=False,
                backend="heuristic",
                insufficient_data=True,
            )

        if self._model.loaded:
            prediction = self._predict_with_model(transaction)
            if prediction is not None:
                return prediction

        return self._predict_with_signals(transaction, stats)

    def info(self) -> ModelInfo:
        return ModelInfo(
            name=self.name,
            loaded=self._model.loaded,
            backend="model" if self._model.loaded else "heuristic",
            artifact_path=str(self._model.path),
            error=self._model.error,
        )

    # ------------------------------------------------------------------
    # Backend: trained model
    # ------------------------------------------------------------------

    def _predict_with_model(
        self, transaction: TransactionInput
    ) -> Optional[AnomalyPrediction]:
        """Run an IsolationForest-style estimator. None means "fall back"."""
        estimator: Any = self._model.estimator
        features = build_features(transaction)

        try:
            raw = float(estimator.score_samples([features.to_numeric()])[0])
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Anomaly model inference failed (%s); using heuristic", exc
            )
            return None

        # score_samples returns roughly -1 (anomalous) .. 0 (normal). Flip and
        # clamp so the output matches the heuristic's 0..1 convention.
        score = min(max(-raw, 0.0), 1.0)

        return AnomalyPrediction(
            score=round(score, 4),
            is_anomaly=score >= self.settings.ML_ANOMALY_THRESHOLD,
            backend="model",
        )

    # ------------------------------------------------------------------
    # Backend: explainable signals
    # ------------------------------------------------------------------

    def _predict_with_signals(
        self, transaction: TransactionInput, stats: HistoryStats
    ) -> AnomalyPrediction:
        """Weighted sum of five interpretable 0..1 signals."""
        features = build_features(transaction)
        key = merchant_key(transaction)
        amount = abs(float(transaction.amount))
        signals: list[AnomalySignal] = []

        # --- Signal 1: amount outlier ------------------------------------
        zscore = stats.amount_zscore(amount)
        amount_value = min(zscore / AMOUNT_ZSCORE_CAP, 1.0)
        signals.append(AnomalySignal(
            name="amount_outlier",
            weight=ANOMALY_SIGNAL_WEIGHTS["amount_outlier"],
            value=round(amount_value, 4),
            explanation=(
                f"Amount {amount:,.2f} is {zscore:.1f} robust std devs from "
                f"the usual {stats.median_amount:,.2f}"
            ),
        ))

        # --- Signal 2: rare merchant -------------------------------------
        frequency = stats.merchant_frequency(key)
        if frequency == 0:
            rare_value, rare_note = 1.0, "Merchant never seen before"
        elif frequency == 1:
            rare_value, rare_note = 0.5, "Merchant seen only once before"
        else:
            rare_value, rare_note = 0.0, f"Merchant seen {frequency} times before"
        signals.append(AnomalySignal(
            name="rare_merchant",
            weight=ANOMALY_SIGNAL_WEIGHTS["rare_merchant"],
            value=rare_value,
            explanation=rare_note,
        ))

        # --- Signal 3: odd hour ------------------------------------------
        signals.append(AnomalySignal(
            name="odd_hour",
            weight=ANOMALY_SIGNAL_WEIGHTS["odd_hour"],
            value=1.0 if features.is_odd_hour else 0.0,
            explanation=(
                f"Transacted at {features.hour:02d}:00 (overnight)"
                if features.is_odd_hour
                else "Transacted during normal hours"
            ),
        ))

        # --- Signal 4: round amount --------------------------------------
        signals.append(AnomalySignal(
            name="round_amount",
            weight=ANOMALY_SIGNAL_WEIGHTS["round_amount"],
            value=1.0 if features.is_round_amount else 0.0,
            explanation=(
                "Suspiciously round amount"
                if features.is_round_amount
                else "Amount is not suspiciously round"
            ),
        ))

        # --- Signal 5: rapid repeat --------------------------------------
        timestamp = (
            transaction.transaction_date.timestamp()
            if transaction.transaction_date is not None
            else None
        )
        is_repeat = stats.has_recent_duplicate(key, amount, timestamp)
        signals.append(AnomalySignal(
            name="rapid_repeat",
            weight=ANOMALY_SIGNAL_WEIGHTS["rapid_repeat"],
            value=1.0 if is_repeat else 0.0,
            explanation=(
                "Identical charge from the same merchant within 24h"
                if is_repeat
                else "No identical recent charge"
            ),
        ))

        # Weights sum to 1.0, so the total is already a 0..1 score.
        score = sum(s.weight * s.value for s in signals)
        score = min(max(score, 0.0), 1.0)

        return AnomalyPrediction(
            score=round(score, 4),
            is_anomaly=score >= self.settings.ML_ANOMALY_THRESHOLD,
            backend="heuristic",
            signals=signals,
        )
