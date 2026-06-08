"""
Fetch TAIEX monthly K-lines via Yahoo Finance (^TWII) and compute:
  - 6K/9K bullish theory count (red K consecutive)
  - Black 6K downtrend theory count (black K consecutive)
  - Daily MACD (9,12,26) and (200,209,210) for Step ② panel
Saves to taiex_monthly.json
"""
import json, sys
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed")
    sys.exit(1)

def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def compute_6k9k(monthly_df):
    """
    6K/9K 紅K理論:
      - 從第一根突破下降K線最高點的紅K開始計算
      - 每根有效紅K收盤必須高於前一根有效K最高點
      - 每根有效紅K漲幅必須 > 300點 (6K規定; 9K不限)
      - 不能跌破前K低點
      - 內含K無效 (high <= prev_high and low >= prev_low)
      - 黑K不計入
    Returns dict with current count and history.
    """
    rows = monthly_df.sort_index()
    o = rows['Open'].values
    h = rows['High'].values
    l = rows['Low'].values
    c = rows['Close'].values
    dates = [str(d.date())[:7] for d in rows.index]  # YYYY-MM

    valid_ks = []   # list of dicts for valid red Ks
    broken = False  # flag: has a K broken the sequence

    i = 0
    count_6k = 0
    count_9k = 0
    current_chain = []

    for idx in range(len(dates)):
        bar = {'date': dates[idx], 'open': o[idx], 'high': h[idx],
               'low': l[idx], 'close': c[idx]}
        is_red = c[idx] > o[idx]
        is_black = c[idx] < o[idx]
        gain = c[idx] - o[idx]

        if not current_chain:
            # Start new chain on any red K with gain > 300
            if is_red and gain > 300:
                current_chain.append(bar)
            continue

        prev = current_chain[-1]
        # Inside K check: invalid
        if h[idx] <= prev['high'] and l[idx] >= prev['low']:
            continue  # skip inside K

        if is_black:
            # Black K doesn't count — but LOW breach resets chain
            if l[idx] < prev['low']:
                current_chain = []
            continue

        # Red K: low breach resets chain
        if l[idx] < prev['low']:
            current_chain = []
            if is_red and gain > 300:
                current_chain.append(bar)
            continue

        # Must close above prev valid K HIGH (each red K close > prev valid K high)
        if c[idx] <= prev['high']:
            continue  # doesn't count but doesn't break (low was ok above)

        # 6K requires gain > 300; 9K no gain limit
        current_chain.append(bar)

    count_now = len(current_chain)

    # Also compute the black 6K downtrend count
    black_chain = []
    for idx in range(len(dates)):
        is_black = c[idx] < o[idx]
        drop = o[idx] - c[idx]

        if not black_chain:
            if is_black and drop > 300:
                black_chain.append({'date': dates[idx], 'open': o[idx],
                                    'high': h[idx], 'low': l[idx], 'close': c[idx]})
            continue

        prev = black_chain[-1]
        if h[idx] <= prev['high'] and l[idx] >= prev['low']:
            continue  # inside K

        if not is_black:
            if h[idx] > prev['high']:
                black_chain = []
            continue

        if c[idx] >= prev['low']:
            if h[idx] > prev['high']:
                black_chain = []
            continue

        if h[idx] > prev['high']:
            black_chain = []
            if is_black and drop > 300:
                black_chain.append({'date': dates[idx], 'open': o[idx],
                                    'high': h[idx], 'low': l[idx], 'close': c[idx]})
            continue

        black_chain.append({'date': dates[idx], 'open': o[idx],
                            'high': h[idx], 'low': l[idx], 'close': c[idx]})

    black_count = len(black_chain)

    # Last 24 monthly bars for display
    recent = []
    for idx in range(max(0, len(dates)-24), len(dates)):
        in_chain = any(k['date'] == dates[idx] for k in current_chain)
        in_black = any(k['date'] == dates[idx] for k in black_chain)
        recent.append({
            'date': dates[idx], 'open': round(o[idx], 2), 'high': round(h[idx], 2),
            'low': round(l[idx], 2), 'close': round(c[idx], 2),
            'is_red': bool(c[idx] > o[idx]),
            'in_chain': in_chain, 'in_black': in_black
        })

    return {
        'red_count': count_now,
        'black_count': black_count,
        'red_chain': [{'date': k['date'], 'close': round(k['close'], 2)} for k in current_chain],
        'black_chain': [{'date': k['date'], 'close': round(k['close'], 2)} for k in black_chain],
        'monthly_bars': recent,
        'signal_6k': count_now >= 6,
        'signal_9k': count_now >= 9,
        'signal_black6k': black_count >= 6,
    }

