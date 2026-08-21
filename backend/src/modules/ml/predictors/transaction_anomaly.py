"""
MODULE 7 - Transaction Anomaly Detector Predictor.

Loads the trained TransactionAnomalyDetector model from checkpoints and
provides inference for the Vietnamese transaction dataset.

Model format: IsolationForest with pre-trained scaler, encoders, and feature weights.
Checkpoint location: checkpoints/archive/TransactionAnomalyDetector/
"""
import json
import logging
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

from src.modules.ml.config import MLSettings, get_ml_settings
from src.modules.ml.registry import get_registry

logger = logging.getLogger(__name__)


class TransactionAnomalyDetector:
    """
    Anomaly Detection Pipeline cho Wealify.
    Load model đã train và predict cho transaction mới.
    """

    def __init__(self, model_path: str):
        """Load tất cả model components từ checkpoint."""
        self.model_path = Path(model_path)

        # Load model files
        self.model = joblib.load(self.model_path / "isolation_forest_model.pkl")
        self.scaler = joblib.load(self.model_path / "scaler.pkl")
        self.encoders = joblib.load(self.model_path / "encoders.pkl")

        # Load config
        with open(self.model_path / "feature_columns.json", "r") as f:
            self.feature_cols = json.load(f)
        with open(self.model_path / "feature_weights.json", "r") as f:
            self.weights = np.array(list(json.load(f).values()))
        with open(self.model_path / "model_config.json", "r") as f:
            self.config = json.load(f)

        logger.info(
            "TransactionAnomalyDetector loaded: version=%s, features=%d",
            self.config.get("version", "1.0.0"),
            len(self.feature_cols),
        )

    def safe_transform(self, encoder, series):
        """Mã hóa an toàn cho dữ liệu mới chứa nhãn chưa từng xuất hiện."""
        mapping = {cls: i for i, cls in enumerate(encoder.classes_)}
        return series.map(mapping).fillna(-1).astype(int)

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Feature Engineering cho transaction data."""
        df = df.copy()

        # Map tên cột (hỗ trợ cả có dấu & không dấu)
        col_map = {
            "Số tiền": "So_tien",
            "Số thẻ": "So_the",
            "Thời gian": "Thoi_gian",
            "Loại giao dịch": "Loai_giao_dich",
            "Nội dung chuyển khoản": "Noi_dung_chuyen_khoan",
            "Số dư": "So_du",
            "Phí": "Phi",
            "Tỷ giá": "Ty_gia",
        }
        for old_col, new_col in col_map.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
            elif new_col in df.columns and old_col not in df.columns:
                df[old_col] = df[new_col]

        # Time features
        if "Thoi_gian" in df.columns:
            df["Thoi_gian_dt"] = pd.to_datetime(df["Thoi_gian"])
            df["gio"] = df["Thoi_gian_dt"].dt.hour
            df["ngay_trong_tuan"] = df["Thoi_gian_dt"].dt.dayofweek
            df["ngay_trong_thang"] = df["Thoi_gian_dt"].dt.day
            df["thang"] = df["Thoi_gian_dt"].dt.month

        # Aggregate features
        id_col = "Id" if "Id" in df.columns else ("id" if "id" in df.columns else "So_tien")
        if "So_the" in df.columns and "Thoi_gian_dt" in df.columns:
            df["tan_suat_the"] = df.groupby(
                ["So_the", df["Thoi_gian_dt"].dt.date], dropna=False
            )[id_col].transform("count")
        if "So_the" in df.columns and "So_tien" in df.columns:
            df["tb_tien_the"] = df.groupby("So_the")["So_tien"].transform("mean")
            df["do_lech_tien"] = abs(df["So_tien"] - df["tb_tien_the"]) / (
                df["tb_tien_the"] + 1
            )
        if "So_du" in df.columns and "So_tien" in df.columns:
            df["ti_le_du_tien"] = df["So_du"] / (df["So_tien"] + 1)

        # Encode categorical
        if "Loai_giao_dich" in df.columns and "loai" in self.encoders:
            df["loai_encoded"] = self.safe_transform(
                self.encoders["loai"], df["Loai_giao_dich"]
            )
        if "Noi_dung_chuyen_khoan" in df.columns and "ck" in self.encoders:
            df["ck_encoded"] = self.safe_transform(
                self.encoders["ck"],
                df["Noi_dung_chuyen_khoan"].fillna("-").astype(str),
            )

        # Bù đắp các feature còn thiếu
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0.0

        return df

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict anomaly cho transactions."""
        df = self._preprocess(df)

        # Extract features & scale
        X = df[self.feature_cols].fillna(0).values.astype(np.float32)
        X_scaled = self.scaler.transform(X)
        X_weighted = X_scaled * self.weights.reshape(1, -1)

        # Lấy điểm gốc (càng âm càng nguy hiểm)
        df["anomaly_score"] = self.model.decision_function(X_weighted)

        # Gán Outlier: Điểm âm là Outlier (-1), dương là Normal (1)
        df["outlier"] = np.where(df["anomaly_score"] < 0, -1, 1)

        # Phân mức Risk Tier
        conditions = [
            df["anomaly_score"] < -0.05,  # CRITICAL
            df["anomaly_score"] < 0.00,  # HIGH
            df["anomaly_score"] < 0.03,  # MEDIUM
            df["anomaly_score"] < 0.08,  # LOW
        ]
        choices = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        df["risk_tier"] = np.select(conditions, choices, default="NORMAL")

        return df

    def get_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Lấy danh sách các giao dịch thực sự là Anomaly."""
        return df[df["outlier"] == -1].copy()

    def get_summary(self, df: pd.DataFrame) -> dict:
        """Lấy tóm tắt kết quả."""
        total = len(df)
        anomalies = (df["outlier"] == -1).sum()
        tier_counts = df["risk_tier"].value_counts().to_dict()

        return {
            "total_transactions": int(total),
            "anomalies_detected": int(anomalies),
            "anomaly_rate": f"{anomalies / total * 100:.2f}%",
            "tier_distribution": tier_counts,
        }


class TransactionAnomalyPredictor:
    """
    Wrapper predictor that uses TransactionAnomalyDetector model.

    Integrates with the ML module's registry pattern for consistent loading.
    """

    name = "transaction_anomaly"

    def __init__(self, settings: Optional[MLSettings] = None):
        self.settings = settings or get_ml_settings()
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the TransactionAnomalyDetector model."""
        checkpoint_path = Path(self.settings.ML_TRANSACTION_ANOMALY_PATH)

        if not checkpoint_path.exists():
            logger.warning(
                "TransactionAnomalyDetector checkpoint not found at %s",
                checkpoint_path,
            )
            return

        try:
            self._model = TransactionAnomalyDetector(str(checkpoint_path))
            logger.info(
                "TransactionAnomalyDetector model loaded from %s",
                checkpoint_path,
            )
        except Exception as exc:
            logger.error(
                "Failed to load TransactionAnomalyDetector: %s", exc
            )
            self._model = None

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def predict(self, transactions: list[dict]) -> dict[str, Any]:
        """
        Run anomaly detection on a batch of transactions.

        Args:
            transactions: List of transaction dicts with keys like
                         'So_tien', 'So_the', 'Thoi_gian', 'Loai_giao_dich', etc.

        Returns:
            Dict with 'results' (DataFrame-like), 'summary', and 'anomalies'.
        """
        if not self._model:
            return {"error": "Model not loaded", "results": [], "summary": {}}

        df = pd.DataFrame(transactions)

        if df.empty:
            return {"results": [], "summary": {}, "anomalies": []}

        results = self._model.predict(df)
        summary = self._model.get_summary(results)
        anomalies = self._model.get_anomalies(results)

        return {
            "results": results.to_dict("records"),
            "summary": summary,
            "anomalies": anomalies.to_dict("records") if not anomalies.empty else [],
            "model_version": self._model.config.get("version", "unknown"),
        }

    def info(self) -> dict[str, Any]:
        """Return model info for health checks."""
        return {
            "name": self.name,
            "loaded": self.loaded,
            "path": str(self.settings.ML_TRANSACTION_ANOMALY_PATH),
            "version": self._model.config.get("version", "unknown") if self._model else None,
        }
