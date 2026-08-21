"""Lop inference dung cho backend."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier

from .config import Config, load_config
from .data import validate_schema
from .features import FEATURE_MODES, build_features, normalize_columns
from .modeling import FeatureSpec
from .registry import get_current, resolve


class SubscriptionDetector:
    """Nap model tu registry va cham diem giao dich moi.

    >>> det = SubscriptionDetector()                  # phien ban `current`
    >>> out = det.predict(df)                         # df dung ten cot GOC
    >>> out[["subscription_proba", "is_subscription"]]
    """

    def __init__(self, registry_dir: str | Path | None = None,
                 version: str | None = None, config: Config | None = None):
        cfg = config or load_config()
        self.registry_dir = Path(registry_dir or cfg.registry_dir)
        self.dir = resolve(self.registry_dir, version)
        self.version = self.dir.name
        self.spec = FeatureSpec.from_dict(json.loads(
            (self.dir / "feature_spec.json").read_text()))
        self.manifest = json.loads((self.dir / "manifest.json").read_text())
        self.metrics = json.loads((self.dir / "metrics.json").read_text())
        self.feature_mode = self.manifest["feature_mode"]
        self.threshold = float(self.metrics["threshold"])
        self.model = CatBoostClassifier()
        self.model.load_model(str(self.dir / "model.cbm"))
        self.is_current = (self.version == get_current(self.registry_dir))

    # ── noi bo ────────────────────────────────────────────────────────
    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        d = normalize_columns(df)
        validate_schema(d, require_label=False)
        X, names, cat, text = build_features(d, **FEATURE_MODES[self.feature_mode])
        return X[self.spec.names]

    # ── API ───────────────────────────────────────────────────────────
    def predict_proba(self, df: pd.DataFrame):
        from catboost import Pool
        X = self._prepare(df)
        return self.model.predict_proba(
            Pool(X, cat_features=self.spec.cat_idx,
                 text_features=self.spec.text_idx))[:, 1]

    def predict(self, df: pd.DataFrame, threshold: float | None = None) -> pd.DataFrame:
        thr = self.threshold if threshold is None else float(threshold)
        proba = self.predict_proba(df)
        out = df.copy()
        out["subscription_proba"] = proba
        out["is_subscription"] = (proba >= thr).astype(int)
        out["model_version"] = self.version
        return out

    def info(self) -> dict:
        cv = self.metrics.get("cv", {})
        return {
            "version": self.version,
            "is_current": self.is_current,
            "feature_mode": self.feature_mode,
            "threshold": self.threshold,
            "trained_on": self.manifest.get("train_file"),
            "train_rows": self.manifest.get("n_rows"),
            "cv_mcc_mean": cv.get("mcc_mean"),
            "cv_mcc_std": cv.get("mcc_std"),
            "created_at": self.manifest.get("created_at"),
            "git_sha": self.manifest.get("git_sha"),
        }
