# Module 7 — ML Inference

Inference-only. **Training does not happen here.** This module loads pre-trained
artifacts and serves predictions; models are trained offline and dropped into
`artifacts/`.

Two tasks:

| Task | Question it answers |
|---|---|
| **Categorization** | "What kind of spending is this transaction?" |
| **Anomaly scoring** | "Is this transaction unusual *for this user*?" |

---

## Layout

```
backend/src/modules/ml/
├── config.py             # settings, category taxonomy, keywords, signal weights
├── schemas.py            # Pydantic request/response contracts
├── preprocessor.py       # raw transaction -> normalized FeatureVector
├── registry.py           # artifact loading + caching, never raises
├── predictors/
│   ├── categorizer.py    # model OR keyword heuristic
│   └── anomaly.py        # model OR weighted-signal heuristic
├── service.py            # orchestration, batching, history baseline
├── router.py             # FastAPI endpoints
├── artifacts/            # .joblib files (gitignored)
└── tests/test_ml.py      # 37 tests
```

Placed under `src/modules/` to mirror the existing `modules/chat/` convention:
self-contained, own config/schemas/router/tests, integrated via one line in
`api/main.py`.

---

## The core design decision: graceful degradation

**Every predictor has a heuristic fallback, and no artifact is committed.**

This means the module is fully functional on a fresh `git clone` with zero setup
and without scikit-learn installed. `predict_proba` failures, corrupt artifacts,
and missing files all degrade to the heuristic instead of raising — a broken
model must never fail a user's file upload.

The tradeoff: a silent fallback can hide a deployment mistake where your trained
artifact isn't actually being served. `GET /api/ml/models` exists specifically to
answer that — it reports the active backend and the load error, if any.

```json
[{"name": "categorizer", "loaded": false, "backend": "heuristic",
  "artifact_path": ".../artifacts/categorizer.joblib",
  "error": "artifact not found"}]
```

To activate a model, drop `categorizer.joblib` / `anomaly_scorer.joblib` into
`artifacts/` and restart. The categorizer expects an sklearn pipeline taking the
normalized text string and exposing `predict_proba` + `classes_`.

---

## Honest-uncertainty behavior

Two deliberate refusals to guess:

- **Low-confidence categories collapse to `other`** (`ML_MIN_CONFIDENCE`, default
  `0.35`). A confidently-wrong category is worse for a user than an honest
  "uncategorized". The original confidence is preserved in the response.
- **Anomaly scoring abstains below 5 historical transactions**, returning
  `insufficient_data: true` and `is_anomaly: false`. Flagging "anomalies" against
  a 2-transaction baseline is noise, not signal.

---

## Anomaly signals

The score is a weighted sum of five signals, each returned with a human-readable
`explanation` so a flag shown to a user can always say *why*:

| Signal | Weight | Meaning |
|---|---|---|
| `amount_outlier` | 0.40 | robust z-score (median/MAD) vs. the user's own history |
| `rare_merchant` | 0.20 | merchant seen rarely or never before |
| `odd_hour` | 0.15 | transacted 00:00–05:00 |
| `round_amount` | 0.10 | suspiciously round figure (≥100) |
| `rapid_repeat` | 0.15 | same merchant+amount within 24h (double-charge) |

Median/MAD is used rather than mean/stddev because a single huge outlier
corrupts a mean-based z-score — the very thing being detected. MAD of zero
(identical amounts) is explicitly guarded against division-by-zero.

---

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/ml/predict` | Batch categorize + anomaly-score |
| POST | `/api/ml/predict/one` | Single transaction |
| GET | `/api/ml/models` | Which backend is live, and why |
| GET | `/api/ml/categories` | Taxonomy, for frontend dropdowns |

`/predict` derives the anomaly baseline from the `history` field; when omitted it
falls back to the batch itself. `/predict/one` has no history, so it always
reports `insufficient_data` — use `/predict` for meaningful anomaly scores.

Output order and length always match input exactly, so callers can zip results
back onto their own rows positionally.

---

## Configuration

All keys are `ML_`-prefixed to avoid collision with app-wide and chat settings.

| Variable | Default | Purpose |
|---|---|---|
| `ML_ENABLED` | `true` | Master switch; returns `backend: "disabled"`, same response shape |
| `ML_ARTIFACT_DIR` | `<module>/artifacts` | Point at a mounted volume in prod |
| `ML_MIN_CONFIDENCE` | `0.35` | Below this, category → `other` |
| `ML_ANOMALY_THRESHOLD` | `0.65` | Score at/above which `is_anomaly` is true |
| `ML_MAX_BATCH_SIZE` | `500` | Oversized batches are truncated, not rejected |

---

## Vietnamese text handling

`preprocessor.py` strips diacritics via NFD decomposition (`"Cà Phê Trung Nguyên"`
→ `"ca phe trung nguyen"`) and explicitly maps `đ`/`Đ`, which has no combining
form and would otherwise survive normalization. Bank-statement noise (`POS`,
`REF`, trailing digits) is dropped so `"POS 12345 STARBUCKS REF 99"` → `"starbucks"`.

Because matching happens *after* diacritic stripping, Vietnamese keywords in
`CATEGORY_KEYWORDS` are stored unaccented (`"ca phe"`, `"nha hang"`).

Single-word keywords are matched space-padded so `"ck"` doesn't match inside
`"check"`; multi-word phrases score double, since `"apple music"` is decisive
where `"apple"` alone is not.

---

## Tests

```bash
cd backend && .venv/bin/python -m pytest src/modules/ml/tests/ -v
```

37 tests, all passing. They target the heuristic path deliberately — that's what
runs on a fresh checkout, so it's the behavior users actually get. The model path
is covered by asserting graceful degradation rather than by committing a binary
fixture. Edge cases covered include zero-MAD division, extreme amounts, missing
dates, and empty text.

---

## Integration

```python
from src.modules.ml import ml_router
app.include_router(ml_router, prefix="/api/ml", tags=["ML"])
```

Programmatic use:

```python
from src.modules.ml import MLService, TransactionInput

service = MLService()
result = service.predict_one(TransactionInput(description="STARBUCKS", amount=-5.4))
result.category.category  # "food_drink"
```

`src/services/anomaly_detector.py` is a pre-existing, separate rule-based
implementation and was intentionally left untouched.
