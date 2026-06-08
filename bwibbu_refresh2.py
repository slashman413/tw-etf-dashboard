#!/usr/bin/env python3
"""
Iteration 29: BWIBBU Refresh Round 2 + Grand Unified Update
1. Probe May 2026 revenue (11505)
2. Wait 130s
3. Fetch BWIBBU_ALL for latest P/E, yield, P/B (June 5/6 close)
4. Update grand_unified.json with fresh valuation data
5. Rebuild key metrics
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

# Load existing data
composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
bwibbu_old = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
grand_old  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

name_map = {**{s["code"]: s["name"] for s in composite},
            **{s["code"]: s["name"] for s in expansion}}
all_codes = set(name_map.keys())

# Old BWIBBU for comparison
old_bwi_map = {r["code"]: r for r in bwibbu_old.get("all_refreshed", [])}

# ── STEP 1: Probe May 2026 revenue ─────────────────────────────────────────
print("STEP 1: Probe May 2026 revenue (11505)")
try:
    rev_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods  = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    latest_period = periods[-1] if periods else "?"
    print(f"  Latest period: {latest_period} | May 2026: {'✅ AVAILABLE!' if may_avail else '❌ Not yet'}")
except Exception as e:
    print(f"  ⚠️ Revenue probe failed: {e}")
    may_avail = False
    rev_raw = []

# ── STEP 2: Wait ────────────────────────────────────────────────────────────
print(f"\n⏳ Waiting {WAIT_SEC}s before BWIBBU_ALL…", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 3: Fetch BWIBBU_ALL ────────────────────────────────────────────────
print("\nSTEP 3: Fetch BWIBBU_ALL (fresh P/E, yield, P/B)")
try:
    bwi_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    print(f"  Got {len(bwi_raw)} rows")
    if bwi_raw:
        sample = bwi_raw[0]
        print(f"  Sample fields: {list(sample.keys())}")
        print(f"  Sample: {sample}")
except Exception as e:
    print(f"  ⚠️ BWIBBU_ALL failed: {e}")
    bwi_raw = []

# Build new map
new_bwi_map = {}
for r in bwi_raw:
    code = r.get("Code","").strip()
    if not code: continue
    new_bwi_map[code] = r

data_date = bwi_raw[0].get("Date","?") if bwi_raw else "?"
print(f"  Data date: {data_date} | Mapped {len(new_bwi_map)} entries")

# ── STEP 4: Build refreshed list ────────────────────────────────────────────
refreshed = []
changes   = []

for code in sorted(all_codes):
    nr  = new_bwi_map.get(code, {})
    oldr= old_bwi_map.get(code, {})

    pe_new  = sf(nr.get("PEratio"))
    pb_new  = sf(nr.get("PBratio"))
    div_new = sf(nr.get("DividendYield"))

    pe_old  = sf(oldr.get("pe_new"))
    div_old = sf(oldr.get("div_yield"))

    if not (pe_new or div_new): continue

    pe_chg  = round(pe_new - pe_old, 1) if pe_new and pe_old else None
    div_chg = round(div_new - div_old, 2) if div_new and div_old else None

    entry = {
        "code":     code,
        "name":     name_map.get(code, code),
        "pe_new":   pe_new,
        "pe_old":   pe_old,
        "pe_chg":   pe_chg,
        "pb_new":   pb_new,
        "div_yield": div_new,
        "div_old":  div_old,
        "div_chg":  div_chg,
    }
    refreshed.append(entry)

    # Flag significant changes
    if pe_chg and abs(pe_chg) > 2:
        changes.append(entry)

changes.sort(key=lambda x: abs(x["pe_chg"] or 0), reverse=True)

print(f"\n  Matched {len(refreshed)} stocks | Significant P/E changes: {len(changes)}")
if changes:
    print("  Top P/E changes:")
    for c in changes[:8]:
        print(f"    {c['code']} {c['name'][:8]}: {c['pe_old']:.1f}x → {c['pe_new']:.1f}x ({c['pe_chg']:+.1f})")

# ── STEP 5: Save updated bwibbu_fresh.json ──────────────────────────────────
new_bwibbu = {
    "date":          TODAY,
    "data_date":     data_date,
    "fetch_ts":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "may_available": may_avail,
    "total_matched": len(refreshed),
    "significant_changes": changes,
    "all_refreshed": refreshed,
}
(REPORT_DIR / "bwibbu_fresh.json").write_text(
    json.dumps(new_bwibbu, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ bwibbu_fresh.json updated (date: {data_date})")

# ── STEP 6: Update grand_unified with fresh P/E scores ──────────────────────
bwi2_map = {r["code"]: r for r in refreshed}

def recalc_val(pe, div_yield):
    if pe is not None and pe > 0:
        if pe < 10:   v = 25
        elif pe < 15: v = 22
        elif pe < 20: v = 18
        elif pe < 30: v = 12
        elif pe < 50: v = 6
        else:         v = 2
    else:
        v = 10
    if div_yield is not None and div_yield >= 4.5: v = min(25, v + 3)
    if div_yield is not None and div_yield >= 6.0: v = min(25, v + 2)
    return v

updated = []
for r in grand_old.get("all_ranked", []):
    code  = r["code"]
    bw    = bwi2_map.get(code, {})
    pe    = sf(bw.get("pe_new")) or sf(bw.get("pe_old")) or r.get("pe")
    div   = sf(bw.get("div_yield")) or r.get("div_yield")

    new_val_pts = recalc_val(pe, div)
    old_val_pts = r.get("val_pts", 10)
    delta_val   = new_val_pts - old_val_pts

    new_grand = round(r["grand"] + delta_val, 1)
    updated.append({**r, "pe": pe, "div_yield": div,
                    "val_pts": new_val_pts, "grand": new_grand})

updated.sort(key=lambda x: -x["grand"])

# Re-assign finals
for r in updated:
    bull_signs = r.get("bull_signs") or 0
    g = r["grand"]
    if g >= 70 and bull_signs >= 3: r["final"] = "🚀 TRIPLE CONFIRMED"
    elif g >= 65:                    r["final"] = "✅ STRONG BUY"
    elif g >= 55:                    r["final"] = "📈 BUY"
    elif g >= 40:                    r["final"] = "👀 WATCH"
    elif g >= 25:                    r["final"] = "⬛ HOLD"
    else:                            r["final"] = "❌ REDUCE"

triple = [r for r in updated if "TRIPLE" in r["final"]]
strong = [r for r in updated if r["final"] == "✅ STRONG BUY"]
buy    = [r for r in updated if r["final"] == "📈 BUY"]

print("\n=== Updated Grand Unified Top 10 ===")
for r in updated[:10]:
    print(f"  {r['code']} {r['name'][:10]:<12} {r['grand']:>5.1f} | {r['final']}")

new_grand = {
    "date":              TODAY,
    "data_date":         data_date,
    "fetch_ts":          datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":             len(updated),
    "triple_confirmed":  triple,
    "strong_buy":        strong,
    "buy":               buy,
    "all_ranked":        updated,
}
(REPORT_DIR / "grand_unified.json").write_text(
    json.dumps(new_grand, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ grand_unified.json updated | Triple: {len(triple)} | SB: {len(strong)} | Buy: {len(buy)}")
print(f"  May available: {may_avail}")
