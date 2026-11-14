"""Fetch TWSE data and print structured output for analysis."""
import time, json, requests
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FinAnalyzer/1.0)", "Accept": "application/json"}
TARGETS = {
    "2330":"台積電 TSMC","2317":"鴻海 Foxconn","2454":"聯發科 MediaTek",
    "2882":"國泰金 Cathay Financial","2881":"富邦金 Fubon Financial",
    "2308":"台達電 Delta Electronics","3008":"大立光 LARGAN",
    "2412":"中華電信 Chunghwa Telecom","2382":"廣達 Quanta",
    "2303":"聯電 UMC","2886":"兆豐金 Mega Financial",
    "2891":"中信金 CTBC Financial","2357":"華碩 ASUS",
    "2603":"長榮 Evergreen Marine","2379":"瑞昱 Realtek",
}

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()

val_data  = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
time.sleep(5)
rev_data  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")

val_map = {r["Code"]: r for r in val_data if r.get("Code") in TARGETS}
rev_map = {r["公司代號"]: r for r in rev_data if r.get("公司代號") in TARGETS}

print(f"DATE: {datetime.now().strftime('%Y-%m-%d')} ROC115")
print(f"VALUATION_RECORDS: {len(val_map)}, REVENUE_RECORDS: {len(rev_map)}")
print()

for code, name in TARGETS.items():
    v = val_map.get(code, {})
    r = rev_map.get(code, {})
    print(f"[{code}] {name}")
    print(f"  PE={v.get('PEratio','N/A')}  DIV={v.get('DividendYield','N/A')}%  PB={v.get('PBratio','N/A')}")
    if r:
        print(f"  Revenue({r.get('資料年月','?')}): {r.get('營業收入-當月營收','N/A')} | MoM={r.get('營業收入-上月比較增減(%)','N/A')}% | YoY={r.get('營業收入-去年同月增減(%)','N/A')}%")
        print(f"  Cumulative: {r.get('累計營業收入-當月累計營收','N/A')} | YoY={r.get('累計營業收入-前期比較增減(%)','N/A')}%")
    print()
