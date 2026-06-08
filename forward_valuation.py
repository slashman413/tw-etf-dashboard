#!/usr/bin/env python3
"""
Iteration 4: Forward P/E & Earnings Acceleration Analysis
Fetches live stock prices (STOCK_DAY_ALL) + trailing valuation (BWIBBU_ALL)
+ Q1 2026 quarterly earnings (t187ap14_L) to compute:
  - Forward P/E = Price / (Q1_EPS * 4)
  - EPS acceleration = (Q1_EPS * 4 - Trailing_EPS) / abs(Trailing_EPS)
  - Value score = growth + yield + margin quality

Crawl policy: 2-min minimum between API endpoint calls.
"""

import time, requests, json
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

TARGET_CODES = [
    "2330","2317","2454","2882","2881","2308","3008","2412","2382","2303",
    "2886","2891","2357","2603","2379","2395","2884","5880","2002","1301",
    "1303","2207","2615","2609","2892","5871","6669","3711","2327","2408",
    "2887","1216","1101","2409","3045","4938","2376","3034","6770","2801",
    "2883","2890","1102","2301","5876","2337","2352","6415","3037",
]

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
}

FINANCIAL = {"2882","2881","2886","2891","2884","5880","2892","2887",
             "2801","2883","2890","5876","5871"}

def safe_float(v):
    try: return float(str(v).replace(",","").replace("--",""))
    except: return None

def fetch(url, label):
    print(f"  [{label}] Fetching... ", end="", flush=True)
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    d = r.json()
    print(f"OK ({len(d)} records)")
    return d

def wait(seconds=120):
    for s in range(seconds, 0, -10):
        print(f"  {s}s...", end="\r", flush=True)
        time.sleep(10)
    print("  Fetching now...              ")

