#!/usr/bin/env python3
"""
MOPS Financial Report Analyzer
Scrapes Taiwan TWSE financial reports then uses Claude Opus 4.8
with adaptive thinking for deep, investment-grade analysis.

Usage:
  # Single company
  python financial_analysis.py --co-id 2330

  # Multiple companies (comparison)
  python financial_analysis.py --co-id 2330 2454 2317

  # Specific year/quarter
  python financial_analysis.py --co-id 2330 --year 114 --quarter 3

  # Annual report
  python financial_analysis.py --co-id 2330 --year 114

  # All preset major companies
  python financial_analysis.py --all
"""

import argparse
import anthropic
from pathlib import Path
from mops_scraper import fetch_multiple, fetch_company_report, COMPANIES, _roc_year

MODEL  = "claude-opus-4-8"
client = anthropic.Anthropic()

SYSTEM_SINGLE = """You are an elite buy-side financial analyst specializing in Taiwan Stock Exchange (TWSE/TSEC) listed companies.

When given a financial report, produce a structured analysis covering:

## 1. Company Overview
Brief description of the company and its core business.

## 2. Financial Highlights
Extract and present key metrics: Revenue, Gross Profit, Operating Income, Net Income, EPS, ROE, ROA, Debt-to-Equity, Current Ratio. If values are in thousands (千元) or millions (百萬元) of NTD, note that clearly.

## 3. Trend Analysis
Identify any quarter-over-quarter or year-over-year trends. Is the business growing, stable, or deteriorating?

## 4. Margin Analysis
Gross margin, operating margin, net margin — and what's driving changes.

## 5. Red Flags 🚩
Any accounting anomalies, sudden changes, high leverage, declining cash flow, or other warning signs.

## 6. Competitive Position
How does this company fit within its sector? Any moat or competitive advantages visible in the numbers?

## 7. Investment Verdict
A concise investment outlook: Bull case, Bear case, and a one-line overall verdict.

Important notes:
- Financial figures on TWSE are typically in thousands of NTD (新台幣千元)
- ROC year = Gregorian year − 1911 (e.g. ROC 114 = 2025)
- Be specific: cite actual numbers from the report, not vague statements
- If the data is incomplete or ambiguous, say so explicitly"""


SYSTEM_COMPARISON = """You are an elite buy-side financial analyst specializing in Taiwan Stock Exchange (TWSE/TSEC) listed companies.

You have been given financial reports for multiple companies. Produce a comparative investment analysis:

## 1. Executive Comparison Table
Create a markdown table showing key metrics side-by-side for all companies:
Revenue | Gross Margin | Operating Margin | Net Margin | EPS | ROE | ROA | D/E Ratio

## 2. Sector Context
What sector(s) do these companies represent? How do they compare within their sectors?

## 3. Growth Leaders
Which company/companies show the strongest growth trajectory?

## 4. Profitability Leaders
Which company has the best margins and capital efficiency?

## 5. Risk Assessment
Rank companies by financial risk (leverage, liquidity, earnings stability).

## 6. Red Flags 🚩
Any anomalies or concerns across the companies.

## 7. Investment Rankings
Rank all companies from most to least attractive investment, with reasoning for each.

## 8. Top Pick
Your single strongest conviction pick with a 3-sentence thesis.

Important: Be specific. Cite actual numbers. ROC year = Gregorian year − 1911."""


def _format_report_for_claude(report: dict) -> str:
    """Format a scraped report dict into a clear prompt block."""
    label = f"Q{report['quarter']}" if report.get("quarter") else "Annual"
    header = (f"Company: {report['name']} (Stock: {report['co_id']})\n"
              f"Period: ROC Year {report['year']} {label}\n"
              f"Data format: {'PDF' if 'pdf' in report.get('content_type','').lower() else 'HTML table'}\n\n")
    return header + (report.get("text") or "[No data retrieved]")


