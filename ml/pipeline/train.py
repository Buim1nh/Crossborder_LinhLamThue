"""Orchestration: audit -> cross-validate -> holdout -> refit -> dong goi.

Uoc luong chinh lay tu **cross-validation** (on dinh hon voi tap nho).
Holdout dung de do **gap overfit** (MCC train - MCC test).
Model cuoi cung refit tren TOAN BO du lieu voi so vong lap va nguong lay tu CV.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .audit import leakage_audit, leaking_columns
from .config import Config
from .data import cv_folds, file_hash, load_dataset, make_split
from .evaluate import aggregate_folds, binary_metrics, pick_threshold
from .modeling import build_model, feature_importance, make_features, make_pool


def _inner_valid(rows: np.ndarray, y: np.ndarray, seed: int, frac: float = 0.15):
    """Tach mot phan tap train lam valid de early-stop + chon nguong."""
    rng = np.random.default_rng(seed)
    idx = rows.copy()
    rng.shuffle(idx)
    n_va = max(int(round(frac * len(idx))), 40)
    n_va = min(n_va, len(idx) // 3)
    va, tr = idx[:n_va], idx[n_va:]
    if len(np.unique(y[va])) < 2 or len(np.unique(y[tr])) < 2:   # fallback
        va, tr = idx[: max(len(idx) // 5, 2)], idx[max(len(idx) // 5, 2):]
    return tr, va


def _fit_and_score(X, y, spec, cfg: Config, fit_rows, valid_rows, eval_rows):
    model = build_model(cfg.model_params, cfg.split["seed"])
    model.fit(make_pool(X, spec, y, fit_rows),
              eval_set=make_pool(X, spec, y, valid_rows), use_best_model=True)
    p_va = model.predict_proba(make_pool(X, spec, rows=valid_rows))[:, 1]
    thr = pick_threshold(y[valid_rows], p_va, cfg.threshold_cfg["strategy"],
                         cfg.threshold_cfg.get("value"))
    p_ev = model.predict_proba(make_pool(X, spec, rows=eval_rows))[:, 1]
    return model, thr, binary_metrics(y[eval_rows], p_ev, thr)


def run_training(cfg: Config, data_path: str | None = None,
                 log=print) -> dict:
    path = data_path or cfg.train_path
    df, warnings = load_dataset(path, require_label=True,
                                positive_class=cfg.positive_class)
    y = df["y"].values
    log(f"Du lieu   : {path}")
    log(f"            {len(df):,} giao dich | {cfg.positive_class} = "
        f"{int(y.sum()):,} ({y.mean()*100:.2f}%)")
    for w in warnings:
        log(f"  ⚠ canh bao schema: {w}")

    # ── 1. Audit ro ri ─────────────────────────────────────────────────
    leak = leakage_audit(df, df["y"])
    leaks = leaking_columns(leak)
    if leaks:
        log(f"  ⚠ RO RI NHAN o cot: {leaks} — da bi loai khoi feature set")

    # ── 2. Feature ─────────────────────────────────────────────────────
    X, spec = make_features(df, cfg.feature_mode)
    log(f"Feature   : mode={cfg.feature_mode} | {len(spec.names)} cot "
        f"({len(spec.cat)} categorical, {len(spec.text)} text)")

    # ── 3. Cross-validation (uoc luong chinh) ─────────────────────────
    k = int(cfg.split["cv_folds"])
    seed = int(cfg.split["seed"])
    fold_metrics, fold_thr, fold_iters = [], [], []
    log(f"\nCross-validation {k}-fold")
    for i, (tr_i, te_i) in enumerate(cv_folds(df["y"], k, seed)):
        fit_rows, va_rows = _inner_valid(tr_i, y, seed + i)
        model, thr, m = _fit_and_score(X, y, spec, cfg, fit_rows, va_rows, te_i)
        fold_metrics.append(m)
        fold_thr.append(thr)
        fold_iters.append(int(model.get_best_iteration()))
        log(f"  fold {i}: MCC={m['mcc']:.4f}  P={m['precision']:.4f}  "
            f"R={m['recall']:.4f}  AUC={m.get('roc_auc', float('nan')):.4f}  "
            f"thr={thr:.4f}  iters={fold_iters[-1]}")
    cv = aggregate_folds(fold_metrics)
    log(f"  => MCC = {cv['mcc_mean']:.4f} ± {cv['mcc_std']:.4f}")

    # ── 4. Holdout de do gap overfit ──────────────────────────────────
    tr, va, te = make_split(df, df["y"], cfg.split["strategy"],
                            cfg.split["test_size"], cfg.split["valid_size"], seed)
    model_h, thr_h, m_test = _fit_and_score(X, y, spec, cfg, tr, va, te)
    p_tr = model_h.predict_proba(make_pool(X, spec, rows=tr))[:, 1]
    m_train = binary_metrics(y[tr], p_tr, thr_h)
    gap = round(m_train["mcc"] - m_test["mcc"], 6)
    log(f"\nHoldout   : MCC train={m_train['mcc']:.4f}  test={m_test['mcc']:.4f}  "
        f"gap={gap:+.4f}")

    # ── 5. Refit tren toan bo du lieu ─────────────────────────────────
    final_iters = max(50, int(np.median(fold_iters)) + 1)
    final_thr = float(np.median(fold_thr))
    params = {**cfg.model_params, "iterations": final_iters}
    final = build_model(params, seed, use_od=False)
    final.fit(make_pool(X, spec, y))
    log(f"Refit     : toan bo {len(df):,} dong, {final_iters} vong, "
        f"nguong = {final_thr:.4f}")

    imp = feature_importance(final, make_pool(X, spec, y), spec.names)

    metrics = {
        "primary_metric": "mcc",
        "threshold": round(final_thr, 6),
        "threshold_strategy": cfg.threshold_cfg["strategy"],
        "cv": cv,
        "train": m_train,
        "holdout": m_test,
        "train_test_mcc_gap": gap,
        "fold_thresholds": [round(t, 6) for t in fold_thr],
        "fold_best_iterations": fold_iters,
        "feature_importance": imp,
    }
    manifest = {
        "train_file": str(path),
        "train_file_sha256_16": file_hash(path),
        "n_rows": int(len(df)),
        "positive_rate": round(float(y.mean()), 6),
        "feature_mode": cfg.feature_mode,
        "n_features": len(spec.names),
        "final_iterations": final_iters,
        "config": cfg.to_dict(),
        "leaking_columns": leaks,
        "schema_warnings": warnings,
    }
    return {"model": final, "spec": spec, "metrics": metrics,
            "manifest": manifest, "leakage": leak, "df": df,
            "importance": imp}
