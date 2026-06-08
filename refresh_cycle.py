#!/usr/bin/env python3
"""
Iteration 25: Daily Refresh Cycle
1. Probe for May 2026 revenue (period 11505) — primary pending data event
2. If available: process full May revenue analysis
3. Always: refresh BWIBBU_ALL for updated P/E / P/B / dividend yields
   (market prices move daily; valuation data from iter 10 is stale)
NOTE: 130-second wait between each TWSE API endpoint call.
"""

import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 130   # ≥120s between endpoint calls

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def wait(label):
    print(f"  ⏳ Waiting {WAIT_SEC}s before next endpoint ({label})…", flush=True)
    time.sleep(WAIT_SEC)

# ── Known stock universe ───────────────────────────────────────────────────────
composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
all_codes  = {s["code"] for s in composite} | {s["code"] for s in expansion}
name_map   = {**{s["code"]: s["name"] for s in composite},
              **{s["code"]: s["name"] for s in expansion}}

# ── STEP 1: Probe for May 2026 revenue ────────────────────────────────────────
print("━" * 60)
print("STEP 1: Probe May 2026 revenue (period 11505)")
url_rev = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"
print(f"  Fetching {url_rev}…", flush=True)
try:
    rev_raw = fetch(url_rev)
    print(f"  Got {len(rev_raw)} rows", flush=True)
    # Check what periods are available
    periods = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    print(f"  Available periods: {periods[-5:]}")
    may_avail = "11505" in periods
    apr_avail = "11504" in periods
    print(f"  May 2026 (11505): {'✅ AVAILABLE' if may_avail else '❌ Not yet'}")
    print(f"  Apr 2026 (11504): {'✅ Available' if apr_avail else '❌ Missing'}")
except Exception as e:
    print(f"  ⚠️ Revenue probe failed: {e}")
    rev_raw = []
    may_avail = False
    apr_avail = False

# ── STEP 2: Process May revenue if available ──────────────────────────────────
may_results = []
if may_avail:
    print("\n  🎉 May 2026 revenue is LIVE — processing…")
    # Get April data for MoM comparison
    apr_rows = {r["公司代號"]: r for r in rev_raw if r.get("資料年月") == "11504"}
    may_rows = {r["公司代號"]: r for r in rev_raw if r.get("資料年月") == "11505"}
    # Get prior year May (11405) for YoY
    prior_may_rows = {r["公司代號"]: r for r in rev_raw if r.get("資料年月") == "11405"}

    def parse_rev(row, field):
        v = row.get(field, "").replace(",", "").strip()
        try: return float(v) if v else None
        except: return None

    REV_FIELD = "營業收入-當月營收"
    CUM_FIELD = "累計營業收入-當月累計營收"

    for code in sorted(all_codes):
        may = may_rows.get(code)
        if not may: continue
        apr = apr_rows.get(code, {})
        py  = prior_may_rows.get(code, {})

        rev_may  = parse_rev(may, REV_FIELD)
        rev_apr  = parse_rev(apr, REV_FIELD)
        rev_py   = parse_rev(py,  REV_FIELD)
        cum_may  = parse_rev(may, CUM_FIELD)   # Jan-May 2026
        cum_py   = parse_rev(py,  CUM_FIELD)   # Jan-May 2025 (field in prior-year May row = Jan-May 2025)

        yoy  = (rev_may / rev_py  - 1) * 100 if rev_may and rev_py  else None
        mom  = (rev_may / rev_apr - 1) * 100 if rev_may and rev_apr else None
        cum_yoy = (cum_may / cum_py - 1) * 100 if cum_may and cum_py else None

        # Revenue in billions NTD
        rev_b = rev_may / 1e6 if rev_may else None
        cum_b = cum_may / 1e6 if cum_may else None

        may_results.append({
            "code": code, "name": name_map.get(code, code),
            "may_rev": rev_may, "rev_b": rev_b, "cum_b": cum_b,
            "may_yoy": round(yoy, 1) if yoy is not None else None,
            "mom": round(mom, 1) if mom is not None else None,
            "cum_yoy": round(cum_yoy, 1) if cum_yoy is not None else None,
        })

    print(f"  Processed {len(may_results)} stocks with May 2026 data")
    if may_results:
        top = sorted(may_results, key=lambda x: x["may_yoy"] or -999, reverse=True)[:5]
        print("  Top 5 May YoY:")
        for r in top:
            print(f"    {r['code']} {r['name']}: {r['may_yoy']:+.1f}% YoY")

