"""Metric, chon nguong va cong chat luong.

Metric chinh la MCC (Matthews Correlation Coefficient) — on dinh voi du lieu
mat can bang va phan anh ca 4 o cua confusion matrix, khac F1 vo cam voi TN.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             f1_score, matthews_corrcoef, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)


def binary_metrics(y, proba, threshold: float) -> dict:
    y = np.asarray(y)
    proba = np.asarray(proba)
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    m = {
        "n": int(len(y)),
        "positive_rate": round(float(y.mean()), 6),
        "threshold": round(float(threshold), 6),
        "mcc": round(float(matthews_corrcoef(y, pred)), 6),
        "precision": round(float(precision_score(y, pred, zero_division=0)), 6),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 6),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 6),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }
    if len(np.unique(y)) > 1:
        m["roc_auc"] = round(float(roc_auc_score(y, proba)), 6)
        m["pr_auc"] = round(float(average_precision_score(y, proba)), 6)
    return m


def pick_threshold(y, proba, strategy: str = "max_mcc",
                   fixed_value: float | None = None) -> float:
    """Chon nguong TREN TAP VALID (khong bao gio tren tap test)."""
    if strategy == "fixed":
        if fixed_value is None:
            raise ValueError("strategy=fixed can threshold.value")
        return float(fixed_value)

    y = np.asarray(y)
    proba = np.asarray(proba)
    if len(np.unique(y)) < 2:
        return 0.5

    if strategy == "max_f1":
        prec, rec, thr = precision_recall_curve(y, proba)
        if len(thr) == 0:
            return 0.5
        f1 = np.nan_to_num(2 * prec * rec / np.clip(prec + rec, 1e-12, None))[:-1]
        return float(thr[int(np.argmax(f1))])

    if strategy == "max_mcc":
        qs = np.linspace(0.001, 0.999, 400)
        grid = np.unique(np.round(np.quantile(proba, qs), 6))
        best_t, best_v = 0.5, -2.0
        for t in grid:
            v = matthews_corrcoef(y, (proba >= t).astype(int))
            if v > best_v:
                best_t, best_v = float(t), float(v)
        return best_t

    raise ValueError(f"strategy khong hop le: {strategy}")


def aggregate_folds(fold_metrics: list[dict]) -> dict:
    """Gop metric cua nhieu fold thanh mean/std."""
    keys = ["mcc", "precision", "recall", "f1", "roc_auc", "pr_auc"]
    out: dict = {"n_folds": len(fold_metrics), "folds": fold_metrics}
    for k in keys:
        vals = [f[k] for f in fold_metrics if k in f]
        if vals:
            out[f"{k}_mean"] = round(float(np.mean(vals)), 6)
            out[f"{k}_std"] = round(float(np.std(vals)), 6)
    return out


# ════════════════════════════════════════════════════════════════════════
# CONG CHAT LUONG
# ════════════════════════════════════════════════════════════════════════
def check_gates(summary: dict, gates: dict) -> tuple[bool, list[str]]:
    """`summary` can co: cv (mcc_mean, mcc_std, precision_mean, recall_mean),
    train_mcc, test_mcc. Tra ve (dat?, danh sach ly do truot)."""
    fails: list[str] = []
    cv = summary.get("cv", {})

    def _chk(name, value, limit, op):
        if value is None:
            fails.append(f"{name}: khong co so lieu de kiem tra")
            return
        ok = value >= limit if op == ">=" else value <= limit
        if not ok:
            fails.append(f"{name} = {value:.4f} (yeu cau {op} {limit})")

    _chk("MCC (CV mean)", cv.get("mcc_mean"), gates["min_mcc"], ">=")
    _chk("Precision (CV mean)", cv.get("precision_mean"), gates["min_precision"], ">=")
    _chk("Recall (CV mean)", cv.get("recall_mean"), gates["min_recall"], ">=")
    _chk("Do lech CV (MCC std)", cv.get("mcc_std"), gates["max_cv_std"], "<=")

    gap = summary.get("train_test_mcc_gap")
    _chk("Gap overfit (MCC train - test)", gap, gates["max_train_test_mcc_gap"], "<=")

    return (len(fails) == 0), fails


def format_gate_report(passed: bool, fails: list[str], gates: dict) -> str:
    head = "CONG CHAT LUONG: " + ("DAT ✅" if passed else "TRUOT ❌")
    lines = [head, "-" * 60]
    if passed:
        lines.append("Tat ca tieu chi deu dat:")
        for k, v in gates.items():
            lines.append(f"  • {k} = {v}")
    else:
        for f in fails:
            lines.append(f"  ❌ {f}")
    return "\n".join(lines)
