import numpy as np
import pytest

from ml.pipeline.evaluate import (binary_metrics, check_gates, pick_threshold)

GATES = dict(min_mcc=0.90, min_precision=0.85, min_recall=0.85,
             max_train_test_mcc_gap=0.10, max_cv_std=0.05)


def test_binary_metrics_du_doan_hoan_hao():
    y = np.array([0, 0, 1, 1])
    m = binary_metrics(y, np.array([0.1, 0.2, 0.9, 0.8]), 0.5)
    assert m["mcc"] == 1.0 and m["precision"] == 1.0 and m["recall"] == 1.0
    assert m["confusion_matrix"] == {"tn": 2, "fp": 0, "fn": 0, "tp": 2}


def test_binary_metrics_du_doan_nguoc():
    y = np.array([0, 0, 1, 1])
    m = binary_metrics(y, np.array([0.9, 0.8, 0.1, 0.2]), 0.5)
    assert m["mcc"] == -1.0


def test_mcc_phat_hien_du_doan_toan_am_con_f1_thi_khong():
    """Voi du lieu mat can bang, doan tat ca la 0 cho MCC = 0 — day la ly do
    dung MCC lam metric chinh."""
    y = np.array([0] * 95 + [1] * 5)
    m = binary_metrics(y, np.zeros(100), 0.5)
    assert m["mcc"] == 0.0


def test_pick_threshold_fixed():
    assert pick_threshold([0, 1], [0.1, 0.9], "fixed", 0.42) == 0.42
    with pytest.raises(ValueError):
        pick_threshold([0, 1], [0.1, 0.9], "fixed", None)


def test_pick_threshold_max_mcc_tach_duoc_hai_nhom():
    rng = np.random.default_rng(0)
    y = np.array([0] * 80 + [1] * 20)
    p = np.concatenate([rng.uniform(0, 0.3, 80), rng.uniform(0.7, 1.0, 20)])
    thr = pick_threshold(y, p, "max_mcc")
    assert 0.3 <= thr <= 0.75
    assert binary_metrics(y, p, thr)["mcc"] == 1.0


def test_pick_threshold_mot_lop_thi_tra_ve_mac_dinh():
    assert pick_threshold(np.zeros(10), np.linspace(0, 1, 10), "max_mcc") == 0.5


def _summary(mcc=0.95, std=0.02, prec=0.95, rec=0.95, gap=0.02):
    return {"cv": {"mcc_mean": mcc, "mcc_std": std, "precision_mean": prec,
                   "recall_mean": rec}, "train_test_mcc_gap": gap}


def test_gates_dat():
    ok, fails = check_gates(_summary(), GATES)
    assert ok and fails == []


@pytest.mark.parametrize("kwargs,tu_khoa", [
    (dict(mcc=0.80), "MCC"),
    (dict(prec=0.50), "Precision"),
    (dict(rec=0.50), "Recall"),
    (dict(std=0.20), "Do lech CV"),
    (dict(gap=0.35), "Gap overfit"),
])
def test_gates_truot(kwargs, tu_khoa):
    ok, fails = check_gates(_summary(**kwargs), GATES)
    assert not ok
    assert any(tu_khoa in f for f in fails)


def test_gate_thieu_so_lieu_thi_truot():
    ok, fails = check_gates({"cv": {}}, GATES)
    assert not ok and len(fails) >= 4
