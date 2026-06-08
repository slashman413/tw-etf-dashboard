#!/usr/bin/env python3
"""
Fetch Q1 2026 financial data for OTC (上櫃) companies from TPEX endpoints.
Tries multiple endpoint variants and merges into full_market.json.
Wait: called with 132s already elapsed since last TWSE call.
"""
import json, ssl, time, urllib.request
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

def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            data = json.loads(raw)
            if isinstance(data, list) and len(data) > 0:
                return data
            return None
    except Exception as e:
        return None

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === OTC Q1 2026 Financial Data Fetch ===")
print(f"  Target dir: {REPORT_DIR}")

# Candidate endpoints for OTC Q1 2026 EPS
candidates = [
    ("TWSE-OTC-t187ap14_O",  "https://openapi.twse.com.tw/v1/opendata/t187ap14_O"),
    ("TWSE-OTC-t187ap06_O",  "https://openapi.twse.com.tw/v1/opendata/t187ap06_O_ci"),
    ("TWSE-OTC-t187ap17_O",  "https://openapi.twse.com.tw/v1/opendata/t187ap17_O"),
]

found_url = None
found_data = None
found_label = None

for label, url in candidates:
    print(f"\n  Probing {label}...")
    print(f"    URL: {url}")
    data = fetch_json(url)
    if data:
        print(f"    ✅ Got {len(data)} rows")
        print(f"    Sample keys: {list(data[0].keys())[:8]}")
        print(f"    Sample[0]: {str(data[0])[:200]}")
        found_url   = url
        found_data  = data
        found_label = label
        break
    else:
        print(f"    ❌ Empty or invalid")
    print(f"  ⏳ Waiting {WAIT_SEC}s...")
    time.sleep(WAIT_SEC)

if not found_data:
    print("\n  No valid OTC endpoint found. Trying TPEX direct API...")
    tpex_candidates = [
        ("TPEX-t187ap14",  "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap14_O"),
        ("TPEX-income",    "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci"),
        ("TPEX-margins",   "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap17_O"),
    ]
    for label, url in tpex_candidates:
        print(f"\n  Probing {label}...")
        data = fetch_json(url)
        if data:
            print(f"    ✅ Got {len(data)} rows")
            print(f"    Sample keys: {list(data[0].keys())[:8]}")
            found_url   = url
            found_data  = data
            found_label = label
            break
        else:
            print(f"    ❌ Empty or invalid")
        print(f"  ⏳ Waiting {WAIT_SEC}s...")
        time.sleep(WAIT_SEC)

if not found_data:
    print("\n❌ No OTC Q1 data found from any endpoint.")
    exit(0)

print(f"\n✅ Using {found_label}: {len(found_data)} rows")

# Parse EPS from the data
# Check which fields contain EPS info
sample = found_data[0]
print(f"\nAll fields: {list(sample.keys())}")

# Load full_market.json
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}
print(f"\nOTC companies in full_market: {len(otc_map)}")

# Try to find EPS field
eps_field = None
code_field = None
for field in sample.keys():
    if "eps" in field.lower() or "每股" in field or "基本" in field.lower():
        eps_field = field
    if "code" in field.lower() or "股票" in field.lower() or "代號" in field:
        code_field = field

print(f"  Detected code field: {code_field}")
print(f"  Detected EPS field:  {eps_field}")

if not code_field:
    # Try to identify code field
    for f in sample.keys():
        v = str(sample[f])
        if len(v) == 4 and v.isdigit():
            code_field = f
            print(f"  Guessed code field: {code_field} = {v}")
            break

updated = 0
for row in found_data:
    code = str(row.get(code_field, "")).strip() if code_field else None
    if not code or code not in otc_map:
        continue
    c = otc_map[code]
    if eps_field:
        v = sf(row.get(eps_field))
        if v is not None:
            c["eps_q1"] = v
            updated += 1

# Also try to parse revenue, op_income, net_income fields
rev_field = None
op_field  = None
net_field = None
for f in sample.keys():
    fl = f.lower()
    if "revenue" in fl or "營收" in f or "收入" in f:
        rev_field = f
    if "op_income" in fl or "營業" in f and "利" in f:
        op_field = f
    if "net" in fl and "income" in fl or "稅後" in f:
        net_field = f

if rev_field or op_field:
    for row in found_data:
        code = str(row.get(code_field, "")).strip() if code_field else None
        if not code or code not in otc_map:
            continue
        c = otc_map[code]
        if rev_field:
            v = sf(row.get(rev_field))
            if v is not None: c["revenue_q1"] = v
        if op_field:
            v = sf(row.get(op_field))
            if v is not None: c["net_income_q1"] = v

print(f"\n  Updated {updated} OTC companies with Q1 EPS")

# Save full_market.json
fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved: {REPORT_DIR}/full_market.json")

# Save probe result
probe_result = {
    "generated":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    "endpoint":    found_url,
    "label":       found_label,
    "total_rows":  len(found_data),
    "otc_updated": updated,
    "sample_keys": list(found_data[0].keys()) if found_data else [],
}
(REPORT_DIR / "otc_q1_probe.json").write_text(
    json.dumps(probe_result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Probe result: {REPORT_DIR}/otc_q1_probe.json")
print(f"\n[{datetime.now():%H:%M:%S}] Done")
