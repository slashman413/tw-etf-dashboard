#!/usr/bin/env python3
"""
Fetch Q1 2026 margin ratios for OTC companies from TPEX t187ap17_O.
Merges gross/op/pretax/net margins into full_market.json.
"""
import json, ssl, urllib.request
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === OTC Margin Ratios (t187ap17_O) ===")

req = urllib.request.Request(
    "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap17_O",
    headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
except Exception as e:
    print(f"  ❌ Failed: {e}")
    exit(0)

if not data or not isinstance(data, list):
    print("  ❌ Empty or invalid response")
    exit(0)

print(f"  Got {len(data)} rows")
print(f"  Fields: {list(data[0].keys())}")
print(f"  Sample: {data[0]}")

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}

# Map margin fields from TPEX t187ap17_O
# Expected fields similar to: 毛利率, 營業利益率, 稅前純益率, 稅後純益率
sample = data[0]
code_field   = "SecuritiesCompanyCode"
gross_field  = None
op_field     = None
pretax_field = None
net_field    = None

for f in sample.keys():
    if "毛利" in f:    gross_field  = f
    if "營業利益率" in f: op_field    = f
    if "稅前" in f:    pretax_field = f
    if "稅後" in f:    net_field    = f

print(f"\n  Code: {code_field}")
print(f"  Gross margin: {gross_field}")
print(f"  Op margin:    {op_field}")
print(f"  Pretax:       {pretax_field}")
print(f"  Net:          {net_field}")

updated = 0
for row in data:
    code = str(row.get(code_field, "")).strip()
    if not code or code not in otc_map:
        continue
    c = otc_map[code]
    if gross_field:
        v = sf(row.get(gross_field))
        if v is not None: c["gross_margin"] = v
    if op_field:
        v = sf(row.get(op_field))
        if v is not None: c["op_margin"] = v
    if net_field:
        v = sf(row.get(net_field))
        if v is not None: c["net_margin"] = v
    updated += 1

print(f"\n  Updated {updated} OTC companies with margin ratios")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved: {REPORT_DIR}/full_market.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
