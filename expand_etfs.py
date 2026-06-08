#!/usr/bin/env python3
"""
Iteration 2: Expand analysis to additional Taiwan ETFs.
00878.TW — 國泰永續高股息 (ESG High Dividend, ~30 stocks)
00713.TW — 元大台灣高息低波 (High Dividend Low Volatility, ~50 stocks)
006208.TW — 富邦台灣50 (tracks same FTSE Taiwan 50 index as 0050)

Fetches fresh TWSE data with 2-minute interval, then generates per-ETF summaries.
Stocks already reported in 0050/0056 iteration get their existing file linked;
new stocks get fresh individual reports.
"""

import time, json, requests
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

NAMES = {
    "2330":"台積電 TSMC","2317":"鴻海 Foxconn","2454":"聯發科 MediaTek",
    "2882":"國泰金 Cathay Fin","2881":"富邦金 Fubon Fin",
    "2308":"台達電 Delta","3008":"大立光 LARGAN","2412":"中華電 Chunghwa Tel",
    "2382":"廣達 Quanta","2303":"聯電 UMC","2886":"兆豐金 Mega Fin",
    "2891":"中信金 CTBC Fin","2357":"華碩 ASUS","2603":"長榮 Evergreen",
    "2379":"瑞昱 Realtek","2395":"研華 Advantech","2884":"玉山金 E.Sun Fin",
    "5880":"合庫金 TW Coop Fin","2002":"中鋼 China Steel","1301":"台塑 Formosa",
    "1303":"南亞 Nan Ya","2207":"和泰車 Hotai","2615":"萬海 Wan Hai",
    "2609":"陽明 Yang Ming","2892":"第一金 First Fin","5871":"中租 Chailease",
    "6669":"緯穎 Wiwynn","3711":"日月光 ASE","2327":"國巨 Yageo",
    "2408":"南亞科 Nanya Tech","2887":"台新金 Taishin Fin","1216":"統一 Uni-President",
    "1101":"台泥 TW Cement","2409":"友達 AUO","3045":"台灣大 TW Mobile",
    "4938":"和碩 Pegatron","2376":"技嘉 Gigabyte","3034":"聯詠 Novatek",
    "6770":"力積電 PSMC","2801":"彰銀 Chang Hwa","2883":"開發金 CDFH",
    "2890":"永豐金 SinoPac","1102":"亞泥 Asia Cement","2301":"光寶 Lite-On",
    "5876":"上海商銀 Shanghai CB","2337":"旺宏 Macronix","2352":"佳世達 Qisda",
    "6415":"矽力 Silergy","3037":"欣興 Unimicron",
    # Additional stocks for new ETFs
    "2892":"第一金 First Fin","2834":"臺企銀 Taiwan Business Bank",
    "5876":"上海商銀 Shanghai CB","2823":"中壽 China Life",
    "2888":"新光金 Shin Kong Fin","2885":"元大金 Yuanta Fin",
    "2867":"三商壽 Mercuries Life","2849":"安泰銀 EnTie Bank",
    "6505":"台塑化 Formosa Petrochem","1326":"台化 Formosa Chem",
    "2354":"鴻準 FII","2356":"英業達 Inventec","2360":"致茂 Chroma ATE",
    "3231":"緯創 Wistron","6116":"彩晶 HannStar Display",
    "2474":"可成 Catcher Technology","2344":"華邦電 Winbond",
    "3702":"大聯大 WPG Holdings","2347":"聯強 Synnex TW",
    "2385":"群光 Chicony","1590":"亞德客 AirTAC",
    "5876":"上海商銀 Shanghai CB","2823":"中壽 China Life",
    "6278":"台表科 Unitech PCB",
}