def main():
    print(f"\n{'='*60}")
    print(f"  Iteration 4: Forward P/E Analysis — {TODAY}")
    print(f"{'='*60}")

    # ── Fetch 1: Q1 2026 Quarterly EPS ────────────────────────────────────
    print("\n[1/3] Q1 2026 quarterly earnings (t187ap14_L)...")
    q1_raw = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap14_L", "t187ap14_L")
    q1_map = {r["公司代號"]: r for r in q1_raw if r.get("公司代號") in TARGET_CODES}
    print(f"  Matched {len(q1_map)} stocks")

    # ── Fetch 2: Trailing P/E + P/B + Dividend ────────────────────────────
    print("\n[2/3] Trailing valuation (2-min wait)...")
    wait()
    val_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL", "BWIBBU_ALL")
    val_map = {r["Code"]: r for r in val_raw}

    # ── Fetch 3: Stock Prices ─────────────────────────────────────────────
    print("\n[3/3] Stock prices STOCK_DAY_ALL (2-min wait)...")
    wait()
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", "STOCK_DAY_ALL")
    price_map = {r.get("Code","") or r.get("股票代號",""): r for r in price_raw}

    # ── Compute forward metrics ───────────────────────────────────────────
    print("\nComputing forward P/E metrics...")
    results = []

    for code in TARGET_CODES:
        name = NAMES.get(code, code)
        q = q1_map.get(code, {})
        v = val_map.get(code, {})
        p = price_map.get(code, {})

        # Q1 data
        q1_eps      = safe_float(q.get("基本每股盈餘(元)"))
        q1_rev      = safe_float(q.get("營業收入"))
        q1_op_pft   = safe_float(q.get("營業利益"))
        q1_net      = safe_float(q.get("稅後淨利"))

        # Valuation
        trailing_pe = safe_float(v.get("PEratio"))
        pb          = safe_float(v.get("PBratio"))
        div_yield   = safe_float(v.get("DividendYield"))

        # Price (STOCK_DAY_ALL field names vary — try both)
        price = (safe_float(p.get("ClosingPrice")) or
                 safe_float(p.get("收盤價")) or
                 safe_float(p.get("close")))

        # Derived metrics
        fwd_eps        = q1_eps * 4 if q1_eps else None
        fwd_pe         = price / fwd_eps if (price and fwd_eps and fwd_eps > 0) else None
        trailing_eps   = price / trailing_pe if (price and trailing_pe and trailing_pe > 0) else None
        eps_accel_pct  = ((fwd_eps - trailing_eps) / abs(trailing_eps) * 100
                         if (fwd_eps and trailing_eps and trailing_eps != 0) else None)
        pe_compression = (trailing_pe - fwd_pe if (trailing_pe and fwd_pe) else None)
        op_margin      = (q1_op_pft / q1_rev * 100
                         if q1_op_pft and q1_rev and q1_rev > 0 else None)

        results.append({
            "code": code, "name": name,
            "is_financial": code in FINANCIAL,
            "q1_eps": q1_eps, "fwd_eps": fwd_eps,
            "trailing_eps": trailing_eps,
            "eps_accel_pct": eps_accel_pct,
            "trailing_pe": trailing_pe, "fwd_pe": fwd_pe,
            "pe_compression": pe_compression,
            "pb": pb, "div_yield": div_yield, "price": price,
            "op_margin": op_margin,
        })

    # ── Sort by EPS acceleration (best first) ────────────────────────────
    non_fin = [r for r in results if not r["is_financial"]]
    acc_ranked = sorted(
        [r for r in non_fin if r.get("eps_accel_pct") is not None],
        key=lambda x: x["eps_accel_pct"], reverse=True
    )
    fwd_pe_ranked = sorted(
        [r for r in non_fin if r.get("fwd_pe") and r["fwd_pe"] > 0],
        key=lambda x: x["fwd_pe"]
    )

    # ── Generate Forward Valuation Report ────────────────────────────────
    lines = [
        "# Taiwan ETF Components — Forward P/E & Earnings Acceleration",
        f"**Date:** {TODAY} | **Quarterly Data:** Q1 2026 | **Forward EPS:** Q1 × 4 (annualized)",
        "**Source:** TWSE Open API (t187ap14_L + BWIBBU_ALL + STOCK_DAY_ALL)",
        "",
        "> Note: Forward EPS = Q1 2026 EPS × 4. Q1 may be seasonally atypical.",
        "> Financial sector stocks excluded from P/E analysis (different earnings structure).",
        "",
        "---",
        "",
        "## EPS Acceleration Leaders",
        "(Stocks where annualized Q1 2026 EPS greatly exceeds trailing 12-month EPS)",
        "",
        "| Code | Name | Trailing EPS | Fwd EPS (Q1×4) | EPS Accel | Trailing P/E | Fwd P/E | Signal |",
        "|------|------|-------------|----------------|-----------|-------------|---------|--------|",
    ]

    for r in acc_ranked[:15]:
        te = f"{r['trailing_eps']:.2f}" if r['trailing_eps'] else "N/A"
        fe = f"{r['fwd_eps']:.2f}" if r['fwd_eps'] else "N/A"
        ac = f"+{r['eps_accel_pct']:.0f}%" if r['eps_accel_pct'] and r['eps_accel_pct'] > 0 else f"{r['eps_accel_pct']:.0f}%"
        tpe = f"{r['trailing_pe']:.1f}x" if r['trailing_pe'] else "N/A"
        fpe = f"{r['fwd_pe']:.1f}x" if r['fwd_pe'] else "N/A"
        signal = "🚀 STRONG" if (r['eps_accel_pct'] or 0) > 100 else ("📈 UP" if (r['eps_accel_pct'] or 0) > 30 else "↗")
        lines.append(f"| {r['code']} | {r['name'].split()[0]} | {te} | {fe} | {ac} | {tpe} | {fpe} | {signal} |")

    lines += [
        "",
        "---",
        "",
        "## Cheapest by Forward P/E (non-financial, min EPS > 0)",
        "",
        "| Rank | Code | Name | Price | Fwd EPS | Fwd P/E | Trailing P/E | P/E Compression | Div% |",
        "|------|------|------|-------|---------|---------|-------------|-----------------|------|",
    ]

    for i, r in enumerate(fwd_pe_ranked[:15], 1):
        px = f"¥{r['price']:.1f}" if r['price'] else "N/A"
        fe = f"¥{r['fwd_eps']:.2f}" if r['fwd_eps'] else "N/A"
        fpe = f"{r['fwd_pe']:.1f}x" if r['fwd_pe'] else "N/A"
        tpe = f"{r['trailing_pe']:.1f}x" if r['trailing_pe'] else "N/A"
        comp = f"-{r['pe_compression']:.1f}x" if r['pe_compression'] and r['pe_compression'] > 0 else "N/A"
        div = f"{r['div_yield']:.2f}%" if r['div_yield'] else "N/A"
        lines.append(f"| {i} | {r['code']} | {r['name'].split()[0]} | {px} | {fe} | {fpe} | {tpe} | {comp} | {div} |")

    lines += [
        "",
        "---",
        "",
        "## Expensive by Forward P/E (possible value traps)",
        "",
        "| Code | Name | Price | Fwd EPS | Fwd P/E | Trailing P/E | Assessment |",
        "|------|------|-------|---------|---------|-------------|------------|",
    ]

    expensive = sorted(
        [r for r in fwd_pe_ranked if r.get("fwd_pe") and r["fwd_pe"] > 40],
        key=lambda x: -x["fwd_pe"]
    )
    for r in expensive[:10]:
        px = f"¥{r['price']:.1f}" if r['price'] else "N/A"
        fe = f"¥{r['fwd_eps']:.2f}" if r['fwd_eps'] else "N/A"
        fpe = f"{r['fwd_pe']:.1f}x" if r['fwd_pe'] else "N/A"
        tpe = f"{r['trailing_pe']:.1f}x" if r['trailing_pe'] else "N/A"
        assess = "AVOID" if (r['fwd_pe'] or 0) > 80 else "CAUTION"
        lines.append(f"| {r['code']} | {r['name'].split()[0]} | {px} | {fe} | {fpe} | {tpe} | **{assess}** |")

    lines += [
        "",
        "---",
        "",
        "## Financial Sector (P/B based, earnings distorted by IFRS 17)",
        "",
        "| Code | Name | P/B | Div Yield | Q1 EPS | Assessment |",
        "|------|------|-----|-----------|--------|------------|",
    ]

    fin_stocks = sorted(
        [r for r in results if r["is_financial"]],
        key=lambda x: -(x.get("div_yield") or 0)
    )
    for r in fin_stocks:
        pb = f"{r['pb']:.2f}x" if r['pb'] else "N/A"
        div = f"{r['div_yield']:.2f}%" if r['div_yield'] else "N/A"
        eps = f"¥{r['q1_eps']:.2f}" if r['q1_eps'] else "N/A"
        assess = ("BUY" if (r.get("div_yield") or 0) > 4.5 else
                  ("BUY" if (r.get("pb") or 99) < 1.2 else "HOLD"))
        lines.append(f"| {r['code']} | {r['name'].split()[0]} | {pb} | {div} | {eps} | **{assess}** |")

    # Key insight section
    top_acc = acc_ranked[0] if acc_ranked else None
    cheapest_fwd = fwd_pe_ranked[0] if fwd_pe_ranked else None

    lines += [
        "",
        "---",
        "",
        "## Investment Thesis Summary",
        "",
    ]

    if top_acc:
        lines.append(
            f"**#1 EPS Accelerator:** {top_acc['code']} {top_acc['name']} — "
            f"EPS grew {top_acc['eps_accel_pct']:+.0f}% from TTM to Q1×4 annualized. "
            f"If this rate persists, current P/E implies significant upside."
        )
    if cheapest_fwd:
        lines.append(
            f"\n**Cheapest Forward P/E:** {cheapest_fwd['code']} {cheapest_fwd['name']} — "
            f"Forward P/E only {cheapest_fwd['fwd_pe']:.1f}x on Q1 annualized EPS. "
            f"Trailing P/E was {cheapest_fwd['trailing_pe'] or 'N/A'}x."
        )

    lines += [
        "",
        "**Key Rule:** Stocks where Forward P/E < Trailing P/E show EPS ACCELERATION.",
        "The bigger the gap, the more the market has yet to re-rate.",
        "",
        "---",
        f"*Generated: {TODAY} | 2-min crawl interval | Loop: af8a5b5d (every 5 min)*",
    ]

    out_path = OUT / "FORWARD_VALUATION.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ Saved: {out_path}")

    # Console summary
    print(f"\n{'='*60}")
    if acc_ranked:
        print("  Top 5 EPS Accelerators:")
        for r in acc_ranked[:5]:
            fpe = f"{r['fwd_pe']:.1f}x" if r['fwd_pe'] else "N/A"
            print(f"    {r['code']} {r['name'].split()[0]:15} EPS Accel={r['eps_accel_pct']:+.0f}%  FwdP/E={fpe}")
    if fwd_pe_ranked:
        print("\n  Cheapest 5 by Forward P/E:")
        for r in fwd_pe_ranked[:5]:
            print(f"    {r['code']} {r['name'].split()[0]:15} FwdP/E={r['fwd_pe']:.1f}x  Price=¥{r['price'] or 'N/A'}")
    print(f"{'='*60}")

    return acc_ranked, fwd_pe_ranked, fin_stocks

if __name__ == "__main__":
    main()
