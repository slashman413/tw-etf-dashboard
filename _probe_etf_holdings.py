#!/usr/bin/env python3
"""Probe TWSE for ETF constituent/holding data for 0056, 00878, 00713, 006208."""
import json, ssl, urllib.request, time
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0", "Accept": "*/*", "Referer": "https://www.twse.com.tw/"}

urls = [
    ("https://www.twse.com.tw/rwd/zh/fund/LISTED_FUND_ST?response=json&stockNo=0056", "0056_ST"),
    ("https://www.twse.com.tw/rwd/zh/fund/LISTED_FUND_ST?response=json&stockNo=00878", "00878_ST"),
    ("https://www.twse.com.tw/rwd/zh/fund/LISTED_FUND_ST?response=json&stockNo=00713", "00713_ST"),
    ("https://www.twse.com.tw/rwd/zh/fund/LISTED_FUND_ST?response=json&stockNo=006208", "006208_ST"),
]
for url, label in urls:
    try:
        req = urllib.request.Request(url, headers=H)
        with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
            raw = r.read().decode("utf-8")
            if raw.strip() and raw.strip()[0] in "{[":
                d = json.loads(raw)
                if isinstance(d, dict):
                    print(f"  OK {label}: status={d.get('stat')} title={d.get('title')} fields={d.get('fields')}")
                    if d.get("data"):
                        print(f"     rows={len(d['data'])} sample={d['data'][:2]}")
                else:
                    print(f"  OK {label}: list {len(d)} recs")
            else:
                print(f"  non-JSON {label}: {raw[:80]}")
    except Exception as e:
        print(f"  ERR {label}: {e}")
    time.sleep(2)