# ── STEP 3: Wait then refresh BWIBBU_ALL ──────────────────────────────────────
wait("BWIBBU_ALL")
print("\n━" * 60)
print("STEP 3: Refresh BWIBBU_ALL (updated P/E, P/B, dividend yields)")
url_bwi = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"
print(f"  Fetching {url_bwi}…", flush=True)
try:
    bwi_raw = fetch(url_bwi)
    print(f"  Got {len(bwi_raw)} rows", flush=True)
except Exception as e:
    print(f"  ⚠️ BWIBBU_ALL failed: {e}")
    bwi_raw = []

# Parse BWIBBU fields
# Fields: 代號,名稱,本益比,殖利率(%),股價淨值比
bwi_map = {}
for r in bwi_raw:
    code = r.get("代號","").strip()
    if not code: continue
    def sf(k):
        v = r.get(k,"").replace(",","").strip()
        try: return float(v) if v else None
        except: return None
    bwi_map[code] = {
        "pe":  sf("本益比"),
        "div": sf("殖利率(%)"),
        "pb":  sf("股價淨值比"),
    }

# Compare with prior composite scores
prior_comp = {s["code"]: s for s in composite}
refreshed = []
for code in sorted(all_codes):
    prior = prior_comp.get(code, {})
    new   = bwi_map.get(code, {})
    if not new.get("pe") and not new.get("pb"): continue

    pe_old  = prior.get("fwd_pe")
    pe_new  = new.get("pe")
    div_old = prior.get("div_yield")
    div_new = new.get("div")
    pb_old  = prior.get("pb")
    pb_new  = new.get("pb")

    delta_pe = round(pe_new - pe_old, 2) if pe_new and pe_old else None
    refreshed.append({
        "code": code,
        "name": name_map.get(code, code),
        "pe_old": pe_old, "pe_new": pe_new, "delta_pe": delta_pe,
        "div_old": div_old, "div_new": div_new,
        "pb_old": pb_old, "pb_new": pb_new,
    })

print(f"  Updated {len(refreshed)} stocks with fresh BWIBBU data")

# Biggest P/E expansions and contractions
pe_changed = [r for r in refreshed if r["delta_pe"] is not None]
if pe_changed:
    expanded   = sorted(pe_changed, key=lambda x: x["delta_pe"] or 0,  reverse=True)[:5]
    contracted = sorted(pe_changed, key=lambda x: x["delta_pe"] or 0)[:5]
    print("\n  Biggest P/E expansions (price rose more than earnings implied):")
    for r in expanded:
        print(f"    {r['code']} {r['name'][:6]}: {r['pe_old']:.1f}x → {r['pe_new']:.1f}x ({r['delta_pe']:+.2f}x)")
    print("  Biggest P/E contractions:")
    for r in contracted:
        print(f"    {r['code']} {r['name'][:6]}: {r['pe_old']:.1f}x → {r['pe_new']:.1f}x ({r['delta_pe']:+.2f}x)")

# High div yield picks (≥4.5%)
high_div = [r for r in refreshed if (r["div_new"] or 0) >= 4.5]
high_div.sort(key=lambda x: x["div_new"] or 0, reverse=True)
print(f"\n  Stocks with div yield ≥4.5%: {len(high_div)}")
for r in high_div[:8]:
    old_str = f" (was {r['div_old']:.2f}%)" if r["div_old"] else ""
    print(f"    {r['code']} {r['name'][:6]}: {r['div_new']:.2f}%{old_str}")

