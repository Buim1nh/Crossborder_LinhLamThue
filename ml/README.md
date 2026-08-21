# Subscription Detection — CatBoost + MLOps

Phát hiện giao dịch **SUBSCRIPTION** (đăng ký định kỳ) trong sao kê, phục vụ tính năng
cảnh báo "subscription bị quên" của Wealify.

- **Thuật toán**: CatBoost (`CatBoostClassifier`, `auto_class_weights="Balanced"`)
- **Metric chính**: **MCC** (Matthews Correlation Coefficient) — ổn định với dữ liệu
  mất cân bằng và phản ánh cả 4 ô confusion matrix, khác F1 vô cảm với TN
- **Dữ liệu train**: `subscription_labels.csv` — 1.895 giao dịch, 306 SUBSCRIPTION (16,15%)

---

## 1. Kết quả — có overfit không?

**Không overfit.**

| Phép đo | MCC | Kết luận |
|---|---:|---|
| Cross-validation 5-fold (ước lượng chính) | **0.9684 ± 0.0291** | ổn định giữa các fold |
| Holdout — tập train | 1.0000 | |
| Holdout — tập test | 0.9507 | |
| **Gap overfit (train − test)** | **+0.0493** | dưới ngưỡng chặn 0.10 ✅ |

MCC từng fold: `0.9509 · 0.9902 · 0.9804 · 0.9205 · 1.0000` — độ lệch chuẩn 0.029,
không fold nào sụp. Chỉ số khác trên CV: Precision 0.9863 ± 0.0168, Recall 0.9607 ± 0.0338,
ROC-AUC 0.9963 ± 0.0035, PR-AUC 0.9884 ± 0.0115.

Holdout test (379 dòng): TP=56 · FP=0 · FN=5 · TN=318, ngưỡng quyết định **0.6400**.

Gap +0.049 là mức bình thường cho boosting trên 1.895 dòng: model fit gần hoàn hảo tập
train (MCC 1.0) nhưng test vẫn 0.95 và CV std chỉ 0.029. Nếu overfit thật thì các fold
sẽ phân tán mạnh và MCC test sẽ tụt xuống 0.6–0.8.

**Feature quan trọng nhất**: `Loai_giao_dich` 18.5 · `Noi_dung_text` 17.6 ·
`ti_le_du_tien` 9.1 · `So_tien` 7.5 · `desc_co_subscription` 5.9 · `Don_vi_tien_te` 5.7 ·
`desc_so_ky_tu` 3.8 · `rec_ngay_ke_tu_lan_truoc` 3.3.

---

## 2. Hai phát hiện quan trọng về dữ liệu

### 2.1. Cột `kind` rò rỉ nhãn

`python -m ml.cli audit` chấm mọi cột bằng luật "cột == giá trị":

| Cột | Luật tốt nhất | P | R | F1 |
|---|---|---:|---:|---:|
| `kind` | `== "receipt"` | 1.000 | 0.990 | **0.995** ← RÒ RỈ |
| `user_account` | `== "wealifytester"` | 0.779 | 0.990 | 0.872 |
| `Loại giao dịch` | `== "CARD_PAYMENT"` | 0.505 | 0.951 | 0.660 |

`kind == "receipt"` gần như trùng khớp 1-1 với nhãn. Bốn cột đối soát email
(`kind`, `from`, `subject`, `matched_txn_id`) bị loại khỏi feature set
(`pipeline/features.py: LEAK_COLS`) và pipeline tự chặn lại nếu chúng quay lại.

### 2.2. Dataset Kaggle 200k KHÔNG dùng để train được

Dataset `duckyyyrobinson/transaction2` (200.000 dòng) có nhãn sinh theo luật khác hẳn.
Đo thực tế:

| Công thức train | MCC trên golden |
|---|---:|
| Train trên golden (5-fold CV) | **0.9684** |
| Train trên 200k + 4/5 golden | 0.7158 ± 0.0825 |
| Train **chỉ** trên 200k, chấm golden | **0.0000** (TP=0, FN=306) |

Model train trên 200k không bắt được **một** giao dịch subscription nào trong golden vì:
- 78,5% dòng golden mang giá trị `Nội dung chuyển khoản` chưa từng thấy — tập 200k chỉ có
  đúng 2 chuỗi subscription (`Subscription Spotify`, `Subscription NETFLIX`), golden có 12
  merchant thật (`Subscription PADDLE.NET* NOTION`, `ADOBE *CREATIVE CLD`, `OPENAI *CHATGPT
  SUBSCR`, …);
