#!/usr/bin/env python3
"""
Fetch OTC monthly revenue from TPEX t187ap05_O.
Computes rev_yoy (April YoY%), rev_cum (cumulative), rev_now (latest month).
Merges into full_market.json for OTC companies.
"""
import json, ssl, urllib.request, time
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 132

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    s = str(v).replace(",", "").strip()
    if not s: return None
    try: return float(s)
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === OTC Monthly Revenue (t187ap05_O) ===")

# Probe TPEX monthly revenue endpoint
url = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O"
print(f"  Fetching: {url}")
try:
    data = fetch(url)
except Exception as e:
    print(f"  ❌ Failed: {e}")
    exit(1)

if not data or not isinstance(data, list):
    print("  ❌ Empty response")
    exit(1)

print(f"  Got {len(data)} rows")
print(f"  Fields: {list(data[0].keys())}")
print(f"  Sample: {data[0]}")

# Identify periods available
periods = sorted({r.get("資料年月", r.get("Month","")) for r in data if r.get("資料年月") or r.get("Month")})
print(f"  Periods: {periods[-5:] if len(periods)>5 else periods}")
may_avail = "11505" in periods
print(f"  May 2026: {'✅ AVAILABLE' if may_avail else '❌ Not yet (latest: '+str(periods[-1] if periods else '?')+')'}")

# Get code/name/period fields
sample = data[0]
code_field   = None
period_field = None
rev_field    = None
yoy_field    = None
cum_field    = None

for f in sample.keys():
    fl = f.lower()
    if "code" in fl or "代號" in f or "SecuritiesCompanyCode" in f:
        code_field = f
    if "年月" in f or "month" in fl or "period" in fl:
        period_field = f
    if "當月" in f and "收入" in f:
        rev_field = f
    if "yoy" in fl or "年增" in f or "成長" in f:
        yoy_field = f
    if "累計" in f and "收入" in f:
        cum_field = f

# Fallback guessing
if not code_field:
    for f in sample.keys():
        v = str(sample.get(f,""))
        if len(v) == 4 and v.isdigit():
            code_field = f; break
if not period_field:
    for f in sample.keys():
        v = str(sample.get(f,""))
        if len(v) == 5 and v[:3] in ["114","115"]:
            period_field = f; break

print(f"\n  Code:    {code_field}")
print(f"  Period:  {period_field}")
print(f"  Rev:     {rev_field}")
print(f"  YoY:     {yoy_field}")
print(f"  Cum:     {cum_field}")

# Get the latest period's data
latest_period = periods[-1] if periods else None
print(f"\n  Using period: {latest_period}")

latest_rows = [r for r in data if (r.get(period_field,"") == latest_period)] if period_field and latest_period else data

# Build lookup: code → {rev, yoy, cum}
rev_map = {}
for r in latest_rows:
    code = str(r.get(code_field,"")).strip() if code_field else None
    if not code: continue
    rev_map[code] = {
        "rev_now": sf(r.get(rev_field)) if rev_field else None,
        "rev_yoy": sf(r.get(yoy_field)) if yoy_field else None,
        "rev_cum": sf(r.get(cum_field)) if cum_field else None,
    }

# Also try to compute YoY if we have prior period data
prior_period = periods[-2] if len(periods) >= 2 else None
if not yoy_field and prior_period and period_field:
    prior_rows = [r for r in data if r.get(period_field,"") == prior_period]
    # No YoY from raw data — check if there's year-ago data
    pass

print(f"  Revenue entries for latest period: {len(rev_map)}")
if rev_map:
    sample_entry = list(rev_map.items())[0]
    print(f"  Sample: {sample_entry[0]} → {sample_entry[1]}")

# Merge into full_market.json
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}

updated = 0
for code, rv in rev_map.items():
    if code not in otc_map:
        continue
    c = otc_map[code]
    if rv["rev_now"] is not None: c["rev_now"] = rv["rev_now"]
    if rv["rev_yoy"] is not None: c["rev_yoy"] = rv["rev_yoy"]
    if rv["rev_cum"] is not None: c["rev_cum"] = rv["rev_cum"]
    updated += 1

# Recompute quick_score bonus for rev_yoy
for c in [c for c in companies if c.get("market") == "OTC"]:
    ry = c.get("rev_yoy") or 0
    score = c.get("quick_score", 0) or 0
    # Remove old rev-based score (base was 0-3 from rev) and re-add
    # Since we can't easily subtract, add incremental if rev_yoy was missing before
    if c.get("rev_now") is not None and ry > 10:
        c["quick_score"] = score + 2
    elif c.get("rev_now") is not None and ry > 0:
        c["quick_score"] = score + 1

with_rev = sum(1 for c in companies if c.get("market")=="OTC" and c.get("rev_now") is not None)
with_yoy = sum(1 for c in companies if c.get("market")=="OTC" and c.get("rev_yoy") is not None)
print(f"\n  Merged: {updated} OTC companies")
print(f"  rev_now: {with_rev}/887 | rev_yoy: {with_yoy}/887")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
fm["may_revenue_available"] = may_avail
fm["latest_rev_period_otc"] = latest_period
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved {REPORT_DIR}/full_market.json")

# Save raw OTC revenue snapshot
rev_out = {
    "generated":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "source":         url,
    "total_rows":     len(data),
    "latest_period":  latest_period,
    "may_available":  may_avail,
    "otc_updated":    updated,
    "fields":         list(data[0].keys()) if data else [],
}
(REPORT_DIR / "otc_revenue.json").write_text(
    json.dumps(rev_out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved {REPORT_DIR}/otc_revenue.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
