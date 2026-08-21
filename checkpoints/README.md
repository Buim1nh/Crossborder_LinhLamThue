# Checkpoints — ML model artifacts (inference only)

Thư mục này chứa **checkpoint đã train sẵn** để module `backend/src/modules/ml`
load lên và phục vụ inference. **Không train ở đây**, không commit file nhị phân.

Đặt ở repo root (thay vì trong source tree) vì 3 lý do:

1. Checkpoint là **dữ liệu**, không phải code — không nên nằm lẫn trong `src/`.
2. Mount được thẳng vào container như một volume read-only.
3. Deploy pipeline / script đồng bộ model chỉ cần ghi vào đúng 1 đường dẫn.

---

## Cấu trúc

```
checkpoints/
├── README.md
├── categorizer.joblib      # (bạn tự thêm) model phân loại giao dịch
├── anomaly_scorer.joblib   # (bạn tự thêm) model chấm điểm bất thường
└── archive/                # các version cũ, đặt tên kèm ngày/version
```

**Tên file phải khớp chính xác** với config, nếu không registry sẽ coi như
thiếu artifact và im lặng rơi về heuristic:

| File | Biến config | Mặc định |
|---|---|---|
| `categorizer.joblib` | `ML_CATEGORIZER_ARTIFACT` | `categorizer.joblib` |
| `anomaly_scorer.joblib` | `ML_ANOMALY_ARTIFACT` | `anomaly_scorer.joblib` |

`archive/` để giữ bản cũ (vd. `categorizer-2026-08-20-v3.joblib`) nhằm rollback
nhanh. File trong `archive/` không được load — chỉ file ở thư mục gốc mới được.

---

## Kích hoạt

Trỏ `ML_ARTIFACT_DIR` vào thư mục này rồi restart backend:

```bash
# backend/.env
ML_ARTIFACT_DIR=/home/manhnd/Crossborder_LinhLamThue/checkpoints
```

Chạy bằng Docker thì `docker-compose.yml` đã mount sẵn `./checkpoints` vào
`/app/checkpoints` (read-only) và set `ML_ARTIFACT_DIR` tương ứng — chỉ cần copy
file `.joblib` vào đây và restart container.

---

## Kiểm tra đã load được chưa

Điểm dễ sai nhất: module **có fallback heuristic**, nên checkpoint sai đường dẫn
sẽ *không* gây lỗi — API vẫn trả kết quả bình thường. Luôn xác nhận bằng:

```bash
curl -s localhost:8000/api/ml/models | jq
```

```json
[{"name": "categorizer", "loaded": true, "backend": "model",
  "artifact_path": "/app/checkpoints/categorizer.joblib", "error": null}]
```

- `"backend": "model"` → checkpoint đang chạy thật.
- `"backend": "heuristic"` → đọc field `error` để biết lý do (sai tên file, sai
  đường dẫn, thiếu `joblib`, hoặc pickle lỗi version).

Cần `pip install joblib scikit-learn` thì mới deserialize được; thiếu thư viện
cũng bị rơi về heuristic.

---

## Yêu cầu với artifact

- **Format**: `joblib.dump(...)`, load bằng `joblib.load()`.
- **Categorizer**: sklearn pipeline nhận vào **chuỗi text đã normalize**
  (preprocessor tự strip dấu tiếng Việt + xóa noise `POS`/`REF`/số đuôi trước
  khi đưa vào model), expose `predict_proba` và `classes_`. Nhãn trong
  `classes_` nên nằm trong taxonomy ở `backend/src/modules/ml/config.py`.
- **Anomaly scorer**: expose `score_samples` hoặc `decision_function`.

Pickle của sklearn **không ổn định giữa các version** — nên ghi kèm version đã
dùng để train khi lưu vào `archive/`.
