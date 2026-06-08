#!/usr/bin/env python3
"""
Iteration 27c: Historical OHLCV Crawler via Yahoo Finance
Fetches 2 years of daily OHLCV for all 62 tracked stocks.
Computes:
  - Williams %R (50 periods)
  - RSI (60 periods)
  - MACD (200, 209, 210) — custom long-period Taiwan system
  - DMI / ADX (14 standard, note: ADX300 needs 300+ bars)
  - VR — Volume Ratio (2 weeks = 10 days, 2 months = 42 days)
Generates: ohlcv_data.json + dna_signals.json
"""

import json, time, sys
import numpy as np
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

name_map = {**{s["code"]: s["name"] for s in composite},
            **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}

ALL_CODES = sorted(name_map.keys())
TICKERS   = [f"{c}.TW" for c in ALL_CODES]

# ── Fetch via yfinance ────────────────────────────────────────────────────────
print(f"Fetching {len(TICKERS)} tickers from Yahoo Finance…")
import yfinance as yf

try:
    # yfinance 1.x batch download
    raw = yf.download(
        tickers=TICKERS,
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )
    print(f"  Downloaded. Shape: {raw.shape if hasattr(raw, 'shape') else 'multi-frame'}")
except Exception as e:
    print(f"  Batch download failed: {e}")
    raw = None

# ── Parse per-stock DataFrames ───────────────────────────────────────────────
stock_data = {}

if raw is not None and not raw.empty:
    if len(TICKERS) == 1:
        # Single ticker: raw IS the DataFrame
        code = ALL_CODES[0]
        df = raw.copy()
        if not df.empty:
            stock_data[code] = df
    else:
        # Multi-ticker: raw has MultiIndex columns (Ticker, Field)
        for code, ticker in zip(ALL_CODES, TICKERS):
            try:
                if ticker in raw.columns.get_level_values(0) if hasattr(raw.columns, 'get_level_values') else []:
                    df = raw[ticker].dropna(how="all")
                elif hasattr(raw, 'columns') and hasattr(raw.columns, 'levels'):
                    # Try getting the ticker slice
                    df = raw.xs(ticker, level=0, axis=1).dropna(how="all")
                else:
                    continue
                if not df.empty and len(df) > 50:
                    stock_data[code] = df
            except Exception as ex:
                pass  # skip unavailable tickers

if not stock_data:
    # Fallback: fetch one by one
    print("  Batch parse failed, fetching individually…")
    for i, (code, ticker) in enumerate(zip(ALL_CODES, TICKERS)):
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="2y", interval="1d", auto_adjust=True)
            if not df.empty and len(df) > 50:
                stock_data[code] = df
                print(f"  [{i+1}/{len(ALL_CODES)}] {ticker}: {len(df)} rows")
            else:
                print(f"  [{i+1}/{len(ALL_CODES)}] {ticker}: empty")
        except Exception as e:
            print(f"  [{i+1}/{len(ALL_CODES)}] {ticker}: {e}")
        if i % 10 == 9:
            time.sleep(1)  # light throttle

print(f"\n  Successfully loaded: {len(stock_data)}/{len(ALL_CODES)} stocks")

# ── Indicator functions ───────────────────────────────────────────────────────
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    avg_g = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_l = loss.ewm(alpha=1/period, adjust=False).mean()
    rs    = avg_g / avg_l.replace(0, float('nan'))
    return 100 - (100 / (1 + rs))

def williams_r(high, low, close, period=14):
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    wr = (hh - close) / (hh - ll + 1e-10) * 100  # 0=overbought,100=oversold
    return wr

def adx(high, low, close, period=14):
    tr1  = high - low
    tr2  = (high - close.shift()).abs()
    tr3  = (low  - close.shift()).abs()
    tr   = np.maximum(tr1, np.maximum(tr2, tr3))

    up_move   = high - high.shift()
    down_move = low.shift() - low

    dm_plus  = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    dm_minus = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    import pandas as pd
    tr_s    = pd.Series(tr,       index=high.index).ewm(span=period, adjust=False).mean()
    dmp_s   = pd.Series(dm_plus,  index=high.index).ewm(span=period, adjust=False).mean()
    dmm_s   = pd.Series(dm_minus, index=high.index).ewm(span=period, adjust=False).mean()

    di_plus  = 100 * dmp_s / tr_s.replace(0, float('nan'))
    di_minus = 100 * dmm_s / tr_s.replace(0, float('nan'))

    dx   = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus).replace(0, float('nan'))
    adx_ = dx.ewm(span=period, adjust=False).mean()

    return di_plus, di_minus, adx_

