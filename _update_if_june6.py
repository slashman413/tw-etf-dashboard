#!/usr/bin/env python3
"""
Wait 130s, then check BWIBBU_ALL for June 6 data.
If available: run full update pipeline and rebuild grand/mos/action/conviction.
"""
import json, ssl, time, subprocess, sys
from pathlib import Path
from datetime import datetime

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

import urllib.request
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

print(f"[{datetime.now():%H:%M:%S}] Waiting 132s before BWIBBU_ALL probe…")
time.sleep(132)

print(f"[{datetime.now():%H:%M:%S}] Probing BWIBBU_ALL…")
try:
    data = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    date = data[0].get("Date","?") if data else "?"
    print(f"  Date: {date} | Records: {len(data)}")
    if date == "1150606":
        print("  ✅ June 6 data is live! Running full update pipeline…")
        sys.exit(0)  # signal: update needed
    else:
        print(f"  Still June 5 data ({date}). Will retry next iteration.")
        sys.exit(1)  # signal: no update needed
except Exception as e:
    print(f"  Error: {e}")
    sys.exit(2)
