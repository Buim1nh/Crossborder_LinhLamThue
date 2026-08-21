import pandas as pd
import pytest

from ml.pipeline.data import SchemaError, validate_schema
from ml.pipeline.features import add_target, normalize_columns


def test_normalize_columns_bo_dau_va_bom(raw_df):
    df = raw_df.rename(columns={"Id": "﻿Id"})
    out = normalize_columns(df)
    for c in ["Id", "So_the", "Loai_giao_dich", "So_tien", "Don_vi_tien_te",
              "Noi_dung", "Thoi_gian", "email_kind"]:
        assert c in out.columns, c


def test_normalize_columns_chap_nhan_ten_khong_dau(raw_df):
    df = raw_df.rename(columns={"Số thẻ": "So the", "Loại giao dịch": "Loai giao dich"})
    out = normalize_columns(df)
    assert "So_the" in out.columns and "Loai_giao_dich" in out.columns


def test_validate_schema_pass(raw_df):
    warnings = validate_schema(normalize_columns(raw_df))
    assert isinstance(warnings, list)


def test_validate_schema_thieu_cot(raw_df):
    df = normalize_columns(raw_df).drop(columns=["So_tien"])
    with pytest.raises(SchemaError, match="So_tien"):
        validate_schema(df)


def test_validate_schema_thieu_nhan(raw_df):
    df = normalize_columns(raw_df).drop(columns=["label"])
    with pytest.raises(SchemaError, match="label"):
        validate_schema(df, require_label=True)
    validate_schema(df, require_label=False)      # khong nhan thi van OK


def test_validate_schema_bang_rong(raw_df):
    with pytest.raises(SchemaError):
        validate_schema(normalize_columns(raw_df).head(0))


def test_add_target(raw_df):
    d = add_target(normalize_columns(raw_df))
    assert d["y"].sum() == (raw_df["label"] == "SUBSCRIPTION").sum()
    assert set(d["y"].unique()) <= {0, 1}