- 41% dòng SUBSCRIPTION trong golden thậm chí **không có** chữ "Subscription" trong mô tả
  (`Grab`, `Shopee`, `Apple`, `Facebook Ads`) — phải nhận ra bằng tính lặp lại;
- tỷ lệ dương tính lệch 12 lần (1,29% vs 16,15%) nên ngưỡng cũng không chuyển được.

Đây **không phải overfit** (train MCC ≈ test MCC trên chính tập 200k) mà là **dataset
shift**. Vì vậy `config.yaml` để 200k ở mục `data.reference` — chỉ dùng để audit và đo
drift, không train. Kiểm chứng lại bất cứ lúc nào:

```bash
.venv/bin/python -m ml.cli drift --data data/raw/synthetic_200k_labels.csv
```

---

## 3. Cấu trúc

```
ml/
├── config.yaml              # nguồn sự thật duy nhất: data, feature, model, gates
├── cli.py                   # audit | train | evaluate | predict | promote | versions | drift | info
├── Makefile                 # shortcut cho các lệnh trên
├── Dockerfile               # image chạy pipeline
├── requirements.txt
├── pipeline/
│   ├── config.py            # đọc & validate config
│   ├── data.py              # nạp, kiểm tra schema, chia tập / CV fold
│   ├── features.py          # feature engineering, dùng chung train + serve
│   ├── audit.py             # audit rò rỉ nhãn + đo drift
│   ├── modeling.py          # FeatureSpec, dựng Pool/model CatBoost
│   ├── evaluate.py          # metric (MCC), chọn ngưỡng, cổng chất lượng
│   ├── train.py             # orchestration: audit → CV → holdout → refit
│   ├── registry.py          # registry có version + model card + con trỏ current
│   └── serve.py             # SubscriptionDetector cho backend
├── registry/                # ĐƯỢC COMMIT — API chạy được ngay từ bản clone
│   ├── current.json
│   └── v20260821T191514Z/
│       ├── model.cbm  feature_spec.json  metrics.json  manifest.json  MODEL_CARD.md
└── tests/                   # 36 unit + integration test
```

Backend:
- `backend/src/services/subscription_model.py` — nạp model (lazy, cache)
- `backend/src/api/subscriptions.py` — `GET /api/subscriptions/model`, `POST /api/subscriptions/score`
- `backend/tests/test_subscriptions_api.py`

CI: `.github/workflows/ml-ci.yml` — chạy test → audit rò rỉ → train → **chặn merge nếu
truợt cổng chất lượng**.

---

## 4. Vòng đời MLOps

```
config.yaml
    │
    ▼
audit ──► phát hiện cột rò rỉ, loại khỏi feature set
    │
    ▼
train ──► 5-fold CV (ước lượng chính)
    │     holdout (đo gap overfit)
    │     refit toàn bộ dữ liệu, iterations & ngưỡng lấy từ CV
    ▼
cổng chất lượng ──► trượt thì exit code 1, CI fail, không promote được
    │
    ▼
registry/<version>/ ──► model.cbm + metrics + manifest (hash dữ liệu, git sha,
    │                    version thư viện) + MODEL_CARD.md
    ▼
promote ──► registry/current.json
    │
    ▼
serve ──► SubscriptionDetector → FastAPI
    │
    ▼
drift / evaluate ──► phát hiện lệch phân phối → quay lại train
```

### Cổng chất lượng (`config.yaml: gates`)

| Tiêu chí | Ngưỡng | Giá trị hiện tại |
|---|---:|---:|
| `min_mcc` (CV mean) | ≥ 0.90 | 0.9684 ✅ |
| `min_precision` (CV mean) | ≥ 0.85 | 0.9863 ✅ |
| `min_recall` (CV mean) | ≥ 0.85 | 0.9607 ✅ |
| `max_cv_std` | ≤ 0.05 | 0.0291 ✅ |
| `max_train_test_mcc_gap` | ≤ 0.10 | 0.0493 ✅ |

`train` trả exit code 1 khi trượt; `promote` từ chối trừ khi có `--force`.

---

## 5. Cách chạy

```bash
make -f ml/Makefile setup
```

```bash
make -f ml/Makefile test audit train-promote
```

Hoặc gọi trực tiếp:

```bash
.venv/bin/python -m ml.cli train --promote
```

