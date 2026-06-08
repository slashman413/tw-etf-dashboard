#!/usr/bin/env python3
"""
Taiwan ETF Component Financial Analyzer
Fetches TWSE data for 0050.TW and 0056.TW components,
generates individual per-stock markdown reports.

Crawl policy: 2-minute minimum between API endpoint calls (TWSE rate limit).
Each TWSE Open API call returns ALL listed stocks at once, so we only need
2 bulk calls total per run rather than N calls per stock.
"""

import time
import json
import requests
import anthropic
from pathlib import Path
from datetime import datetime

client = anthropic.Anthropic()
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ETFAnalyzer/1.0)", "Accept": "application/json"}
TODAY = datetime.now().strftime("%Y-%m-%d")
ROC_YEAR = datetime.now().year - 1911

# ── ETF Component Lists ───────────────────────────────────────────────────────
# Source: FTSE TWSE Taiwan 50 Index — top 50 TWSE stocks by free-float market cap
# Note: Verify current list at https://www.twse.com.tw for latest rebalancing
ETF_0050 = {
    "2330": "台積電 TSMC",
    "2317": "鴻海 Foxconn",
    "2454": "聯發科 MediaTek",
    "2882": "國泰金 Cathay Financial",
    "2881": "富邦金 Fubon Financial",
    "2308": "台達電 Delta Electronics",
    "3008": "大立光 LARGAN",
    "2412": "中華電信 Chunghwa Telecom",
    "2382": "廣達 Quanta",
    "2303": "聯電 UMC",
    "2886": "兆豐金 Mega Financial",
    "2891": "中信金 CTBC Financial",
    "2357": "華碩 ASUS",
    "2603": "長榮 Evergreen Marine",
    "2379": "瑞昱 Realtek",
    "2395": "研華 Advantech",
    "2884": "玉山金 E.Sun Financial",
    "5880": "合庫金 Taiwan Cooperative Financial",
    "2002": "中鋼 China Steel",
    "1301": "台塑 Formosa Plastics",
    "1303": "南亞 Nan Ya Plastics",
    "2207": "和泰車 Hotai Motor",
    "2615": "萬海 Wan Hai Lines",
    "2609": "陽明 Yang Ming Marine",
    "2892": "第一金 First Financial",
    "5871": "中租 Chailease Holdings",
    "6669": "緯穎 Wiwynn",
    "3711": "日月光 ASE Technology",
    "2327": "國巨 Yageo",
    "2408": "南亞科 Nanya Technology",
    "2887": "台新金 Taishin Financial",
    "1216": "統一 Uni-President",
    "1101": "台泥 Taiwan Cement",
    "2409": "友達 AUO",
    "3045": "台灣大 Taiwan Mobile",
    "4938": "和碩 Pegatron",
    "2376": "技嘉 Gigabyte",
    "3034": "聯詠 Novatek",
    "6770": "力積電 PSMC",
    "2801": "彰銀 Chang Hwa Bank",
    "2883": "開發金 China Development Financial",
    "2890": "永豐金 SinoPac Financial",
    "1102": "亞泥 Asia Cement",
    "2301": "光寶 Lite-On Technology",
    "5876": "上海商銀 Shanghai Commercial Bank",
    "2337": "旺宏 Macronix",
    "2883": "開發金 CDFH",
    "2352": "佳世達 Qisda",
    "6415": "矽力 Silergy",
    "3037": "欣興 Unimicron",
}

# 0056.TW: 元大高股息 — high dividend yield ETF (30 stocks selected by dividend forecast)
ETF_0056 = {
    "2887": "台新金 Taishin Financial",
    "2892": "第一金 First Financial",
    "2886": "兆豐金 Mega Financial",
    "5880": "合庫金 Taiwan Cooperative Financial",
    "2884": "玉山金 E.Sun Financial",
    "2890": "永豐金 SinoPac Financial",
    "2801": "彰銀 Chang Hwa Bank",
    "2883": "開發金 CDFH",
    "1101": "台泥 Taiwan Cement",
    "1102": "亞泥 Asia Cement",
    "1216": "統一 Uni-President",
    "2002": "中鋼 China Steel",
    "2207": "和泰車 Hotai Motor",
    "2301": "光寶 Lite-On",
    "2327": "國巨 Yageo",
    "2352": "佳世達 Qisda",
    "2357": "華碩 ASUS",
    "2379": "瑞昱 Realtek",
    "2395": "研華 Advantech",
    "2412": "中華電 Chunghwa Telecom",
    "2603": "長榮 Evergreen Marine",
    "2609": "陽明 Yang Ming Marine",
    "2615": "萬海 Wan Hai Lines",
    "3034": "聯詠 Novatek",
    "3045": "台灣大 Taiwan Mobile",
    "5871": "中租 Chailease",
    "6415": "矽力 Silergy",
    "2303": "聯電 UMC",
    "3711": "日月光 ASE",
    "2408": "南亞科 Nanya",
}

