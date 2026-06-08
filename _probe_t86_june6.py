#!/usr/bin/env python3
"""Quick probe: T86 institutional flows for June 6, 2026."""
import json, ssl, urllib.request, time
from datetime import datetime

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

URL = "https://www.twse.com.tw/rwd/zh/fund/T86?date=20260606&selectType=ALL&response=json"
print(f"[{datetime.now():%H:%M:%S}] Probing T86 for 2026-06-06…")
try:
    d = fetch(URL)
    stat = d.get("stat", "")
    rows = d.get("data", [])
    print(f"  stat: {stat} | rows: {len(rows)}")
    if rows:
        print(f"  Sample: {rows[0][:5]}")
        print("  ✅ June 6 T86 data is available!")
    else:
        print("  ❌ No data rows for June 6 yet")
except Exception as e:
    print(f"  Error: {e}")
