#!/usr/bin/env python3
"""
Fetch OTC PE/PB/dividend yield from TPEX BWIBBU-equivalent endpoint.
Tries multiple TPEX endpoints for valuation data.
Also tries TWSE endpoint for OTC valuation if listed there.
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

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            raw = r.read().decode("utf-8")
            if not raw.strip() or raw.strip() in ("[]", "{}"):
                return None
            d = json.loads(raw)
            return d if (isinstance(d, list) and d) else None
    except Exception as e:
        print(f"    Error: {e}")
        return None

def sf(v):
    if v is None: return None
    s = str(v).replace(",","").strip()
    if not s or s in ("-","—","N/A","n/a",""): return None
    try: return float(s)
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === OTC Valuation Data ===")

# Load existing data
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}

before_pe = sum(1 for c in otc_map.values() if c.get("pe") is not None)
print(f"  Before: {before_pe}/887 OTC companies have PE")

# Candidate endpoints
candidates = [
    ("TPEX-BWIBBU",  "https://www.tpex.org.tw/openapi/v1/tpex_BWIBBU_ALL"),
    ("TPEX-BWIBBU2", "https://www.tpex.org.tw/openapi/v1/BWIBBU_ALL"),
    ("TPEX-valuation","https://www.tpex.org.tw/openapi/v1/tpex_stk_index_per_day"),
    ("TWSE-OTC-BWIBBU","https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL_O"),
    ("TWSE-BWIBBU_ALL","https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"),
]

found_data = None
found_label = None
for label, url in candidates:
    print(f"  Probing {label}: {url}")
    d = fetch(url)
    if d:
        print(f"    ✅ Got {len(d)} rows | keys: {list(d[0].keys())[:6]}")
        found_data  = d
        found_label = label
        break
    else:
        print(f"    ❌ Empty")
    print(f"  ⏳ Waiting {WAIT_SEC}s...")
    time.sleep(WAIT_SEC)

if not found_data:
    print("\n❌ No valuation endpoint found")
    exit(0)

print(f"\n  Using {found_label}: {len(found_data)} rows")
sample = found_data[0]
print(f"  Fields: {list(sample.keys())}")
print(f"  Sample: {sample}")

# Field detection for PE/PB/yield/code
code_field = None
pe_field   = None
pb_field   = None
dy_field   = None
for f in sample.keys():
    fl = f.lower()
    if "code" in fl or "股票代號" in f or "Code" in f:
        code_field = f
    if "pe" in fl or "本益比" in f:
        pe_field = f
    if "pb" in fl or "股價淨值" in f or "淨值比" in f:
        pb_field = f
    if "yield" in fl or "殖利率" in f or "dividend" in fl:
        dy_field = f

print(f"  code={code_field} pe={pe_field} pb={pb_field} yield={dy_field}")

updated = 0
for row in found_data:
    code = str(row.get(code_field,"")).strip() if code_field else None
    if not code or code not in otc_map:
        continue
    c = otc_map[code]
    if pe_field:
        v = sf(row.get(pe_field))
        if v is not None and 0 < v < 9999: c["pe"] = v
    if pb_field:
        v = sf(row.get(pb_field))
        if v is not None: c["pb"] = v
    if dy_field:
        v = sf(row.get(dy_field))
        if v is not None: c["yield"] = v
    updated += 1

after_pe = sum(1 for c in otc_map.values() if c.get("pe") is not None)
print(f"\n  After: {after_pe}/887 OTC have PE (was {before_pe})")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved {REPORT_DIR}/full_market.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
