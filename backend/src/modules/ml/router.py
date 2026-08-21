"""
MODULE 7 - HTTP surface.

Ships its own APIRouter so integrating the module is a one-liner:

    from src.modules.ml import ml_router
    app.include_router(ml_router, prefix="/api/ml", tags=["ML"])
"""
from typing import Any

from fastapi import APIRouter, Depends

from src.modules.ml.config import CATEGORIES
from src.modules.ml.schemas import (
    ModelInfo,
    PredictRequest,
    PredictResponse,
    TransactionInput,
    TransactionPrediction,
)
from src.modules.ml.service import MLService, get_ml_service
from src.modules.ml.predictors.transaction_anomaly import TransactionAnomalyPredictor

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
@router.post("/predict/", response_model=PredictResponse, include_in_schema=False)
async def predict(
    payload: PredictRequest,
    service: MLService = Depends(get_ml_service),
) -> PredictResponse:
    """
    Categorize and anomaly-score a batch of transactions.

    Inference is CPU-bound but sub-millisecond per row on the heuristic path,
    so it runs inline. If a heavy model artifact is ever added, move this to a
    threadpool (`run_in_threadpool`) to avoid blocking the event loop.
    """
    return service.predict(payload)


@router.post("/predict/one", response_model=TransactionPrediction)
async def predict_one(
    payload: TransactionInput,
    service: MLService = Depends(get_ml_service),
) -> TransactionPrediction:
    """
    Score a single transaction.

    Note: with no history, anomaly detection reports `insufficient_data`
    rather than guessing. Use `/predict` with a `history` list for meaningful
    anomaly scores.
    """
    return service.predict_one(payload)


@router.get("/models", response_model=list[ModelInfo])
async def models(
    service: MLService = Depends(get_ml_service),
) -> list[ModelInfo]:
    """
    Report which backend each predictor is using and why.

    The main operational question this answers: "is my trained artifact
    actually being served, or did it silently fall back to heuristics?"
    """
    return service.model_info()


@router.get("/categories", response_model=list[str])
async def categories() -> list[str]:
    """The category taxonomy, for populating frontend filters and dropdowns."""
    return list(CATEGORIES)


# =============================================================================
# TransactionAnomalyDetector Endpoints (Vietnamese transaction model)
# =============================================================================

@router.post("/detect-anomalies")
async def detect_anomalies(
    transactions: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Run TransactionAnomalyDetector on a batch of transactions.

    This endpoint uses the trained model from checkpoints/archive/TransactionAnomalyDetector/
    and outputs anomaly scores, risk tiers, and detected anomalies.

    Request body: List of transaction dicts with fields like:
        - So_tien (amount)
        - So_the (card number)
        - Thoi_gian (datetime)
        - Loai_giao_dich (transaction type)
        - Noi_dung_chuyen_khoan (description)
        - So_du (balance)
        - Phi (fee)
        - Ty_gia (exchange rate)

    Returns:
        - results: Full prediction results for each transaction
        - summary: Aggregated stats (total, anomalies detected, rate, tier distribution)
        - anomalies: List of detected anomalies (outlier == -1)
        - model_version: Version of the loaded model
    """
    predictor = TransactionAnomalyPredictor()
    return predictor.predict(transactions)


@router.get("/detect-anomalies/info")
async def detect_anomalies_info() -> dict[str, Any]:
    """Get info about the TransactionAnomalyDetector model."""
    predictor = TransactionAnomalyPredictor()
    return predictor.info()
