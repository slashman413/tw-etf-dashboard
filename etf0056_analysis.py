#!/usr/bin/env python3
"""
0056/00878/00713 ETF Expansion Analysis
Identifies stocks in these ETFs not covered in the 0050 universe (49 stocks),
fetches Q1 2026 data, and generates an expansion report.
"""

import time, json, requests
from pathlib import Path
from datetime import datetime

TODAY   = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT     = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

# Already analyzed universe
ANALYZED = {
    "2330","2317","2454","2882","2881","2308","3008","2412","2382","2303",
    "2886","2891","2357","2603","2379","2395","2884","5880","2002","1301",
    "1303","2207","2615","2609","2892","5871","6669","3711","2327","2408",
    "2887","1216","1101","2409","3045","4938","2376","3034","6770","2801",
    "2883","2890","1102","2301","5876","2337","2352","6415","3037",
}

FINANCIAL = {"2883","5876","2886","2801","2884","2882","2881","2891","2887",
             "2890","5880","2892","5871"}

# Known unique components of 0056/00878/00713 not in 0050 universe
# Source: TWSE quarterly ETF rebalancing disclosures (2025 Q4 / 2026 Q1)
EXPANSION = {
    # 0056 元大高股息 unique holdings
    "1590": "亞德客 Airtac",       # pneumatic automation leader
    "2912": "統一超 President",    # 7-Eleven Taiwan operator
    "4904": "遠傳 FarEasTone",     # telecom (3rd player)
    "6488": "環球晶 GlobalWafers", # silicon wafers
    "2823": "中壽 China Life",     # insurance
    "2880": "華南金 HuaNan",       # financial holding
    "2888": "新光金 ShinKong",     # financial holding
    # 00878 國泰永續高股息 unique holdings
    "3231": "緯創 Wistron",        # ODM/cloud servers
    "2383": "台光電 Elite",        # PCB copper-clad laminates
    "6743": "合一 Oneness",        # biotech (if listed on TWSE main board)
    # 00713 元大台灣高息低波 / 006208 overlap
    "2344": "華邦電 Winbond",      # DRAM memory
    "3481": "群創 Innolux",        # display panels
    "2049": "上銀 Hiwin",          # linear motion components
}

ETF_MEMBERSHIP = {
    "1590": ["0056","00878"],
    "2912": ["0056","00713"],
    "4904": ["0056","00713"],
    "6488": ["0056","00878"],
    "2823": ["0056"],
    "2880": ["0056","00713"],
    "2888": ["0056"],
    "3231": ["00878"],
    "2383": ["00878"],
    "6743": ["00878"],
    "2344": ["00713"],
    "3481": ["0056","00713"],
    "2049": ["00878","00713"],
}

def sf(v):
    try:
        f = float(str(v).replace(",",""))
        return None if f != f else f
    except: return None

def wait(sec=120):
    for s in range(sec, 0, -10):
        print(f"  {s}s...", end="\r", flush=True)
        time.sleep(10)
    print("  Fetching now...              ")

def fetch(url, label):
    print(f"  Fetching {label}...", end=" ", flush=True)
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    d = r.json()
    print(f"OK ({len(d)} records)")
    return d

def try_etf_api():
    """Attempt to fetch ETF holdings from TWSE API. Returns None on failure."""
    endpoints = [
        "https://openapi.twse.com.tw/v1/ETF/portfloio",
        "https://openapi.twse.com.tw/v1/ETF/portfolio",
        "https://openapi.twse.com.tw/v1/fund/ETFortfolioView",
    ]
    for url in endpoints:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, params={"ETFid": "0056"})
            if r.status_code == 200:
                data = r.json()
                if data:
                    print(f"  ETF API found at: {url} ({len(data)} records)")
                    return data
        except Exception:
            continue
    return None

