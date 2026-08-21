"""
Subscription Detection Service.

Thin wrapper around the CatBoost model packaged in `ml/registry/`.
The model is loaded lazily on first use and cached for the process lifetime,
so the FastAPI app starts even when no model has been promoted yet.

See ml/README.md for how the model is trained, gated and promoted.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import pandas as pd

# The `ml` package lives at the repository root, next to `backend/`.
_ML_ROOT = Path(os.getenv("ML_ROOT", Path(__file__).resolve().parents[3]))
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))


class ModelNotAvailable(RuntimeError):
    """Raised when no promoted model can be loaded."""


@lru_cache(maxsize=1)
def get_detector(version: Optional[str] = None):
    """Load the promoted detector. Cached — call is cheap after the first hit."""
    try:
        from ml.pipeline.config import load_config
        from ml.pipeline.serve import SubscriptionDetector
    except ImportError as exc:  # catboost / ml package missing
        raise ModelNotAvailable(
            f"Cannot import the ml package from {_ML_ROOT}: {exc}"
        ) from exc

    try:
        cfg = load_config(_ML_ROOT / "ml" / "config.yaml")
        registry_dir = _ML_ROOT / cfg.registry_dir
        return SubscriptionDetector(registry_dir=registry_dir,
                                    version=version, config=cfg)
    except FileNotFoundError as exc:
        raise ModelNotAvailable(str(exc)) from exc


def is_available() -> bool:
    try:
        get_detector()
        return True
    except ModelNotAvailable:
        return False


def model_info() -> dict[str, Any]:
    return get_detector().info()


def score_transactions(rows: list[dict[str, Any]],
                       threshold: Optional[float] = None) -> list[dict[str, Any]]:
    """Score raw statement rows (original CSV column names, with or without
    Vietnamese diacritics).

    Returns one dict per row: subscription_proba, is_subscription, model_version.
    """
    if not rows:
        return []
    det = get_detector()
    out = det.predict(pd.DataFrame(rows), threshold)
    return out[["subscription_proba", "is_subscription", "model_version"]].to_dict("records")
