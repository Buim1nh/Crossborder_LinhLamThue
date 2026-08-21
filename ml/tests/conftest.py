import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Bang giao dich nho, dung ten cot GOC co dau nhu file that."""
    n = 120
    rng = np.random.default_rng(0)
    is_sub = np.arange(n) % 4 == 0
    desc = np.where(is_sub, "Subscription NETFLIX.COM", "Rút về ngân hàng ACB")
    return pd.DataFrame({
        "Id": [f"TW{i:06d}" for i in range(n)],
        "Số thẻ": rng.choice(["****0101", "****0102"], n),
        "Loại giao dịch": np.where(is_sub, "CARD_PAYMENT", "WALLET_WITHDRAW"),
        "Trạng thái": rng.choice(["SUCCESS", "PENDING"], n),
        "Số tiền": rng.uniform(5, 500, n).round(2),
        "Đơn vị tiền tệ": rng.choice(["USD", "VND"], n),
        "Số dư": rng.uniform(0, 2000, n).round(2),
        "Phí": 0.0,
        "Tỷ giá": 1.0,
        "Nội dung chuyển khoản": desc,
        "Thời gian": pd.date_range("2026-01-01", periods=n, freq="6h").astype(str),
        "Lý do từ chối": None,
        "matched_txn_id": None,
        "from": np.where(is_sub, "receipts@netflix.com", None),
        "subject": np.where(is_sub, "Your receipt", None),
        "kind": np.where(is_sub, "receipt", None),
        "user_account": "tester",
        "label": np.where(is_sub, "SUBSCRIPTION", "OTHER"),
    })