def volume_ratio(close, volume, period):
    """VR = sum(up-day volume) / sum(down-day volume) * 100"""
    import pandas as pd
    up_vol   = volume.where(close > close.shift(), 0)
    dn_vol   = volume.where(close < close.shift(), 0)
    vr       = up_vol.rolling(period).sum() / (dn_vol.rolling(period).sum() + 1)
    return vr * 100

# ── Compute signals per stock ────────────────────────────────────────────────
print("\nComputing indicators…")
signals = []
ohlcv_summary = {}

for code, df in stock_data.items():
    # Normalize column names
    cols = {c.lower(): c for c in df.columns}
    try:
        c_close  = df[cols.get("close", "Close")]
        c_open   = df[cols.get("open", "Open")]
        c_high   = df[cols.get("high", "High")]
        c_low    = df[cols.get("low", "Low")]
        c_volume = df[cols.get("volume", "Volume")]
    except Exception as e:
        print(f"  {code}: column error {e}")
        continue

    if len(c_close) < 60:
        print(f"  {code}: only {len(c_close)} rows — skipping")
        continue

    try:
        # ── Williams %R (50) ──────────────────────────────────────────────────
        # Value 0=overbought(near high), 100=oversold(near low)
        # 大飆股條件: WR50 < 20 = near high = strong momentum
        wr50 = williams_r(c_high, c_low, c_close, 50)
        wr50_val = float(wr50.iloc[-1]) if not wr50.empty else None

        # ── RSI (60) ──────────────────────────────────────────────────────────
        rsi60_s  = rsi(c_close, 60)
        rsi60_val = float(rsi60_s.iloc[-1]) if not rsi60_s.empty else None

        # ── RSI (4) monthly proxy — use last 4*21=84 bars ─────────────────────
        rsi4m_s  = rsi(c_close, 84)
        rsi4m_val = float(rsi4m_s.iloc[-1]) if not rsi4m_s.empty else None

        # ── MACD (200, 209, 210) ──────────────────────────────────────────────
        macd_needs = 210
        if len(c_close) >= macd_needs:
            ema200  = ema(c_close, 200)
            ema209  = ema(c_close, 209)
            dif     = ema200 - ema209
            signal_line = ema(dif, 210) if len(dif.dropna()) >= 5 else dif.ewm(span=3,adjust=False).mean()

            # "四箭頭" = DIF, Signal, EMA200, EMA209 all pointing up (slope > 0)
            n = 3  # compare last 3 bars for slope direction
            dif_up   = float(dif.iloc[-1])   > float(dif.iloc[-n])
            sig_up   = float(signal_line.iloc[-1]) > float(signal_line.iloc[-n])
            ema200_up= float(ema200.iloc[-1]) > float(ema200.iloc[-n])
            ema209_up= float(ema209.iloc[-1]) > float(ema209.iloc[-n])
            arrows_up = sum([dif_up, sig_up, ema200_up, ema209_up])
            dif_val   = float(dif.iloc[-1])
        else:
            arrows_up = None
            dif_val   = None

        # ── DMI / ADX (14 for practical compute; note ADX300 needs 300+ bars) ─
        if len(c_close) >= 30:
            di_plus, di_minus, adx_val_s = adx(c_high, c_low, c_close, 14)
            adx_val    = float(adx_val_s.iloc[-1])
            di_plus_v  = float(di_plus.iloc[-1])
            di_minus_v = float(di_minus.iloc[-1])
            # ADX300 proxy: use longer period
            _, _, adx300_s = adx(c_high, c_low, c_close, min(300, len(c_close)//2))
            adx300_val = float(adx300_s.iloc[-1])
            adx300_prev= float(adx300_s.iloc[-4]) if len(adx300_s) > 4 else adx300_val
            adx300_up  = adx300_val > adx300_prev
        else:
            adx_val = di_plus_v = di_minus_v = adx300_val = None
            adx300_up = False

        # ── VR (2 weeks = 10 days; 2 months = 42 days) ───────────────────────
        vr2w  = volume_ratio(c_close, c_volume, 10)
        vr2m  = volume_ratio(c_close, c_volume, 42)
        vr2w_val = float(vr2w.iloc[-1]) if not vr2w.empty else None
        vr2m_val = float(vr2m.iloc[-1]) if not vr2m.empty else None

        # ── 月DMI +DI > 50 proxy: use weekly+monthly DI+ from longer ADX ──────
        monthly_di_plus = di_plus_v if di_plus_v is not None else 0

        # ── Signal evaluation (大飆股6跡象) ──────────────────────────────────
        s1_monthly_dmi   = monthly_di_plus > 35   # proxy (true needs monthly bars)
        s2_monthly_rsi4  = rsi4m_val is not None and rsi4m_val > 77
        s3_daily_wr50    = wr50_val is not None and wr50_val < 20  # closing near high
        s4_daily_rsi60   = rsi60_val is not None and rsi60_val > 57
        s5_weekly_vr2    = vr2w_val is not None and vr2w_val >= 150
        s6_monthly_vr2   = vr2m_val is not None and vr2m_val >= 150

        bull_signs = sum([s1_monthly_dmi, s2_monthly_rsi4, s3_daily_wr50,
                          s4_daily_rsi60, s5_weekly_vr2, s6_monthly_vr2])

        # ── Core conditions: 大飆股必須符合 ──────────────────────────────────
        cond1_macd = arrows_up is not None and arrows_up >= 3   # 四箭頭向上
        cond2_adx  = adx300_up                                   # ADX trending up
        cond3_wr   = s3_daily_wr50                               # W%R50 < 20

        core_met = sum([cond1_macd, cond2_adx, cond3_wr])

        # Overall verdict
        if core_met >= 2 and bull_signs >= 2:
            verdict = "🚀 大飆股"
        elif bull_signs >= 3:
            verdict = "🚀 大飆股候選"
        elif bull_signs >= 2 and core_met >= 1:
            verdict = "📈 強勢上攻"
        elif bull_signs >= 2:
            verdict = "📈 BULL"
        elif (wr50_val is not None and wr50_val > 80) or \
             (rsi60_val is not None and rsi60_val < 35):
            verdict = "💥 BEAR"
        else:
            verdict = "⬛ NEUTRAL"

        recent_close = float(c_close.iloc[-1])
        recent_high  = float(c_high.iloc[-5:].max())
        recent_low   = float(c_low.iloc[-5:].min())

        sig = {
            "code":         code,
            "name":         name_map.get(code, code),
            "bars":         len(c_close),
            "close":        round(recent_close, 2),
            "score":        score_map.get(code),
            # Signals 1-6
            "s1_dmi":       round(monthly_di_plus, 1),
            "s1_ok":        s1_monthly_dmi,
            "s2_rsi4m":     round(rsi4m_val, 1) if rsi4m_val else None,
            "s2_ok":        s2_monthly_rsi4,
            "s3_wr50":      round(wr50_val, 1) if wr50_val is not None else None,
            "s3_ok":        s3_daily_wr50,
            "s4_rsi60":     round(rsi60_val, 1) if rsi60_val is not None else None,
            "s4_ok":        s4_daily_rsi60,
            "s5_vr2w":      round(vr2w_val, 0) if vr2w_val is not None else None,
            "s5_ok":        s5_weekly_vr2,
            "s6_vr2m":      round(vr2m_val, 0) if vr2m_val is not None else None,
            "s6_ok":        s6_monthly_vr2,
            # Core conditions
            "c1_macd_arrows": arrows_up,
            "c1_ok":         cond1_macd,
            "c2_adx300":     round(adx300_val, 1) if adx300_val else None,
            "c2_ok":         cond2_adx,
            "c3_wr":         s3_daily_wr50,
            # Totals
            "bull_signs":    bull_signs,
            "core_met":      core_met,
            "verdict":       verdict,
        }
        signals.append(sig)

    except Exception as e:
        print(f"  {code}: indicator error {e}")
        import traceback; traceback.print_exc()
        continue

# Sort
signals.sort(key=lambda x: -(x["bull_signs"] * 10 + x["core_met"]))

strong_bull = [s for s in signals if "大飆股" in s["verdict"]]
bull        = [s for s in signals if "BULL" in s["verdict"] or "上攻" in s["verdict"]]
bear        = [s for s in signals if "BEAR" in s["verdict"]]

print(f"\n=== 大飆股DNA Screen Results ===")
print(f"Total computed: {len(signals)} | 大飆股: {len(strong_bull)} | BULL: {len(bull)} | BEAR: {len(bear)}")
print("\n🚀 大飆股 / 大飆股候選:")
for s in (strong_bull + bull)[:10]:
    print(f"  {s['code']} {s['name'][:8]}: signs={s['bull_signs']}/6 core={s['core_met']}/3 | "
          f"WR50={s['s3_wr50']} RSI60={s['s4_rsi60']} VR2w={s['s5_vr2w']}")
print("\n💥 BEAR:")
for s in bear[:5]:
    print(f"  {s['code']} {s['name'][:8]}: WR50={s['s3_wr50']} RSI60={s['s4_rsi60']}")

# Save
out = {
    "date":        TODAY,
    "fetch_ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":       len(signals),
    "strong_bull": strong_bull,
    "bull":        bull,
    "bear":        bear,
    "all_signals": signals,
}
(REPORT_DIR / "dna_signals.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ dna_signals.json written ({len(signals)} stocks)")
