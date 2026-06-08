#!/usr/bin/env python3
"""
Iteration 26: Price Momentum + Fresh STOCK_DAY_ALL
1. Probe May 2026 revenue (11505) — quick freshness check
2. Wait 130s
3. Fetch STOCK_DAY_ALL — current prices, volume, 52w range
4. Compute price momentum vs prior analysis:
   - Price change since our original fetch (iteration 10)
   - Stocks hitting new highs / breaking down
   - Volume signals (surge > 3x average)
   - Updated RSI proxy using daily close vs range
Generates: PRICE_MOMENTUM.md + price_momentum.json
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

# Load prior data
composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
tech_data  = json.loads((REPORT_DIR / "technical_data.json").read_text(encoding="utf-8"))
bwibbu_new = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
conviction = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}
all_codes = set(name_map.keys())

# Prior price from composite (iteration 10 daily refresh)
prior_price_map = {s["code"]: sf(s.get("price")) for s in composite}

# Prior 30d MA from technical data
ma_map = {t["code"]: sf(t.get("ma30")) for t in tech_data.get("all_stocks", [])}

# Conviction
conv_map = {r["code"]: r for r in conviction.get("all_ranked", [])}

# ── STEP 1: Probe May 2026 revenue ─────────────────────────────────────────────
print("STEP 1: Probe May 2026 revenue (11505)")
print(f"  Fetching t187ap05_L…", flush=True)
try:
    rev_raw = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    print(f"  Latest period: {periods[-1]} | May 2026: {'✅ AVAILABLE' if may_avail else '❌ Not yet'}")
except Exception as e:
    print(f"  ⚠️ Revenue probe failed: {e}")
    may_avail = False
    rev_raw = []

# ── STEP 2: Wait ───────────────────────────────────────────────────────────────
print(f"\n⏳ Waiting {WAIT_SEC}s before STOCK_DAY_ALL…", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 3: Fetch STOCK_DAY_ALL ────────────────────────────────────────────────
print("\nSTEP 3: Fetch STOCK_DAY_ALL (fresh prices)")
try:
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    print(f"  Got {len(price_raw)} rows | Date: {price_raw[0].get('Date','?') if price_raw else '?'}")
except Exception as e:
    print(f"  ⚠️ STOCK_DAY_ALL failed: {e}")
    price_raw = []

price_map = {}
for r in price_raw:
    code = r.get("Code","").strip()
    if not code: continue
    price_map[code] = r

# ── STEP 4: Compute momentum signals ───────────────────────────────────────────
momentum = []
data_date = price_raw[0].get("Date","") if price_raw else ""

for code in sorted(all_codes):
    r = price_map.get(code)
    if not r: continue

    close    = sf(r.get("ClosingPrice") or r.get("收盤價"))
    open_    = sf(r.get("OpeningPrice") or r.get("開盤價"))
    high     = sf(r.get("HighestPrice") or r.get("最高價"))
    low      = sf(r.get("LowestPrice")  or r.get("最低價"))
    volume   = sf(r.get("TradeVolume")  or r.get("成交股數"))

    prior_p  = prior_price_map.get(code)
    ma30     = ma_map.get(code)
    conv_r   = conv_map.get(code, {})

    # Price change vs prior analysis
    pct_vs_prior = (close / prior_p - 1) * 100 if close and prior_p and prior_p > 0 else None

    # Price vs 30d MA
    pct_vs_ma = (close / ma30 - 1) * 100 if close and ma30 and ma30 > 0 else None

    # Intraday position (0=at low, 100=at high)
    intraday_pct = ((close - low) / (high - low) * 100) if high and low and high > low else None

    # Williams %R proxy: position in today's range
    # >80 = bullish (closing near high), <20 = bearish
    williams_r = intraday_pct  # same as intraday_pct conceptually

    # Momentum signal
    sig = "NEUTRAL"
    if pct_vs_prior is not None:
        if pct_vs_prior > 20 and (pct_vs_ma or 0) > 5:
            sig = "STRONG_UP"
        elif pct_vs_prior > 10:
            sig = "UP"
        elif pct_vs_prior < -15 and (pct_vs_ma or 0) < -5:
            sig = "STRONG_DOWN"
        elif pct_vs_prior < -8:
            sig = "DOWN"

    momentum.append({
        "code":          code,
        "name":          name_map.get(code, code),
        "close":         close,
        "prior_price":   prior_p,
        "pct_vs_prior":  round(pct_vs_prior, 1) if pct_vs_prior is not None else None,
        "ma30":          ma30,
        "pct_vs_ma":     round(pct_vs_ma, 1) if pct_vs_ma is not None else None,
        "intraday_pct":  round(intraday_pct, 1) if intraday_pct is not None else None,
        "high":          high,
        "low":           low,
        "volume":        volume,
        "signal":        sig,
        "score":         score_map.get(code),
        "conv":          conv_r.get("action","—"),
    })

# ── Analysis ───────────────────────────────────────────────────────────────────
valid = [m for m in momentum if m["pct_vs_prior"] is not None]
strong_up   = [m for m in valid if m["signal"] == "STRONG_UP"]
up          = [m for m in valid if m["signal"] == "UP"]
strong_down = [m for m in valid if m["signal"] == "STRONG_DOWN"]
down        = [m for m in valid if m["signal"] == "DOWN"]

# Top gainers / losers since analysis
top_gainers = sorted(valid, key=lambda x: x["pct_vs_prior"] or 0, reverse=True)[:10]
top_losers  = sorted(valid, key=lambda x: x["pct_vs_prior"] or 0)[:10]

# Stocks now below 30d MA that were previously above (bearish reversal)
below_ma = sorted([m for m in valid if (m["pct_vs_ma"] or 0) < -5], key=lambda x: x["pct_vs_ma"] or 0)
above_ma = sorted([m for m in valid if (m["pct_vs_ma"] or 0) > 5], key=lambda x: -(x["pct_vs_ma"] or 0))

# Conviction picks that have moved significantly (entry opportunities?)
conv_strong = [c for c in ["2376","2357","2887","5871","2801","5876","2408"]]
conviction_updates = []
for code in conv_strong:
    m = next((x for x in valid if x["code"] == code), None)
    if m:
        conviction_updates.append(m)

print(f"\n  Matched {len(momentum)} stocks ({len(valid)} with price comparison)")
print(f"  Strong UP: {len(strong_up)} | UP: {len(up)} | DOWN: {len(down)} | Strong DOWN: {len(strong_down)}")
print("\n  Top gainers since analysis:")
for m in top_gainers[:5]:
    print(f"    {m['code']} {m['name'][:6]}: {m['prior_price']:.1f} → {m['close']:.1f} "
          f"({m['pct_vs_prior']:+.1f}%) | 30dMA: {m['pct_vs_ma']:+.1f}%" if m['pct_vs_ma'] else "")
print("\n  Top losers:")
for m in top_losers[:5]:
    print(f"    {m['code']} {m['name'][:6]}: {m['prior_price']:.1f} → {m['close']:.1f} "
          f"({m['pct_vs_prior']:+.1f}%)")
print("\n  STRONG BUY conviction + price update:")
for m in conviction_updates:
    if m["pct_vs_prior"] is not None:
        print(f"    {m['code']} {m['name'][:6]}: ¥{m['prior_price']:.1f} → ¥{m['close']:.1f} "
              f"({m['pct_vs_prior']:+.1f}%)")

# ── Save JSON ──────────────────────────────────────────────────────────────────
result = {
    "date": TODAY,
    "data_date": data_date,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "may_available": may_avail,
    "total_tracked": len(momentum),
    "valid_comparison": len(valid),
    "signal_counts": {
        "STRONG_UP": len(strong_up),
        "UP": len(up),
        "NEUTRAL": len([m for m in valid if m["signal"] == "NEUTRAL"]),
        "DOWN": len(down),
        "STRONG_DOWN": len(strong_down),
    },
    "top_gainers":    top_gainers[:10],
    "top_losers":     top_losers[:10],
    "above_ma":       above_ma[:10],
    "below_ma":       below_ma[:10],
    "conviction_updates": conviction_updates,
    "all_momentum":   momentum,
}
(REPORT_DIR / "price_momentum.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

# ── PRICE_MOMENTUM.md ──────────────────────────────────────────────────────────
def fv(v, fmt=".1f", fallback="—"):
    if v is None: return fallback
    return format(float(v), fmt)

lines = [
    f"# Price Momentum Analysis — {TODAY} (Iteration 26)",
    f"*Fresh prices: {data_date} | Prior baseline: composite_data.json 原始建立基準*",
    "",
    "---",
    "",
    "## Signal Summary",
    "",
    f"| Signal | Count | Description |",
    f"|--------|-------|-------------|",
    f"| 🚀 STRONG UP | {len(strong_up)} | >+20% vs prior + above 30dMA |",
    f"| 📈 UP | {len(up)} | >+10% vs prior |",
    f"| ⬛ NEUTRAL | {len([m for m in valid if m['signal']=='NEUTRAL'])} | -8% to +10% vs prior |",
    f"| 📉 DOWN | {len(down)} | >-8% vs prior |",
    f"| 💥 STRONG DOWN | {len(strong_down)} | >-15% vs prior + below 30dMA |",
    "",
    "---",
    "",
    "## 🚀 Top Gainers Since Analysis",
    "",
    "| Code | Name | Prior | Now | Change | vs 30dMA | Conv | Score |",
    "|------|------|-------|-----|--------|---------|------|-------|",
]
for m in top_gainers[:10]:
    lines.append(
        f"| **{m['code']}** | {m['name'].split()[0]} | ¥{fv(m['prior_price'])} | "
        f"**¥{fv(m['close'])}** | "
        f"**{'+'if (m['pct_vs_prior'] or 0)>=0 else ''}{fv(m['pct_vs_prior'])}%** | "
        f"{fv(m['pct_vs_ma'],'+.1f')}% | {m['conv']} | {m['score'] or '—'} |"
    )

lines += [
    "",
    "## 💥 Top Losers Since Analysis",
    "",
    "| Code | Name | Prior | Now | Change | vs 30dMA | Conv | Score |",
    "|------|------|-------|-----|--------|---------|------|-------|",
]
for m in top_losers[:10]:
    lines.append(
        f"| **{m['code']}** | {m['name'].split()[0]} | ¥{fv(m['prior_price'])} | "
        f"**¥{fv(m['close'])}** | "
        f"**{fv(m['pct_vs_prior'],'+.1f')}%** | "
        f"{fv(m['pct_vs_ma'],'+.1f')}% | {m['conv']} | {m['score'] or '—'} |"
    )

lines += [
    "",
    "## ✅ STRONG BUY Picks — Current Price vs Entry Thesis",
    "",
    "| Code | Name | Analysis Price | Now | Change | vs 30dMA | Entry Thesis Valid? |",
    "|------|------|---------------|-----|--------|---------|-------------------|",
]
for m in conviction_updates:
    if m["pct_vs_prior"] is None: continue
    valid_thesis = "✅ Still valid" if (m["pct_vs_prior"] or 0) < 20 else "⚠️ Price rose — re-check entry"
    if (m["pct_vs_prior"] or 0) < -10: valid_thesis = "🟢 Better entry — price dipped"
    lines.append(
        f"| **{m['code']}** | {m['name'].split()[0]} | ¥{fv(m['prior_price'])} | "
        f"¥{fv(m['close'])} | "
        f"{'+'if (m['pct_vs_prior'] or 0)>=0 else ''}{fv(m['pct_vs_prior'])}% | "
        f"{fv(m['pct_vs_ma'],'+.1f')}% | {valid_thesis} |"
    )

lines += [
    "",
    "## 📊 Stocks Above/Below 30-Day MA",
    "",
    "### Above 30d MA (momentum +5%):",
    "",
    "| Code | Name | Price | 30dMA | % Above | Signal |",
    "|------|------|-------|-------|---------|--------|",
]
for m in above_ma[:10]:
    lines.append(
        f"| **{m['code']}** | {m['name'].split()[0]} | ¥{fv(m['close'])} | "
        f"¥{fv(m['ma30'])} | **+{fv(m['pct_vs_ma'])}%** | {m['signal']} |"
    )

lines += [
    "",
    "### Below 30d MA (risk -5%):",
    "",
    "| Code | Name | Price | 30dMA | % Below | Signal |",
    "|------|------|-------|-------|---------|--------|",
]
for m in below_ma[:10]:
    lines.append(
        f"| **{m['code']}** | {m['name'].split()[0]} | ¥{fv(m['close'])} | "
        f"¥{fv(m['ma30'])} | **{fv(m['pct_vs_ma'],'+.1f')}%** | {m['signal']} |"
    )

lines += [
    "",
    "---",
    f"May 2026 revenue: {'✅ AVAILABLE — see updated analysis' if may_avail else '❌ Not yet (expected ~June 10)'}",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 26*",
]

(REPORT_DIR / "PRICE_MOMENTUM.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ PRICE_MOMENTUM.md + price_momentum.json")
print(f"  May available: {may_avail}")
print(f"  Data date: {data_date}")
