# Model Card — wealify-subscription-detector

**Phien ban**: `v20260821T191514Z`

## Muc dich
Phan loai nhi phan: mot giao dich co phai khoan **SUBSCRIPTION** (dang ky dinh ky)
hay khong, phuc vu tinh nang canh bao "subscription bi quen" cua Wealify.

## Du lieu
- Tap huan luyen: `subscription_labels.csv` — 1,895 giao dich,
  ty le duong tinh **16.15%**
- Cot bi loai vi **ro ri nhan**: email_kind

## Thuat toan
CatBoost (`CatBoostClassifier`), feature mode = `robust`,
`auto_class_weights = Balanced`,
nguong chon theo `max_mcc` tren tap valid.

## Ket qua

### Cross-validation 5-fold (uoc luong chinh)
| Metric | Mean | Std |
|---|---:|---:|
| **MCC** | **0.9684** | 0.0291 |
| Precision | 0.9863 | 0.0168 |
| Recall | 0.9607 | 0.0338 |
| F1 | 0.9732 | 0.0247 |
| ROC-AUC | 0.9963 | 0.0035 |

### Holdout
| Tap | MCC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| train | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| test | 0.9507 | 1.0000 | 0.9180 | 0.9573 |

Gap overfit (MCC train − test) = **+0.0493**

Nguong quyet dinh da chot: **0.6400**

CONG CHAT LUONG: DAT ✅
------------------------------------------------------------
Tat ca tieu chi deu dat:
  • min_mcc = 0.9
  • min_precision = 0.85
  • min_recall = 0.85
  • max_train_test_mcc_gap = 0.1
  • max_cv_std = 0.05

## Feature quan trong nhat
| Feature | Importance |
|---|---:|
| Loai_giao_dich | 18.49 |
| Noi_dung_text | 17.61 |
| ti_le_du_tien | 9.07 |
| So_tien | 7.48 |
| desc_co_subscription | 5.90 |
| Don_vi_tien_te | 5.66 |
| desc_so_ky_tu | 3.81 |
| rec_ngay_ke_tu_lan_truoc | 3.33 |
| gio | 3.21 |
| rec_lech_chu_ky_thang | 3.12 |
| card_lech_tien | 2.92 |
| log_so_tien | 2.89 |
| ngay_trong_tuan | 2.59 |
| desc_so_tu | 2.37 |
| So_du | 2.11 |

## Gioi han da biet
- Model hoc chu yeu tu **mo ta giao dich** va **tinh lap lai**. Voi merchant hoan
  toan moi va khong co tu khoa nao quen thuoc, do tin cay giam.
- Nguong duoc chon tren phan phoi co ty le duong tinh ~16.1%.
  Neu du lieu production lech nhieu khoi ty le nay, phai chon lai nguong
  (`python -m ml.cli evaluate --data <file moi>`).
- **Khong** dung cac cot doi soat email (`kind`, `from`, `subject`,
  `matched_txn_id`) — chung ro ri nhan.

## Cach dung
```python
from ml.pipeline.serve import SubscriptionDetector
det = SubscriptionDetector()          # nap phien ban `current`
out = det.predict(df_giao_dich)
```
