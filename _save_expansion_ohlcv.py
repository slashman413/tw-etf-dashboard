#!/usr/bin/env python3
"""Save expansion stocks OHLCV to expansion_ohlcv.json (persists across dashboard rebuilds)."""
import json, time
from pathlib import Path

EXPANSION_CODES = [
    '1101','1102','1216','1301','1303','1590','2002','2049','2207','2301',
    '2303','2317','2330','2337','2352','2376','2379','2408','2412','2603',
    '2609','2615','2801','2880','2884','2886','2890','2891','2892','2912',
    '3008','3034','3037','3045','3231','3711','4904','5871','5876','5880',
    '6415','6488','6669','6743','6770'
]  # excludes 2823 and 2888 (no Yahoo Finance data)

import yfinance as yf
import numpy as np

def rsi_calc(series, period=14):
    delta = series.diff()
    ag = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    al = (-delta).clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    rs = ag / al.replace(0, float('nan'))
    return 100 - (100 / (1 + rs))

def wr_calc(high, low, close, period=50):
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    return (hh - close) / (hh - ll + 1e-10) * 100

def vr_calc(close, volume, period):
    up = volume.where(close > close.shift(), 0)
    dn = volume.where(close < close.shift(), 0)
    return up.rolling(period).sum() / (dn.rolling(period).sum() + 1) * 100

def adx_di(high, low, close, period=14):
    import pandas as pd
    tr = np.maximum(high-low, np.maximum((high-close.shift()).abs(), (low-close.shift()).abs()))
    up = high - high.shift(); dn = low.shift() - low
    dmp = np.where((up > dn) & (up > 0), up, 0.0)
    tr_s  = pd.Series(tr,  index=high.index).ewm(span=period, adjust=False).mean()
    dmp_s = pd.Series(dmp, index=high.index).ewm(span=period, adjust=False).mean()
    return 100 * dmp_s / tr_s.replace(0, float('nan'))

def to_series(s, n=120):
    vals = s.dropna().iloc[-n:]
    return [[vals.index[j].strftime('%Y-%m-%d'), round(float(vals.iloc[j]), 2)] for j in range(len(vals))]

OTC_CODES = {'6488'}  # stocks only listed on TPEX, use .TWO suffix

out = {}
for i, code in enumerate(EXPANSION_CODES):
    ticker = f"{code}.TWO" if code in OTC_CODES else f"{code}.TW"
    print(f"[{i+1}/{len(EXPANSION_CODES)}] {ticker}...", end=' ', flush=True)
    try:
        df = yf.Ticker(ticker).history(period="2y", interval="1d", auto_adjust=True)
        df = df.dropna(subset=['Open','High','Low','Close'])
        if len(df) < 30:
            print(f"empty"); continue
        c, h, lo, o, v = df['Close'], df['High'], df['Low'], df['Open'], df['Volume']
        d_list = [[row.Index.strftime('%Y-%m-%d'), round(float(row.Open),2),
                   round(float(row.Close),2), round(float(row.Low),2), round(float(row.High),2)]
                  for row in df.itertuples() if row.Close == row.Close]
        out[code] = {
            "d":     d_list[-120:],
            "wr":    to_series(wr_calc(h, lo, c, 50)),
            "rsi60": to_series(rsi_calc(c, 60)),
            "m_rsi4":to_series(rsi_calc(c, 84)),
            "m_di":  to_series(adx_di(h, lo, c, 14)),
            "vr10":  to_series(vr_calc(c, v, 10)),
            "vr42":  to_series(vr_calc(c, v, 42)),
        }
        print(f"OK ({len(d_list)} rows)")
    except Exception as e:
        print(f"ERROR: {e}")
    if i < len(EXPANSION_CODES) - 1:
        time.sleep(0.3)

path = Path(__file__).parent / "expansion_ohlcv.json"
path.write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
print(f"\nSaved {len(out)} stocks → expansion_ohlcv.json ({path.stat().st_size//1024} KB)")
