#!/usr/bin/env python3
"""
Iteration 30: 大飆股DNA Backtest Validation
Uses the 2yr Yahoo Finance OHLCV data already fetched.
For each stock, identifies ALL historical points where DNA conditions were met
and measures forward returns at 10/20/60 trading day horizons.
Generates: dna_backtest.json + DNA_BACKTEST.md
"""

import json, time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
dna_cur   = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}

# Current signals for context
cur_map = {s["code"]: s for s in dna_cur.get("all_signals", []) if s.get("code")}

ALL_CODES = sorted(name_map.keys())
TICKERS   = [f"{c}.TW" for c in ALL_CODES]

print("Fetching 2yr OHLCV for backtest…")
import yfinance as yf

try:
    raw = yf.download(TICKERS, period="2y", interval="1d",
                      auto_adjust=True, progress=False, group_by="ticker")
    print(f"  Downloaded. Shape: {raw.shape}")
except Exception as e:
    print(f"  Download error: {e}")
    raw = None

# ── Indicator helpers (same as crawl_ohlcv.py) ────────────────────────────
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi_series(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    ag = gain.ewm(alpha=1/period, adjust=False).mean()
    al = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = ag / al.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))

def williams_r_series(high, low, close, period=50):
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    return (hh - close) / (hh - ll + 1e-10) * 100  # 0=overbought, 100=oversold

def vr_series(close, volume, period=10):
    up_vol = volume.where(close > close.shift(), 0.0)
    dn_vol = volume.where(close < close.shift(), 0.0)
    vr = up_vol.rolling(period).sum() / (dn_vol.rolling(period).sum() + 1)
    return vr * 100

# ── Backtest per stock ─────────────────────────────────────────────────────
HORIZONS  = [10, 20, 60]
all_stock_results = []
signal_trades = []   # all triggered trades across all stocks

for code, ticker in zip(ALL_CODES, TICKERS):
    try:
        if hasattr(raw.columns, "get_level_values"):
            df = raw.xs(ticker, level=0, axis=1).dropna(how="all")
        else:
            continue
    except Exception:
        continue

    if len(df) < 120:
        continue

    # Normalize columns
    cols = {c.lower(): c for c in df.columns}
    try:
        c = df[cols.get("close","Close")]
        h = df[cols.get("high","High")]
        l = df[cols.get("low","Low")]
        v = df[cols.get("volume","Volume")]
    except Exception:
        continue

    # Compute indicators
    wr50  = williams_r_series(h, l, c, 50)
    rsi60 = rsi_series(c, 60)
    vr2w  = vr_series(c, v, 10)    # 2 weeks
    rsi4m = rsi_series(c, 84)      # 4-month proxy

    # Signal columns (same logic as crawl_ohlcv.py)
    s3 = wr50  < 20                   # W%R50 < 20 (near high)
    s4 = rsi60 > 57                   # RSI60 > 57
    s5 = vr2w  >= 150                 # VR2w >= 150
    s2 = rsi4m > 77                   # Month RSI4 > 77

    bull_signs = s2.astype(int) + s3.astype(int) + s4.astype(int) + s5.astype(int)

    # MACD arrows proxy: price above 200-EMA and trending
    e200 = ema(c, 200)
    e50  = ema(c, 50)
    macd_bull = (c > e200) & (e50 > e50.shift(3))

    core_signals = s3.astype(int) + macd_bull.astype(int)

    # Entry condition: bull_signs >= 2 AND at least 1 core condition
    entry_mask = (bull_signs >= 2) & (core_signals >= 1)
    entry_mask = entry_mask.fillna(False)

    # Avoid re-entry within 20 bars of last signal
    entries = []
    last_entry = -999
    for i, (idx, val) in enumerate(entry_mask.items()):
        if val and (i - last_entry) > 20:
            entries.append(i)
            last_entry = i

    # Measure forward returns
    close_arr = c.values
    date_arr  = c.index

    stock_trades = []
    for ei in entries:
        ep = close_arr[ei]
        if ep <= 0: continue
        trade = {
            "code":  code,
            "name":  name_map.get(code, code),
            "date":  str(date_arr[ei].date()),
            "entry": round(float(ep), 2),
            "signs": int(bull_signs.iloc[ei]),
            "core":  int(core_signals.iloc[ei]),
        }
        for h in HORIZONS:
            fi = ei + h
            if fi < len(close_arr):
                fp = close_arr[fi]
                ret = (fp / ep - 1) * 100
                trade[f"ret_{h}d"] = round(float(ret), 2)
            else:
                trade[f"ret_{h}d"] = None
        stock_trades.append(trade)
        signal_trades.append(trade)

    # Per-stock stats
    if not stock_trades:
        continue

    stats = {"code": code, "name": name_map.get(code, code),
             "num_signals": len(stock_trades)}
    for h in HORIZONS:
        rets = [t[f"ret_{h}d"] for t in stock_trades if t[f"ret_{h}d"] is not None]
        if rets:
            stats[f"avg_{h}d"]  = round(float(np.mean(rets)), 2)
            stats[f"win_{h}d"]  = round(sum(1 for r in rets if r > 0) / len(rets) * 100, 1)
            stats[f"med_{h}d"]  = round(float(np.median(rets)), 2)
        else:
            stats[f"avg_{h}d"] = stats[f"win_{h}d"] = stats[f"med_{h}d"] = None

    cur = cur_map.get(code, {})
    stats["current_signs"]   = cur.get("bull_signs")
    stats["current_verdict"] = cur.get("verdict","—")
    all_stock_results.append(stats)