| Lệnh | Việc |
|---|---|
| `audit` | chấm rò rỉ nhãn từng cột |
| `train [--promote]` | CV + holdout + refit + đóng gói vào registry, chạy cổng chất lượng |
| `evaluate --data f.csv` | chấm model `current` trên dữ liệu có nhãn, cảnh báo nếu MCC tụt |
| `predict --input f.csv` | xuất `subscription_proba` + `is_subscription` ra CSV |
| `drift --data f.csv` | % dòng mang giá trị categorical chưa từng thấy + phân bố xác suất |
| `promote [--version v]` | đặt phiên bản làm `current` (chặn nếu trượt cổng) |
| `versions` | liệt kê registry |
| `info` | metadata model đang serve |

Docker:

```bash
docker compose run --rm ml train --promote
```

---

## 6. Dùng trong code

```python
from ml.pipeline.serve import SubscriptionDetector

det = SubscriptionDetector()              # nạp phiên bản `current`
out = det.predict(df)                     # df dùng tên cột GỐC, có dấu hay không đều được
out[["subscription_proba", "is_subscription", "model_version"]]
```

REST:

```bash
curl -s localhost:8000/api/subscriptions/model
```

```bash
curl -s -X POST localhost:8000/api/subscriptions/score -H 'Content-Type: application/json' -d '{"transactions":[{"Số thẻ":"****0101","Loại giao dịch":"CARD_PAYMENT","Trạng thái":"SUCCESS","Số tiền":15.88,"Đơn vị tiền tệ":"USD","Số dư":96.33,"Phí":0,"Tỷ giá":1,"Nội dung chuyển khoản":"Subscription NETFLIX.COM","Thời gian":"2026-08-21 04:51:00"}]}'
```

Trả `503` khi chưa có model nào được promote, `422` khi thiếu cột bắt buộc.

---

## 7. Feature

| Nhóm | Feature |
|---|---|
| Số tiền | `So_tien`, `So_du`, `Phi`, `Ty_gia`, `log_so_tien`, `ti_le_du_tien`, `phi_tren_tien` |
| Thời gian | `gio`, `ngay_trong_tuan`, `ngay_trong_thang`, `thang`, `is_dem`, `is_cuoi_tuan` |
| Lặp lại (causal) | `rec_seq`, `rec_ngay_ke_tu_lan_truoc`, `rec_lech_chu_ky_thang`, `rec_ti_le_tien_vs_lan_truoc`, `rec_ti_le_tien_vs_trung_binh` |
| Theo thẻ (causal) | `card_seq`, `card_lech_tien` |
| Mô tả | `Noi_dung_text` (CatBoost `text_features`), `desc_co_subscription`, `desc_co_chu_ky`, `desc_so_tu`, `desc_so_ky_tu` |
| Categorical | `Loai_giao_dich`, `Trang_thai`, `Don_vi_tien_te` |

Nhóm "lặp lại" và "theo thẻ" chỉ dùng lịch sử **phía trước** theo thời gian
(`groupby().shift()`, `expanding()`) nên không rò rỉ tương lai — có test kiểm chứng
(`tests/test_features.py::test_recurrence_la_causal`).

**Mô tả giao dịch đi qua `text_features` chứ không phải categorical nguyên chuỗi.**
Đây là điểm then chốt: dùng categorical thì merchant mới rơi vào giá trị chưa từng thấy và
model câm; dùng text thì `Subscription OPENAI *CHATGPT SUBSCR` vẫn chia sẻ token
`subscription` với dữ liệu train. Bốn feature mode có sẵn trong `config.yaml`:
`robust` (deploy) · `categorical` · `nodesc` · `withleak` (chỉ để kiểm chứng rò rỉ).

Tên cột đầu vào được chuẩn hoá tự động (bỏ BOM, bỏ dấu tiếng Việt) nên
`Số thẻ` / `So the` / `SỐ THẺ` đều nhận.

---

## 8. Giới hạn đã biết

1. **1.895 dòng là ít.** CV 5-fold cho ± 0.029 nên con số đáng tin, nhưng mỗi fold test chỉ
   ~61 dòng dương tính. Có thêm dữ liệu thật thì train lại.
2. **Ngưỡng 0.6400 gắn với tỷ lệ dương tính 16,15%.** Dữ liệu production lệch nhiều khỏi
   mức này thì phải chọn lại ngưỡng — `evaluate` sẽ cảnh báo, `drift` chỉ ra cột nào lệch.
3. **Merchant hoàn toàn mới, không có token quen thuộc nào** thì model dựa vào tính lặp lại
   và số tiền, độ tin cậy giảm.
4. Dataset Kaggle 200k chỉ dùng để audit/drift — xem mục 2.2.
