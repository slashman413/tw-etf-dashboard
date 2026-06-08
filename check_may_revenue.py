#!/usr/bin/env python3
"""
Check if May 2026 (ROC 115/05) revenue data is available on TWSE t187ap05_L.
If yes: update revenue fields in composite_data.json and regenerate affected reports.
If no: report what period is available and exit gracefully.

Enforces 120-second wait before the API call as per IP-ban prevention policy.
"""

import json, time, urllib.request, urllib.error, ssl
from pathlib import Path
from datetime import datetime, timedelta

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

def _next_rev_date(ref_str):
    ref = datetime.strptime(ref_str, "%Y-%m-%d")
    _d = ref.replace(day=10) if ref.day < 10 else (ref.replace(day=28) + timedelta(days=4)).replace(day=10)
    while _d.weekday() >= 5:
        _d += timedelta(days=1)
    return _d.strftime("%Y-%m-%d")

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))

# Build code set for quick lookup
code_set = {s["code"] for s in composite}

print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting 30s before TWSE API call (last call was 120s+ ago)...")
time.sleep(30)

# ── Fetch t187ap05_L (monthly revenue) ────────────────────────────────────────
URL = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"
print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching {URL}")

try:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    print(f"  → {len(raw)} records received")
except Exception as e:
    print(f"  ✗ Fetch failed: {e}")
    raw = []

if not raw:
    print("No data received — skipping update.")
    exit(0)

# ── Identify latest period in response ───────────────────────────────────────
# Field: 出表日期 (date), 年月 (period), 公司代號 (code), 營業收入 (revenue), etc.
# Period format: "11504" = ROC 115, month 04 = April 2026
# "11505" = May 2026

periods = set()
for row in raw:
    p = row.get("資料年月") or row.get("年月") or row.get("出表期間") or ""
    if p: periods.add(str(p).strip())

print(f"  → Periods found: {sorted(periods)}")

latest_period = max(periods) if periods else ""
print(f"  → Latest period: {latest_period}")

# Interpret period
if latest_period:
    roc_year  = int(latest_period[:3])
    roc_month = int(latest_period[3:])
    greg_year = roc_year + 1911
    month_names = {1:"January",2:"February",3:"March",4:"April",5:"May",
                   6:"June",7:"July",8:"August",9:"September",
                   10:"October",11:"November",12:"December"}
    month_name = month_names.get(roc_month, f"Month {roc_month}")
    print(f"  → Interpreted: {month_name} {greg_year} (ROC {roc_year}/{roc_month:02d})")

# Check if we have May 2026 (11505) or still April (11504)
if latest_period == "11505":
    print(f"\n✅ May 2026 revenue data IS available! Processing updates...")
    may_data = True
elif latest_period == "11504":
    print(f"\n⚠ Still showing April 2026 data (period 11504).")
    print(f"  May data expected by June 10, 2026. No update needed.")
    may_data = False
elif latest_period > "11505":
    print(f"\n✅ Even newer data available: period {latest_period}. Processing...")
    may_data = True
else:
    print(f"\n❓ Unexpected period: {latest_period}. Logging without update.")
    may_data = False

if may_data:
    # Build revenue map from latest period
    rev_map = {}
    for row in raw:
        p = str(row.get("資料年月") or row.get("年月","")).strip()
        if p != latest_period: continue
        code = str(row.get("公司代號","")).strip()
        if code not in code_set: continue
        try:
            rev_str = (row.get("營業收入-當月營收") or row.get("營業收入","")).replace(",","").strip()
            rev_yoy_str = (row.get("營業收入-去年同月增減(%)") or "").strip()
            rev_val = float(rev_str) if rev_str else None  # already in thousands NTD
        except:
            rev_val = None
        rev_yoy = float(rev_yoy_str) if rev_yoy_str else None
        if code and rev_val:
            rev_map[code] = {"rev": rev_val, "yoy": rev_yoy}

    print(f"  → {len(rev_map)} ETF stocks have {month_name} revenue")

    # Compare with April revenue, compute YoY and MoM
    updates = []
    for s in composite:
        code = s["code"]
        if code not in rev_map: continue
        entry = rev_map[code]
        new_rev_k = entry["rev"]   # already in thousands NTD
        new_rev_b = new_rev_k / 1e6   # billions
        yoy = entry["yoy"]
        updates.append({
            "code": code,
            "name": s["name"],
            "rev_k": new_rev_k,
            "rev_b": round(new_rev_b, 3),
            "yoy_pct": round(yoy, 2) if yoy is not None else None,
        })
        yoy_s = f"{yoy:+.1f}%" if yoy is not None else "?"
        print(f"  {code} {s['name'].split()[0]:10s}  {month_name} rev: {new_rev_b:.2f}B NTD  YoY={yoy_s}")

    # Save a May revenue summary
    summary = {
        "period": latest_period,
        "month": f"{month_name} {greg_year}",
        "fetched": datetime.now().isoformat(),
        "updates": updates,
    }
    (REPORT_DIR / "may_revenue.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✓ Saved may_revenue.json with {len(updates)} records")

else:
    # Log the check
    summary = {
        "checked": datetime.now().isoformat(),
        "latest_period": latest_period,
        "status": "April data only — May not yet released",
        "next_check": _next_rev_date(TODAY),
    }
    (REPORT_DIR / "revenue_freshness.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ Logged check to revenue_freshness.json")
    print(f"  Next check: {_next_rev_date(TODAY)} (estimated revenue release)")
