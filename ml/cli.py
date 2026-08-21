#!/usr/bin/env python3
"""CLI cua pipeline SUBSCRIPTION.

    python -m ml.cli audit                     # kiem tra ro ri nhan
    python -m ml.cli train                     # train + CV + dong goi vao registry
    python -m ml.cli evaluate --data f.csv     # cham model `current` tren du lieu moi
    python -m ml.cli predict --input f.csv     # xuat du doan ra CSV
    python -m ml.cli promote                   # promote phien ban moi nhat (qua cong)
    python -m ml.cli versions                  # liet ke phien ban trong registry
    python -m ml.cli drift --data f.csv        # do lech phan phoi so voi luc train
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ml.pipeline import registry  # noqa: E402
from ml.pipeline.audit import (coverage_drift, format_leakage_table,  # noqa: E402
                               leakage_audit)
from ml.pipeline.config import load_config  # noqa: E402
from ml.pipeline.data import load_dataset  # noqa: E402
from ml.pipeline.evaluate import (binary_metrics, check_gates,  # noqa: E402
                                  format_gate_report, pick_threshold)
from ml.pipeline.serve import SubscriptionDetector  # noqa: E402
from ml.pipeline.train import run_training  # noqa: E402

DRIFT_COLS = ["Noi_dung", "Loai_giao_dich", "Trang_thai", "Don_vi_tien_te", "So_the"]


def _write_json(path: str, payload: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Da ghi: {p}")


def _hr(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ════════════════════════════════════════════════════════════════════════
def cmd_audit(args) -> int:
    cfg = load_config(args.config)
    path = args.data or cfg.train_path
    df, warns = load_dataset(path, positive_class=cfg.positive_class)
    _hr(f"LEAKAGE AUDIT — {path}")
    print(f"{len(df):,} dong | duong tinh {df['y'].mean()*100:.2f}%\n")
    for w in warns:
        print(f"  ⚠ {w}")
    rep = leakage_audit(df, df["y"])
    print(format_leakage_table(rep))
    leaks = [c for c, r in rep.items() if r["leak"]]
    print(f"\nCot ro ri nhan: {leaks if leaks else 'khong co'}")
    if args.out:
        _write_json(args.out, rep)
    return 0


def cmd_train(args) -> int:
    cfg = load_config(args.config)
    _hr(f"TRAIN — {cfg.project}")
    res = run_training(cfg, args.data)

    passed, fails = check_gates(res["metrics"], cfg.gates)
    gate_txt = format_gate_report(passed, fails, cfg.gates)
    print("\n" + gate_txt)

    version = registry.new_version()
    card = registry.render_model_card(
        project=cfg.project, version=version, config=cfg.to_dict(),
        metrics=res["metrics"], leakage=res["leakage"],
        importance=res["importance"], n_rows=res["manifest"]["n_rows"],
        positive_rate=res["manifest"]["positive_rate"], gate_report=gate_txt)
    d = registry.save_version(cfg.registry_dir, version, res["model"],
                              res["spec"].to_dict(),
                              {**res["metrics"], "gates_passed": passed,
                               "gate_failures": fails},
                              res["manifest"], card)
    print(f"\nDa dong goi phien ban: {d}")

    if args.promote:
        if not passed:
            print("KHONG promote: chua qua cong chat luong.")
            return 1
        registry.promote(cfg.registry_dir, version)
        print(f"Da promote `{version}` thanh phien ban current.")
    else:
        print(f"Promote bang: python -m ml.cli promote --version {version}")
    return 0 if passed else 1


def cmd_evaluate(args) -> int:
    cfg = load_config(args.config)
    det = SubscriptionDetector(version=args.version, config=cfg)
    df, warns = load_dataset(args.data, positive_class=cfg.positive_class)
    y = df["y"].values
    proba = det.predict_proba(df)

    _hr(f"EVALUATE — model {det.version} tren {args.data}")
    for w in warns:
        print(f"  ⚠ {w}")
    print(f"{len(df):,} dong | duong tinh {y.mean()*100:.2f}% "
          f"(luc train {det.manifest['positive_rate']*100:.2f}%)\n")

    m = binary_metrics(y, proba, det.threshold)
    thr_opt = pick_threshold(y, proba, "max_mcc")
    m_opt = binary_metrics(y, proba, thr_opt)
    print(f"{'':<26}{'MCC':>9}{'P':>9}{'R':>9}{'F1':>9}{'ROC-AUC':>10}")
    print("-" * 78)
    for name, mm in [(f"@ nguong chot {det.threshold:.4f}", m),
                     (f"@ nguong toi uu {thr_opt:.4f}", m_opt)]:
        print(f"{name:<26}{mm['mcc']:>9.4f}{mm['precision']:>9.4f}"
              f"{mm['recall']:>9.4f}{mm['f1']:>9.4f}"
              f"{mm.get('roc_auc', float('nan')):>10.4f}")
    c = m["confusion_matrix"]
    print(f"\nConfusion @ nguong chot: TP={c['tp']} FP={c['fp']} "
          f"FN={c['fn']} TN={c['tn']}")

    cv_mcc = (det.metrics.get("cv") or {}).get("mcc_mean")
    if cv_mcc is not None:
        d = m["mcc"] - cv_mcc
        print(f"\nMCC luc train (CV) = {cv_mcc:.4f} | tren du lieu nay = "
              f"{m['mcc']:.4f} | chenh {d:+.4f}")
        if d < -0.15:
            print("  ⚠ Giam manh -> nghi ngo dataset shift. Chay "
                  "`python -m ml.cli drift --data ...` de xem chi tiet.")
    if args.out:
        _write_json(args.out, {"model_version": det.version, "data": args.data,
                               "at_locked_threshold": m,
                               "at_optimal_threshold": {**m_opt, "threshold": thr_opt}})
    return 0


def cmd_predict(args) -> int:
    cfg = load_config(args.config)
    det = SubscriptionDetector(version=args.version, config=cfg)
    df = pd.read_csv(args.input)
    if args.limit:
        df = df.head(args.limit)
    out = det.predict(df, args.threshold)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)
    n = int(out["is_subscription"].sum())
    print(f"Model {det.version} | {len(out):,} giao dich | nguong "
          f"{args.threshold or det.threshold:.4f} | SUBSCRIPTION = {n:,} "
          f"({n/len(out)*100:.2f}%)")
    print(f"Da ghi: {args.output}")
    return 0


def cmd_promote(args) -> int:
    cfg = load_config(args.config)
    versions = registry.list_versions(cfg.registry_dir)
    if not versions:
        print("Registry rong. Chay `python -m ml.cli train` truoc.")
        return 1
    version = args.version or versions[-1]
    metrics = json.loads((cfg.registry_dir / version / "metrics.json").read_text())
    passed = metrics.get("gates_passed")
    if passed is False and not args.force:
        print(f"`{version}` truot cong chat luong:")
        for f in metrics.get("gate_failures", []):
            print(f"  ❌ {f}")
        print("Dung --force neu van muon promote.")
        return 1
    registry.promote(cfg.registry_dir, version)
    print(f"Da promote `{version}` thanh current "
          f"(MCC CV = {metrics.get('cv', {}).get('mcc_mean')}).")
    return 0


def cmd_versions(args) -> int:
    cfg = load_config(args.config)
    cur = registry.get_current(cfg.registry_dir)
    versions = registry.list_versions(cfg.registry_dir)
    _hr(f"REGISTRY — {cfg.registry_dir}")
    if not versions:
        print("(rong)")
        return 0
    print(f"{'':<3}{'phien ban':<24}{'MCC (CV)':>11}{'std':>9}{'gate':>8}  train file")
    print("-" * 78)
    for v in versions:
        m = json.loads((cfg.registry_dir / v / "metrics.json").read_text())
        mf = json.loads((cfg.registry_dir / v / "manifest.json").read_text())
        cv = m.get("cv", {})
        mark = "->" if v == cur else "  "
        gate = "DAT" if m.get("gates_passed") else "TRUOT"
        print(f"{mark:<3}{v:<24}{cv.get('mcc_mean', float('nan')):>11.4f}"
              f"{cv.get('mcc_std', float('nan')):>9.4f}{gate:>8}  {mf.get('train_file')}")
    print(f"\ncurrent = {cur}")
    return 0


def cmd_drift(args) -> int:
    cfg = load_config(args.config)
    det = SubscriptionDetector(version=args.version, config=cfg)
    train_df, _ = load_dataset(det.manifest["train_file"],
                               positive_class=cfg.positive_class)
    new_df, _ = load_dataset(args.data, require_label=False)
    _hr(f"DRIFT — {args.data} vs du lieu train cua {det.version}")
    rep = coverage_drift(train_df, new_df, DRIFT_COLS)
    print(f"{'cot':<20}{'#uniq train':>13}{'#uniq moi':>12}{'% dong GIA TRI MOI':>22}")
    print("-" * 78)
    worst = 0.0
    for c, r in rep.items():
        worst = max(worst, r["pct_rows_unseen"])
        print(f"{c:<20}{r['n_unique_train']:>13}{r['n_unique_new']:>12}"
              f"{r['pct_rows_unseen']:>22.2f}")
    proba = det.predict_proba(new_df)
    print(f"\nPhan bo xac suat: mean={proba.mean():.4f} "
          f"p50={np.median(proba):.4f} p95={np.quantile(proba, 0.95):.4f}")
    print(f"Ty le vuot nguong {det.threshold:.4f}: "
          f"{(proba >= det.threshold).mean()*100:.2f}% "
          f"(luc train {det.manifest['positive_rate']*100:.2f}%)")
    if worst > 50:
        print(f"\n⚠ {worst:.1f}% dong mang gia tri categorical chua tung thay -> "
              f"nen train lai co them du lieu nay.")
    if args.out:
        _write_json(args.out, rep)
    return 0


def cmd_info(args) -> int:
    cfg = load_config(args.config)
    det = SubscriptionDetector(version=args.version, config=cfg)
    print(json.dumps(det.info(), indent=2, ensure_ascii=False))
    return 0


# ════════════════════════════════════════════════════════════════════════
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ml.cli", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None, help="mac dinh ml/config.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("audit", help="kiem tra ro ri nhan")
    p.add_argument("--data"); p.add_argument("--out")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("train", help="train + CV + dong goi vao registry")
    p.add_argument("--data"); p.add_argument("--promote", action="store_true")
    p.set_defaults(func=cmd_train)

    p = sub.add_parser("evaluate", help="cham model tren du lieu co nhan")
    p.add_argument("--data", required=True); p.add_argument("--version")
    p.add_argument("--out")
    p.set_defaults(func=cmd_evaluate)

    p = sub.add_parser("predict", help="xuat du doan ra CSV")
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="ml/artifacts/predictions.csv")
    p.add_argument("--version"); p.add_argument("--threshold", type=float)
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(func=cmd_predict)

    p = sub.add_parser("promote", help="dat phien ban lam current")
    p.add_argument("--version"); p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_promote)

    p = sub.add_parser("versions", help="liet ke registry")
    p.set_defaults(func=cmd_versions)

    p = sub.add_parser("drift", help="do lech phan phoi")
    p.add_argument("--data", required=True); p.add_argument("--version")
    p.add_argument("--out")
    p.set_defaults(func=cmd_drift)

    p = sub.add_parser("info", help="thong tin model dang serve")
    p.add_argument("--version")
    p.set_defaults(func=cmd_info)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
