"""Nap du lieu, kiem tra schema, chia tap."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from .features import add_target, load_raw, normalize_columns  # noqa: F401

# Cot toi thieu (sau khi chuan hoa ten) de pipeline chay duoc
REQUIRED_COLUMNS = [
    "So_the", "Loai_giao_dich", "Trang_thai", "So_tien", "Don_vi_tien_te",
    "So_du", "Phi", "Ty_gia", "Noi_dung", "Thoi_gian",
]


class SchemaError(ValueError):
    pass


def validate_schema(df: pd.DataFrame, require_label: bool = True,
                    label_col: str = "label") -> list[str]:
    """Kiem tra schema. Nem SchemaError neu thieu cot bat buoc.
    Tra ve danh sach canh bao (khong chan)."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(
            f"Thieu cot bat buoc: {missing}. Cot dang co: {list(df.columns)}")
    if require_label and label_col not in df.columns:
        raise SchemaError(f"Thieu cot nhan '{label_col}'")

    warnings: list[str] = []
    if len(df) == 0:
        raise SchemaError("Bang rong")
    t = pd.to_datetime(df["Thoi_gian"], errors="coerce")
    if t.isna().any():
        warnings.append(f"{int(t.isna().sum())} dong co 'Thoi gian' khong parse duoc")
    for c in ("So_tien", "So_du", "Phi", "Ty_gia"):
        v = pd.to_numeric(df[c], errors="coerce")
        n_missing = int(df[c].isna().sum())
        n_unparsed = int(v.isna().sum()) - n_missing
        if n_missing:
            warnings.append(f"{n_missing} dong thieu gia tri '{c}'")
        if n_unparsed:
            warnings.append(f"{n_unparsed} dong co '{c}' khong parse duoc thanh so")
    if df["Noi_dung"].isna().mean() > 0.5:
        warnings.append("Hon 50% dong thieu 'Noi dung chuyen khoan'")
    return warnings


def load_dataset(path: str | Path, require_label: bool = True,
                 positive_class: str = "SUBSCRIPTION") -> tuple[pd.DataFrame, list[str]]:
    df = load_raw(str(path))
    warnings = validate_schema(df, require_label=require_label)
    if require_label:
        df = add_target(df, positive_class=positive_class)
    return df, warnings


def file_hash(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def make_split(df: pd.DataFrame, y: pd.Series, strategy: str, test_size: float,
               valid_size: float, seed: int):
    """Tra ve (train_idx, valid_idx, test_idx) dang mang vi tri."""
    n = len(df)
    if strategy == "time":
        order = np.argsort(pd.to_datetime(df["Thoi_gian"]).values, kind="mergesort")
        n_te = int(round(test_size * n))
        n_va = int(round(valid_size * (n - n_te)))
        te = order[n - n_te:]
        va = order[n - n_te - n_va: n - n_te]
        tr = order[: n - n_te - n_va]
        return tr, va, te
    idx = np.arange(n)
    tr_va, te = train_test_split(idx, test_size=test_size, random_state=seed,
                                 stratify=y.values)
    tr, va = train_test_split(tr_va, test_size=valid_size, random_state=seed,
                              stratify=y.values[tr_va])
    return tr, va, te


def cv_folds(y: pd.Series, n_splits: int, seed: int):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    return list(skf.split(np.zeros(len(y)), y.values))
