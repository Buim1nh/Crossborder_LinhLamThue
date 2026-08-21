"""Subscription detection endpoints (CatBoost model from ml/registry)."""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.subscription_model import (ModelNotAvailable, get_detector,
                                             is_available, model_info,
                                             score_transactions)

router = APIRouter()


class ScoreRequest(BaseModel):
    transactions: list[dict[str, Any]] = Field(
        ..., description="Raw statement rows keyed by the original CSV column names"
    )
    threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Override the model's locked decision threshold"
    )


class ScoredTransaction(BaseModel):
    subscription_proba: float
    is_subscription: int
    model_version: str


class ScoreResponse(BaseModel):
    model_version: str
    threshold: float
    n_scored: int
    n_subscription: int
    results: list[ScoredTransaction]


@router.get("/model")
async def get_model_info():
    """Metadata of the model currently being served."""
    if not is_available():
        raise HTTPException(
            status_code=503,
            detail="No promoted model. Run: python -m ml.cli train --promote",
        )
    return model_info()


@router.post("/score", response_model=ScoreResponse)
async def score(request: ScoreRequest):
    """Score a batch of transactions for being subscription payments."""
    if not request.transactions:
        raise HTTPException(status_code=400, detail="transactions is empty")
    try:
        det = get_detector()
        results = score_transactions(request.transactions, request.threshold)
    except ModelNotAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid rows: {exc}") from exc

    return ScoreResponse(
        model_version=det.version,
        threshold=request.threshold if request.threshold is not None else det.threshold,
        n_scored=len(results),
        n_subscription=sum(r["is_subscription"] for r in results),
        results=results,
    )
