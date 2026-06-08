#!/usr/bin/env python3
"""
Iteration 32: Multi-Timeframe DNA Signals (Weekly + Monthly)
Resamples 2yr daily OHLCV to weekly and monthly bars.
Computes all 6 大飆股DNA signals with correct timeframes:
  S1: 月DMI +DI(1) > 50  [monthly bars, 1-period DI]
  S2: 月RSI(4) > 77       [monthly bars, 4-period RSI]
  S3: 日W%R(50) < 20      [daily, already computed]
  S4: 日RSI(60) > 57      [daily, already computed]
  S5: 週VR(2) >= 150      [weekly bars, 2-period VR]
  S6: 月VR(2) >= 150      [monthly bars, 2-period VR]
Updates: dna_signals.json + grand_unified.json
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
dna_old   = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
grand_old = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}
dna_old_map = {s["code"]: s for s in dna_old.get("all_signals", []) if s.get("code")}

ALL_CODES = sorted(name_map.keys())
OTC_CODES = {"6488"}
TICKERS   = [f"{c}.TWO" if c in OTC_CODES else f"{c}.TW" for c in ALL_CODES]

print("Fetching 2yr OHLCV for multi-timeframe analysis…")
import yfinance as yf

try:
    raw = yf.download(TICKERS, period="2y", interval="1d",
                      auto_adjust=True, progress=False, group_by="ticker")
    print(f"  Downloaded. Shape: {raw.shape}")
except Exception as e:
    print(f"  Error: {e}"); raw = None

# ── Indicator helpers ─────────────────────────────────────────────────────
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi_s(s, n):
    d = s.diff(); g = d.clip(lower=0); l = (-d).clip(lower=0)
    ag = g.ewm(alpha=1/n, adjust=False).mean()
    al = l.ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1 + ag/al.replace(0, float("nan")))

def williams_r_s(h, l, c, n):
    hh = h.rolling(n).max(); ll = l.rolling(n).min()
    return (hh - c) / (hh - ll + 1e-10) * 100  # 0=overbought, 100=oversold

def vr_s(c, v, n):
    up = v.where(c > c.shift(), 0.0); dn = v.where(c < c.shift(), 0.0)
    return up.rolling(n).sum() / (dn.rolling(n).sum() + 1) * 100

def di_plus_s(h, l, c, n):
    """DI+ series using Wilder smoothing"""
    up_move   = h.diff(); dn_move = l.shift() - l
    dm_plus   = pd.Series(
        np.where((up_move > dn_move) & (up_move > 0), up_move, 0.0), index=h.index)
    tr1 = h - l; tr2 = (h - c.shift()).abs(); tr3 = (l - c.shift()).abs()
    tr  = pd.Series(np.maximum(tr1, np.maximum(tr2, tr3)), index=h.index)
    tr_s  = tr.ewm(span=n, adjust=False).mean()
    dmp_s = dm_plus.ewm(span=n, adjust=False).mean()
    return 100 * dmp_s / tr_s.replace(0, float("nan"))

# ── Resample helper ───────────────────────────────────────────────────────
def resample_ohlcv(df, freq):
    """Resample daily OHLCV to weekly ('W') or monthly ('ME')"""
    agg = {
        "Open":   "first",
        "High":   "max",
        "Low":    "min",
        "Close":  "last",
        "Volume": "sum",
    }
    # Use available columns
    cols = {c: c for c in df.columns}
    agg2 = {cols[k]: v for k, v in agg.items() if k in cols}
    return df.resample(freq).agg(agg2).dropna(how="all")

# ── Per-stock computation ─────────────────────────────────────────────────
updated_signals = []

for code, ticker in zip(ALL_CODES, TICKERS):
    try:
        df = raw.xs(ticker, level=0, axis=1).dropna(how="all")
    except Exception:
        continue

    if len(df) < 60: continue

    # Normalize column names
    col_map = {c.lower(): c for c in df.columns}
    try:
        dc = df[col_map.get("close","Close")]
        dh = df[col_map.get("high","High")]
        dl = df[col_map.get("low","Low")]
        dv = df[col_map.get("volume","Volume")]
    except Exception:
        continue

    # ── Daily signals (S3, S4) ────────────────────────────────────────────
    if len(dc) >= 60:
        wr50_d  = williams_r_s(dh, dl, dc, 50)
        rsi60_d = rsi_s(dc, 60)
        s3_val  = float(wr50_d.iloc[-1])  if not wr50_d.empty  else None
        s4_val  = float(rsi60_d.iloc[-1]) if not rsi60_d.empty else None
        s3_ok   = s3_val is not None and s3_val < 20
        s4_ok   = s4_val is not None and s4_val > 57
    else:
        s3_val = s4_val = None; s3_ok = s4_ok = False

    # ── Weekly resampling (S5: 週VR2) ────────────────────────────────────
    try:
        wdf = resample_ohlcv(df, "W")
        if len(wdf) >= 4:
            wc = wdf[col_map.get("close","Close")]
            wv = wdf[col_map.get("volume","Volume")]
            vr2w  = vr_s(wc, wv, 2)
            s5_val = float(vr2w.iloc[-1]) if not vr2w.empty else None
            s5_ok  = s5_val is not None and s5_val >= 150
        else:
            s5_val = None; s5_ok = False
    except Exception:
        s5_val = None; s5_ok = False

    # ── Monthly resampling (S1: 月DMI+DI, S2: 月RSI4, S6: 月VR2) ────────
    try:
        mdf = resample_ohlcv(df, "ME")
        if len(mdf) >= 6:
            mc = mdf[col_map.get("close","Close")]
            mh = mdf[col_map.get("high","High")]
            ml = mdf[col_map.get("low","Low")]
            mv = mdf[col_map.get("volume","Volume")]

            # S1: 月DMI +DI(1) > 50
            di_plus_m = di_plus_s(mh, ml, mc, 1)
            s1_val = float(di_plus_m.iloc[-1]) if not di_plus_m.empty else None
            s1_ok  = s1_val is not None and s1_val > 50

            # S2: 月RSI(4) > 77
            rsi4_m = rsi_s(mc, 4)
            s2_val = float(rsi4_m.iloc[-1]) if not rsi4_m.empty else None
            s2_ok  = s2_val is not None and s2_val > 77

            # S6: 月VR2 >= 150
            vr2m  = vr_s(mc, mv, 2)
            s6_val = float(vr2m.iloc[-1]) if not vr2m.empty else None
            s6_ok  = s6_val is not None and s6_val >= 150
        else:
            s1_val = s2_val = s6_val = None
            s1_ok = s2_ok = s6_ok = False
    except Exception as e:
        s1_val = s2_val = s6_val = None
        s1_ok = s2_ok = s6_ok = False

    # ── Core conditions (MACD + ADX using daily) ──────────────────────────
    old = dna_old_map.get(code, {})
    c1_ok = old.get("c1_ok", False)
    c2_ok = old.get("c2_ok", False)

    bull_signs = sum([s1_ok, s2_ok, s3_ok, s4_ok, s5_ok, s6_ok])
    core_met   = sum([c1_ok, c2_ok, s3_ok])

    if core_met >= 2 and bull_signs >= 2:
        verdict = "🚀 大飆股"
    elif bull_signs >= 3:
        verdict = "🚀 大飆股候選"
    elif bull_signs >= 2 and core_met >= 1:
        verdict = "📈 強勢上攻"
    elif bull_signs >= 2:
        verdict = "📈 BULL"
    elif (s3_val or 100) > 80 or (s4_val or 100) < 35:
        verdict = "💥 BEAR"
    else:
        verdict = "⬛ NEUTRAL"

    updated_signals.append({
        **old,  # preserve old fields
        "code":     code,
        "name":     name_map.get(code, code),
        "s1_dmi":   round(s1_val, 1) if s1_val else None,
        "s1_ok":    s1_ok,
        "s2_rsi4m": round(s2_val, 1) if s2_val else None,
        "s2_ok":    s2_ok,
        "s3_wr50":  round(s3_val, 1) if s3_val else None,
        "s3_ok":    s3_ok,
        "s4_rsi60": round(s4_val, 1) if s4_val else None,
        "s4_ok":    s4_ok,
        "s5_vr2w":  round(s5_val, 0) if s5_val else None,
        "s5_ok":    s5_ok,
        "s6_vr2m":  round(s6_val, 0) if s6_val else None,
        "s6_ok":    s6_ok,
        "bull_signs": bull_signs,
        "core_met":   core_met,
        "verdict":    verdict,
        "timeframe":  "multi",
    })

updated_signals.sort(key=lambda x: -(x["bull_signs"]*10 + x["core_met"]))

strong_bull = [s for s in updated_signals if "大飆股" in s["verdict"]]
bull        = [s for s in updated_signals if "BULL" in s["verdict"] or "上攻" in s["verdict"]]
bear        = [s for s in updated_signals if "BEAR" in s["verdict"]]

# Summary
print(f"\n=== Multi-Timeframe DNA Results ===")
print(f"Total: {len(updated_signals)} | 大飆股: {len(strong_bull)} | BULL: {len(bull)} | BEAR: {len(bear)}")
print("\n🚀 大飆股 / 候選 (top 10):")
for s in (strong_bull + bull)[:12]:
    sigs = f"S1={'✅' if s['s1_ok'] else '—'} S2={'✅' if s['s2_ok'] else '—'} S3={'✅' if s['s3_ok'] else '—'} S4={'✅' if s['s4_ok'] else '—'} S5={'✅' if s['s5_ok'] else '—'} S6={'✅' if s['s6_ok'] else '—'}"
    print(f"  {s['code']} {s['name'][:8]}: {s['bull_signs']}/6 | {sigs}")

# Compare with old signals
old_strong = len([s for s in dna_old.get("all_signals",[]) if "大飆股" in s.get("verdict","")])
new_strong = len(strong_bull)
print(f"\n  Change vs daily-only: {old_strong} → {new_strong} 大飆股 candidates")

# Save updated dna_signals.json
new_dna = {
    **dna_old,
    "fetch_ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "timeframe":   "multi (daily+weekly+monthly)",
    "strong_bull": strong_bull,
    "bull":        bull,
    "bear":        bear,
    "all_signals": updated_signals,
}
(REPORT_DIR / "dna_signals.json").write_text(
    json.dumps(new_dna, ensure_ascii=False, indent=2), encoding="utf-8")

# Update grand_unified tech_pts with new bull_signs
dna_new_map = {s["code"]: s for s in updated_signals if s.get("code")}
grand_updated = []
for r in grand_old.get("all_ranked", []):
    code = r["code"]
    dn   = dna_new_map.get(code, {})
    bs   = dn.get("bull_signs", r.get("bull_signs") or 0)
    cm   = dn.get("core_met",   r.get("core_met")   or 0)
    new_tech = (bs / 6 * 15) + (cm / 3 * 10)
    delta    = new_tech - r.get("tech_pts", 0)
    new_grand= round(r["grand"] + delta, 1)
    g = {**r, "bull_signs": bs, "core_met": cm,
         "tech_pts": round(new_tech,1), "grand": new_grand,
         "dna_verdict": dn.get("verdict", r.get("dna_verdict","—"))}
    grand_updated.append(g)

grand_updated.sort(key=lambda x: -x["grand"])
for r in grand_updated:
    bs = r.get("bull_signs") or 0; g = r["grand"]
    if g >= 70 and bs >= 3: r["final"] = "🚀 TRIPLE CONFIRMED"
    elif g >= 65:            r["final"] = "✅ STRONG BUY"
    elif g >= 55:            r["final"] = "📈 BUY"
    elif g >= 40:            r["final"] = "👀 WATCH"
    elif g >= 25:            r["final"] = "⬛ HOLD"
    else:                    r["final"] = "❌ REDUCE"

triple = [r for r in grand_updated if "TRIPLE" in r["final"]]
strong = [r for r in grand_updated if r["final"] == "✅ STRONG BUY"]
buy    = [r for r in grand_updated if r["final"] == "📈 BUY"]

print("\n=== Updated Grand Unified Top 10 ===")
for r in grand_updated[:10]:
    print(f"  {r['code']} {r['name'][:10]:<12} {r['grand']:>5.1f} DNA={r.get('bull_signs','?')}/6 | {r['final']}")

new_grand = {**grand_old,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "triple_confirmed": triple, "strong_buy": strong, "buy": buy,
    "all_ranked": grand_updated}
(REPORT_DIR / "grand_unified.json").write_text(
    json.dumps(new_grand, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n✓ dna_signals.json + grand_unified.json updated")
print(f"  Triple: {len(triple)} | SB: {len(strong)} | Buy: {len(buy)}")
