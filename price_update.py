#!/usr/bin/env python3
"""
Iteration 33: Fresh Price Update + May Revenue Probe
1. Probe May 2026 revenue (11505)
2. Wait 130s
3. Fetch STOCK_DAY_ALL for latest close prices
4. Update price_momentum.json with fresh data
5. Update grand_unified momentum scores
"""

import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 130

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    s = str(v).replace(",","").strip()
    try: return float(s) if s else None
    except: return None

composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
mom_old    = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
ma_data    = json.loads((REPORT_DIR / "ma_refresh.json").read_text(encoding="utf-8"))
grand_old  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
conviction = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}
prior_map = {s["code"]: sf(s.get("price")) for s in composite}
ma_map    = {r["code"]: sf(r.get("ma30")) for r in ma_data.get("all_results", [])}
conv_map  = {r["code"]: r.get("action","—") for r in conviction.get("all_ranked", [])}
old_mom_map = {m["code"]: m for m in mom_old.get("all_momentum", [])}
all_codes = set(name_map.keys())

# ── STEP 1: Probe May revenue ───────────────────────────────────────────────
print("STEP 1: Probe May 2026 revenue (11505)")
try:
    rev_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods  = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    print(f"  Latest period: {periods[-1]} | May 2026: {'✅ AVAILABLE!' if may_avail else '❌ Not yet'}")
    if may_avail:
        print("  *** MAY REVENUE IS NOW AVAILABLE — processing! ***")
except Exception as e:
    print(f"  Revenue probe failed: {e}")
    may_avail = False; rev_raw = []

