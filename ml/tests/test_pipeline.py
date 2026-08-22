"""Test tich hop: train -> dong goi -> promote -> serve, tren du lieu nho."""
import json

import pandas as pd
import pytest
import yaml

from ml.pipeline import registry
from ml.pipeline.config import Config, load_config
from ml.pipeline.serve import SubscriptionDetector
from ml.pipeline.train import run_training


@pytest.fixture
def cfg(tmp_path, raw_df) -> Config:
    csv = tmp_path / "mini.csv"
    raw_df.to_csv(csv, index=False)
    base = yaml.safe_load((load_config().path).read_text(encoding="utf-8"))
    base["data"]["train"] = str(csv)
    base["split"]["cv_folds"] = 3
    base["model"] = {**base["model"], "iterations": 60, "od_wait": 20}
    base["registry"]["dir"] = str(tmp_path / "registry")
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(base), encoding="utf-8")
    return load_config(p)


def test_config_thieu_section(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.safe_dump({"project": "x"}), encoding="utf-8")
    with pytest.raises(ValueError, match="thieu section"):
        load_config(p)


def test_config_mode_khong_hop_le(tmp_path, cfg):
    raw = dict(cfg.raw)
    raw["features"] = {"mode": "khong-ton-tai"}
    p = tmp_path / "bad2.yaml"
    p.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="features.mode"):
        load_config(p)


def test_train_va_serve_round_trip(cfg):
    res = run_training(cfg, log=lambda *a, **k: None)
    m = res["metrics"]
    assert 0.0 <= m["cv"]["mcc_mean"] <= 1.0
    assert m["cv"]["n_folds"] == 3
    assert "train_test_mcc_gap" in m
    assert res["manifest"]["feature_mode"] == "robust"
    # cot ro ri phai bi phat hien
    assert "email_kind" in res["manifest"]["leaking_columns"]

    version = registry.new_version()
    registry.save_version(cfg.registry_dir, version, res["model"],
                          res["spec"].to_dict(), m, res["manifest"], "# card")
    assert registry.get_current(cfg.registry_dir) is None
    registry.promote(cfg.registry_dir, version)
    assert registry.get_current(cfg.registry_dir) == version
    assert registry.list_versions(cfg.registry_dir) == [version]

    det = SubscriptionDetector(config=cfg)
    assert det.version == version and det.is_current

    df = pd.read_csv(cfg.train_path)
    out = det.predict(df)
    assert len(out) == len(df)
    assert out["subscription_proba"].between(0, 1).all()
    assert set(out["is_subscription"].unique()) <= {0, 1}
    assert (out["model_version"] == version).all()


def test_serve_khi_registry_rong(cfg):
    with pytest.raises(FileNotFoundError, match="promote"):
        SubscriptionDetector(config=cfg)


def test_predict_khong_can_cot_nhan(cfg):
    res = run_training(cfg, log=lambda *a, **k: None)
    version = registry.new_version()
    registry.save_version(cfg.registry_dir, version, res["model"],
                          res["spec"].to_dict(), res["metrics"],
                          res["manifest"], "# card")
    registry.promote(cfg.registry_dir, version)
    det = SubscriptionDetector(config=cfg)
    df = pd.read_csv(cfg.train_path).drop(columns=["label", "kind", "from", "subject"])
    out = det.predict(df)
    assert "subscription_proba" in out.columns


def test_model_card_va_manifest_duoc_ghi(cfg):
    res = run_training(cfg, log=lambda *a, **k: None)
    v = registry.new_version()
    d = registry.save_version(cfg.registry_dir, v, res["model"],
                              res["spec"].to_dict(), res["metrics"],
                              res["manifest"], "# Model Card")
    for f in ["model.cbm", "feature_spec.json", "metrics.json",
              "manifest.json", "MODEL_CARD.md"]:
        assert (d / f).exists(), f
    mf = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    assert mf["version"] == v
    assert "catboost" in mf["environment"]
    assert mf["train_file_sha256_16"]
