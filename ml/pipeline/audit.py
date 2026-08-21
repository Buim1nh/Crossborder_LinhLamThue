"""Kiem tra ro ri nhan (label leakage) va do lech phan phoi (drift)."""
from __future__ import annotations

import pandas as pd

LEAK_F1_THRESHOLD = 0.99


def leakage_audit(df: pd.DataFrame, y: pd.Series,
                  exclude: tuple[str, ...] = ("label", "y", "Id", "Thoi_gian",
                                              "Noi_dung_text")) -> dict:
    """Voi moi cot, tim luat 'cot == gia tri' co F1 cao nhat.
    F1 >= 0.99 => cot do gan nhu chinh la nhan."""
    report: dict[str, dict] = {}
    pos = int(y.sum())
    if pos == 0:
        return report
    for c in df.columns:
        if c in exclude:
            continue
        s = df[c].fillna("__NA__").astype(str)
        if s.nunique() > 200:
            continue
        ct = pd.crosstab(s, y)
        best = None
        for v in ct.index:
            tp = int(ct.loc[v, 1]) if 1 in ct.columns else 0
            fp = int(ct.loc[v, 0]) if 0 in ct.columns else 0
            if tp == 0:
                continue
            prec, rec = tp / (tp + fp), tp / pos
            f1 = 2 * prec * rec / (prec + rec)
            if best is None or f1 > best["f1"]:
                best = dict(value=v, precision=round(prec, 4),
                            recall=round(rec, 4), f1=round(f1, 4), support=tp + fp)
        if best:
            best["leak"] = bool(best["f1"] >= LEAK_F1_THRESHOLD)
            report[c] = best
    return report


def leaking_columns(report: dict) -> list[str]:
    return [c for c, r in report.items() if r["leak"]]


def coverage_drift(train_df: pd.DataFrame, new_df: pd.DataFrame,
                   cols: list[str]) -> dict:
    """% dong trong `new_df` mang gia tri categorical chua tung thay luc train."""
    rep = {}
    for c in cols:
        if c not in train_df.columns or c not in new_df.columns:
            continue
        seen = set(train_df[c].fillna("UNKNOWN").astype(str).str.strip())
        g = new_df[c].fillna("UNKNOWN").astype(str).str.strip()
        rep[c] = {
            "n_unique_train": len(seen),
            "n_unique_new": int(g.nunique()),
            "pct_rows_unseen": round(float((~g.isin(seen)).mean() * 100), 2),
        }
    return rep


def format_leakage_table(report: dict) -> str:
    lines = [f"{'cot':<24}{'gia tri tot nhat':<34}{'P':>7}{'R':>7}{'F1':>7}  ro ri",
             "-" * 82]
    for c, r in sorted(report.items(), key=lambda kv: -kv[1]["f1"]):
        val = (r["value"][:31] + "...") if len(r["value"]) > 34 else r["value"]
        flag = "  <== LEAK" if r["leak"] else ""
        lines.append(f"{c:<24}{val:<34}{r['precision']:>7.3f}{r['recall']:>7.3f}"
                     f"{r['f1']:>7.3f}{flag}")
    return "\n".join(lines)
