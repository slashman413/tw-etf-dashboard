#!/usr/bin/env python3
"""
Iteration 27: Fresh 30d MA Refresh + Updated Technical Signals
1. Probe May 2026 revenue (11505)
2. Wait 130s
3. Fetch STOCK_DAY_AVG_ALL — fresh 30d moving averages
4. Cross with current prices (from price_momentum.json)
5. Recompute above/below MA signals for all 62 stocks
Generates: ma_refresh.json + MA_REFRESH.md
"""

import json, ssl, time, urllib.request, sys
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
SKIP_WAIT    = "--skip-wait"    in sys.argv
SKIP_REVENUE = "--skip-revenue" in sys.argv
WAIT_SEC     = 0 if SKIP_WAIT else 130

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    s = str(v).replace(",", "").strip()
    try: return float(s) if s else None
    except: return None

# Load prior data
composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
momentum   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
conviction = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}
all_codes = set(name_map.keys())

# Current prices from momentum
price_map = {m["code"]: m["close"] for m in momentum.get("all_momentum", []) if m.get("close")}

# Conviction
conv_map = {r["code"]: r.get("action", "—") for r in conviction.get("all_ranked", [])}

# ── STEP 1: Probe May 2026 revenue ─────────────────────────────────────────
may_avail = False
rev_raw   = []
if SKIP_REVENUE:
    print("STEP 1: Skipping revenue probe (--skip-revenue)")
else:
    print("STEP 1: Probe May 2026 revenue (11505)")
    try:
        rev_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
        periods  = sorted({r.get("資料年月", "") for r in rev_raw if r.get("資料年月")})
        may_avail = "11505" in periods
        print(f"  Latest period: {periods[-1]} | May 2026: {'✅ AVAILABLE' if may_avail else '❌ Not yet'}")
    except Exception as e:
        print(f"  ⚠️ Revenue probe failed: {e}")

