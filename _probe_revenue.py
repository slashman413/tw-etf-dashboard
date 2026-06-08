"""Probe for May 2026 revenue availability on TSE and TPEX."""
import json, ssl, urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))

# TSE
try:
    d = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods = sorted({r.get("資料年月", "") for r in d if r.get("資料年月")})
    print(f"TSE latest periods: {periods[-3:]}")
    print(f"May 2026 (11505): {'AVAILABLE' if '11505' in periods else 'not yet'}")
    print(f"TSE row count: {len(d)}")
except Exception as e:
    print(f"TSE probe failed: {e}")
