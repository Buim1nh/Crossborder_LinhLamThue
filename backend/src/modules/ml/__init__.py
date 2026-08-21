"""
MODULE 7: ML Inference.

Self-contained inference layer for transaction categorization and anomaly
detection. Mirrors the structure of `src.modules.chat`.

Design rules for this package:

1. INFERENCE ONLY. No training code runs at import or request time. Training
   lives in `training/` and produces artifacts consumed by `registry.py`.
2. ALWAYS ANSWERS. Every predictor has a dependency-free heuristic fallback,
   so the API works on a fresh checkout with no artifacts and no sklearn.
3. NEVER RAISES. A missing, corrupt or incompatible model degrades to the
   heuristic path; it never turns into a 500 on the user's upload.

Typical use from another module:

    from src.modules.ml import get_ml_service, TransactionInput

    service = get_ml_service()
    result = service.predict_one(
        TransactionInput(description="STARBUCKS COFFEE", amount=-5.40)
    )
    result.category.category  # "food_dining"
"""
from src.modules.ml.config import CATEGORIES, MLSettings, get_ml_settings
from src.modules.ml.router import router as ml_router
from src.modules.ml.schemas import (
    AnomalyPrediction,
    CategoryPrediction,
    ModelInfo,
    PredictRequest,
    PredictResponse,
    TransactionInput,
    TransactionPrediction,
)
from src.modules.ml.service import MLService, get_ml_service
from src.modules.ml.predictors.transaction_anomaly import TransactionAnomalyDetector, TransactionAnomalyPredictor

__all__ = [
    "CATEGORIES",
    "MLSettings",
    "get_ml_settings",
    "ml_router",
    "MLService",
    "get_ml_service",
    "TransactionInput",
    "TransactionPrediction",
    "CategoryPrediction",
    "AnomalyPrediction",
    "PredictRequest",
    "PredictResponse",
    "ModelInfo",
    "TransactionAnomalyDetector",
    "TransactionAnomalyPredictor",
]
