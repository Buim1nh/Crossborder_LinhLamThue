"""Concrete predictors. Each exposes `.predict()` and `.info()`."""
from src.modules.ml.predictors.anomaly import AnomalyScorer
from src.modules.ml.predictors.categorizer import CategoryPredictor

__all__ = ["AnomalyScorer", "CategoryPredictor"]
