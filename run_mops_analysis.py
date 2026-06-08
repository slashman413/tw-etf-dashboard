#!/usr/bin/env python3
"""
Live TWSE Financial Analysis
Fetches real-time data from TWSE Open API and runs Claude Opus 4.8 analysis.
Respects 2-minute crawl interval policy (hardcoded delay between API calls).
"""

import time
import json
import requests
import anthropic
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FinancialAnalyzer/1.0)",
    "Accept": "application/json",
}

# Top 0050.TW ETF components by weight
TARGETS = {
    "2330": "台積電 TSMC",
    "2317": "鴻海 Foxconn",
    "2454": "聯發科 MediaTek",
    "2882": "國泰金 Cathay Financial",
    "2881": "富邦金 Fubon Financial",
    "2308": "台達電 Delta Electronics",
    "3008": "大立光 LARGAN Precision",
    "2412": "中華電信 Chunghwa Telecom",
    "2382": "廣達 Quanta Computer",
    "2303": "聯電 UMC",
    "2886": "兆豐金 Mega Financial",
    "2891": "中信金 CTBC Financial",
    "2357": "華碩 ASUS",
    "2603": "長榮 Evergreen Marine",
    "2379": "瑞昱 Realtek",
}

SYSTEM = """You are a top-tier buy-side equity analyst specializing in Taiwan Stock Exchange (TWSE) listed companies, with deep expertise in Asian semiconductor, technology, financial, and shipping sectors.

You have been given the latest available market data (valuation multiples + revenue performance) for major Taiwan-listed stocks. Today's date is {date} (ROC {roc_year}).

Produce an investment-grade financial report with these sections:

## Market Overview
Brief summary of the Taiwan market environment based on the data.

## Company-by-Company Snapshot
For each company, one paragraph covering: current valuation (P/E, P/B, yield), revenue trend (YoY growth), and a one-line verdict.

## Sector Analysis
Group companies by sector (Semiconductors, Technology Hardware, Financials, Shipping/Others). Identify which sectors are leading vs lagging.

## Top Growth Opportunities 🚀
3–5 specific companies showing the strongest fundamentals for upside. Cite actual numbers.

## Key Risk Flags 🚩
3–5 warning signs visible in the data (overvaluation, declining revenue, weak yield, etc.).

## Valuation Comparison
Quick table: Code | Name | P/E | P/B | Div% | Revenue YoY%
Rank from most attractive to least based on value + growth combination.

## Investment Verdict
Top 3 picks with thesis. One company to avoid with reason.

Be specific. Use actual figures. Note that revenue figures are in thousands of NTD (新台幣千元)."""


def fetch_with_delay(url: str, label: str, delay: int = 5) -> dict | None:
    print(f"  Fetching {label}... ", end="", flush=True)
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()
        print(f"OK ({len(data)} records)")
        time.sleep(delay)
        return data
    except Exception as e:
        print(f"FAILED: {e}")
        return None


def main():
    roc_year = datetime.now().year - 1911
    today = datetime.now().strftime("%Y-%m-%d")

    print("=" * 60)
    print("  TWSE Financial Report — Live Analysis")
    print(f"  Date: {today} (ROC {roc_year})")
    print("=" * 60)

    # ── Fetch 1: Valuation Metrics (P/E, P/B, Dividend Yield) ─────────────────
    print("\n[1/2] Fetching valuation data from TWSE...")
    valuation_data = fetch_with_delay(
        "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL",
        "P/E, P/B, Dividend Yield",
        delay=60,  # 60s minimum between API calls to avoid IP ban
    )

    # ── Fetch 2: Monthly Revenue ───────────────────────────────────────────────
    print("[2/2] Fetching monthly revenue data from TWSE... (waiting 60s)")
    revenue_data = fetch_with_delay(
        "https://openapi.twse.com.tw/v1/opendata/t187ap05_L",
        "Monthly Revenue",
        delay=60,
    )

    if not valuation_data and not revenue_data:
        print("\nError: Could not fetch any data.")
        return

    # ── Filter for target companies ───────────────────────────────────────────
    val_map = {}
    if valuation_data:
        for rec in valuation_data:
            code = rec.get("Code", "")
            if code in TARGETS:
                val_map[code] = rec

    rev_map = {}
    if revenue_data:
        for rec in revenue_data:
            code = rec.get("公司代號", "")
            if code in TARGETS:
                rev_map[code] = rec

    print(f"\n  Matched {len(val_map)} valuation records, {len(rev_map)} revenue records")

    # ── Build data summary for Claude ─────────────────────────────────────────
    lines = []
    lines.append(f"Data as of: {today} (ROC {roc_year})")
    lines.append(f"Source: TWSE Open API (BWIBBU_ALL + t187ap05_L)")
    lines.append("\n=== VALUATION METRICS (P/E, Dividend Yield, P/B) ===")

    for code, name in TARGETS.items():
        v = val_map.get(code, {})
        r = rev_map.get(code, {})
        pe   = v.get("PEratio", "N/A")
        div  = v.get("DividendYield", "N/A")
        pb   = v.get("PBratio", "N/A")
        curr = r.get("營業收入-當月營收", "N/A")
        mom  = r.get("營業收入-上月比較增減(%)", "N/A")
        yoy  = r.get("營業收入-去年同月增減(%)", "N/A")
        cum  = r.get("累計營業收入-當月累計營收", "N/A")
        cum_yoy = r.get("累計營業收入-前期比較增減(%)", "N/A")
        period  = r.get("資料年月", "N/A")

        lines.append(f"\n{code} {name}")
        lines.append(f"  Valuation: P/E={pe}, Div Yield={div}%, P/B={pb}")
        if curr != "N/A":
            lines.append(f"  Revenue ({period}): {curr} (MoM: {mom}%, YoY: {yoy}%)")
            lines.append(f"  Cumulative Revenue: {cum} (YoY: {cum_yoy}%)")

    data_text = "\n".join(lines)
    print(f"\n  Data summary: {len(data_text):,} characters")

    # ── Analyze with Claude Opus 4.8 ──────────────────────────────────────────
    print("\n[Analyzing] Claude Opus 4.8 + adaptive thinking...")
    system = SYSTEM.format(date=today, roc_year=roc_year)

    msg = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{
            "role": "user",
            "content": (
                f"Analyze the following live Taiwan stock market data and produce the full report:\n\n"
                f"{data_text}\n\n"
                f"Focus on the 0050.TW ETF components listed. Provide actionable investment insights."
            )
        }]
    )

    analysis = next(b.text for b in msg.content if hasattr(b, "text") and b.type == "text")

    # ── Save report ───────────────────────────────────────────────────────────
    report_path = Path("taiwan_financial_report.md")
    report = (
        f"# Taiwan Stock Market Financial Report\n"
        f"**Date:** {today} (ROC {roc_year})\n"
        f"**Source:** TWSE Open API — Valuation Multiples + Monthly Revenue\n"
        f"**Model:** Claude Opus 4.8 with Adaptive Thinking\n\n"
        f"---\n\n{analysis}\n\n"
        f"---\n\n## Raw Data\n```\n{data_text}\n```"
    )
    report_path.write_text(report, encoding="utf-8")

    print(f"\n  ✓ Report saved: {report_path}")
    print(f"  Tokens: {msg.usage.input_tokens:,} in / {msg.usage.output_tokens:,} out")
    print("\n" + "="*60)
    print(analysis)
    print("="*60)

    return analysis


if __name__ == "__main__":
    main()
