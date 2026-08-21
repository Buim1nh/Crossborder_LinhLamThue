"""Dung Pool / model CatBoost tu cau hinh."""
from __future__ import annotations

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, Pool

from .features import FEATURE_MODES, build_features


class FeatureSpec:
    """Giu dung thu tu cot + chi so cat/text de train va serve khop nhau."""

    def __init__(self, names: list[str], cat: list[str], text: list[str]):
        self.names = names
        self.cat = cat
        self.text = text
        self.cat_idx = [names.index(c) for c in cat]
        self.text_idx = [names.index(c) for c in text]

    def to_dict(self) -> dict:
        return {"features": self.names, "cat_features": self.cat,
                "cat_feature_indices": self.cat_idx, "text_features": self.text,
                "text_feature_indices": self.text_idx}

    @classmethod
    def from_dict(cls, d: dict) -> "FeatureSpec":
        return cls(d["features"], d["cat_features"], d.get("text_features", []))


def make_features(df: pd.DataFrame, mode: str) -> tuple[pd.DataFrame, FeatureSpec]:
    if mode not in FEATURE_MODES:
        raise ValueError(f"feature mode khong hop le: {mode}")
    X, names, cat, text = build_features(df, **FEATURE_MODES[mode])
    return X, FeatureSpec(names, cat, text)


def make_pool(X: pd.DataFrame, spec: FeatureSpec, y=None, rows=None) -> Pool:
    Xs = X if rows is None else X.iloc[rows]
    ys = None if y is None else (y if rows is None else np.asarray(y)[rows])
    return Pool(Xs, ys, cat_features=spec.cat_idx, text_features=spec.text_idx)


def build_model(params: dict, seed: int, use_od: bool = True) -> CatBoostClassifier:
    """use_od=False cho lan refit cuoi (khong co eval_set nen khong early-stop)."""
    p = dict(params)
    od = dict(od_type="Iter", od_wait=p.get("od_wait", 150)) if use_od else {}
    return CatBoostClassifier(
        iterations=p.get("iterations", 1500),
        learning_rate=p.get("learning_rate", 0.05),
        depth=p.get("depth", 6),
        l2_leaf_reg=p.get("l2_leaf_reg", 3.0),
        loss_function="Logloss",
        eval_metric=p.get("eval_metric", "PRAUC:use_weights=false"),
        auto_class_weights=p.get("auto_class_weights", "Balanced"),
        random_seed=seed,
        thread_count=-1,
        allow_writing_files=False,
        verbose=p.get("verbose", 0),
        **od,
    )


def fit(model: CatBoostClassifier, pool_train: Pool, pool_valid: Pool) -> CatBoostClassifier:
    model.fit(pool_train, eval_set=pool_valid, use_best_model=True)
    return model


def feature_importance(model: CatBoostClassifier, pool: Pool,
                       names: list[str], top: int | None = None) -> list[dict]:
    vals = model.get_feature_importance(pool)
    pairs = sorted(zip(names, vals), key=lambda kv: -kv[1])
    if top:
        pairs = pairs[:top]
    return [{"feature": n, "importance": round(float(v), 4)} for n, v in pairs]
