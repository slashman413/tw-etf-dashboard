#!/usr/bin/env python3
"""
Iteration 36: Fresh BWIBBU_ALL + May Revenue Probe
1. Probe May 2026 revenue (11505)
2. Wait 130s
3. Fetch BWIBBU_ALL (P/E, DividendYield, PBratio)
4. Update bwibbu_fresh.json + recalculate grand valuation scores
5. Update sector_analysis.json PE/yield
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
    try: return float(str(v).replace(",","").strip())
    except: return None

comp       = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp        = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
grand_old  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
bwi_old    = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
sector_old = json.loads((REPORT_DIR / "sector_analysis.json").read_text(encoding="utf-8"))

name_map = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}
all_codes = set(name_map.keys())
old_bwi_map = {r["code"]: r for r in bwi_old.get("all_refreshed", [])}

# ── STEP 1: Probe May revenue ─────────────────────────────────────────────────
print("STEP 1: Probe May 2026 revenue (11505)")
try:
    rev_raw   = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods   = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    print(f"  Latest period: {periods[-1]} | May 2026: {'✅ AVAILABLE!' if may_avail else '❌ Not yet'}")
except Exception as e:
    print(f"  Revenue probe failed: {e}")
    may_avail = False; rev_raw = []

print(f"\n⏳ Waiting {WAIT_SEC}s before BWIBBU_ALL…", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 3: Fetch BWIBBU_ALL ─────────────────────────────────────────────────
print("\nSTEP 3: Fetch BWIBBU_ALL (P/E, Yield, PBR)")
try:
    bwi_raw   = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    data_date = bwi_raw[0].get("Date","?") if bwi_raw else "?"
    print(f"  Got {len(bwi_raw)} rows | Date: {data_date}")
except Exception as e:
    print(f"  BWIBBU_ALL failed: {e}")
    bwi_raw = []; data_date = "?"

bwi_idx = {r.get("Code","").strip(): r for r in bwi_raw if r.get("Code")}

# ── STEP 4: Build refreshed records ──────────────────────────────────────────
all_refreshed = []
changed = []
for code in sorted(all_codes):
    bw     = bwi_idx.get(code, {})
    old    = old_bwi_map.get(code, {})
    pe_new = sf(bw.get("PEratio"))
    pb_new = sf(bw.get("PBratio"))
    dy_new = sf(bw.get("DividendYield"))
    pe_old = old.get("pe_new")
    dy_old = old.get("div_yield")
    pe_chg = round(pe_new - pe_old, 2) if pe_new and pe_old else None

    rec = {
        "code": code, "name": name_map.get(code, code),
        "pe_new": round(pe_new, 2) if pe_new else None,
        "pe_old": pe_old,
        "pe_chg": pe_chg,
        "pb_new": round(pb_new, 2) if pb_new else None,
        "div_yield": round(dy_new, 2) if dy_new else None,
        "div_old": dy_old,
        "div_chg": round(dy_new - dy_old, 2) if dy_new and dy_old else None,
    }
    all_refreshed.append(rec)
    if pe_chg and abs(pe_chg) > 5:
        changed.append(rec)

matched = sum(1 for r in all_refreshed if r["pe_new"])
print(f"  Matched {matched}/{len(all_codes)} | Significant PE changes: {len(changed)}")
if changed:
    for c in sorted(changed, key=lambda x: abs(x["pe_chg"] or 0), reverse=True)[:5]:
        print(f"    {c['code']} {c['name'][:8]}: PE {c['pe_old']} → {c['pe_new']} (Δ{c['pe_chg']:+.1f})")

(REPORT_DIR / "bwibbu_fresh.json").write_text(
    json.dumps({**bwi_old, "data_date": data_date,
                "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "may_available": may_avail,
                "total_matched": matched,
                "significant_changes": changed,
                "all_refreshed": all_refreshed},
               ensure_ascii=False, indent=2), encoding="utf-8")

# ── STEP 5: Recalculate valuation scores in grand_unified ─────────────────────
bwi_map2 = {r["code"]: r for r in all_refreshed}
grand_upd = []
for r in grand_old.get("all_ranked", []):
    code = r["code"]
    bw   = bwi_map2.get(code, {})
    pe   = bw.get("pe_new")
    dy   = bw.get("div_yield") or 0

    # Valuation scoring: PE tiers + dividend bonus
    if   pe and pe < 10:  v_pts = 25
    elif pe and pe < 15:  v_pts = 22
    elif pe and pe < 20:  v_pts = 18
    elif pe and pe < 30:  v_pts = 12
    elif pe and pe < 50:  v_pts = 6
    elif pe:              v_pts = 2
    else:                 v_pts = r.get("val_pts", 10)  # keep old if no data

    if dy >= 6:   v_pts = min(25, v_pts + 2)
    elif dy >= 4.5: v_pts = min(25, v_pts + 1)

    old_v   = r.get("val_pts", 10)
    delta_v = v_pts - old_v
    new_grand = round(r["grand"] + delta_v, 1)
    grand_upd.append({**r, "val_pts": v_pts, "grand": new_grand,
                      "pe_live": pe, "dy_live": dy})

grand_upd.sort(key=lambda x: -x["grand"])
for r in grand_upd:
    bs = r.get("bull_signs") or 0; g = r["grand"]
    if   g >= 70 and bs >= 3: r["final"] = "🚀 TRIPLE CONFIRMED"
    elif g >= 65:              r["final"] = "✅ STRONG BUY"
    elif g >= 55:              r["final"] = "📈 BUY"
    elif g >= 40:              r["final"] = "👀 WATCH"
    elif g >= 25:              r["final"] = "⬛ HOLD"
    else:                      r["final"] = "❌ REDUCE"

triple = [r for r in grand_upd if "TRIPLE" in r["final"]]
strong = [r for r in grand_upd if r["final"] == "✅ STRONG BUY"]
buy    = [r for r in grand_upd if r["final"] == "📈 BUY"]

print(f"\n  Grand Unified updated | Triple:{len(triple)} SB:{len(strong)} Buy:{len(buy)}")
print("  Top 5:")
for r in grand_upd[:5]:
    print(f"    {r['code']} {r['name'][:10]}: {r['grand']:.1f} PE={r.get('pe_live','?')} Yield={r.get('dy_live','?')}% | {r['final']}")

(REPORT_DIR / "grand_unified.json").write_text(
    json.dumps({**grand_old,
                "data_date": data_date,
                "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "triple_confirmed": triple, "strong_buy": strong, "buy": buy,
                "all_ranked": grand_upd},
               ensure_ascii=False, indent=2), encoding="utf-8")

# ── STEP 6: Update sector PE/yield ───────────────────────────────────────────
bwi_quick = {r["code"]: r for r in all_refreshed}
for sec in sector_old.get("sectors", []):
    pes, yields = [], []
    for s in sec.get("stocks", []):
        bw = bwi_quick.get(s["code"], {})
        pe = bw.get("pe_new"); dy = bw.get("div_yield")
        s["pe"] = round(pe,1) if pe else None
        s["div_yield"] = round(dy,2) if dy else None
        if pe and 0 < pe < 200: pes.append(pe)
        if dy and 0 < dy < 20:  yields.append(dy)
    sec["avg_pe"]    = round(sum(pes)/len(pes),1) if pes else None
    sec["avg_yield"] = round(sum(yields)/len(yields),2) if yields else None

sector_old["fetch_ts"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "sector_analysis.json").write_text(
    json.dumps(sector_old, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n✓ bwibbu_fresh.json + grand_unified.json + sector_analysis.json updated")
print(f"  data_date: {data_date} | may_available: {may_avail}")
