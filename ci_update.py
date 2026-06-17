#!/usr/bin/env python3
"""
Comprehensive daily CI update — tw-etf-dashboard
Updates: MOMENTUM, MAREFRESH, DNASIGNALS, GRANDDATA, MOVERS
Also appends today's prices to series_map.json for indicator history.
No external dependencies — stdlib only (json, ssl, urllib.request).
"""
import json, ssl, sys
from datetime import date, datetime
from pathlib import Path

DASHBOARD   = Path("dashboard.html")
SERIES_MAP  = Path("series_map.json")
TODAY       = date.today().strftime("%Y-%m-%d")
TODAY_ROC   = str(int(TODAY[:4]) - 1911) + TODAY[5:7] + TODAY[8:]

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

# ── Fetch ──────────────────────────────────────────────────────────────────────

def _get(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read())

def fetch_prices():
    """Returns (data_date_roc_str, {code: {close,open,high,low,volume}})."""
    # Primary: OpenAPI
    try:
        rows = _get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
        if not rows: raise ValueError("empty")
        data_date = rows[0].get("Date", TODAY_ROC)
        prices = {}
        for row in rows:
            try:
                c = row["ClosingPrice"].replace(",", "")
                if not c or c in ("--", "0"): continue
                prices[row["Code"]] = {
                    "close":  float(c),
                    "open":   float(row["OpeningPrice"].replace(",", "")),
                    "high":   float(row["HighestPrice"].replace(",", "")),
                    "low":    float(row["LowestPrice"].replace(",", "")),
                    "volume": float(row["TradeVolume"].replace(",", "")),
                }
            except: pass
        return data_date, prices
    except Exception as e:
        print(f"  OpenAPI failed: {e}, trying RWD...")
    # Fallback: RWD
    try:
        d = date.today().strftime("%Y%m%d")
        rwd = _get(f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=json&date={d}")
        data_date = rwd.get("date", TODAY_ROC)
        prices = {}
        for row in rwd.get("data", []):
            if len(row) < 8: continue
            try:
                prices[str(row[0]).strip()] = {
                    "close":  float(str(row[7]).replace(",", "")),
                    "open":   float(str(row[4]).replace(",", "")),
                    "high":   float(str(row[5]).replace(",", "")),
                    "low":    float(str(row[6]).replace(",", "")),
                    "volume": float(str(row[2]).replace(",", "")),
                }
            except: pass
        return data_date, prices
    except Exception as e2:
        print(f"  RWD failed: {e2}"); return TODAY_ROC, {}

# ── Indicators ─────────────────────────────────────────────────────────────────

def _ma(closes, period):
    if not closes: return 0.0
    n = min(period, len(closes))
    return sum(closes[-n:]) / n

def _wr(series, period=14):
    """Williams %R. series = [[date,open,close,low,high],...]"""
    if len(series) < 2: return -50.0
    recent = series[-period:] if len(series) >= period else series
    hh = max(r[4] for r in recent)   # index 4 = high
    ll = min(r[3] for r in recent)   # index 3 = low
    cl = series[-1][2]               # index 2 = close
    return round((hh - cl) / (hh - ll) * -100, 1) if hh != ll else -50.0

def _rsi(closes, period=14):
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

def _closes(series_map, code, n=60):
    return [r[2] for r in series_map.get(code, {}).get("d", [])[-n:]]

def _series(series_map, code):
    return series_map.get(code, {}).get("d", [])

# ── series_map update ──────────────────────────────────────────────────────────

def update_series(series_map, prices):
    updated = 0
    for code, p in prices.items():
        if code not in series_map: continue
        d = series_map[code].setdefault("d", [])
        if d and d[-1][0] == TODAY: continue
        d.append([TODAY, p["open"], p["close"], p["low"], p["high"]])
        updated += 1
    return updated

# ── JSON const helpers ─────────────────────────────────────────────────────────

def _extract(html, name):
    m = f"const {name}"
    idx = html.find(m)
    if idx < 0: return None
    eq = html.find("=", idx + len(m)) + 1
    while html[eq] == " ": eq += 1
    obj, _ = json.JSONDecoder().raw_decode(html, eq)
    return obj

def _patch(html, name, obj):
    m = f"const {name}"
    idx = html.find(m)
    if idx < 0:
        print(f"  WARNING: const {name} not found"); return html
    eq = html.find("=", idx + len(m)) + 1
    while html[eq] == " ": eq += 1
    try:
        _, length = json.JSONDecoder().raw_decode(html, eq)
    except Exception as e:
        print(f"  WARNING: parse {name}: {e}"); return html
    return html[:eq] + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + html[eq+length:]

def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Const patchers ─────────────────────────────────────────────────────────────

def patch_momentum(html, prices, data_date):
    mom = _extract(html, "MOMENTUM")
    all_mom = mom.get("all_momentum", [])
    updated = 0
    for e in all_mom:
        p = prices.get(e.get("code", ""))
        if not p: continue
        e["close"] = p["close"]; e["high"] = p["high"]
        e["low"]   = p["low"];   e["volume"] = p["volume"]
        prior = e.get("prior_price") or p["close"]
        if prior and prior > 0:
            e["pct_vs_prior"] = round((p["close"]/prior - 1)*100, 1)
        ma30 = e.get("ma30")
        if ma30 and ma30 > 0:
            e["pct_vs_ma"] = round((p["close"]/ma30 - 1)*100, 1)
        if p["high"] > p["low"]:
            e["intraday_pct"] = round((p["close"]-p["low"])/(p["high"]-p["low"])*100, 1)
        pct = e.get("pct_vs_prior", 0) or 0
        pma = e.get("pct_vs_ma", 0) or 0
        if pct > 20 and pma > 5:    e["signal"] = "STRONG_UP"
        elif pct > 10:              e["signal"] = "UP"
        elif pct < -15 and pma < -5: e["signal"] = "STRONG_DOWN"
        elif pct < -8:              e["signal"] = "DOWN"
        else:                       e["signal"] = "NEUTRAL"
        updated += 1
    mom["date"] = TODAY; mom["data_date"] = data_date; mom["fetch_ts"] = _ts()
    valid = [m for m in all_mom if m.get("pct_vs_prior") is not None]
    sc = {s: 0 for s in ["STRONG_UP","UP","NEUTRAL","DOWN","STRONG_DOWN"]}
    for m in valid: sc[m.get("signal","NEUTRAL")] += 1
    mom["signal_counts"] = sc
    mom["top_gainers"] = sorted(valid, key=lambda x: -(x.get("pct_vs_prior",0) or 0))[:10]
    mom["top_losers"]  = sorted(valid, key=lambda x:  (x.get("pct_vs_prior",0) or 0))[:10]
    print(f"  MOMENTUM: {updated} stocks | {sc}")
    return _patch(html, "MOMENTUM", mom)

def patch_movers(html):
    """Re-derive from already-patched MOMENTUM."""
    mom = _extract(html, "MOMENTUM")
    valid = [m for m in mom.get("all_momentum", []) if m.get("pct_vs_prior") is not None]
    top6  = sorted(valid, key=lambda x: abs(x.get("pct_vs_prior",0) or 0), reverse=True)[:6]
    movers = [{"code": m["code"], "name": m.get("name",""), "chg": m.get("pct_vs_prior",0), "score": m.get("score",0)} for m in top6]
    print(f"  MOVERS: {len(movers)} entries")
    return _patch(html, "MOVERS", movers)

def patch_marefresh(html, series_map, prices, data_date):
    ma = _extract(html, "MAREFRESH")
    all_results = ma.get("all_results", [])
    above, below, s_above, s_below = [], [], [], []
    for e in all_results:
        code = e.get("code", "")
        p = prices.get(code)
        closes = _closes(series_map, code, 35)
        if p: e["close"] = p["close"]
        close = e.get("close", 0) or 0
        if not close: continue
        if len(closes) >= 10:
            ma30 = _ma(closes, 30)
            e["ma30"] = round(ma30, 2)
        ma30_v = e.get("ma30", 0) or 0
        if ma30_v > 0:
            pct = round((close / ma30_v - 1) * 100, 2)
            e["pct_vs_ma"] = pct
            if pct >= 0:
                above.append(e)
                if pct >= 5: s_above.append(e)
            else:
                below.append(e)
                if pct <= -5: s_below.append(e)
    ma["date"] = TODAY; ma["data_date"] = data_date; ma["fetch_ts"] = _ts()
    ma["above_ma"]     = len(above);   ma["below_ma"]     = len(below)
    ma["strong_above"] = len(s_above); ma["strong_below"] = len(s_below)
    ma["above_list"]   = sorted(above, key=lambda x: -(x.get("pct_vs_ma",0) or 0))
    ma["below_list"]   = sorted(below, key=lambda x:  (x.get("pct_vs_ma",0) or 0))
    ma["all_results"]  = all_results
    print(f"  MAREFRESH: above={len(above)} below={len(below)} | s_above={len(s_above)} s_below={len(s_below)}")
    return _patch(html, "MAREFRESH", ma)

def patch_dnasignals(html, series_map, prices, data_date):
    dna = _extract(html, "DNASIGNALS")
    for s in dna.get("all_signals", []):
        code = s.get("code", "")
        p = prices.get(code)
        if p:
            s["close_now"] = p["close"]
            s["close"]     = p["close"]
            s["data_date"] = data_date
        ser = _series(series_map, code)
        if len(ser) >= 15:
            wr = _wr(ser, min(50, len(ser)))
            s["s3_wr50"] = wr
            s["s3_ok"]   = wr <= -15   # not in overbought zone
        if len(ser) >= 20:
            closes = [r[2] for r in ser]
            rsi = _rsi(closes, 14)
            s["s4_rsi60"] = rsi
            s["s4_ok"]    = 40 <= rsi <= 82   # trending but not extreme overbought
        ok_keys = [k for k in s if k.endswith("_ok")]
        s["bull_signs"] = sum(1 for k in ok_keys if s.get(k))
        core = sum(1 for k in ["s1_ok","s2_ok","s3_ok","s4_ok"] if s.get(k))
        s["core_met"] = core
        total = s["bull_signs"]
        if total >= 7:   s["verdict"] = "STRONG_BULL"
        elif total >= 5: s["verdict"] = "BULL"
        elif total >= 3: s["verdict"] = "WATCH"
        else:            s["verdict"] = "NEUTRAL"
    sigs = dna.get("all_signals", [])
    dna["date"]        = TODAY
    dna["data_date"]   = data_date
    dna["fetch_ts"]    = _ts()
    dna["strong_bull"] = sum(1 for s in sigs if s.get("verdict") == "STRONG_BULL")
    dna["bull"]        = sum(1 for s in sigs if s.get("verdict") == "BULL")
    dna["bear"]        = sum(1 for s in sigs if s.get("verdict") in ("WATCH","NEUTRAL"))
    print(f"  DNASIGNALS: strong_bull={dna['strong_bull']} bull={dna['bull']} bear={dna['bear']}")
    return _patch(html, "DNASIGNALS", dna)

def patch_granddata(html, series_map, prices, data_date):
    gd = _extract(html, "GRANDDATA")
    for e in gd.get("all_ranked", []):
        code = e.get("code", "")
        p = prices.get(code)
        if not p: continue
        closes = _closes(series_map, code, 25)
        if len(closes) >= 10:
            ma20 = _ma(closes, 20)
            if ma20 > 0:
                pct = (p["close"] / ma20 - 1) * 100
                # mom_pts: 0-25 scale; 0% deviation → 12.5 pts; ±20% → 0 or 25
                mom = max(0.0, min(25.0, 12.5 + pct * 0.625))
                e["mom_pts"] = round(mom, 1)
                e["grand"] = round(
                    (e.get("fund_pts", 0) or 0) +
                    (e.get("tech_pts", 0) or 0) +
                    (e.get("val_pts",  0) or 0) +
                    mom, 1
                )
    ranked = gd.get("all_ranked", [])
    gd["date"]      = TODAY
    gd["data_date"] = data_date
    gd["fetch_ts"]  = _ts()
    gd["all_ranked"]       = sorted(ranked, key=lambda x: -(x.get("grand", 0) or 0))
    gd["strong_buy"]       = sum(1 for r in ranked if (r.get("grand",     0) or 0) >= 80)
    gd["triple_confirmed"] = sum(1 for r in ranked if (r.get("bull_signs",0) or 0) >= 3
                                                   and (r.get("core_met",  0) or 0) >= 2)
    print(f"  GRANDDATA: strong_buy={gd['strong_buy']} triple={gd['triple_confirmed']}")
    return _patch(html, "GRANDDATA", gd)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"[{_ts()}] Comprehensive CI update starting...")

    data_date, prices = fetch_prices()
    if not prices:
        print("No price data — non-trading day, skipping."); sys.exit(0)
    print(f"  {len(prices)} stocks fetched, data_date={data_date}")

    # Update series_map.json
    series_map = {}
    if SERIES_MAP.exists():
        print("  Loading series_map.json...")
        series_map = json.loads(SERIES_MAP.read_text(encoding="utf-8"))
        n = update_series(series_map, prices)
        print(f"  Appended today's prices to {n} series")
        SERIES_MAP.write_text(
            json.dumps(series_map, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8"
        )
        print("  series_map.json saved")

    # Load dashboard.html
    print("  Loading dashboard.html...")
    html = DASHBOARD.read_text(encoding="utf-8")

    # Patch consts in order (MOMENTUM first — MOVERS depends on it)
    html = patch_momentum(html, prices, data_date)
    html = patch_movers(html)
    html = patch_marefresh(html, series_map, prices, data_date)
    html = patch_dnasignals(html, series_map, prices, data_date)
    html = patch_granddata(html, series_map, prices, data_date)

    DASHBOARD.write_text(html, encoding="utf-8")
    print(f"  dashboard.html saved ({len(html)//1024} KB)")
    print(f"[{_ts()}] Done.")

if __name__ == "__main__":
    main()
