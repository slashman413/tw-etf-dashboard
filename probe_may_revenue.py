#!/usr/bin/env python3
"""
Probe TWSE t187ap05_L for May 2026 (period 11505) revenue data.
If available, saves to may_revenue.json and prints summary.
"""
import json, ssl, urllib.request, time
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
PERIOD     = "11505"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

URL = f"https://openapi.twse.com.tw/v1/opendata/t187ap05_L"

print(f"[{datetime.now():%H:%M:%S}] Probing latest revenue period (looking for {PERIOD})…")
try:
    data = fetch(URL)
    if isinstance(data, list) and len(data) > 0:
        first = data[0]
        actual_period = first.get("資料年月") or first.get("年月","?")
        print(f"  Received {len(data)} records, actual period: {actual_period}")
        if actual_period != PERIOD:
            print(f"  ⚠ Latest is {actual_period}, not {PERIOD}. May data not yet published.")
        else:
            print(f"  ✅ May 2026 data confirmed! Sample: {first.get('公司代號','?')} {first.get('公司名稱','?')}")
        # Save raw data only if it's actually May
        out = {
            "period": actual_period,
            "target_period": PERIOD,
            "is_may": actual_period == PERIOD,
            "fetched": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "count": len(data),
            "raw": data,
        }
        fname = "may_revenue_raw.json" if actual_period == PERIOD else "latest_revenue_raw.json"
        (REPORT_DIR / fname).write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Saved: {REPORT_DIR}/{fname}")
    else:
        print(f"  ❌ No data for period {PERIOD}. Response: {str(data)[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Also probe April for comparison
print(f"\n[{datetime.now():%H:%M:%S}] Waiting 130s before next probe…")
time.sleep(130)

PERIOD2 = "11504"
URL2 = f"https://openapi.twse.com.tw/v1/opendata/t187ap05_L?response=json&emgno=sii&date={PERIOD2}"
print(f"[{datetime.now():%H:%M:%S}] Confirming April 2026 (period {PERIOD2}) is still latest…")
try:
    data2 = fetch(URL2)
    if isinstance(data2, list) and len(data2) > 0:
        print(f"  ✅ April confirmed: {len(data2)} records (baseline = 11504)")
    else:
        print(f"  ❓ April data response: {str(data2)[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Revenue probe complete.")