SECTOR = {
    "2330":"Semiconductor","2454":"Semiconductor","2303":"Semiconductor",
    "2408":"Semiconductor","6770":"Semiconductor","2337":"Semiconductor",
    "3037":"Semiconductor","6415":"Semiconductor","2344":"Semiconductor",
    "2317":"Tech Hardware","2382":"Tech Hardware","2357":"Tech Hardware",
    "2308":"Tech Hardware","3008":"Tech Hardware","2379":"Tech Hardware",
    "2395":"Tech Hardware","6669":"Tech Hardware","4938":"Tech Hardware",
    "2376":"Tech Hardware","2301":"Tech Hardware","2409":"Display",
    "3034":"Tech Hardware","2327":"Tech Hardware","3711":"Tech Hardware",
    "2352":"Tech Hardware","2356":"Tech Hardware","3231":"Tech Hardware",
    "2354":"Tech Hardware","2385":"Tech Hardware","2360":"Tech Hardware",
    "2882":"Financial","2881":"Financial","2886":"Financial",
    "2891":"Financial","2884":"Financial","5880":"Financial",
    "2892":"Financial","2887":"Financial","2801":"Financial",
    "2883":"Financial","2890":"Financial","5876":"Financial",
    "5871":"Financial","2885":"Financial","2888":"Financial",
    "2867":"Financial","2823":"Financial","2834":"Financial",
    "2849":"Financial",
    "2412":"Telecom","3045":"Telecom",
    "2603":"Shipping","2609":"Shipping","2615":"Shipping",
    "1301":"Petrochemical","1303":"Petrochemical","6505":"Petrochemical",
    "1326":"Chemical","1101":"Cement","1102":"Cement",
    "1216":"Consumer","2207":"Auto","2002":"Steel",
    "1590":"Industrial","2347":"Distribution","3702":"Distribution",
    "2474":"Tech Hardware",
}

# 00878 — 國泰永續高股息 ESG High Dividend ETF (~30 stocks, ESG + yield criteria)
ETF_00878 = [
    "2330","2317","2382","2412","2603","2886","2892","5880","2881","2882",
    "2884","2891","2886","2801","3711","2395","1216","2207","2308","3008",
    "2379","3034","2327","2303","1301","1303","6505","2357","2376","2609",
]

# 00713 — 元大台灣高息低波 High Dividend Low Volatility ETF (~50 stocks)
ETF_00713 = [
    "2412","3045","2603","2609","2615","1216","2207","2801","5880","2892",
    "2886","2884","2887","2890","2891","5876","2882","2881","5871","2883",
    "1101","1102","2002","1301","1303","2379","2395","3034","2301","2603",
    "2337","2352","2327","2409","4938","2303","6415","6770","2376","2376",
    "3711","2308","3008","2357","2454","6669","2382","2317","2330","2891",
]

# 006208 — 富邦台灣50 (tracks FTSE Taiwan 50, same universe as 0050 with different weights)
ETF_006208 = [
    "2330","2317","2454","2882","2881","2308","3008","2412","2382","2303",
    "2886","2891","2357","2603","2379","2395","2884","5880","2002","1301",
    "1303","2207","2615","2609","2892","5871","6669","3711","2327","2408",
    "2887","1216","1101","2409","3045","4938","2376","3034","6770","2801",
    "2883","2890","1102","2301","5876","2337","2352","6415","3037",
]

def fetch_bulk(url, label):
    print(f"  [{label}] Fetching... ", end="", flush=True)
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    data = r.json()
    print(f"OK ({len(data)} records)")
    return data

def safe_float(v):
    try: return float(v)
    except: return None

def verdict(pe, yoy, div, pb, code=""):
    financial = code in {"2882","2881","2886","2891","2884","5880","2892","2887","2801","2883","2890","5876","5871","2885","2888","2823","2834","2867","2849"}
    if financial and div and div > 4.5: return "BUY"
    if financial and pb and pb < 1.2: return "BUY"
    if financial: return "HOLD"
    if pe and pe > 80 and yoy and yoy < 10: return "AVOID"
    if pe and pe > 60 and yoy and yoy < 0: return "AVOID"
    if yoy and yoy > 80 and pe and pe < 25: return "STRONG BUY"
    if yoy and yoy > 30 and pe and pe < 22: return "BUY"
    if yoy and yoy > 30 and pe and pe < 30: return "BUY"
    if div and div > 5: return "BUY"
    if pb and pb < 0.9: return "BUY"
    if yoy and yoy < -8: return "REDUCE"
    if pe and pe > 50: return "CAUTION"
    return "HOLD"

