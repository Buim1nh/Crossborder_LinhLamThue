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


def _get_col(df: pd.DataFrame, name: str) -> pd.Series:
    """Safely get a column, handling duplicate names by taking the first match.
    When normalize_columns creates duplicate column names (because both the original
    column name AND a matched alias both exist), df[col] returns a DataFrame.
    This function always returns a Series."""
    raw = df[name]
    if isinstance(raw, pd.DataFrame):
        # Duplicate columns — take first
        return raw.iloc[:, 0]
    return raw


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

    # Thoi_gian
    t = pd.to_datetime(_get_col(df, "Thoi_gian"), errors="coerce")
    if t.isna().any():
        warnings.append(f"{int(t.isna().sum())} dong co 'Thoi gian' khong parse duoc")

    for c in ("So_tien", "So_du", "Phi", "Ty_gia"):
        col = _get_col(df, c)
        if col.dtype.name and col.dtype.name.startswith("int"):
            col = col.astype("float64")
        v = pd.to_numeric(col, errors="coerce")
        n_missing = int(col.isna().sum())
        n_unparsed = int(v.isna().sum()) - n_missing
        if n_missing:
            warnings.append(f"{n_missing} dong thieu gia tri '{c}'")
        if n_unparsed:
            warnings.append(f"{n_unparsed} dong co '{c}' khong parse duoc thanh so")

    noi_dung = _get_col(df, "Noi_dung")
    if noi_dung.isna().mean() > 0.5:
        warnings.append("Hon 50% dong thieu 'Noi dung chuyen khoan'")
    return warnings


def load_dataset(path: str | Path, require_label: bool = True,
                 positive_class: str = "SUBSCRIPTION") -> tuple[pd.DataFrame, list[str]]:
    df = load_raw(str(path))
    warnings = validate_schema(df, require_label=require_label)
    if require_label:
        df = add_target(df, positive_class=positive_class)
    return df, warnings


def load_raw(path: str) -> pd.DataFrame:
    """Doc CSV goc va chuan hoa ten cot."""
    df = pd.read_csv(path)
    return normalize_columns(df)


def add_target(df: pd.DataFrame, positive_class: str = "SUBSCRIPTION",
               label_col: str = "label") -> pd.DataFrame:
    """Gan cot nhan tu gia tri trong cot 'label'."""
    df = df.copy()
    df[label_col] = (df[label_col] == positive_class).astype(int)
    return df


def split_data(df: pd.DataFrame, label_col: str = "label",
               test_size: float = 0.2, seed: int = 42
               ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chia tap train/test theo ti le."""
    return train_test_split(df, test_size=test_size, random_state=seed,
                            stratify=df[label_col])


def crossval_splits(df: pd.DataFrame, label_col: str = "label",
                    n_splits: int = 5, seed: int = 42
                    ) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Sinh n_splits folds cho cross-validation."""
    kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    splits = []
    for train_idx, val_idx in kfold.split(df, df[label_col]):
        splits.append((df.iloc[train_idx], df.iloc[val_idx]))
    return splits
