#!/usr/bin/env python3
"""Probe T86 June 6, wait 130s, probe BWIBBU June 6. Report both."""
import json, ssl, time, urllib.request
from datetime import datetime

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

# Probe 1: T86 June 6
print(f"[{datetime.now():%H:%M:%S}] Probe 1: T86 2026-06-06…")
t86_ok = False
try:
    d = fetch("https://www.twse.com.tw/rwd/zh/fund/T86?date=20260606&selectType=ALL&response=json")
    rows = d.get("data", [])
    stat = d.get("stat","")
    print(f"  stat={stat!r} | rows={len(rows)}")
    t86_ok = len(rows) > 0
    if t86_ok:
        print(f"  ✅ T86 June 6 is LIVE! {len(rows)} rows")
    else:
        print("  ❌ T86 June 6 not yet published")
except Exception as e:
    print(f"  Error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s before BWIBBU probe…")
time.sleep(132)

# Probe 2: BWIBBU date
print(f"[{datetime.now():%H:%M:%S}] Probe 2: BWIBBU_ALL date…")
bwibbu_june6 = False
try:
    data = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    date = data[0].get("Date","?") if data else "?"
    print(f"  Date={date} | Records={len(data)}")
    bwibbu_june6 = (date == "1150606")
    if bwibbu_june6:
        print("  ✅ BWIBBU June 6 is LIVE!")
    else:
        print(f"  Still {date}")
except Exception as e:
    print(f"  Error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Summary: T86={t86_ok} BWIBBU={bwibbu_june6}")

import sys
if t86_ok and bwibbu_june6: sys.exit(0)
elif bwibbu_june6: sys.exit(2)
elif t86_ok: sys.exit(1)
else: sys.exit(3)