# ── Aggregate stats ────────────────────────────────────────────────────────
print(f"\n  Total signal triggers: {len(signal_trades)}")
print(f"  Stocks with signals:   {len(all_stock_results)}")

agg = {}
for h in HORIZONS:
    rets = [t[f"ret_{h}d"] for t in signal_trades if t.get(f"ret_{h}d") is not None]
    if rets:
        agg[f"{h}d"] = {
            "n":      len(rets),
            "avg":    round(float(np.mean(rets)), 2),
            "median": round(float(np.median(rets)), 2),
            "win_pct":round(sum(1 for r in rets if r > 0) / len(rets) * 100, 1),
            "p25":    round(float(np.percentile(rets, 25)), 2),
            "p75":    round(float(np.percentile(rets, 75)), 2),
        }
        print(f"  {h}d: n={len(rets)} avg={agg[f'{h}d']['avg']:+.1f}% "
              f"win={agg[f'{h}d']['win_pct']:.0f}% med={agg[f'{h}d']['median']:+.1f}%")

# Sort per-stock by 20d average return
all_stock_results.sort(key=lambda x: -(x.get("avg_20d") or -999))

print("\n  Top 10 stocks by avg 20d return when DNA fired:")
for r in all_stock_results[:10]:
    print(f"    {r['code']} {r['name'][:8]}: n={r['num_signals']} "
          f"avg20d={r.get('avg_20d','?'):+.1f}% win={r.get('win_20d','?'):.0f}%"
          f" | now: {r['current_verdict']}")

# ── Save ───────────────────────────────────────────────────────────────────
out = {
    "date":        TODAY,
    "fetch_ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_signals": len(signal_trades),
    "stocks_tested": len(all_stock_results),
    "aggregate":   agg,
    "per_stock":   all_stock_results,
    "all_trades":  signal_trades[-200:],  # last 200 for space
}
(REPORT_DIR / "dna_backtest.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# ── DNA_BACKTEST.md ────────────────────────────────────────────────────────
def fv(v, fmt=".1f", fb="—"):
    if v is None: return fb
    return format(float(v), fmt)

lines = [
    f"# 大飆股DNA Backtest Validation — {TODAY} (Iteration 30)",
    f"*2yr daily Yahoo Finance data | Entry: bull_signs≥2 + core≥1 | {len(signal_trades)} total triggers*",
    "",
    "## Aggregate Performance (All 62 Stocks)",
    "",
    "| Horizon | Signals | Avg Return | Win Rate | Median | P25–P75 |",
    "|---------|---------|-----------|---------|--------|---------|",
]
for h in HORIZONS:
    a = agg.get(f"{h}d", {})
    lines.append(
        f"| **{h} days** | {a.get('n','—')} | "
        f"**{fv(a.get('avg'),'+.1f')}%** | "
        f"**{fv(a.get('win_pct'),'.0f')}%** | "
        f"{fv(a.get('median'),'+.1f')}% | "
        f"{fv(a.get('p25'),'+.1f')}% – {fv(a.get('p75'),'+.1f')}% |"
    )

lines += [
    "",
    "## Per-Stock Performance (Sorted by Avg 20d Return)",
    "",
    "| Code | Name | Signals | Avg 10d | Win 10d | Avg 20d | Win 20d | Avg 60d | Now |",
    "|------|------|---------|---------|---------|---------|---------|---------|-----|",
]
for r in all_stock_results[:20]:
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | {r['num_signals']} | "
        f"{fv(r.get('avg_10d'),'+.1f')}% | {fv(r.get('win_10d'),'.0f')}% | "
        f"**{fv(r.get('avg_20d'),'+.1f')}%** | **{fv(r.get('win_20d'),'.0f')}%** | "
        f"{fv(r.get('avg_60d'),'+.1f')}% | {r.get('current_verdict','—')} |"
    )

lines += [
    "",
    "---",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 30*",
]
(REPORT_DIR / "DNA_BACKTEST.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ dna_backtest.json + DNA_BACKTEST.md written")