SECTOR_MAP = {
    "2330": "Semiconductor", "2454": "Semiconductor", "2303": "Semiconductor",
    "2408": "Semiconductor", "6770": "Semiconductor", "2337": "Semiconductor",
    "3037": "Semiconductor", "6415": "Semiconductor",
    "2317": "Tech Hardware", "2382": "Tech Hardware", "2357": "Tech Hardware",
    "2308": "Tech Hardware", "3008": "Tech Hardware", "2379": "Tech Hardware",
    "2395": "Tech Hardware", "6669": "Tech Hardware", "4938": "Tech Hardware",
    "2376": "Tech Hardware", "2301": "Tech Hardware", "2409": "Tech Hardware",
    "3034": "Tech Hardware", "2327": "Tech Hardware", "3711": "Tech Hardware",
    "2352": "Tech Hardware",
    "2882": "Financial", "2881": "Financial", "2886": "Financial",
    "2891": "Financial", "2884": "Financial", "5880": "Financial",
    "2892": "Financial", "2887": "Financial", "2801": "Financial",
    "2883": "Financial", "2890": "Financial", "5876": "Financial",
    "5871": "Financial",
    "2412": "Telecom", "3045": "Telecom",
    "2603": "Shipping", "2609": "Shipping", "2615": "Shipping",
    "1301": "Petrochemical", "1303": "Petrochemical", "1101": "Cement",
    "1102": "Cement", "1216": "Consumer", "2207": "Auto",
}


def fetch_bulk(url: str, label: str) -> list:
    """Fetch a TWSE Open API endpoint that returns all stocks at once."""
    print(f"  [{label}] Fetching... ", end="", flush=True)
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()
        data = r.json()
        print(f"OK ({len(data)} records)")
        return data
    except Exception as e:
        print(f"FAILED: {e}")
        return []


def build_stock_data(val_map: dict, rev_map: dict, codes: dict) -> dict:
    """Merge valuation + revenue data for the given stock codes."""
    result = {}
    for code, name in codes.items():
        v = val_map.get(code, {})
        r = rev_map.get(code, {})
        result[code] = {
            "code": code, "name": name,
            "sector": SECTOR_MAP.get(code, "Other"),
            "pe":    v.get("PEratio", "N/A"),
            "pb":    v.get("PBratio", "N/A"),
            "div":   v.get("DividendYield", "N/A"),
            "rev_curr":  r.get("營業收入-當月營收", "N/A"),
            "rev_mom":   r.get("營業收入-上月比較增減(%)", "N/A"),
            "rev_yoy":   r.get("營業收入-去年同月增減(%)", "N/A"),
            "rev_cum":   r.get("累計營業收入-當月累計營收", "N/A"),
            "rev_cum_yoy": r.get("累計營業收入-前期比較增減(%)", "N/A"),
            "period":    r.get("資料年月", "N/A"),
        }
    return result


