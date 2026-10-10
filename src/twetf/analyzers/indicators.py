"""Pure technical indicators over series_map rows ([date, open, close, low, high]).

Used by the CI dashboard refresh; no I/O.
"""


def ma(closes, period):
    if not closes: return 0.0
    n = min(period, len(closes))
    return sum(closes[-n:]) / n

def williams_r(series, period=14):
    """Williams %R. series = [[date,open,close,low,high],...]"""
    if len(series) < 2: return -50.0
    recent = series[-period:] if len(series) >= period else series
    hh = max(r[4] for r in recent)   # index 4 = high
    ll = min(r[3] for r in recent)   # index 3 = low
    cl = series[-1][2]               # index 2 = close
    return round((hh - cl) / (hh - ll) * -100, 1) if hh != ll else -50.0

def rsi(closes, period=14):
    """RSI (Wilder smoothing)."""
    if len(closes) < period + 2: return 50.0
    deltas = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
    gains  = [max(0.0, d) for d in deltas]
    losses = [max(0.0, -d) for d in deltas]
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        ag = (ag * (period-1) + gains[i]) / period
        al = (al * (period-1) + losses[i]) / period
    if al == 0: return 100.0
    return round(100 - 100 / (1 + ag/al), 1)

def closes(series_map, code, n=60):
    return [r[2] for r in series_map.get(code, {}).get("d", [])[-n:]]

def series(series_map, code):
    return series_map.get(code, {}).get("d", [])


# ── series_map maintenance ──

def append_today(series_map, prices, today):
    updated = 0
    for code, p in prices.items():
        if code not in series_map: continue
        d = series_map[code].setdefault("d", [])
        if d and d[-1][0] == today: continue
        d.append([today, p["open"], p["close"], p["low"], p["high"]])
        updated += 1
    return updated
