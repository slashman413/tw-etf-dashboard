#!/usr/bin/env python3
"""
CI daily price update ? tw-etf-dashboard
Directly patches the MOMENTUM const in dashboard.html with today's TWSE prices.
No dependency on reports/ directory ? works from a clean checkout.
"""
import json, ssl, sys
from datetime import date, datetime
from pathlib import Path
import urllib.request

DASHBOARD = Path("dashboard.html")
TODAY     = date.today().strftime("%Y-%m-%d")
TODAY_ROC = str(int(TODAY[:4]) - 1911) + TODAY[5:7] + TODAY[8:]  # e.g. 1150617

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read())

def fetch_prices():
    try:
        rows = fetch_json("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
        if not rows: raise ValueError("empty")
        data_date = rows[0].get("Date", TODAY_ROC)
        prices = {}
        for row in rows:
            try:
                prices[row["Code"]] = {
                    "close":  float(row["ClosingPrice"].replace(",","")),
                    "high":   float(row["HighestPrice"].replace(",","")),
                    "low":    float(row["LowestPrice"].replace(",","")),
                    "volume": float(row["TradeVolume"].replace(",","")),
                }
            except: pass
        return data_date, prices
    except Exception as e:
        print(f"  OpenAPI failed: {e}, trying RWD...")
    try:
        d = date.today().strftime("%Y%m%d")
        rwd = fetch_json(f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=json&date={d}")
        data_date = rwd.get("date", TODAY_ROC)
        prices = {}
        for row in rwd.get("data", []):
            if len(row) < 8: continue
            try:
                prices[str(row[0]).strip()] = {
                    "close":  float(str(row[7]).replace(",","")),
                    "high":   float(str(row[5]).replace(",","")),
                    "low":    float(str(row[6]).replace(",","")),
                    "volume": float(str(row[2]).replace(",","")),
                }
            except: pass
        return data_date, prices
    except Exception as e2:
        print(f"  RWD also failed: {e2}"); return TODAY_ROC, {}

def replace_json_const(html, var_name, new_obj):
    """Find const VAR_NAME = {...}; and replace the JSON value."""
    marker = f"const {var_name}"
    idx = html.find(marker)
    if idx < 0:
        print(f"  WARNING: const {var_name} not found")
        return html
    eq = html.find("=", idx + len(marker)) + 1
    while html[eq] == " ": eq += 1
    decoder = json.JSONDecoder()
    try:
        _, parsed_len = decoder.raw_decode(html, eq)
    except Exception as e:
        print(f"  WARNING: cannot parse {var_name}: {e}"); return html
    new_json = json.dumps(new_obj, ensure_ascii=False, separators=(",", ":"))
    return html[:eq] + new_json + html[eq + parsed_len:]

def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Patching dashboard.html prices...")
    data_date, prices = fetch_prices()
    if not prices:
        print("No price data ? non-trading day?"); sys.exit(0)
    print(f"  Got {len(prices)} stocks, data_date={data_date}")

    html = DASHBOARD.read_text(encoding="utf-8")

    # Extract current MOMENTUM const
    marker = "const MOMENTUM"
    idx = html.find(marker)
    if idx < 0:
        print("ERROR: const MOMENTUM not found in dashboard.html"); sys.exit(1)
    eq = html.find("=", idx + len(marker)) + 1
    while html[eq] == " ": eq += 1
    decoder = json.JSONDecoder()
    momentum, _ = decoder.raw_decode(html, eq)

    # Update all_momentum with today's prices
    all_mom = momentum.get("all_momentum", [])
    updated = 0
    for entry in all_mom:
        code = entry.get("code", "")
        p = prices.get(code)
        if not p:
            continue
        entry["close"]  = p["close"]
        entry["high"]   = p["high"]
        entry["low"]    = p["low"]
        entry["volume"] = p["volume"]
        # Recompute pct vs prior (keep prior_price unchanged)
        prior = entry.get("prior_price") or p["close"]
        if prior and prior > 0:
            entry["pct_vs_prior"] = round((p["close"]/prior - 1)*100, 1)
        # Recompute pct vs MA30 (keep ma30 unchanged)
        ma30 = entry.get("ma30")
        if ma30 and ma30 > 0:
            entry["pct_vs_ma"] = round((p["close"]/ma30 - 1)*100, 1)
        # Intraday position
        if p["high"] and p["low"] and p["high"] > p["low"]:
            entry["intraday_pct"] = round((p["close"]-p["low"])/(p["high"]-p["low"])*100, 1)
        # Update signal
        pct = entry.get("pct_vs_prior", 0) or 0
        pma = entry.get("pct_vs_ma", 0) or 0
        if pct > 20 and pma > 5:   entry["signal"] = "STRONG_UP"
        elif pct > 10:              entry["signal"] = "UP"
        elif pct < -15 and pma < -5: entry["signal"] = "STRONG_DOWN"
        elif pct < -8:              entry["signal"] = "DOWN"
        else:                       entry["signal"] = "NEUTRAL"
        updated += 1

    # Update metadata
    momentum["date"]      = TODAY
    momentum["data_date"] = data_date
    momentum["fetch_ts"]  = datetime.now().strftime("%Y-%m-%d %H:%M")
    valid = [m for m in all_mom if m.get("pct_vs_prior") is not None]
    sc = {"STRONG_UP":0,"UP":0,"NEUTRAL":0,"DOWN":0,"STRONG_DOWN":0}
    for m in valid: sc[m.get("signal","NEUTRAL")] = sc.get(m.get("signal","NEUTRAL"),0)+1
    momentum["signal_counts"] = sc
    momentum["top_gainers"]   = sorted(valid, key=lambda x:-(x.get("pct_vs_prior",0) or 0))[:10]
    momentum["top_losers"]    = sorted(valid, key=lambda x: (x.get("pct_vs_prior",0) or 0))[:10]

    html = replace_json_const(html, "MOMENTUM", momentum)
    DASHBOARD.write_text(html, encoding="utf-8")
    print(f"  Updated {updated} stocks | Signal counts: {sc}")

if __name__ == "__main__":
    main()
