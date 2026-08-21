"""Model registry: luu artifact co phien ban, model card, va con tro `current`.

    ml/registry/
    ├── current.json                 # {"version": "..."} — phien ban dang serve
    └── v20260822T021500Z/
        ├── model.cbm
        ├── feature_spec.json
        ├── metrics.json
        ├── manifest.json            # hash du lieu, git sha, tham so, moi truong
        └── MODEL_CARD.md
"""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CURRENT_FILE = "current.json"


def new_version() -> str:
    return datetime.now(timezone.utc).strftime("v%Y%m%dT%H%M%SZ")


def _git_sha() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


def environment() -> dict:
    import catboost
    import numpy
    import pandas
    import sklearn
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "catboost": catboost.__version__,
        "pandas": pandas.__version__,
        "numpy": numpy.__version__,
        "scikit_learn": sklearn.__version__,
    }


def save_version(registry_dir: Path, version: str, model, feature_spec: dict,
                 metrics: dict, manifest: dict, model_card: str) -> Path:
    d = Path(registry_dir) / version
    d.mkdir(parents=True, exist_ok=True)
    model.save_model(str(d / "model.cbm"))
    (d / "feature_spec.json").write_text(json.dumps(feature_spec, indent=2, ensure_ascii=False))
    (d / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    manifest = {**manifest, "version": version, "git_sha": _git_sha(),
                "environment": environment(),
                "created_at": datetime.now(timezone.utc).isoformat()}
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    (d / "MODEL_CARD.md").write_text(model_card)
    return d


def list_versions(registry_dir: Path) -> list[str]:
    d = Path(registry_dir)
    if not d.exists():
        return []
    return sorted(p.name for p in d.iterdir()
                  if p.is_dir() and (p / "model.cbm").exists())


def get_current(registry_dir: Path) -> str | None:
    f = Path(registry_dir) / CURRENT_FILE
    if not f.exists():
        return None
    return json.loads(f.read_text()).get("version")


def promote(registry_dir: Path, version: str) -> None:
    d = Path(registry_dir) / version
    if not (d / "model.cbm").exists():
        raise FileNotFoundError(f"Phien ban khong ton tai: {d}")
    (Path(registry_dir) / CURRENT_FILE).write_text(json.dumps(
        {"version": version,
         "promoted_at": datetime.now(timezone.utc).isoformat()}, indent=2))


def resolve(registry_dir: Path, version: str | None = None) -> Path:
    """Tra ve thu muc cua phien ban chi dinh, mac dinh la `current`."""
    v = version or get_current(registry_dir)
    if v is None:
        raise FileNotFoundError(
            f"Chua co phien ban nao duoc promote trong {registry_dir}. "
            f"Chay: python -m ml.cli train && python -m ml.cli promote")
    d = Path(registry_dir) / v
    if not d.exists():
        raise FileNotFoundError(f"Khong tim thay phien ban {v} trong {registry_dir}")
    return d


def render_model_card(*, project: str, version: str, config: dict, metrics: dict,
                      leakage: dict, importance: list[dict], n_rows: int,
                      positive_rate: float, gate_report: str) -> str:
    cv = metrics.get("cv", {})
    ho = metrics.get("holdout", {})
    leaks = [c for c, r in leakage.items() if r.get("leak")]
    imp_lines = "\n".join(f"| {i['feature']} | {i['importance']:.2f} |"
                          for i in importance[:15])
    return f"""# Model Card — {project}

**Phien ban**: `{version}`

## Muc dich
Phan loai nhi phan: mot giao dich co phai khoan **SUBSCRIPTION** (dang ky dinh ky)
hay khong, phuc vu tinh nang canh bao "subscription bi quen" cua Wealify.

## Du lieu
- Tap huan luyen: `{config['data']['train']}` — {n_rows:,} giao dich,
  ty le duong tinh **{positive_rate*100:.2f}%**
- Cot bi loai vi **ro ri nhan**: {', '.join(leaks) if leaks else 'khong phat hien'}

## Thuat toan
CatBoost (`CatBoostClassifier`), feature mode = `{config['features']['mode']}`,
`auto_class_weights = {config['model'].get('auto_class_weights')}`,
nguong chon theo `{config['threshold']['strategy']}` tren tap valid.

## Ket qua

### Cross-validation {cv.get('n_folds', '?')}-fold (uoc luong chinh)
| Metric | Mean | Std |
|---|---:|---:|
| **MCC** | **{cv.get('mcc_mean', float('nan')):.4f}** | {cv.get('mcc_std', float('nan')):.4f} |
| Precision | {cv.get('precision_mean', float('nan')):.4f} | {cv.get('precision_std', float('nan')):.4f} |
| Recall | {cv.get('recall_mean', float('nan')):.4f} | {cv.get('recall_std', float('nan')):.4f} |
| F1 | {cv.get('f1_mean', float('nan')):.4f} | {cv.get('f1_std', float('nan')):.4f} |
| ROC-AUC | {cv.get('roc_auc_mean', float('nan')):.4f} | {cv.get('roc_auc_std', float('nan')):.4f} |

### Holdout
| Tap | MCC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| train | {metrics.get('train', {}).get('mcc', float('nan')):.4f} | {metrics.get('train', {}).get('precision', float('nan')):.4f} | {metrics.get('train', {}).get('recall', float('nan')):.4f} | {metrics.get('train', {}).get('f1', float('nan')):.4f} |
| test | {ho.get('mcc', float('nan')):.4f} | {ho.get('precision', float('nan')):.4f} | {ho.get('recall', float('nan')):.4f} | {ho.get('f1', float('nan')):.4f} |

Gap overfit (MCC train − test) = **{metrics.get('train_test_mcc_gap', float('nan')):+.4f}**

Nguong quyet dinh da chot: **{metrics.get('threshold', float('nan')):.4f}**

{gate_report}

## Feature quan trong nhat
| Feature | Importance |
|---|---:|
{imp_lines}

## Gioi han da biet
- Model hoc chu yeu tu **mo ta giao dich** va **tinh lap lai**. Voi merchant hoan
  toan moi va khong co tu khoa nao quen thuoc, do tin cay giam.
- Nguong duoc chon tren phan phoi co ty le duong tinh ~{positive_rate*100:.1f}%.
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
"""
