#!/usr/bin/env python3
"""
Populate sector field for OTC companies using 產業別 from TPEX t187ap06_O_ci.
"""
import json, ssl, urllib.request
from pathlib import Path
from datetime import datetime
from collections import Counter

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

print(f"[{datetime.now():%H:%M:%S}] === Populate OTC Sectors ===")

req = urllib.request.Request(
    "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci",
    headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
    data = json.loads(r.read().decode("utf-8"))
print(f"  Got {len(data)} rows from t187ap06_O_ci")

# Build code → 產業別 mapping
sector_map = {}
for row in data:
    code = str(row.get("SecuritiesCompanyCode","")).strip()
    sec  = row.get("產業別","").strip()
    if code and sec:
        sector_map[code] = sec

print(f"  Sector mappings: {len(sector_map)}")
unique_sectors = sorted(set(sector_map.values()))
print(f"  Unique sectors: {len(unique_sectors)}")
for s in unique_sectors[:15]:
    print(f"    {s}")

# Load and update full_market.json
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
updated = 0
for c in companies:
    if c.get("market") != "OTC":
        continue
    sec = sector_map.get(c["code"])
    if sec:
        c["sector"] = sec
        updated += 1

print(f"\n  OTC companies with sector populated: {updated}/887")

# Sector distribution
dist = Counter(c.get("sector","") for c in companies if c.get("market") == "OTC")
print("\n  Top sectors:")
for sec, cnt in dist.most_common(10):
    print(f"    {sec}: {cnt}")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ Saved {REPORT_DIR}/full_market.json")

# Also update quarterly_financials.json
qf = json.loads((REPORT_DIR / "quarterly_financials.json").read_text(encoding="utf-8"))
for c in qf["companies"]:
    if c.get("market") != "OTC":
        continue
    sec = sector_map.get(c["code"])
    if sec:
        c["sector"] = sec
qf["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "quarterly_financials.json").write_text(
    json.dumps(qf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved {REPORT_DIR}/quarterly_financials.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