# ── STEP 4: Save refresh data ─────────────────────────────────────────────────
refresh_result = {
    "date": TODAY,
    "refresh_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "may_available": may_avail,
    "may_results": may_results,
    "bwibbu_updated": len(refreshed),
    "bwibbu_refreshed": refreshed,
    "high_div_picks": [r["code"] for r in high_div],
    "pe_expanded_top5": [{"code":r["code"],"name":r["name"],"delta_pe":r["delta_pe"]} for r in (pe_changed and expanded or [])],
    "pe_contracted_top5": [{"code":r["code"],"name":r["name"],"delta_pe":r["delta_pe"]} for r in (pe_changed and contracted or [])],
}
(REPORT_DIR / "daily_refresh2.json").write_text(
    json.dumps(refresh_result, ensure_ascii=False, indent=2), encoding="utf-8")

# ── STEP 5: Generate REFRESH_REPORT.md ───────────────────────────────────────
lines = [
    f"# Daily Refresh Report — {TODAY} (Iteration 25)",
    "",
    f"**Run time:** {datetime.now().strftime('%H:%M')}",
    "",
    "---",
    "",
    "## May 2026 Revenue Status",
    "",
    f"**Period 11505 (May 2026):** {'✅ AVAILABLE — processed below' if may_avail else '❌ Not yet published (expected ~June 10, 2026)'}",
    "",
]

if may_avail and may_results:
    sorted_may = sorted(may_results, key=lambda x: x["may_yoy"] or -999, reverse=True)
    lines += [
        "### May 2026 Top Revenue Growth (YoY)",
        "",
        "| Code | Name | Rev YoY | MoM | Jan-May Cum YoY | Rev (B NTD) |",
        "|------|------|---------|-----|----------------|-------------|",
    ]
    for r in sorted_may[:20]:
        lines.append(
            f"| **{r['code']}** | {r['name'].split()[0]} | "
            f"{'**+'+str(r['may_yoy'])+'%**' if (r['may_yoy'] or 0)>20 else (str(r['may_yoy'])+'%' if r['may_yoy'] else '—')} | "
            f"{('+' if (r['mom'] or 0)>=0 else '')+str(r['mom'])+'%' if r['mom'] else '—'} | "
            f"{('+' if (r['cum_yoy'] or 0)>=0 else '')+str(r['cum_yoy'])+'%' if r['cum_yoy'] else '—'} | "
            f"{'¥'+str(round(r['rev_b'],1))+'B' if r['rev_b'] else '—'} |"
        )
    lines.append("")
else:
    lines += [
        "> May 2026 revenue data not yet available from TWSE t187ap05_L.",
        "> April 2026 (11504) remains the latest period. Check again ~June 10.",
        "",
    ]

lines += [
    "---",
    "",
    "## BWIBBU_ALL Valuation Refresh",
    "",
    f"Updated {len(refreshed)} stocks with fresh P/E, P/B, and dividend yield data.",
    "",
    "### Largest P/E Changes",
    "",
    "| Direction | Code | Name | Old P/E | New P/E | Change |",
    "|-----------|------|------|---------|---------|--------|",
]

for r in (pe_changed and expanded[:5] or []):
    lines.append(f"| 📈 Expansion | **{r['code']}** | {r['name'].split()[0]} | {r['pe_old']:.1f}x | {r['pe_new']:.1f}x | **+{r['delta_pe']:.2f}x** |")
for r in (pe_changed and contracted[:5] or []):
    lines.append(f"| 📉 Contraction | **{r['code']}** | {r['name'].split()[0]} | {r['pe_old']:.1f}x | {r['pe_new']:.1f}x | **{r['delta_pe']:.2f}x** |")

lines += [
    "",
    "### High Dividend Yield Stocks (≥4.5%)",
    "",
    "| Code | Name | Div Yield | Prior Yield | Change |",
    "|------|------|-----------|------------|--------|",
]
for r in high_div[:10]:
    chg = ""
    if r["div_old"] and r["div_new"]:
        d = r["div_new"] - r["div_old"]
        chg = f"**{'+' if d>=0 else ''}{d:.2f}%**"
    lines.append(f"| **{r['code']}** | {r['name'].split()[0]} | **{r['div_new']:.2f}%** | {r['div_old']:.2f}% | {chg} |")

lines += [
    "",
    "---",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 25*",
]

(REPORT_DIR / "REFRESH_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ REFRESH_REPORT.md + daily_refresh2.json")
print(f"  May 2026 available: {may_avail}")
print(f"  BWIBBU refreshed: {len(refreshed)} stocks")