def compute_taiex_macd(daily_df):
    """Compute MACD (9,12,26) and (200,209,210) for TAIEX daily."""
    c = daily_df['Close']
    if len(c) < 30:
        return {}

    # Short MACD (9,12,26)
    e12 = ema(c, 12); e26 = ema(c, 26)
    dif_s = e12 - e26
    dea_s = ema(dif_s, 9)
    hist_s = (dif_s - dea_s) * 2
    dif_s_val = float(dif_s.iloc[-1])
    dea_s_val = float(dea_s.iloc[-1])

    # Short arrows: DIF crossing zero or DEA
    arrow_s = None
    if len(dif_s.dropna()) >= 3:
        dif_s_arr = dif_s.dropna()
        if dif_s_arr.iloc[-2] < 0 and dif_s_val > 0:
            arrow_s = 1  # cross above zero
        elif dif_s_arr.iloc[-2] > 0 and dif_s_val < 0:
            arrow_s = 3  # cross below zero
        elif dif_s_val > dea_s_val and float(dif_s_arr.iloc[-2]) <= float(dea_s.iloc[-2]):
            arrow_s = 2  # golden cross
        elif dif_s_val < dea_s_val and float(dif_s_arr.iloc[-2]) >= float(dea_s.iloc[-2]):
            arrow_s = 4  # death cross

    result = {
        'short_dif': round(dif_s_val, 2),
        'short_dea': round(dea_s_val, 2),
        'short_hist': round(float(hist_s.iloc[-1]), 2),
        'short_arrow': arrow_s,
        'short_dif_positive': dif_s_val > 0,
    }

    # Long MACD (200,209,210) — needs 210+ bars
    if len(c) >= 210:
        e200 = ema(c, 200); e209 = ema(c, 209)
        dif_l = e200 - e209
        dea_l = ema(dif_l, 210) if len(dif_l.dropna()) >= 5 else ema(dif_l, 3)
        hist_l = (dif_l - dea_l) * 2
        dif_l_val = float(dif_l.iloc[-1])
        dea_l_val = float(dea_l.iloc[-1])

        # Long arrows
        arrow_l = None
        if len(dif_l.dropna()) >= 3:
            dif_l_arr = dif_l.dropna()
            if dif_l_arr.iloc[-2] < 0 and dif_l_val > 0:
                arrow_l = 1
            elif dif_l_arr.iloc[-2] > 0 and dif_l_val < 0:
                arrow_l = 3
            elif dif_l_val > dea_l_val and float(dif_l_arr.iloc[-2]) <= float(dea_l.iloc[-2]):
                arrow_l = 2
            elif dif_l_val < dea_l_val and float(dif_l_arr.iloc[-2]) >= float(dea_l.iloc[-2]):
                arrow_l = 4

        # DIF210 spiral: positive + rising + higher troughs
        recent_dif = dif_l.dropna().iloc[-30:]
        dif_rising = float(recent_dif.iloc[-1]) > float(recent_dif.iloc[0]) if len(recent_dif) >= 5 else False
        dif_positive = dif_l_val > 0

        result.update({
            'long_dif': round(dif_l_val, 2),
            'long_dea': round(dea_l_val, 2),
            'long_hist': round(float(hist_l.iloc[-1]), 2),
            'long_arrow': arrow_l,
            'long_dif_positive': dif_positive,
            'long_dif_rising': dif_rising,
            'long_spiral': bool(dif_positive and dif_rising),
        })

        # Last 60 daily bars for chart
        recent60 = daily_df.tail(60)
        dif_hist = dif_l.tail(60)
        dea_hist = dea_l.tail(60)
        bars = []
        for dt, row in recent60.iterrows():
            bars.append({
                'date': str(dt.date()),
                'close': round(float(row['Close']), 2),
                'dif210': round(float(dif_hist.loc[dt]), 4) if dt in dif_hist.index else None,
                'dea210': round(float(dea_hist.loc[dt]), 4) if dt in dea_hist.index else None,
            })
        result['daily_bars'] = bars

    return result

def main():
    print("[fetch_taiex_monthly] Fetching TAIEX via Yahoo Finance (^TWII)...")
    ticker = yf.Ticker("^TWII")

    # Monthly data (3 years)
    monthly = ticker.history(period="3y", interval="1mo", auto_adjust=True)
    # Daily data (2 years for MACD200)
    daily = ticker.history(period="2y", interval="1d", auto_adjust=True)

    if monthly.empty or daily.empty:
        print("  No data returned from Yahoo Finance!")
        return None

    print(f"  Monthly bars: {len(monthly)} | Daily bars: {len(daily)}")
    print(f"  Monthly range: {monthly.index[0].date()} to {monthly.index[-1].date()}")
    print(f"  Daily range:   {daily.index[0].date()} to {daily.index[-1].date()}")

    k6k9k = compute_6k9k(monthly)
    macd  = compute_taiex_macd(daily)

    print(f"  6K count: {k6k9k['red_count']} | Black 6K: {k6k9k['black_count']}")
    print(f"  6K signal: {k6k9k['signal_6k']} | 9K signal: {k6k9k['signal_9k']}")
    if macd.get('long_dif') is not None:
        print(f"  MACD200 DIF: {macd['long_dif']} | Rising: {macd.get('long_dif_rising')} | Spiral: {macd.get('long_spiral')}")

    output = {
        'generated': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'sixk_ninekk': k6k9k,
        'macd': macd,
    }
    Path("taiex_monthly.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  Saved taiex_monthly.json")
    return output

if __name__ == "__main__":
    main()