def analyze_single(co_id: str, year: int = None, quarter: int = None, save_to: str = None) -> dict:
    """
    Fetch and analyze a single company's financial report.

    Args:
        co_id:   Stock code, e.g. '2330'.
        year:    ROC year. Defaults to current year.
        quarter: 1–4 for quarterly, None for annual.
        save_to: Optional Markdown file path for the report.

    Returns:
        dict with analysis, report data, and token usage.
    """
    print(f"\n{'='*60}")
    print(f"  Fetching report: {COMPANIES.get(co_id, co_id)}")
    print(f"{'='*60}")

    report = fetch_company_report(co_id, year, quarter)

    if report.get("error") and not report.get("text"):
        print(f"Error: {report['error']}")
        return report

    print("\nAnalyzing with Claude Opus 4.8 (adaptive thinking)...")

    msg = client.messages.create(
        model=MODEL,
        max_tokens=6000,
        thinking={"type": "adaptive"},
        system=SYSTEM_SINGLE,
        messages=[{
            "role": "user",
            "content": f"Please analyze the following financial report:\n\n{_format_report_for_claude(report)}"
        }]
    )

    analysis = next(b.text for b in msg.content if hasattr(b, "text") and b.type == "text")

    label = f"Q{quarter}" if quarter else "Annual"
    full_report = (
        f"# Financial Analysis: {report['name']} ({co_id})\n"
        f"**Period:** ROC {report['year']} {label}\n\n---\n\n{analysis}"
    )

    if save_to:
        Path(save_to).write_text(full_report, encoding="utf-8")
        print(f"\n  ✓ Saved: {save_to}")

    print(f"\n  Tokens used: {msg.usage.input_tokens:,} in / {msg.usage.output_tokens:,} out")
    print("\n" + "="*60)
    print(analysis)

    return {
        "co_id": co_id,
        "name": report["name"],
        "analysis": analysis,
        "report": report,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
        "saved_to": save_to,
    }


def analyze_comparison(
    co_ids: list,
    year: int = None,
    quarter: int = None,
    save_to: str = None,
) -> dict:
    """
    Fetch reports for multiple companies and produce a comparative analysis.

    Args:
        co_ids:  List of stock codes.
        year:    ROC year. Defaults to current year.
        quarter: 1–4 for quarterly, None for annual.
        save_to: Optional Markdown file path.

    Returns:
        dict with analysis and all individual reports.
    """
    print(f"\n{'='*60}")
    print(f"  Comparative Analysis: {', '.join(co_ids)}")
    print(f"{'='*60}")

    reports = fetch_multiple(co_ids, year, quarter)

    # Build combined prompt
    blocks = []
    for r in reports:
        if not (r.get("error") and not r.get("text")):
            blocks.append(f"---\n{_format_report_for_claude(r)}")

    if not blocks:
        print("Error: No reports could be fetched.")
        return {"error": "No data", "reports": reports}

    combined = "\n\n".join(blocks)
    print(f"\nAnalyzing {len(blocks)} report(s) with Claude Opus 4.8 (adaptive thinking)...")

    msg = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=SYSTEM_COMPARISON,
        messages=[{
            "role": "user",
            "content": f"Perform a comparative financial analysis of these {len(blocks)} companies:\n\n{combined}"
        }]
    )

    analysis = next(b.text for b in msg.content if hasattr(b, "text") and b.type == "text")

    names = ", ".join(r["name"] for r in reports)
    label = f"Q{quarter}" if quarter else "Annual"
    year_used = year or _roc_year()

    full_report = (
        f"# Comparative Financial Analysis\n"
        f"**Companies:** {names}\n"
        f"**Period:** ROC {year_used} {label}\n\n---\n\n{analysis}"
    )

    if save_to:
        Path(save_to).write_text(full_report, encoding="utf-8")
        print(f"\n  ✓ Saved: {save_to}")

    print(f"\n  Tokens: {msg.usage.input_tokens:,} in / {msg.usage.output_tokens:,} out")
    print("\n" + "="*60)
    print(analysis)

    return {
        "companies": co_ids,
        "analysis": analysis,
        "reports": reports,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
        "saved_to": save_to,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Taiwan TWSE Financial Report Analyzer (Claude Opus 4.8)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Preset companies (use with --co-id or --all):
{chr(10).join(f'  {k}: {v}' for k, v in COMPANIES.items())}

Examples:
  python financial_analysis.py --co-id 2330
  python financial_analysis.py --co-id 2330 2454 2317
  python financial_analysis.py --co-id 2330 --year 114 --quarter 3
  python financial_analysis.py --all --save report.md
        """
    )
    parser.add_argument("--co-id", nargs="+", metavar="CODE",
                        help="Stock code(s) to analyze (e.g. 2330 2454)")
    parser.add_argument("--all", action="store_true",
                        help="Analyze all preset major companies")
    parser.add_argument("--year", type=int, default=None,
                        help=f"ROC year (default: current = {_roc_year()})")
    parser.add_argument("--quarter", type=int, choices=[1, 2, 3, 4], default=None,
                        help="Quarter 1–4 (omit for annual report)")
    parser.add_argument("--save", metavar="FILE", default=None,
                        help="Save analysis as Markdown file")

    args = parser.parse_args()

    if args.all:
        co_ids = list(COMPANIES.keys())
    elif args.co_id:
        co_ids = args.co_id
    else:
        parser.error("Specify --co-id CODE [CODE ...] or --all")
        return

    if len(co_ids) == 1:
        analyze_single(co_ids[0], args.year, args.quarter, args.save)
    else:
        analyze_comparison(co_ids, args.year, args.quarter, args.save)


if __name__ == "__main__":
    main()