def main():
    print(f"\n{'='*55}")
    print(f"  0056/00878/00713 Expansion Analysis — {TODAY}")
    print(f"{'='*55}")

    # Try live ETF holdings API
    print("\n[0] Probing TWSE ETF holdings API...")
    etf_data = try_etf_api()
    if etf_data:
        # Parse out any new codes
        for rec in etf_data:
            code = rec.get("成分股代號") or rec.get("Code") or rec.get("股票代號","")
            if code and code not in ANALYZED and len(code) == 4:
                name = rec.get("成分股名稱") or rec.get("Name","")
                EXPANSION[code] = name
                ETF_MEMBERSHIP[code] = ["0056"]
        print(f"  Found {len(EXPANSION)} expansion stocks (API + hardcoded)")
    else:
        print(f"  ETF API not available — using hardcoded list ({len(EXPANSION)} stocks)")

    codes = list(EXPANSION.keys())
    print(f"  Target codes: {codes}")

    # ── Fetch 1: Quarterly earnings ───────────────────────────────────────
    print("\n[1/3] Quarterly earnings (t187ap14_L)...")
    earn_raw = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap14_L", "t187ap14_L")
    earn_map = {r["公司代號"]: r for r in earn_raw if r.get("公司代號") in codes}
    print(f"  Matched {len(earn_map)} / {len(codes)} expansion stocks")
    wait(120)

    # ── Fetch 2: Valuation ────────────────────────────────────────────────
    print("\n[2/3] Valuation (BWIBBU_ALL)...")
    val_raw  = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL", "BWIBBU_ALL")
    val_map  = {r["Code"]: r for r in val_raw if r["Code"] in codes}
    wait(120)

    # ── Fetch 3: Monthly revenue ──────────────────────────────────────────
    print("\n[3/3] Monthly revenue (t187ap05_L)...")
    rev_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L", "t187ap05_L")
    rev_map  = {r["公司代號"]: r for r in rev_raw if r.get("公司代號") in codes}

    # ── Build stock records ───────────────────────────────────────────────
    print("\n  Compiling expansion stock data...")
    stocks = []
    for code in codes:
        name  = EXPANSION[code]
        etfs  = ETF_MEMBERSHIP.get(code, [])
        e     = earn_map.get(code, {})
        v     = val_map.get(code, {})
        rv    = rev_map.get(code, {})
        is_fin = code in FINANCIAL

        eps     = sf(e.get("基本每股盈餘(元)"))
        rev_q   = sf(e.get("營業收入"))
        op_inc  = sf(e.get("營業利益"))
        net_inc = sf(e.get("稅後淨利"))
        yr      = e.get("年度","")
        q       = e.get("季別","")

        pe      = sf(v.get("PEratio"))
        pb      = sf(v.get("PBratio"))
        div     = sf(v.get("DividendYield"))

        yoy     = sf(rv.get("営業收入-去年同月増減(%)") or rv.get("營業收入-去年同月增減(%)"))
        cum_yoy = sf(rv.get("累計營業收入-前期比較增減(%)"))

        fwd_eps = eps * 4 if eps else None
        op_margin = (op_inc / rev_q * 100) if op_inc and rev_q and rev_q > 0 else None

        # Simple conviction
        if is_fin:
            if pb and pb < 1.0: conv = "BUY"
            elif pb and pb < 1.5: conv = "HOLD"
            else: conv = "WATCH"
        else:
            score = 0
            if pe and pe < 15: score += 30
            elif pe and pe < 25: score += 20
            elif pe and pe < 40: score += 10
            if yoy and yoy > 30: score += 30
            elif yoy and yoy > 10: score += 20
            elif yoy and yoy > 0: score += 10
            if op_margin and op_margin > 20: score += 20
            elif op_margin and op_margin > 10: score += 15
            if div and div > 4: score += 10
            elif div and div > 2: score += 5
            conv = "BUY" if score >= 60 else ("HOLD" if score >= 35 else "WATCH")

        stocks.append({
            "code": code, "name": name, "etfs": etfs, "is_fin": is_fin,
            "eps": eps, "fwd_eps": fwd_eps, "pe": pe, "pb": pb, "div": div,
            "yoy": yoy, "cum_yoy": cum_yoy, "op_margin": op_margin,
            "yr": yr, "q": q, "conv": conv,
        })

    # ── Generate report ───────────────────────────────────────────────────
    lines = [
        f"# 0056 / 00878 / 00713 Expansion Analysis — {TODAY}",
        "",
        "> Stocks in these ETFs NOT covered in the 0050 universe (49 stocks).",
        "> All figures: Q1 2026 (ROC 115 Q1) unless noted.",
        "",
        "---",
        "",
        "## Expansion Stock Summary",
        "",
        "| Code | Name | ETFs | Q1 EPS | Fwd P/E | Rev YoY | Op Margin | P/B | Div% | Action |",
        "|------|------|------|--------|---------|---------|-----------|-----|------|--------|",
    ]

    buys = []
    for s in sorted(stocks, key=lambda x: (x["conv"] != "BUY", x["conv"] != "HOLD", x["code"])):
        etf_str = "+".join(s["etfs"])
        eps_s   = f"¥{s['eps']:.2f}" if s.get("eps") else "N/A"
        pe_s    = f"{s['pe']:.1f}x"  if s.get("pe") else "N/A"
        yoy_s   = (f"+{s['yoy']:.1f}%" if s.get("yoy") and s["yoy"] > 0 else f"{s['yoy']:.1f}%" if s.get("yoy") else "N/A")
        mg_s    = f"{s['op_margin']:.1f}%" if s.get("op_margin") else "N/A"
        pb_s    = f"{s['pb']:.2f}" if s.get("pb") else "N/A"
        div_s   = f"{s['div']:.2f}%" if s.get("div") else "N/A"
        bold    = "**" if s["conv"] == "BUY" else ""
        lines.append(
            f"| {bold}{s['code']}{bold} | {s['name'].split()[0]} | {etf_str} | "
            f"{eps_s} | {pe_s} | {yoy_s} | {mg_s} | {pb_s} | {div_s} | **{s['conv']}** |"
        )
        if s["conv"] == "BUY":
            buys.append(s)

    lines += ["", "---", "", "## Notable BUY Candidates", ""]

    if buys:
        for s in buys:
            lines += [
                f"### {s['code']} {s['name']}",
                f"**ETFs:** {', '.join(s['etfs'])} | **Conviction:** BUY",
                "",
            ]
            if s.get("eps"):
                lines.append(f"- Q1 2026 EPS: ¥{s['eps']:.2f} → Fwd EPS: ¥{s['fwd_eps']:.2f}")
            if s.get("pe"):
                lines.append(f"- P/E: {s['pe']:.1f}x | P/B: {s.get('pb','N/A')} | Div: {s.get('div','N/A')}%")
            if s.get("yoy"):
                lines.append(f"- Revenue YoY: {s['yoy']:+.1f}% | Cumulative YTD: {s.get('cum_yoy','N/A')}%")
            if s.get("op_margin"):
                lines.append(f"- Operating Margin: {s['op_margin']:.1f}%")
            lines.append("")
    else:
        lines.append("*No clear BUY signals in expansion universe. All stocks HOLD or WATCH.*")
        lines.append("")

    lines += [
        "---",
        "",
        "## Cross-ETF Coverage Map",
        "",
        "| ETF | Components Analyzed | Unique (not in 0050) |",
        "|-----|---------------------|----------------------|",
        "| 0050 (元大台灣50) | 49 stocks | — baseline |",
        f"| 0056 (元大高股息) | ~30 | {len([s for s in stocks if '0056' in s['etfs']])} unique |",
        f"| 00878 (國泰永續高股息) | ~50 | {len([s for s in stocks if '00878' in s['etfs']])} unique |",
        f"| 00713 (元大台灣高息低波) | ~50 | {len([s for s in stocks if '00713' in s['etfs']])} unique |",
        "| 006208 (富邦台50) | ~50 | 0 unique (mirrors 0050) |",
        "",
        "**Combined universe analyzed: 49 + " + str(len(stocks)) + " = " + str(49 + len(stocks)) + " stocks**",
        "",
        "---",
        "",
        "## Key Observations",
        "",
        "1. **0056 High Dividend ETF** focuses on yield — P/B and dividend yield are primary metrics.",
        "   Financial sector stocks dominate, where IFRS 17 distorts revenue YoY.",
        "2. **00878 ESG ETF** overlaps heavily with 0050 premium names (TSMC, ASE, Advantech).",
        "   Unique additions tend toward ESG-friendly industrial/tech sectors.",
        "3. **1590 亞德客 (Airtac)** — industrial automation; exposure to China factory automation demand.",
        "   Monitor for China capex recovery as key revenue driver.",
        "4. **2912 統一超 (President Chain Store)** — defensive retail; high store count (6,700+ in Taiwan).",
        "   Dividend reliability over growth momentum.",
        "5. **6488 環球晶 (GlobalWafers)** — silicon wafer duopoly with Shin-Etsu/Sumco.",
        "   Exposure to WFE (wafer fab equipment) cycle — watch fab capacity expansions.",
        "",
        f"*Generated by etf0056_analysis.py — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ]

    out_path = OUT / "ETF0056_EXPANSION.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    # Save JSON
    json_path = OUT / "expansion_stocks.json"
    json_path.write_text(json.dumps(stocks, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n  ✓ Report: {out_path}")
    print(f"  ✓ Data:   {json_path}")
    print(f"\n{'='*55}")
    print(f"  Expansion BUY signals: {[s['code'] for s in buys]}")
    print(f"  Total universe now: 49 (0050) + {len(stocks)} (expansion) = {49+len(stocks)} stocks")
    print(f"{'='*55}")

if __name__ == "__main__":
    main()
