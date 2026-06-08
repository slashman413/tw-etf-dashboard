#!/usr/bin/env python3
"""Fetch OHLCV for dashboard stocks missing from series_map.json and patch it in."""
import json, time
from pathlib import Path
from datetime import datetime

MISSING = [
    '1101','1102','1216','1301','1590','2002','2049','2207','2337','2352',
    '2412','2603','2615','2801','2823','2880','2884','2886','2888','2890',
    '2892','2912','3037','3231','4904','5871','5876','5880','6669','6743'
]

import yfinance as yf
import numpy as np

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi_calc(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    ag = gain.ewm(alpha=1/period, adjust=False).mean()
    al = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = ag / al.replace(0, float('nan'))
    return 100 - (100 / (1 + rs))

def wr_calc(high, low, close, period=50):
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    return (hh - close) / (hh - ll + 1e-10) * 100

def vr_calc(close, volume, period):
    up_vol = volume.where(close > close.shift(), 0)
    dn_vol = volume.where(close < close.shift(), 0)
    return up_vol.rolling(period).sum() / (dn_vol.rolling(period).sum() + 1) * 100

def adx_di(high, low, close, period=14):
    import pandas as pd
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low  - close.shift()).abs()
    tr  = np.maximum(tr1, np.maximum(tr2, tr3))
    up  = high - high.shift()
    dn  = low.shift() - low
    dmp = np.where((up > dn) & (up > 0), up, 0.0)
    dmm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr_s  = pd.Series(tr,  index=high.index).ewm(span=period, adjust=False).mean()
    dmp_s = pd.Series(dmp, index=high.index).ewm(span=period, adjust=False).mean()
    dmm_s = pd.Series(dmm, index=high.index).ewm(span=period, adjust=False).mean()
    di_p = 100 * dmp_s / tr_s.replace(0, float('nan'))
    di_m = 100 * dmm_s / tr_s.replace(0, float('nan'))
    return di_p, di_m

sm_path = Path(__file__).parent / "series_map.json"
sm = json.loads(sm_path.read_text(encoding='utf-8'))
print(f"series_map: {len(sm)} stocks before patch")

tickers = [f"{c}.TW" for c in MISSING]
added = 0

for i, (code, ticker) in enumerate(zip(MISSING, tickers)):
    print(f"[{i+1}/{len(MISSING)}] Fetching {ticker}...", end=' ', flush=True)
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="2y", interval="1d", auto_adjust=True)
        if df.empty or len(df) < 30:
            print(f"empty/short ({len(df)} rows)")
            continue
        df = df.dropna(subset=['Open','High','Low','Close'])

        close  = df['Close']
        high   = df['High']
        low    = df['Low']
        opn    = df['Open']
        vol    = df['Volume']

        # OHLCV: [date, open, close, low, high]
        d_list = [
            [row.Index.strftime('%Y-%m-%d'),
             round(float(row.Open), 2),
             round(float(row.Close), 2),
             round(float(row.Low), 2),
             round(float(row.High), 2)]
            for row in df.itertuples() if not (
                row.Open != row.Open or row.Close != row.Close)
        ]

        # Indicators
        wr50   = wr_calc(high, low, close, 50)
        rsi60  = rsi_calc(close, 60)
        rsi4m  = rsi_calc(close, 84)
        vr10   = vr_calc(close, vol, 10)
        vr42   = vr_calc(close, vol, 42)
        di_p, di_m = adx_di(high, low, close, 14)

        def to_series(s, n=120):
            vals = s.dropna().iloc[-n:]
            return [[vals.index[j].strftime('%Y-%m-%d'), round(float(vals.iloc[j]), 2)]
                    for j in range(len(vals))]

        sm[code] = {
            "d":    d_list[-120:],
            "wr":   to_series(wr50),
            "rsi60":to_series(rsi60),
            "m_rsi4": to_series(rsi4m),
            "m_di": to_series(di_p),
            "vr10": to_series(vr10),
            "vr42": to_series(vr42),
        }
        added += 1
        print(f"OK ({len(d_list)} rows)")
    except Exception as e:
        print(f"ERROR: {e}")
    if i < len(MISSING) - 1:
        time.sleep(0.5)

sm_path.write_text(json.dumps(sm, ensure_ascii=False), encoding='utf-8')
print(f"\nseries_map: {len(sm)} stocks after patch (+{added})")
print(f"File size: {sm_path.stat().st_size // 1024} KB")
