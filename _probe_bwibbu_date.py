#!/usr/bin/env python3
"""Quick probe: check if BWIBBU_ALL has been updated to June 6 data."""
import json, ssl, urllib.request
from datetime import datetime

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

print(f"[{datetime.now():%H:%M:%S}] Probing BWIBBU_ALL date…")
try:
    data = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    date = data[0].get("Date","?") if data else "?"
    print(f"  Date: {date} | Records: {len(data)}")
    if date == "1150606":
        print("  ✅ June 6 data is live!")
    else:
        print(f"  Still showing {date} (June 5)")
except Exception as e:
    print(f"  Error: {e}")
