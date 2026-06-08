#!/usr/bin/env python3
"""
Iteration 31: Relative Strength vs TAIEX + Correlation Matrix
Uses existing 2yr Yahoo Finance OHLCV.
1. Fetches ^TWII (TAIEX) alongside stocks
2. Computes RS ratio = stock / index, and RS momentum (rate of change)
3. Identifies stocks outperforming / underperforming the index
4. Builds 62x62 correlation matrix (for portfolio risk)
Generates: relative_strength.json
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

import sys
_rs_path = REPORT_DIR / "relative_strength.json"
if _rs_path.exists():
    try:
        _prev_rs = json.loads(_rs_path.read_text(encoding="utf-8"))
        _rs_date = _prev_rs.get("data_date") or _prev_rs.get("date", "")
        if _rs_date >= TODAY:
            print(f"relative_strength already fresh ({_rs_date}) — skipping download")
            sys.exit(0)
    except Exception:
        pass

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
dna_data  = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
grand     = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map   = {s["code"]: s for s in dna_data.get("all_signals", []) if s.get("code")}

ALL_CODES  = sorted(name_map.keys())
TICKERS    = [f"{c}.TW" for c in ALL_CODES] + ["^TWII"]

print("Fetching 2yr OHLCV + TAIEX…")
import yfinance as yf

try:
    raw = yf.download(TICKERS, period="2y", interval="1d",
                      auto_adjust=True, progress=False, group_by="ticker")
    print(f"  Downloaded. Shape: {raw.shape}")
    LATEST_BAR = str(raw.index[-1].date()) if raw is not None and len(raw) > 0 else TODAY
except Exception as e:
    print(f"  Error: {e}"); raw = None; LATEST_BAR = TODAY

# ── Extract close prices ──────────────────────────────────────────────────
close_df = {}

for ticker in TICKERS:
    try:
        df = raw.xs(ticker, level=0, axis=1)
        s  = df["Close"].dropna()
        if len(s) > 60:
            code = ticker.replace(".TW","").replace("^","")
            close_df[code] = s
    except Exception:
        pass

taiex = close_df.pop("TWII", None)
print(f"  Stocks loaded: {len(close_df)} | TAIEX: {'✅' if taiex is not None else '❌'}")

if taiex is None:
    print("  TAIEX unavailable — using equal-weight basket as proxy")
    # Use the equal-weight of all stocks as proxy
    taiex = pd.concat(close_df.values(), axis=1).mean(axis=1)

# ── Align all series ──────────────────────────────────────────────────────
all_closes = pd.DataFrame(close_df)
# Align to common dates
all_closes, taiex = all_closes.align(taiex, join="inner", axis=0)
all_closes = all_closes.dropna(how="all")
taiex      = taiex.reindex(all_closes.index).ffill()

print(f"  Common dates: {len(all_closes)} trading days")

# ── Relative Strength computation ─────────────────────────────────────────
WINDOWS = [20, 60, 120]
rs_results = []

for code, col in all_closes.items():
    s = col.dropna()
    if len(s) < 40: continue

    # Align with taiex
    common_idx = s.index.intersection(taiex.index)
    if len(common_idx) < 40: continue

    sc = s.reindex(common_idx)
    tc = taiex.reindex(common_idx)

    entry = {"code": code, "name": name_map.get(code, code)}

    for w in WINDOWS:
        if len(sc) < w: continue
        # RS ratio: stock return / index return over window
        stock_ret = (sc.iloc[-1] / sc.iloc[-w] - 1) * 100
        idx_ret   = (tc.iloc[-1] / tc.iloc[-w] - 1) * 100
        rs_diff   = stock_ret - idx_ret   # excess return vs index

        # RS line slope (trending up = improving relative strength)
        rs_line = sc / tc
        rs_slope= float(rs_line.iloc[-1] - rs_line.iloc[-w//2]) / (w//2)

        entry[f"ret_{w}d"]      = round(float(stock_ret), 2)
        entry[f"idx_ret_{w}d"]  = round(float(idx_ret), 2)
        entry[f"rs_{w}d"]       = round(float(rs_diff), 2)
        entry[f"rs_slope_{w}d"] = round(float(rs_slope * 1000), 4)  # scaled

    # 52-week high/low context
    if len(sc) >= 252:
        hi52 = float(sc.iloc[-252:].max())
        lo52 = float(sc.iloc[-252:].min())
        cur  = float(sc.iloc[-1])
        entry["pct_from_52w_high"] = round((cur / hi52 - 1) * 100, 1)
        entry["pct_from_52w_low"]  = round((cur / lo52 - 1) * 100, 1)
    else:
        entry["pct_from_52w_high"] = None
        entry["pct_from_52w_low"]  = None

    # Attach grand score + DNA
    g = grand_map.get(code, {})
    d = dna_map.get(code, {})
    entry["grand"]      = g.get("grand")
    entry["final"]      = g.get("final","—")
    entry["bull_signs"] = d.get("bull_signs")
    entry["dna_verdict"]= d.get("verdict","—")

    rs_results.append(entry)

# Sort by 60d RS
rs_results.sort(key=lambda x: -(x.get("rs_60d") or -999))

# ── Correlation matrix (top 30 by grand score) ────────────────────────────
top_codes = [r["code"] for r in sorted(rs_results,
             key=lambda x: -(x.get("grand") or 0))[:30]
             if r["code"] in all_closes.columns]

if len(top_codes) >= 5:
    corr_df = all_closes[top_codes].pct_change().dropna().corr()
    # Find pairs with high correlation (>0.7) — concentration risk
    high_corr_pairs = []
    codes = list(corr_df.columns)
    for i in range(len(codes)):
        for j in range(i+1, len(codes)):
            v = float(corr_df.iloc[i,j])
            if abs(v) > 0.7:
                high_corr_pairs.append({
                    "a": codes[i], "b": codes[j],
                    "r": round(v, 3),
                    "name_a": name_map.get(codes[i],""),
                    "name_b": name_map.get(codes[j],""),
                })
    high_corr_pairs.sort(key=lambda x: -abs(x["r"]))
    corr_data = {"codes": codes, "matrix": corr_df.round(3).values.tolist()}
else:
    high_corr_pairs = []
    corr_data = {}

# ── Print summary ─────────────────────────────────────────────────────────
outperformers = [r for r in rs_results if (r.get("rs_60d") or 0) > 5]
underperformers = [r for r in rs_results if (r.get("rs_60d") or 0) < -5]

print(f"\n=== Relative Strength vs TAIEX ===")
print(f"  Outperforming 60d (>+5%): {len(outperformers)}")
print(f"  Underperforming 60d (<-5%): {len(underperformers)}")
print("\n  Top 10 RS (60d excess return):")
for r in rs_results[:10]:
    print(f"    {r['code']} {r['name'][:8]}: "
          f"stock={r.get('ret_60d','?'):+.1f}% idx={r.get('idx_ret_60d','?'):+.1f}% "
          f"RS={r.get('rs_60d','?'):+.1f}% | {r['final']}")

print(f"\n  High-correlation pairs (>0.7) in top-30: {len(high_corr_pairs)}")
for p in high_corr_pairs[:5]:
    print(f"    {p['a']} {p['name_a'][:6]} ↔ {p['b']} {p['name_b'][:6]}: r={p['r']:.2f}")

# Stocks with DNA bull signals + positive RS (best combo)
dna_rs_combo = sorted(
    [r for r in rs_results
     if (r.get("bull_signs") or 0) >= 3 and (r.get("rs_60d") or 0) > 0],
    key=lambda x: -(x.get("rs_60d") or 0)
)
print(f"\n  🎯 DNA≥3 + Positive RS: {len(dna_rs_combo)}")
for r in dna_rs_combo[:8]:
    print(f"    {r['code']} {r['name'][:8]}: RS60={r.get('rs_60d',0):+.1f}% DNA={r.get('bull_signs')}/6")

# ── Save ──────────────────────────────────────────────────────────────────
out = {
    "date":             TODAY,
    "data_date":        LATEST_BAR,
    "fetch_ts":         datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":            len(rs_results),
    "outperformers_60d": outperformers,
    "underperformers_60d": underperformers,
    "dna_rs_combo":     dna_rs_combo,
    "high_corr_pairs":  high_corr_pairs[:20],
    "corr_codes":       corr_data.get("codes", []),
    "corr_matrix":      corr_data.get("matrix", []),
    "all_rs":           rs_results,
}
(REPORT_DIR / "relative_strength.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ relative_strength.json written ({len(rs_results)} stocks)")
