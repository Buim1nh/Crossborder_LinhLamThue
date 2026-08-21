import numpy as np
import pandas as pd
import pytest

from ml.pipeline.features import (FEATURE_MODES, LEAK_COLS, build_features,
                                  norm_text, normalize_columns)
from ml.pipeline.modeling import make_features


@pytest.mark.parametrize("mode", list(FEATURE_MODES))
def test_moi_mode_sinh_duoc_feature(raw_df, mode):
    X, spec = make_features(normalize_columns(raw_df), mode)
    assert len(X) == len(raw_df)
    assert list(X.columns) == spec.names
    assert not X[[c for c in spec.names if c not in spec.cat + spec.text]].isna().any().any()


def test_mode_robust_khong_chua_cot_ro_ri(raw_df):
    _, spec = make_features(normalize_columns(raw_df), "robust")
    assert not set(spec.names) & set(LEAK_COLS)
    assert "Noi_dung" not in spec.cat          # da thay bang text feature
    assert "Noi_dung_text" in spec.text
    assert "So_the" not in spec.cat            # id the khong tong quat hoa duoc


def test_mode_withleak_co_cot_ro_ri(raw_df):
    _, spec = make_features(normalize_columns(raw_df), "withleak")
    assert set(LEAK_COLS) & set(spec.names)


def test_norm_text_bo_dau_va_ky_tu_la():
    s = pd.Series(["Rút về ngân hàng ACB ****2231", "Subscription PADDLE.NET* NOTION"])
    out = norm_text(s).tolist()
    assert out[0] == "rut ve ngan hang acb 2231"
    assert out[1] == "subscription paddle net notion"


def test_desc_flag_bat_duoc_merchant_moi(raw_df):
    d = normalize_columns(raw_df).copy()
    d.loc[0, "Noi_dung"] = "Subscription OPENAI *CHATGPT SUBSCR"   # chua tung thay
    X, _, _, _ = build_features(d, **FEATURE_MODES["robust"])
    assert X.loc[0, "desc_co_subscription"] == 1


def test_recurrence_la_causal(raw_df):
    """Dac trung lap lai chi duoc dung lich su phia truoc: cat bot duoi khong
    duoc lam doi gia tri cua cac dong con lai."""
    d = normalize_columns(raw_df).sort_values("Thoi_gian").reset_index(drop=True)
    full, _, _, _ = build_features(d, **FEATURE_MODES["robust"])
    head, _, _, _ = build_features(d.head(60), **FEATURE_MODES["robust"])
    cols = ["rec_seq", "rec_ngay_ke_tu_lan_truoc", "card_seq"]
    np.testing.assert_allclose(full[cols].head(60).values, head[cols].values,
                               rtol=1e-9, equal_nan=True)


def test_thu_tu_dong_duoc_giu_nguyen(raw_df):
    d = normalize_columns(raw_df)
    X, _, _, _ = build_features(d, **FEATURE_MODES["robust"])
    assert (X.index == d.index).all()
    np.testing.assert_allclose(X["So_tien"].values,
                               pd.to_numeric(d["So_tien"]).values)