# ── STEP 2: Wait ────────────────────────────────────────────────────────────
print(f"\n⏳ Waiting {WAIT_SEC}s before STOCK_DAY_ALL…", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 3: Fetch STOCK_DAY_ALL ─────────────────────────────────────────────
print("\nSTEP 3: Fetch STOCK_DAY_ALL (fresh prices)")
try:
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    data_date = price_raw[0].get("Date","?") if price_raw else "?"
    print(f"  Got {len(price_raw)} rows | Date: {data_date}")
except Exception as e:
    print(f"  STOCK_DAY_ALL failed: {e}")
    price_raw = []; data_date = "?"

price_map = {r.get("Code","").strip(): r for r in price_raw if r.get("Code")}

# ── STEP 4: Update momentum ──────────────────────────────────────────────────
momentum = []
for code in sorted(all_codes):
    r     = price_map.get(code, {})
    old_m = old_mom_map.get(code, {})

    close  = sf(r.get("ClosingPrice"))
    open_  = sf(r.get("OpeningPrice"))
    high   = sf(r.get("HighestPrice"))
    low    = sf(r.get("LowestPrice"))
    volume = sf(r.get("TradeVolume"))

    # Fall back to old data if today's not available
    if close is None: close = old_m.get("close")

    prior_p = prior_map.get(code)
    ma30    = ma_map.get(code)

    pct_prior = round((close/prior_p - 1)*100, 1) if close and prior_p and prior_p > 0 else old_m.get("pct_vs_prior")
    pct_ma    = round((close/ma30  - 1)*100, 1) if close and ma30   and ma30   > 0 else old_m.get("pct_vs_ma")
    intraday  = round((close-low)/(high-low)*100, 1) if high and low and high > low else old_m.get("intraday_pct")

    sig = "NEUTRAL"
    if pct_prior is not None:
        if pct_prior > 20 and (pct_ma or 0) > 5: sig = "STRONG_UP"
        elif pct_prior > 10: sig = "UP"
        elif pct_prior < -15 and (pct_ma or 0) < -5: sig = "STRONG_DOWN"
        elif pct_prior < -8: sig = "DOWN"

    momentum.append({
        "code": code, "name": name_map.get(code, code),
        "close": close, "prior_price": prior_p,
        "pct_vs_prior": pct_prior, "ma30": ma30,
        "pct_vs_ma": pct_ma, "intraday_pct": intraday,
        "high": high, "low": low, "volume": volume,
        "signal": sig, "score": score_map.get(code),
        "conv": conv_map.get(code,"—"),
    })

valid       = [m for m in momentum if m["pct_vs_prior"] is not None]
top_gainers = sorted(valid, key=lambda x: x["pct_vs_prior"] or 0, reverse=True)[:10]
top_losers  = sorted(valid, key=lambda x: x["pct_vs_prior"] or 0)[:10]
above_ma    = sorted([m for m in valid if (m["pct_vs_ma"] or 0) > 5],  key=lambda x: -(x["pct_vs_ma"] or 0))
below_ma    = sorted([m for m in valid if (m["pct_vs_ma"] or 0) < -5], key=lambda x:  (x["pct_vs_ma"] or 0))

sc = {k: sum(1 for m in valid if m["signal"]==k)
      for k in ["STRONG_UP","UP","NEUTRAL","DOWN","STRONG_DOWN"]}

print(f"\n  Matched {len(momentum)} | valid {len(valid)} | STRONG_UP:{sc['STRONG_UP']} UP:{sc['UP']} DOWN:{sc['DOWN']}")
print("  Top gainers vs baseline:")
for m in top_gainers[:5]:
    print(f"    {m['code']} {m['name'][:6]}: {m.get('prior_price','?')} → {m['close']} ({m['pct_vs_prior']:+.1f}%)")

new_mom = {
    "date": TODAY, "data_date": data_date,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "may_available": may_avail,
    "total_tracked": len(momentum), "valid_comparison": len(valid),
    "signal_counts": sc,
    "top_gainers": top_gainers, "top_losers": top_losers,
    "above_ma": above_ma[:10], "below_ma": below_ma[:10],
    "conviction_updates": [m for m in valid if m["code"] in ["2376","2357","2887","5871","2801","5876","2408"]],
    "all_momentum": momentum,
}
(REPORT_DIR / "price_momentum.json").write_text(
    json.dumps(new_mom, ensure_ascii=False, indent=2), encoding="utf-8")

# ── STEP 5: Update grand_unified momentum scores ─────────────────────────────
mom_map2 = {m["code"]: m for m in momentum}
grand_upd = []
for r in grand_old.get("all_ranked", []):
    code = r["code"]
    m    = mom_map2.get(code, {})
    pct_ma    = sf(m.get("pct_vs_ma"))
    pct_prior = sf(m.get("pct_vs_prior"))
    upside    = r.get("upside")

    mom_pts = 12.5
    if pct_ma    is not None: mom_pts += min(8,  max(-8,  pct_ma    * 0.5))
    if pct_prior is not None: mom_pts += min(5,  max(-5,  pct_prior * 0.3))
    if upside    is not None and upside > 0: mom_pts += min(5, upside/30)
    mom_pts = max(0, min(25, mom_pts))

    new_grand = round(r["grand"] - r.get("mom_pts",12.5) + mom_pts, 1)
    grand_upd.append({**r, "mom_pts": round(mom_pts,1), "grand": new_grand,
                      "pct_prior": pct_prior, "pct_ma": pct_ma})

grand_upd.sort(key=lambda x: -x["grand"])
for r in grand_upd:
    bs = r.get("bull_signs") or 0; g = r["grand"]
    if g >= 70 and bs >= 3: r["final"] = "🚀 TRIPLE CONFIRMED"
    elif g >= 65:            r["final"] = "✅ STRONG BUY"
    elif g >= 55:            r["final"] = "📈 BUY"
    elif g >= 40:            r["final"] = "👀 WATCH"
    elif g >= 25:            r["final"] = "⬛ HOLD"
    else:                    r["final"] = "❌ REDUCE"

triple = [r for r in grand_upd if "TRIPLE" in r["final"]]
strong = [r for r in grand_upd if r["final"] == "✅ STRONG BUY"]
buy    = [r for r in grand_upd if r["final"] == "📈 BUY"]

print(f"\n  Grand Unified updated | Triple:{len(triple)} SB:{len(strong)} Buy:{len(buy)}")
print("  Top 5:")
for r in grand_upd[:5]:
    print(f"    {r['code']} {r['name'][:10]}: {r['grand']:.1f} | {r['final']}")

new_grand = {**grand_old,
    "data_date": data_date,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "triple_confirmed": triple, "strong_buy": strong, "buy": buy,
    "all_ranked": grand_upd}
(REPORT_DIR / "grand_unified.json").write_text(
    json.dumps(new_grand, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ price_momentum.json + grand_unified.json updated")
print(f"  data_date: {data_date} | may_available: {may_avail}")