# ── STEP 2: Wait ────────────────────────────────────────────────────────────
print(f"\n⏳ Waiting {WAIT_SEC}s before STOCK_DAY_AVG_ALL…", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 3: Fetch STOCK_DAY_AVG_ALL ─────────────────────────────────────────
print("\nSTEP 3: Fetch STOCK_DAY_AVG_ALL (fresh 30d MA)")
try:
    avg_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL")
    print(f"  Got {len(avg_raw)} rows")
    data_date = avg_raw[0].get("Date", "?") if avg_raw else "?"
    print(f"  Date: {data_date}")
except Exception as e:
    print(f"  ⚠️ STOCK_DAY_AVG_ALL failed: {e}")
    avg_raw   = []
    data_date = "?"

# Stale-date guard: don't overwrite newer MA data with older API response
_existing_ma = REPORT_DIR / "ma_refresh.json"
if _existing_ma.exists() and data_date != "?":
    try:
        _prev = json.loads(_existing_ma.read_text(encoding="utf-8"))
        _prev_date = _prev.get("data_date", "")
        if _prev_date and data_date <= _prev_date:
            print(f"  MA data not newer ({data_date} <= {_prev_date}) — skipping write")
            import sys as _sys; _sys.exit(0)
    except Exception:
        pass

ma_map = {}
for r in avg_raw:
    code = r.get("Code", "").strip()
    if not code: continue
    ma = sf(r.get("AveragePrice") or r.get("MovingAverage") or r.get("收盤價均價"))
    # try all possible field names
    for field in r:
        if "verage" in field or "均" in field:
            v = sf(r[field])
            if v and v > 0:
                ma = v
                break
    if ma:
        ma_map[code] = {"ma30": ma, "date": data_date}

print(f"  Mapped {len(ma_map)} stocks with 30d MA")
# Show sample to confirm field name
if avg_raw:
    sample = avg_raw[0]
    print(f"  Sample fields: {list(sample.keys())}")
    print(f"  Sample: {sample}")

# ── STEP 4: Compute updated MA signals ──────────────────────────────────────
results = []
for code in sorted(all_codes):
    close = price_map.get(code)
    ma_r  = ma_map.get(code, {})
    ma30  = ma_r.get("ma30")

    pct_vs_ma = None
    if close and ma30 and ma30 > 0:
        pct_vs_ma = round((close / ma30 - 1) * 100, 2)

    sig = "NEUTRAL"
    if pct_vs_ma is not None:
        if pct_vs_ma > 10:   sig = "STRONG_ABOVE"
        elif pct_vs_ma > 3:  sig = "ABOVE"
        elif pct_vs_ma < -10:sig = "STRONG_BELOW"
        elif pct_vs_ma < -3: sig = "BELOW"

    results.append({
        "code":       code,
        "name":       name_map.get(code, code),
        "close":      close,
        "ma30":       ma30,
        "pct_vs_ma":  pct_vs_ma,
        "signal":     sig,
        "score":      score_map.get(code),
        "conv":       conv_map.get(code, "—"),
    })

valid   = [r for r in results if r["pct_vs_ma"] is not None]
above   = sorted([r for r in valid if r["pct_vs_ma"] > 3],  key=lambda x: -x["pct_vs_ma"])
below   = sorted([r for r in valid if r["pct_vs_ma"] < -3], key=lambda x:  x["pct_vs_ma"])
strong_above = [r for r in valid if r["signal"] == "STRONG_ABOVE"]
strong_below = [r for r in valid if r["signal"] == "STRONG_BELOW"]

print(f"\n  Valid: {len(valid)} | Above MA: {len(above)} | Below MA: {len(below)}")
print(f"  Strong above (>+10%): {len(strong_above)} | Strong below (<-10%): {len(strong_below)}")
print("\n  Top above MA:")
for r in above[:5]:
    print(f"    {r['code']} {r['name'][:6]}: ¥{r['close']:.1f} vs MA ¥{r['ma30']:.1f} ({r['pct_vs_ma']:+.1f}%)")
print("\n  Most below MA:")
for r in below[:5]:
    print(f"    {r['code']} {r['name'][:6]}: ¥{r['close']:.1f} vs MA ¥{r['ma30']:.1f} ({r['pct_vs_ma']:+.1f}%)")

# ── Save JSON ────────────────────────────────────────────────────────────────
out = {
    "date":        TODAY,
    "data_date":   data_date,
    "fetch_ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "may_available": may_avail,
    "total":       len(results),
    "valid":       len(valid),
    "above_ma":    len(above),
    "below_ma":    len(below),
    "strong_above": strong_above,
    "strong_below": strong_below,
    "above_list":  above,
    "below_list":  below,
    "all_results": results,
}
(REPORT_DIR / "ma_refresh.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# ── MA_REFRESH.md ────────────────────────────────────────────────────────────
def fv(v, fmt=".1f", fallback="—"):
    if v is None: return fallback
    return format(float(v), fmt)

lines = [
    f"# 30-Day MA Refresh — {TODAY} (Iteration 27)",
    f"*MA data: {data_date} | Prices: {momentum.get('data_date', TODAY)} close*",
    "",
    f"**{len(above)} above MA** | **{len(below)} below MA** | {len(valid)} total mapped",
    "",
    "---",
    "",
    "## 📈 Stocks Above 30d MA",
    "",
    "| Code | Name | Price | 30dMA | % Above | Signal | Conv | Score |",
    "|------|------|-------|-------|---------|--------|------|-------|",
]
for r in above[:20]:
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | ¥{fv(r['close'])} | "
        f"¥{fv(r['ma30'])} | **+{fv(r['pct_vs_ma'])}%** | {r['signal']} | {r['conv']} | {r['score'] or '—'} |"
    )

lines += [
    "",
    "## 📉 Stocks Below 30d MA",
    "",
    "| Code | Name | Price | 30dMA | % Below | Signal | Conv | Score |",
    "|------|------|-------|-------|---------|--------|------|-------|",
]
for r in below[:20]:
    lines += [
        f"| **{r['code']}** | {r['name'].split()[0]} | ¥{fv(r['close'])} | "
        f"¥{fv(r['ma30'])} | **{fv(r['pct_vs_ma'],'+.1f')}%** | {r['signal']} | {r['conv']} | {r['score'] or '—'} |"
    ]

lines += [
    "",
    "---",
    f"May 2026 revenue: {'✅ AVAILABLE' if may_avail else '❌ Not yet (expected ~June 10)'}",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 27*",
]
(REPORT_DIR / "MA_REFRESH.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ ma_refresh.json + MA_REFRESH.md written")
print(f"  May available: {may_avail} | data_date: {data_date}")
