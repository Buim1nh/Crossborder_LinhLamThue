"""
MODULE 7 - Step 3a: CATEGORY INFERENCE.

Assigns a spending category to a transaction.

Two backends behind one interface:

- "model":     a serialized sklearn pipeline exposing `predict_proba`, taking
               the normalized text string as input (e.g. TfidfVectorizer ->
               LogisticRegression).
- "heuristic": weighted keyword matching. No dependencies, fully deterministic,
               and good enough that the app is useful before any model exists.

Low-confidence predictions are collapsed to `other` on purpose: a wrong-but-
confident category is worse for the user than an honest "uncategorized".
"""
import logging
from typing import Any, Optional

from src.modules.ml.config import (
    CATEGORIES,
    CATEGORY_KEYWORDS,
    UNKNOWN_CATEGORY,
    MLSettings,
    get_ml_settings,
)
from src.modules.ml.preprocessor import build_features
from src.modules.ml.registry import get_registry
from src.modules.ml.schemas import (
    CategoryPrediction,
    FeatureVector,
    ModelInfo,
    TransactionInput,
)

logger = logging.getLogger(__name__)

# Multi-word keywords are stronger evidence than single words ("apple music"
# is decisive, "apple" alone is not), so they score higher.
_PHRASE_WEIGHT = 2.0
_WORD_WEIGHT = 1.0

# Score at which the heuristic is considered fully confident. Keyword hits are
# divided by this to map onto a 0..1 confidence, then clamped.
#
# Keep this at 2.0 so a single unambiguous brand keyword ("netflix", "shopee")
# scores 0.5 and clears ML_MIN_CONFIDENCE. At 3.0 a lone word scored 0.33 and
# was silently downgraded to `other`, which made the heuristic backend - the
# one that runs by default with no artifact - unable to categorize anything
# that didn't hit two keywords at once.
_HEURISTIC_SATURATION = 2.0


class CategoryPredictor:
    """Predicts a spending category, preferring a trained model when present."""

    name = "categorizer"

    def __init__(self, settings: Optional[MLSettings] = None):
        self.settings = settings or get_ml_settings()
        self._model = get_registry().load(self.name, self.settings.categorizer_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, transaction: TransactionInput) -> CategoryPrediction:
        """Categorize one transaction. Never raises."""
        features = build_features(transaction)

        if self._model.loaded:
            prediction = self._predict_with_model(features)
            if prediction is not None:
                return self._apply_confidence_floor(prediction)

        return self._apply_confidence_floor(self._predict_with_keywords(features))

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
        self, features: FeatureVector
    ) -> Optional[CategoryPrediction]:
        """
        Run the sklearn pipeline. Returns None to signal "fall back".

        Any exception here is swallowed: a broken model must degrade to the
        heuristic rather than fail the user's upload.
        """
        estimator: Any = self._model.estimator
        try:
            probabilities = estimator.predict_proba([features.text])[0]
            classes = list(estimator.classes_)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Categorizer model inference failed (%s); using heuristic", exc
            )
            return None

        ranked = sorted(
            zip(classes, (float(p) for p in probabilities)),
            key=lambda pair: pair[1],
            reverse=True,
        )
        if not ranked:
            return None

        best_category, best_confidence = ranked[0]
        return CategoryPrediction(
            category=str(best_category),
            confidence=round(best_confidence, 4),
            backend="model",
            alternatives=[
                (str(c), round(p, 4)) for c, p in ranked[1:4] if p > 0
            ],
        )

    # ------------------------------------------------------------------
    # Backend: keyword heuristic
    # ------------------------------------------------------------------

    def _predict_with_keywords(self, features: FeatureVector) -> CategoryPrediction:
        """Weighted keyword match over the normalized description."""
        text = features.text

        # A credit with no descriptive text is almost always incoming money;
        # that is a safer default than "other".
        if not text:
            if features.is_credit:
                # Must stay at/above ML_MIN_CONFIDENCE, otherwise the floor
                # downgrades it straight back to `other` and this branch is
                # dead code.
                return CategoryPrediction(
                    category="income",
                    confidence=max(0.35, self.settings.ML_MIN_CONFIDENCE),
                    backend="heuristic",
                )
            return CategoryPrediction(
                category=UNKNOWN_CATEGORY, confidence=0.0, backend="heuristic"
            )

        padded = f" {text} "
        scores: dict[str, float] = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = 0.0
            for keyword in keywords:
                normalized_kw = keyword.strip()
                if not normalized_kw:
                    continue
                if " " in normalized_kw:
                    if normalized_kw in text:
                        score += _PHRASE_WEIGHT
                # Pad both sides so "ck" does not match inside "check".
                elif f" {normalized_kw} " in padded:
                    score += _WORD_WEIGHT
            if score > 0:
                scores[category] = score

        if not scores:
            return CategoryPrediction(
                category=UNKNOWN_CATEGORY, confidence=0.0, backend="heuristic"
            )

        ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
        best_category, best_score = ranked[0]

        confidence = min(best_score / _HEURISTIC_SATURATION, 1.0)

        # An income keyword on a debit (or a spend keyword on a credit) is
        # contradictory evidence, so temper the confidence.
        if best_category == "income" and not features.is_credit:
            confidence *= 0.5

        return CategoryPrediction(
            category=best_category,
            confidence=round(confidence, 4),
            backend="heuristic",
            alternatives=[
                (c, round(min(s / _HEURISTIC_SATURATION, 1.0), 4))
                for c, s in ranked[1:4]
            ],
        )

    # ------------------------------------------------------------------
    # Shared post-processing
    # ------------------------------------------------------------------

    def _apply_confidence_floor(
        self, prediction: CategoryPrediction
    ) -> CategoryPrediction:
        """
        Downgrade weak or unknown-label predictions to UNKNOWN_CATEGORY.

        Keeps the original confidence so the UI can still show "we weren't
        sure", and guards against an artifact trained on a stale taxonomy.
        """
        if prediction.category not in CATEGORIES:
            logger.debug(
                "Category '%s' outside taxonomy; downgrading", prediction.category
            )
            prediction.category = UNKNOWN_CATEGORY
            return prediction

        if prediction.confidence < self.settings.ML_MIN_CONFIDENCE:
            prediction.category = UNKNOWN_CATEGORY

        return prediction
