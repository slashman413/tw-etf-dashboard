#!/usr/bin/env python3
"""
Iteration 39: DNA Signal Refresh
Re-downloads 6-month OHLCV from Yahoo Finance for fresh daily signals.
Updates S3 (日W%R50) and S4 (日RSI60) which change most frequently.
Preserves S1/S2/S5/S6 (weekly/monthly) from last full compute.
No TWSE API calls needed.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

comp  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
dna_old  = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
grand_old= json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

name_map = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}
ALL_CODES= sorted(name_map.keys())
OTC_CODES = {"6488"}
TICKERS  = [f"{c}.TWO" if c in OTC_CODES else f"{c}.TW" for c in ALL_CODES]
dna_map  = {s["code"]: s for s in dna_old.get("all_signals", []) if s.get("code")}

print(f"Downloading 6-month OHLCV for {len(TICKERS)} tickers…")
import yfinance as yf

try:
    raw = yf.download(TICKERS, period="6mo", interval="1d",
                      auto_adjust=True, progress=False, group_by="ticker")
    print(f"  Downloaded. Shape: {raw.shape}")
    latest_date = str(raw.index[-1].date()) if len(raw) > 0 else "?"
    print(f"  Latest bar date: {latest_date}")
except Exception as e:
    print(f"  Error: {e}"); import sys; sys.exit(1)

def rsi_s(s, n):
    d = s.diff(); g = d.clip(lower=0); l = (-d).clip(lower=0)
    ag = g.ewm(alpha=1/n, adjust=False).mean()
    al = l.ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1 + ag/al.replace(0, float("nan")))

def williams_r_s(h, l, c, n):
    hh = h.rolling(n).max(); ll = l.rolling(n).min()
    return (hh - c) / (hh - ll + 1e-10) * 100

updated = []
changes = []

for code, ticker in zip(ALL_CODES, TICKERS):
    old = dna_map.get(code, {})

    try:
        df = raw.xs(ticker, level=0, axis=1).dropna(how="all")
    except Exception:
        if old: updated.append({**old, "code": code}); continue

    if len(df) < 60:
        if old: updated.append({**old, "code": code}); continue

    col_map = {c.lower(): c for c in df.columns}
    try:
        dc = df[col_map.get("close","Close")]
        dh = df[col_map.get("high","High")]
        dl = df[col_map.get("low","Low")]
    except Exception:
        if old: updated.append({**old, "code": code}); continue

    # Daily S3: W%R(50) < 20 (oversold zone → bullish)
    wr50  = williams_r_s(dh, dl, dc, 50)
    rsi60 = rsi_s(dc, 60)

    _s3_raw = float(wr50.iloc[-1])  if not wr50.empty  else None
    _s4_raw = float(rsi60.iloc[-1]) if not rsi60.empty else None
    import math as _math
    s3_val = None if (_s3_raw is None or _math.isnan(_s3_raw)) else _s3_raw
    s4_val = None if (_s4_raw is None or _math.isnan(_s4_raw)) else _s4_raw
    s3_ok  = s3_val is not None and s3_val < 20
    s4_ok  = s4_val is not None and s4_val > 57

    # Latest close for context
    _close_raw = float(dc.iloc[-1]) if len(dc) > 0 else None
    close_now = None if (_close_raw is None or _math.isnan(_close_raw)) else _close_raw

    # Check for changes vs old
    old_s3 = old.get("s3_ok", False)
    old_s4 = old.get("s4_ok", False)
    changed_signals = []
    if s3_ok != old_s3:
        changed_signals.append(f"S3:{'ON' if s3_ok else 'OFF'}")
    if s4_ok != old_s4:
        changed_signals.append(f"S4:{'ON' if s4_ok else 'OFF'}")

    # Recompute bull_signs with fresh S3/S4 but preserved S1/S2/S5/S6
    s1_ok = old.get("s1_ok", False)
    s2_ok = old.get("s2_ok", False)
    s5_ok = old.get("s5_ok", False)
    s6_ok = old.get("s6_ok", False)
    bull_signs = sum([s1_ok, s2_ok, s3_ok, s4_ok, s5_ok, s6_ok])
    core_met   = sum([old.get("c1_ok", False), old.get("c2_ok", False), s3_ok])

    if   core_met >= 2 and bull_signs >= 2: verdict = "🚀 大飆股"
    elif bull_signs >= 3:                   verdict = "🚀 大飆股候選"
    elif bull_signs >= 2 and core_met >= 1: verdict = "📈 強勢上攻"
    elif bull_signs >= 2:                   verdict = "📈 BULL"
    elif (s3_val or 100) > 80 or (s4_val or 100) < 35: verdict = "💥 BEAR"
    else:                                   verdict = "⬛ NEUTRAL"

    new_rec = {
        **old,
        "s3_wr50":  round(s3_val, 1) if s3_val is not None else None,
        "s3_ok":    s3_ok,
        "s4_rsi60": round(s4_val, 1) if s4_val is not None else None,
        "s4_ok":    s4_ok,
        "bull_signs": bull_signs,
        "core_met":   core_met,
        "verdict":    verdict,
        "close_now":  round(close_now, 1) if close_now else None,
        "data_date":  latest_date,
    }
    updated.append(new_rec)

    if changed_signals:
        changes.append({
            "code": code, "name": name_map.get(code, code),
            "changes": changed_signals, "bull_signs": bull_signs,
            "verdict": verdict,
            "old_bull": old.get("bull_signs", 0),
        })

updated.sort(key=lambda x: -(x.get("bull_signs",0)*10 + x.get("core_met",0)))
strong_bull = [s for s in updated if "大飆股" in s.get("verdict","")]
bull        = [s for s in updated if "BULL" in s.get("verdict","") or "上攻" in s.get("verdict","")]
bear        = [s for s in updated if "BEAR" in s.get("verdict","")]

print(f"\n  Updated {len(updated)} | Changes: {len(changes)}")
print(f"  大飆股: {len(strong_bull)} | BULL: {len(bull)} | BEAR: {len(bear)}")
if changes:
    print("  Signal changes:")
    for c in changes:
        print(f"    {c['code']} {c['name'][:8]}: {c['changes']} | DNA {c['old_bull']}→{c['bull_signs']}/6 | {c['verdict']}")
else:
    print("  No signal changes detected")

# Save updated dna_signals.json
(REPORT_DIR / "dna_signals.json").write_text(
    json.dumps({**dna_old,
                "fetch_ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
                "data_date":   latest_date,
                "signal_changes": changes,
                "strong_bull": strong_bull, "bull": bull, "bear": bear,
                "all_signals": updated},
               ensure_ascii=False, indent=2), encoding="utf-8")

# Update grand_unified tech_pts if any signals changed
if changes:
    dna_m2 = {s["code"]: s for s in updated if s.get("code")}
    grand_upd = []
    for r in grand_old.get("all_ranked", []):
        code = r["code"]
        dn   = dna_m2.get(code, {})
        bs   = dn.get("bull_signs", r.get("bull_signs") or 0)
        cm   = dn.get("core_met",   r.get("core_met")   or 0)
        new_tech = (bs/6*15) + (cm/3*10)
        delta    = new_tech - r.get("tech_pts", 0)
        new_grand= round(r["grand"] + delta, 1)
        g = {**r, "bull_signs": bs, "core_met": cm,
             "tech_pts": round(new_tech,1), "grand": new_grand,
             "dna_verdict": dn.get("verdict", r.get("dna_verdict","—"))}
        grand_upd.append(g)
    grand_upd.sort(key=lambda x: -x["grand"])
    for r in grand_upd:
        bs=r.get("bull_signs") or 0; g=r["grand"]
        if g>=70 and bs>=3: r["final"]="🚀 TRIPLE CONFIRMED"
        elif g>=65:          r["final"]="✅ STRONG BUY"
        elif g>=55:          r["final"]="📈 BUY"
        elif g>=40:          r["final"]="👀 WATCH"
        elif g>=25:          r["final"]="⬛ HOLD"
        else:                r["final"]="❌ REDUCE"
    triple=[r for r in grand_upd if "TRIPLE" in r["final"]]
    (REPORT_DIR/"grand_unified.json").write_text(
        json.dumps({**grand_old,
                    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "triple_confirmed": triple,
                    "strong_buy":[r for r in grand_upd if r["final"]=="✅ STRONG BUY"],
                    "buy":[r for r in grand_upd if r["final"]=="📈 BUY"],
                    "all_ranked": grand_upd},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  grand_unified updated | Triple: {len(triple)}")

print(f"\n✓ dna_signals.json updated | data_date: {latest_date}")

# Regenerate all secondary computation reports (no API calls)
import subprocess, sys
secondary = [
    "grand_unified.py",          # re-score with fresh bwibbu PE/div
    "action_signal.py",          # master action board
    "watchlist_alerts.py",       # near-TRIPLE alerts
    "score_sensitivity.py",      # upgrade gap analysis
    "conviction_matrix.py",      # conviction scoring
    "triple_reports.py",         # TRIPLE deep-dive
    "monday_plan.py",            # daily trading plan
    "premarket_checklist.py",    # position-level checklist
    "relative_strength.py",      # RS vs TAIEX + 52w high (fresh Yahoo 2y data)
    "dna_trigger_calc.py",       # DNA trigger scores (needs fresh RS + DNA)
    "smart_money_confluence.py", # smart money signals (needs instflows + DNA)
    "generate_stock_reports.py", # per-stock JSON + FULL_REPORT.md (uses fresh RS)
    "catalyst_calendar.py",      # forward-looking catalyst timeline
    "weekly_digest.py",          # self-contained HTML summary report
]
print("\nRegenerating secondary reports…")
for script in secondary:
    r = subprocess.run([sys.executable, script], capture_output=True, text=True)
    status = "✓" if r.returncode == 0 else "✗"
    print(f"  {status} {script}")
    if r.returncode != 0 and r.stderr:
        print(f"    {r.stderr.strip()[:120]}")
print("Secondary reports done.")
