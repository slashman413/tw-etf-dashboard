"""Dump all ETF component data as JSON for in-context analysis."""
import json, time, requests
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

CODES_0050 = [
    "2330","2317","2454","2882","2881","2308","3008","2412","2382","2303",
    "2886","2891","2357","2603","2379","2395","2884","5880","2002","1301",
    "1303","2207","2615","2609","2892","5871","6669","3711","2327","2408",
    "2887","1216","1101","2409","3045","4938","2376","3034","6770","2801",
    "2883","2890","1102","2301","5876","2337","2352","6415","3037",
]
CODES_0056 = [
    "2887","2892","2886","5880","2884","2890","2801","2883","1101","1102",
    "1216","2002","2207","2301","2327","2352","2357","2379","2395","2412",
    "2603","2609","2615","3034","3045","5871","6415","2303","3711","2408",
]
ALL_CODES = set(CODES_0050 + CODES_0056)

val = {r["Code"]: r for r in requests.get(
    "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL",
    headers=HEADERS, timeout=25).json()}
print("VAL_OK")
time.sleep(120)  # 2-minute crawl interval
rev = {r["公司代號"]: r for r in requests.get(
    "https://openapi.twse.com.tw/v1/opendata/t187ap05_L",
    headers=HEADERS, timeout=25).json()}
print("REV_OK")

out = {}
for code in ALL_CODES:
    v = val.get(code, {})
    r = rev.get(code, {})
    out[code] = {
        "pe": v.get("PEratio","N/A"), "pb": v.get("PBratio","N/A"),
        "div": v.get("DividendYield","N/A"),
        "rev": r.get("營業收入-當月營收","N/A"),
        "mom": r.get("營業收入-上月比較增減(%)","N/A"),
        "yoy": r.get("營業收入-去年同月增減(%)","N/A"),
        "cum_yoy": r.get("累計營業收入-前期比較增減(%)","N/A"),
        "period": r.get("資料年月","N/A"),
    }

print(json.dumps(out))
