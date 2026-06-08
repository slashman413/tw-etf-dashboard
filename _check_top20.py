#!/usr/bin/env python3
import json, ssl, urllib.request, time
from pathlib import Path

rd = Path("reports/2026-06-06")
comp   = json.loads((rd/"composite_data.json").read_text(encoding="utf-8"))
bwibbu = json.loads((rd/"bwibbu_fresh.json").read_text(encoding="utf-8"))
bw_map = {r["code"]: r for r in bwibbu.get("all_refreshed", [])}

# Revenue map
rev_raw = json.loads((rd/"may_revenue_raw.json").read_text(encoding="utf-8"))
rev_map = {}
for r in rev_raw.get("raw", []):
    code = r.get("公司代號","").strip()
    try: yoy = float(str(r.get("營業收入-去年同月增減(%)","")).replace(",",""))
    except: yoy = None
    rev_map[code] = yoy

# Top 20 0050 stocks by weight
TOP20 = ["2330","2454","2317","2308","2882","2881","2891","2886","2884",
         "2892","2880","2883","2887","3711","4938","2303","6669","2002","2412","1303"]

comp_map = {s["code"]: s for s in comp}

print(f"\n{'代號':<6} {'名稱':<10} {'本益比(我們)':>12} {'殖利率(我們)':>12} {'PB(我們)':>9} {'營收YoY':>9}")
print("="*65)
our_data = []
for code in TOP20:
    s  = comp_map.get(code, {})
    bw = bw_map.get(code, {})
    pe = bw.get("pe_new") or s.get("fwd_pe")
    pb = bw.get("pb_new") or s.get("pb")
    dy = bw.get("div_yield") or s.get("div")
    yoy = rev_map.get(code)
    name = s.get("name", code)[:8]
    print(f"{code:<6} {name:<10} {str(round(pe,1))+'x' if pe else '—':>12} {str(round(dy,2))+'%' if dy else '—':>12} {str(round(pb,2)) if pb else '—':>9} {(str(round(yoy,1))+'%') if yoy else '—':>9}")
    our_data.append({"code":code,"name":name,"pe":pe,"pb":pb,"div":dy,"rev_yoy":yoy})

# Now fetch GoodInfo for spot-check (5 stocks only, with waits)
print("\n\n=== GoodInfo 交叉驗證 (抽查5支) ===")

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Referer": "https://goodinfo.tw/tw/index.asp",
}

import re

def fetch_goodinfo(code):
    url = f"https://goodinfo.tw/tw/StockInfo.asp?STOCK_ID={code}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")
    result = {}
    # PE ratio
    m = re.search(r'本益比[^<]*</[^>]+>\s*<[^>]+>\s*([\d.]+)', html)
    if m: result["pe"] = float(m.group(1))
    # Dividend yield
    m = re.search(r'殖利率[^<]*</[^>]+>\s*<[^>]+>\s*([\d.]+)%', html)
    if m: result["div"] = float(m.group(1))
    # PB
    m = re.search(r'股價淨值比[^<]*</[^>]+>\s*<[^>]+>\s*([\d.]+)', html)
    if m: result["pb"] = float(m.group(1))
    return result

spot = ["2330", "2454", "2317", "2882", "3711"]
for i, code in enumerate(spot):
    s = comp_map.get(code, {})
    bw = bw_map.get(code, {})
    our_pe = bw.get("pe_new") or s.get("fwd_pe")
    our_pb = bw.get("pb_new") or s.get("pb")
    our_dy = bw.get("div_yield") or s.get("div")

    print(f"\n[{code}] {s.get('name','')}")
    try:
        gi = fetch_goodinfo(code)
        pe_match = "✅" if gi.get("pe") and our_pe and abs(gi["pe"]-our_pe)<2 else "⚠️"
        pb_match = "✅" if gi.get("pb") and our_pb and abs(gi["pb"]-our_pb)<0.3 else "⚠️"
        dy_match = "✅" if gi.get("div") and our_dy and abs(gi["div"]-our_dy)<0.5 else "⚠️"
        print(f"  本益比:  我們={our_pe:.1f if our_pe else '—'}  GoodInfo={gi.get('pe','—')}  {pe_match}")
        print(f"  殖利率:  我們={our_dy:.2f if our_dy else '—'}%  GoodInfo={gi.get('div','—')}%  {dy_match}")
        print(f"  PB:      我們={our_pb:.2f if our_pb else '—'}  GoodInfo={gi.get('pb','—')}  {pb_match}")
    except Exception as e:
        print(f"  GoodInfo fetch error: {e}")

    if i < len(spot)-1:
        print(f"  Waiting 15s...")
        time.sleep(15)

print("\n=== Done ===")
