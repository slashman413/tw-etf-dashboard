#!/usr/bin/env python3
"""Cross-check our stored BWIBBU data against a fresh BWIBBU_ALL fetch."""
import json, ssl, urllib.request
from pathlib import Path

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

rd = Path("reports/2026-06-06")
comp   = json.loads((rd/"composite_data.json").read_text(encoding="utf-8"))
bwibbu = json.loads((rd/"bwibbu_fresh.json").read_text(encoding="utf-8"))
bw_stored = {r["code"]: r for r in bwibbu.get("all_refreshed", [])}
comp_map   = {s["code"]: s for s in comp}

rev_raw = json.loads((rd/"may_revenue_raw.json").read_text(encoding="utf-8"))
rev_map = {}
for r in rev_raw.get("raw", []):
    code = r.get("公司代號","").strip()
    try: yoy = float(str(r.get("營業收入-去年同月增減(%)","")).replace(",",""))
    except: yoy = None
    try: rev = float(str(r.get("營業收入-當月營收","")).replace(",",""))
    except: rev = None
    rev_map[code] = {"yoy": yoy, "rev": rev, "name": r.get("公司名稱","")}

TOP20 = ["2330","2454","2317","2308","2882","2881","2891","2886","2884",
         "2892","2880","2883","2887","3711","4938","2303","6669","2002","2412","1303"]

# Fresh BWIBBU_ALL from TWSE
print("Fetching fresh BWIBBU_ALL from TWSE for cross-check...")
try:
    req = urllib.request.Request(
        "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL",
        headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
        fresh = json.loads(r.read().decode("utf-8"))
    fresh_map = {r["Code"]: r for r in fresh}
    date = fresh[0].get("Date","?") if fresh else "?"
    print(f"Fresh data date: {date}  |  Records: {len(fresh)}\n")
except Exception as e:
    print(f"Error fetching fresh data: {e}")
    fresh_map = {}

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v else None
    except: return None

print(f"{'代號':<6} {'名稱':<8} | {'PE(存)':>8} {'PE(新)':>8} {'符合':>4} | {'PB(存)':>7} {'PB(新)':>7} {'符合':>4} | {'殖(存)':>7} {'殖(新)':>7} {'符合':>4} | {'營收YoY':>9}")
print("="*105)

matches = 0
total_checked = 0

for code in TOP20:
    s    = comp_map.get(code, {})
    bws  = bw_stored.get(code, {})
    bwf  = fresh_map.get(code, {})
    rv   = rev_map.get(code, {})
    name = rv.get("name") or s.get("name","")
    name = name[:6]

    pe_s  = bws.get("pe_new")
    pe_f  = sf(bwf.get("PEratio"))
    pb_s  = bws.get("pb_new") or sf(s.get("pb"))
    pb_f  = sf(bwf.get("PBratio"))
    dy_s  = bws.get("div_yield")
    dy_f  = sf(bwf.get("DividendYield"))
    yoy   = rv.get("yoy")

    def chk(a, b, tol):
        if a is None or b is None: return "—"
        return "✅" if abs(a-b) <= tol else f"⚠️({b:.1f})"

    pe_ok = chk(pe_s, pe_f, 2.0)
    pb_ok = chk(pb_s, pb_f, 0.3)
    dy_ok = chk(dy_s, dy_f, 0.5)

    if pe_ok=="✅": matches += 1
    if pe_f is not None: total_checked += 1

    pes  = f"{pe_s:.1f}"  if pe_s  else "—"
    pef  = f"{pe_f:.1f}"  if pe_f  else "—"
    pbs  = f"{pb_s:.2f}"  if pb_s  else "—"
    pbf  = f"{pb_f:.2f}"  if pb_f  else "—"
    dys  = f"{dy_s:.2f}%" if dy_s  else "—"
    dyf  = f"{dy_f:.2f}%" if dy_f  else "—"
    yoys = f"{yoy:+.1f}%" if yoy is not None else "—"

    print(f"{code:<6} {name:<8} | {pes:>8} {pef:>8} {pe_ok:>4} | {pbs:>7} {pbf:>7} {pb_ok:>4} | {dys:>7} {dyf:>7} {dy_ok:>4} | {yoys:>9}")

print(f"\n{'='*105}")
print(f"PE 符合率 (誤差<2x): {matches}/{total_checked} = {matches/total_checked*100:.0f}%" if total_checked else "N/A")
print(f"資料日期: 存檔={bwibbu.get('data_date','?')}  新取={date}")
