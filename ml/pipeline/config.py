"""Doc & kiem tra file cau hinh pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"


@dataclass
class Config:
    raw: dict[str, Any]
    path: Path

    # ── truy cap tien loi ──────────────────────────────────────────────
    @property
    def project(self) -> str:
        return self.raw["project"]

    @property
    def target_column(self) -> str:
        return self.raw["target"]["column"]

    @property
    def positive_class(self) -> str:
        return self.raw["target"]["positive_class"]

    @property
    def train_path(self) -> str:
        return self.raw["data"]["train"]

    @property
    def reference_path(self) -> str | None:
        return self.raw["data"].get("reference")

    @property
    def feature_mode(self) -> str:
        return self.raw["features"]["mode"]

    @property
    def split(self) -> dict:
        return self.raw["split"]

    @property
    def model_params(self) -> dict:
        return dict(self.raw["model"])

    @property
    def threshold_cfg(self) -> dict:
        return self.raw["threshold"]

    @property
    def gates(self) -> dict:
        return self.raw["gates"]

    @property
    def registry_dir(self) -> Path:
        return Path(self.raw["registry"]["dir"])

    def to_dict(self) -> dict:
        return self.raw


REQUIRED_SECTIONS = ["project", "target", "data", "features", "split",
                     "model", "threshold", "gates", "registry"]


def load_config(path: str | Path | None = None) -> Config:
    p = Path(path or DEFAULT_CONFIG)
    if not p.exists():
        raise FileNotFoundError(f"Khong tim thay config: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    missing = [s for s in REQUIRED_SECTIONS if s not in raw]
    if missing:
        raise ValueError(f"config thieu section: {missing}")
    if raw["features"]["mode"] not in ("robust", "categorical", "nodesc", "withleak"):
        raise ValueError(f"features.mode khong hop le: {raw['features']['mode']}")
    if raw["threshold"]["strategy"] not in ("max_mcc", "max_f1", "fixed"):
        raise ValueError(f"threshold.strategy khong hop le: {raw['threshold']['strategy']}")
    if raw["threshold"]["strategy"] == "fixed" and raw["threshold"].get("value") is None:
        raise ValueError("threshold.strategy = fixed nhung threshold.value = null")
    return Config(raw=raw, path=p)
