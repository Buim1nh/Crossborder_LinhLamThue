"""
Feature engineering cho bài toán phát hiện giao dịch SUBSCRIPTION.

Dataset: Kaggle `duckyyyrobinson/transaction2` -> synthetic_200k_labels.csv
Module nay duoc dung chung boi script train va lop inference, de dam bao
feature luc train va luc serve giong het nhau.
"""
from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd

# ── Ten cot goc trong CSV -> ten chuan hoa dung trong code ──────────────
# Key la ten cot da duoc _norm() lam sach (bo BOM, bo dau tieng Viet, lowercase)
# nen ho tro ca file co dau ("So the" lan "So the" co dau) va co BOM.
COLUMN_ALIASES = {
    "id": "Id",
    "so the": "So_the",
    "loai giao dich": "Loai_giao_dich",
    "trang thai": "Trang_thai",
    "so tien": "So_tien",
    "don vi tien te": "Don_vi_tien_te",
    "so du": "So_du",
    "phi": "Phi",
    "ty gia": "Ty_gia",
    "noi dung chuyen khoan": "Noi_dung",
    "thoi gian": "Thoi_gian",
    "ly do tu choi": "Ly_do_tu_choi",
    "matched_txn_id": "matched_txn_id",
    "from": "email_from",
    "subject": "email_subject",
    "kind": "email_kind",
    "user_account": "user_account",
    "label": "label",
}

# Giu lai ten cu de code cu khong vo
RAW_TO_STD = COLUMN_ALIASES