def generate_stock_report(stock: dict) -> str:
    """Use Claude to generate a per-stock analysis."""
    pe  = stock["pe"]
    pb  = stock["pb"]
    div = stock["div"]
    rev = stock["rev_curr"]
    yoy = stock["rev_yoy"]
    mom = stock["rev_mom"]
    cum_yoy = stock["rev_cum_yoy"]
    period = stock["period"]

    prompt = f"""Generate a concise investment report for this Taiwan-listed stock.

Stock: {stock['code']} {stock['name']}
Sector: {stock['sector']}
Period: {period} (ROC {ROC_YEAR}, Month {str(period)[-2:] if period != 'N/A' else '?'})

Valuation Metrics (as of {TODAY}):
- P/E Ratio: {pe}
- P/B Ratio: {pb}
- Dividend Yield: {div}%

Revenue (NTD thousands):
- Current Month: {rev}
- Month-over-Month: {mom}%
- Year-over-Year: {yoy}%
- Cumulative YTD YoY: {cum_yoy}%

Write a 4-section report:
## Snapshot
One paragraph: what this company does, current valuation assessment (cheap/fair/expensive vs sector peers), and revenue trend.

## Growth Opportunity 🚀
Specific upside catalyst with supporting numbers. If none clear, say so.

## Key Risk 🚩
Single most important risk factor. If financial sector, note IFRS 17 distortion if relevant.

## Verdict
One line: Strong Buy / Buy / Hold / Reduce / Avoid — with one-sentence reason citing a specific metric."""

    msg = client.messages.create(
        model="claude-haiku-4-5",  # Haiku for speed/cost on per-stock mini-reports
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text


def save_stock_report(stock: dict, analysis: str, output_dir: Path) -> Path:
    """Save an individual stock report as markdown."""
    safe_name = stock["code"] + "_" + stock["name"].split()[0].replace("/", "_")
    path = output_dir / f"{safe_name}.md"
    content = (
        f"# {stock['code']} {stock['name']}\n"
        f"**Sector:** {stock['sector']}  |  "
        f"**Date:** {TODAY}  |  "
        f"**P/E:** {stock['pe']}  |  "
        f"**P/B:** {stock['pb']}  |  "
        f"**Div:** {stock['div']}%\n\n"
        f"**Revenue Period:** {stock['period']}  |  "
        f"**YoY:** {stock['rev_yoy']}%  |  "
        f"**Cumul YTD YoY:** {stock['rev_cum_yoy']}%\n\n"
        f"---\n\n{analysis}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def generate_etf_summary(etf_name: str, stocks: dict, all_analyses: dict) -> str:
    """Generate an ETF-level summary report."""
    lines = [f"# {etf_name} ETF Component Analysis", f"**Date:** {TODAY}", ""]
    lines.append("| Code | Name | Sector | P/E | P/B | Div% | Rev YoY% |")
    lines.append("|------|------|--------|-----|-----|------|----------|")
    for code, s in stocks.items():
        lines.append(
            f"| {code} | {s['name'].split()[0]} | {s['sector']} | "
            f"{s['pe']} | {s['pb']} | {s['div']} | {s['rev_yoy']}% |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Individual Stock Reports")
    for code, analysis in all_analyses.items():
        name = stocks[code]["name"]
        lines.append(f"\n### {code} {name}\n")
        lines.append(analysis)
        lines.append("")
    return "\n".join(lines)


def run(etf_codes: dict, etf_label: str, val_map: dict, rev_map: dict,
        output_dir: Path) -> dict:
    """Analyze all stocks in one ETF and save individual + summary reports."""
    print(f"\n{'='*60}")
    print(f"  Analyzing {etf_label} ({len(etf_codes)} components)")
    print(f"{'='*60}")

    stocks = build_stock_data(val_map, rev_map, etf_codes)
    matched = sum(1 for s in stocks.values() if s["rev_curr"] != "N/A")
    print(f"  Data matched: {matched}/{len(etf_codes)} stocks have revenue data")

    etf_dir = output_dir / etf_label.replace(".", "_")
    etf_dir.mkdir(parents=True, exist_ok=True)

    all_analyses = {}
    for i, (code, stock) in enumerate(stocks.items(), 1):
        print(f"  [{i}/{len(stocks)}] Analyzing {code} {stock['name']}...", end=" ", flush=True)
        try:
            analysis = generate_stock_report(stock)
            path = save_stock_report(stock, analysis, etf_dir)
            all_analyses[code] = analysis
            print(f"saved → {path.name}")
        except Exception as e:
            print(f"ERROR: {e}")
            all_analyses[code] = f"[Analysis failed: {e}]"

    # Save ETF-level summary
    summary = generate_etf_summary(etf_label, stocks, all_analyses)
    summary_path = output_dir / f"{etf_label.replace('.', '_')}_SUMMARY.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"\n  ✓ Summary saved: {summary_path}")
    return all_analyses


def main():
    output_dir = Path("reports") / TODAY
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # ── Fetch 1: Valuation data ─────────────────────────────────────────────
    print(f"\n[Fetch 1/2] Valuation metrics (P/E, P/B, Dividend)...")
    val_raw = fetch_bulk(
        "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL",
        "BWIBBU_ALL"
    )
    val_map = {r["Code"]: r for r in val_raw}

    # ── Wait 2 minutes between crawls (per crawl policy) ───────────────────
    print(f"\n  Waiting 120s before next API call (crawl policy: 2-min interval)...")
    for remaining in range(120, 0, -10):
        print(f"  {remaining}s...", end="\r", flush=True)
        time.sleep(10)
    print("  Done waiting.                    ")

    # ── Fetch 2: Monthly revenue ────────────────────────────────────────────
    print(f"\n[Fetch 2/2] Monthly revenue + YoY data...")
    rev_raw = fetch_bulk(
        "https://openapi.twse.com.tw/v1/opendata/t187ap05_L",
        "t187ap05_L"
    )
    rev_map = {r["公司代號"]: r for r in rev_raw}

    # ── Analyze 0050.TW ─────────────────────────────────────────────────────
    run(ETF_0050, "0050.TW", val_map, rev_map, output_dir)

    # ── Analyze 0056.TW ─────────────────────────────────────────────────────
    run(ETF_0056, "0056.TW", val_map, rev_map, output_dir)

    print(f"\n{'='*60}")
    print(f"  All reports saved under: {output_dir}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