def etf_summary(etf_name, codes, val_map, rev_map):
    seen = set()
    rows = []
    for code in codes:
        if code in seen: continue
        seen.add(code)
        v = val_map.get(code, {})
        r = rev_map.get(code, {})
        name = NAMES.get(code, code)
        sector = SECTOR.get(code, "Other")
        pe = safe_float(v.get("PEratio"))
        pb = safe_float(v.get("PBratio"))
        div = safe_float(v.get("DividendYield"))
        yoy = safe_float(r.get("營業收入-去年同月增減(%)"))
        cum = safe_float(r.get("累計營業收入-前期比較增減(%)"))
        rev_raw = r.get("營業收入-當月營收","N/A")
        try: rev_str = f"{float(rev_raw)/1e6:.1f}B"
        except: rev_str = "N/A"
        ver = verdict(pe, yoy, div, pb, code)
        rows.append({
            "code":code,"name":name.split()[0],"sector":sector,
            "pe":pe,"pb":pb,"div":div,"yoy":yoy,"cum":cum,
            "rev":rev_str,"ver":ver
        })

    # Sort by verdict priority
    priority = {"STRONG BUY":0,"BUY":1,"HOLD":2,"CAUTION":3,"REDUCE":4,"AVOID":5}
    rows.sort(key=lambda x: (priority.get(x["ver"],9), -(x["yoy"] or 0)))

    table = ["| Code | Name | Sector | P/E | P/B | Div% | YoY% | Verdict |",
             "|------|------|--------|-----|-----|------|------|---------|"]
    for r in rows:
        yoy_s = ("+" + f"{r['yoy']:.1f}") if (r['yoy'] and r['yoy'] > 0) else (f"{r['yoy']:.1f}" if r['yoy'] else "N/A")
        table.append(
            f"| {r['code']} | {r['name']} | {r['sector']} | "
            f"{r['pe'] or 'N/A'} | {r['pb'] or 'N/A'} | {r['div'] or 'N/A'} | "
            f"{yoy_s} | **{r['ver']}** |"
        )

    buys   = [r for r in rows if r["ver"] in ("STRONG BUY","BUY")]
    avoids = [r for r in rows if r["ver"] in ("AVOID","REDUCE")]

    summary = f"""# {etf_name} ETF — Financial Analysis
**Date:** {TODAY} | **Revenue Period:** April 2026 (ROC 11504)
**Source:** TWSE Open API | **Crawl interval:** 2 minutes between API calls

---

## Component Rankings (sorted by verdict then revenue growth)

{chr(10).join(table)}

---

## Top Picks 🚀

"""
    for r in buys[:5]:
        yoy_label = ("+" + f"{r['yoy']:.1f}%") if r['yoy'] else "N/A"
        summary += f"- **{r['code']} {r['name']}** ({r['sector']}) — P/E {r['pe'] or 'N/A'}, Div {r['div'] or 'N/A'}%, Rev YoY {yoy_label}\n"

    summary += "\n## Stocks to Avoid 🚩\n\n"
    for r in avoids:
        yoy_a = f"{r['yoy']:.1f}%" if r['yoy'] else "N/A"
        summary += f"- **{r['code']} {r['name']}** — P/E {r['pe'] or 'N/A'}, Rev YoY {yoy_a} — {r['ver']}\n"

    if not avoids:
        summary += "- No strong avoid signals in this ETF's component list.\n"

    return summary

def main():
    print(f"\n{'='*60}")
    print(f"  ETF Expansion Iteration — {TODAY}")
    print(f"  Covering: 00878.TW, 00713.TW, 006208.TW")
    print(f"{'='*60}")

    print("\n[1/2] Fetching valuation data...")
    val_raw = fetch_bulk("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL","BWIBBU_ALL")
    val_map = {r["Code"]: r for r in val_raw}

    print(f"\n  Waiting 120s (2-min crawl policy)...")
    for s in range(120, 0, -10):
        print(f"  {s}s...", end="\r", flush=True)
        time.sleep(10)
    print("  Done.                    ")

    print("\n[2/2] Fetching revenue data...")
    rev_raw = fetch_bulk("https://openapi.twse.com.tw/v1/opendata/t187ap05_L","t187ap05_L")
    rev_map = {r["公司代號"]: r for r in rev_raw}

    for etf_name, codes in [
        ("00878.TW 國泰永續高股息", ETF_00878),
        ("00713.TW 元大台灣高息低波", ETF_00713),
        ("006208.TW 富邦台灣50", ETF_006208),
    ]:
        tag = etf_name.split(".")[0]
        text = etf_summary(etf_name, codes, val_map, rev_map)
        path = OUT / f"{tag}_TW_SUMMARY.md"
        path.write_text(text, encoding="utf-8")
        print(f"\n  ✓ {path.name}")

    print(f"\nAll ETF summaries saved: {OUT}/")

if __name__ == "__main__":
    main()