def _norm(name: str) -> str:
    """Bo BOM, bo dau tieng Viet, gom khoang trang, lowercase."""
    s = str(name).replace("\ufeff", "").strip()
    s = s.replace("\u0111", "d").replace("\u0110", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Doi ten cot ve dang chuan, chap nhan moi bien the co/khong dau."""
    mapping = {}
    for c in df.columns:
        key = _norm(c)
        mapping[c] = COLUMN_ALIASES.get(key, c)
    return df.rename(columns=mapping)


TARGET_COL = "label"
POSITIVE_CLASS = "SUBSCRIPTION"

# Cac cot bi RO RI NHAN (leakage): chung mo ta ket qua doi soat email, va
# trong dataset nay `email_kind == "receipt"` trung khop 1-1 voi nhan
# SUBSCRIPTION. Dung chung de train = model dat AUC 1.0 nhung vo dung.
LEAK_COLS = ["matched_txn_id", "email_from", "email_subject", "email_kind"]

# Cot khong mang thong tin / dinh danh
DROP_COLS = ["Id", "user_account", "Ly_do_tu_choi"]

NUMERIC_BASE = ["So_tien", "So_du", "Phi", "Ty_gia"]

CATEGORICAL_FEATURES = [
    "Loai_giao_dich",
    "Trang_thai",
    "Don_vi_tien_te",
    "Noi_dung",
    "So_the",
]

TIME_FEATURES = [
    "gio",
    "ngay_trong_tuan",
    "ngay_trong_thang",
    "thang",
    "is_dem",
    "is_cuoi_tuan",
]

# Feature sinh tu mo ta giao dich, KHONG memorize chuoi goc -> tong quat hoa
# sang merchant chua tung thay.
DESC_FLAGS = [
    "desc_co_subscription",
    "desc_co_chu_ky",
    "desc_so_tu",
    "desc_so_ky_tu",
]

TEXT_FEATURE = "Noi_dung_text"

DERIVED_NUMERIC = [
    "log_so_tien",
    "ti_le_du_tien",
    "phi_tren_tien",
    # dac trung "lap lai" (recurrence) - dac trung nghiep vu cua subscription
    "rec_seq",
    "rec_ngay_ke_tu_lan_truoc",
    "rec_lech_chu_ky_thang",
    "rec_ti_le_tien_vs_lan_truoc",
    "rec_ti_le_tien_vs_trung_binh",
    "card_seq",
    "card_lech_tien",
]


_CHU_KY_TOKENS = ("monthly", "annual", "yearly", "premium", "plan", "pro",
                  "renewal", "recurring", "membership")


def norm_text(s: pd.Series) -> pd.Series:
    """Chuan hoa mo ta giao dich: bo dau, lowercase, thay ky tu la bang space."""
    out = s.fillna("").astype(str)
    out = out.str.replace("\u0111", "d", regex=False).str.replace("\u0110", "D", regex=False)
    out = out.map(lambda x: "".join(
        ch for ch in unicodedata.normalize("NFD", x)
        if unicodedata.category(ch) != "Mn"))
    out = out.str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True)
    out = out.str.replace(r"\s+", " ", regex=True).str.strip()
    return out


def load_raw(path: str) -> pd.DataFrame:
    """Doc CSV goc va chuan hoa ten cot."""
    df = pd.read_csv(path)
    return normalize_columns(df)


def add_target(df: pd.DataFrame, positive_class: str = POSITIVE_CLASS,
               target_col: str = TARGET_COL) -> pd.DataFrame:
    df = df.copy()
    df["y"] = (df[target_col].astype(str).str.strip().str.upper()
               == positive_class.upper()).astype(int)
    return df


# ── Cac bo feature co san ──────────────────────────────────────────────
FEATURE_MODES = {
    # DUNG DE DEPLOY: mo ta di qua CatBoost text_features nen tong quat hoa
    # duoc sang merchant chua tung xuat hien luc train.
    "robust": dict(include_leak=False, include_noi_dung=True,
                   desc_mode="text", include_card_id=False),
    # Mo ta lam categorical nguyen chuoi -> memorize, sap khi doi merchant.
    "categorical": dict(include_leak=False, include_noi_dung=True,
                        desc_mode="categorical", include_card_id=True),
    # Bo han mo ta — dung de do xem mo ta dong gop bao nhieu.
    "nodesc": dict(include_leak=False, include_noi_dung=False,
                   desc_mode="none", include_card_id=True),
    # CO ro ri nhan — chi de kiem chung, TUYET DOI khong deploy.
    "withleak": dict(include_leak=True, include_noi_dung=True,
                     desc_mode="categorical", include_card_id=True),
}


def build_features(df: pd.DataFrame, include_leak: bool = False,
                   include_noi_dung: bool = True, desc_mode: str = "categorical",
                   include_card_id: bool = True
                   ) -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    """
    Sinh feature tu bang giao dich da chuan hoa ten cot.

    Tra ve (X, feature_names, cat_feature_names, text_feature_names).

    desc_mode:
      - "categorical": dung nguyen chuoi mo ta lam categorical (memorize, chi tot
        khi merchant o production trung het voi luc train)
      - "text"       : dung CatBoost text_features + co dac trung -> tong quat hoa
        sang merchant moi
      - "none"       : bo han mo ta

    Cac dac trung "recurrence" duoc tinh CAUSAL (chi dung lich su phia truoc
    theo thoi gian) nen khong bi ro ri tuong lai khi split theo thoi gian.
    """
    d = df.copy()

    d["Thoi_gian"] = pd.to_datetime(d["Thoi_gian"], errors="coerce")
    for c in NUMERIC_BASE:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    # ── Thoi gian ──────────────────────────────────────────────────────
    d["gio"] = d["Thoi_gian"].dt.hour
    d["ngay_trong_tuan"] = d["Thoi_gian"].dt.dayofweek
    d["ngay_trong_thang"] = d["Thoi_gian"].dt.day
    d["thang"] = d["Thoi_gian"].dt.month
    d["is_dem"] = ((d["gio"] >= 22) | (d["gio"] <= 5)).astype(int)
    d["is_cuoi_tuan"] = (d["ngay_trong_tuan"] >= 5).astype(int)

    # ── Ty le tien ─────────────────────────────────────────────────────
    d["log_so_tien"] = np.log1p(d["So_tien"].clip(lower=0))
    d["ti_le_du_tien"] = d["So_du"] / (d["So_tien"].abs() + 1.0)
    d["phi_tren_tien"] = d["Phi"] / (d["So_tien"].abs() + 1.0)

    # ── Feature tu mo ta giao dich (tong quat hoa) ─────────────────────
    d[TEXT_FEATURE] = norm_text(d["Noi_dung"])
    d["desc_co_subscription"] = d[TEXT_FEATURE].str.contains("subscription|subscr|sub ",
                                                             regex=True).astype(int)
    d["desc_co_chu_ky"] = d[TEXT_FEATURE].apply(
        lambda t: int(any(k in t for k in _CHU_KY_TOKENS)))
    d["desc_so_tu"] = d[TEXT_FEATURE].str.split().map(len)
    d["desc_so_ky_tu"] = d[TEXT_FEATURE].str.len()

    # ── Chuan hoa categorical ──────────────────────────────────────────
    for c in CATEGORICAL_FEATURES:
        d[c] = d[c].fillna("UNKNOWN").astype(str).str.strip().replace("", "UNKNOWN")

    # ── Dac trung lap lai (causal) ─────────────────────────────────────
    order = d.index.copy()
    d = d.sort_values("Thoi_gian", kind="mergesort")

    grp = d.groupby(["So_the", "Noi_dung"], observed=True, sort=False)
    d["rec_seq"] = grp.cumcount()
    prev_t = grp["Thoi_gian"].shift(1)
    d["rec_ngay_ke_tu_lan_truoc"] = (d["Thoi_gian"] - prev_t).dt.total_seconds() / 86400.0
    d["rec_lech_chu_ky_thang"] = (d["rec_ngay_ke_tu_lan_truoc"] - 30.0).abs()
    prev_amt = grp["So_tien"].shift(1)
    d["rec_ti_le_tien_vs_lan_truoc"] = d["So_tien"] / (prev_amt.abs() + 1.0)
    exp_mean = grp["So_tien"].transform(lambda s: s.shift(1).expanding().mean())
    d["rec_ti_le_tien_vs_trung_binh"] = d["So_tien"] / (exp_mean.abs() + 1.0)

    gcard = d.groupby("So_the", observed=True, sort=False)
    d["card_seq"] = gcard.cumcount()
    card_mean = gcard["So_tien"].transform(lambda s: s.shift(1).expanding().mean())
    d["card_lech_tien"] = (d["So_tien"] - card_mean).abs() / (card_mean.abs() + 1.0)

    d = d.reindex(order)

    # ── Chon feature ───────────────────────────────────────────────────
    cat_features = list(CATEGORICAL_FEATURES)
    text_features: list[str] = []
    num_features = NUMERIC_BASE + TIME_FEATURES + DERIVED_NUMERIC

    if not include_card_id and "So_the" in cat_features:
        cat_features.remove("So_the")

    if not include_noi_dung or desc_mode == "none":
        cat_features.remove("Noi_dung")
    elif desc_mode == "text":
        cat_features.remove("Noi_dung")
        text_features.append(TEXT_FEATURE)
        num_features = num_features + DESC_FLAGS
    elif desc_mode == "categorical":
        pass
    else:
        raise ValueError(f"desc_mode khong hop le: {desc_mode}")

    if include_leak:
        for c in LEAK_COLS:
            if c in d.columns:
                d[c] = d[c].fillna("NONE").astype(str)
                cat_features.append(c)

    features = num_features + cat_features + text_features
    X = d[features].copy()
    for c in num_features:
        X[c] = pd.to_numeric(X[c], errors="coerce").astype("float64").fillna(-999.0)
    for c in cat_features:
        X[c] = X[c].astype(str)
    for c in text_features:
        X[c] = X[c].fillna("").astype(str)

    return X, features, cat_features, text_features
