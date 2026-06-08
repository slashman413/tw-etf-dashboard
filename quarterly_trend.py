#!/usr/bin/env python3
"""
Iteration 7: True 4Q Earnings Trend via Yahoo Finance
Fetches 6 quarters of historical EPS + Revenue + Operating Income
for top 20 stocks by composite score, then identifies:
  - Earnings acceleration / deceleration trends
  - QoQ growth consistency
  - 4Q trailing EPS vs Q1 2026 forward annualized

Uses yfinance (Yahoo Finance) — no TWSE rate-limit concerns,
but add small delays between tickers to be respectful.
"""

import time, json
from pathlib import Path
from datetime import datetime

import yfinance as yf
import requests

TODAY = datetime.now().strftime("%Y-%m-%d")
OUT   = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

# Top 20 by composite score (from Iteration 5 results, prioritizing non-financial)
PRIORITY_CODES = [
    "2408","6770","2376","2615","2330","3008","2357","2382","2303",
    "2379","2395","2603","2327","3034","2317","4938","2337","1303",
    "2609","2308",
]

NAMES = {
    "2330":"台積電 TSMC","2317":"鴻海 Foxconn","2454":"聯發科 MediaTek",
    "2308":"台達電 Delta","3008":"大立光 LARGAN","2412":"中華電 Chunghwa",
    "2382":"廣達 Quanta","2303":"聯電 UMC","2357":"華碩 ASUS",
    "2603":"長榮 Evergreen","2379":"瑞昱 Realtek","2395":"研華 Advantech",
    "2327":"國巨 Yageo","2408":"南亞科 NanyaTech","1216":"統一 Uni-Pres",
    "2609":"陽明 YangMing","2615":"萬海 WanHai","6669":"緯穎 Wiwynn",
    "3711":"日月光 ASE","2376":"技嘉 Gigabyte","3034":"聯詠 Novatek",
    "6770":"力積電 PSMC","2337":"旺宏 Macronix","1303":"南亞 NanYa",
    "4938":"和碩 Pegatron",
}

def sf(v):
    try:
        f = float(v)
        return None if (f != f) else f  # NaN check
    except: return None

def pct_change(new, old):
    if new is None or old is None or old == 0: return None
    return (new - old) / abs(old) * 100

def fetch_quarterly(code, suffix=".TW"):
    """Fetch quarterly financials from Yahoo Finance. Returns dict or None."""
    ticker_str = f"{code}{suffix}"
    try:
        t = yf.Ticker(ticker_str)
        # Quarterly income statement — has Revenue, Operating Income, Net Income
        qf = t.quarterly_financials  # DataFrame, cols = quarters (newest first)
        if qf is None or qf.empty:
            return None

        # Quarterly earnings per share
        qe = t.quarterly_earnings  # DataFrame with Earnings column
        # Also try quarterly_income_stmt for newer yfinance versions
        qi = getattr(t, "quarterly_income_stmt", None)

        result = {"code": code, "quarters": []}

        # Iterate columns (quarters, newest first → reverse for chronological)
        cols = list(qf.columns)
        for col in reversed(cols[-6:]):  # last 6 quarters, oldest first
            q_label = col.strftime("%Y-Q") + str((col.month - 1) // 3 + 1) if hasattr(col, 'strftime') else str(col)
            rev_row  = qf.loc["Total Revenue"] if "Total Revenue" in qf.index else None
            op_row   = qf.loc["Operating Income"] if "Operating Income" in qf.index else None
            net_row  = (qf.loc["Net Income"] if "Net Income" in qf.index else
                       (qf.loc["Net Income Common Stockholders"] if "Net Income Common Stockholders" in qf.index else None))

            rev = sf(rev_row[col]) if rev_row is not None else None
            op  = sf(op_row[col]) if op_row is not None else None
            net = sf(net_row[col]) if net_row is not None else None

            result["quarters"].append({
                "period": q_label,
                "revenue": rev,
                "operating_income": op,
                "net_income": net,
            })

        # Add EPS from quarterly_earnings if available
        if qe is not None and not qe.empty and "Earnings" in qe.columns:
            eps_list = list(reversed(qe["Earnings"].tail(6)))
            eps_dates = list(reversed([d.strftime("%Y-Q%d") if hasattr(d, 'strftime') else str(d)
                                       for d in qe.index[-6:]]))
            for i, q in enumerate(result["quarters"]):
                if i < len(eps_list):
                    q["eps"] = sf(eps_list[i])

        return result if result["quarters"] else None

    except Exception as e:
        return {"code": code, "error": str(e), "quarters": []}

def trend_signal(values):
    """Classify a series of values as ACCELERATING/STABLE/DECELERATING."""
    clean = [v for v in values if v is not None]
    if len(clean) < 3: return "INSUFFICIENT DATA"
    # Compare last 2 vs first 2
    early = sum(clean[:2]) / 2
    late  = sum(clean[-2:]) / 2
    if early == 0: return "STABLE"
    pct = (late - early) / abs(early) * 100
    if pct > 15:  return "ACCELERATING ↑"
    if pct < -15: return "DECELERATING ↓"
    return "STABLE →"

def main():
    print(f"\n{'='*60}")
    print(f"  Iteration 7: 4Q Historical EPS Trend (Yahoo Finance)")
    print(f"{'='*60}")

    # Load composite scores for context
    data_path = OUT / "composite_data.json"
    comp_map  = {}
    if data_path.exists():
        comp_data = json.loads(data_path.read_text(encoding="utf-8"))
        comp_map  = {s["code"]: s for s in comp_data}

    results = []
    failed  = []

    print(f"\n  Fetching {len(PRIORITY_CODES)} stocks from Yahoo Finance...")
    print("  (0.5s delay between tickers)\n")

    for i, code in enumerate(PRIORITY_CODES, 1):
        name = NAMES.get(code, code)
        print(f"  [{i:2d}/{len(PRIORITY_CODES)}] {code} {name.split()[0]}...", end=" ", flush=True)
        data = fetch_quarterly(code)
        time.sleep(0.5)  # polite delay

        if data and data.get("quarters"):
            results.append(data)
            print(f"OK ({len(data['quarters'])} quarters)")
        elif data and data.get("error"):
            # Try OTC suffix
            data2 = fetch_quarterly(code, ".TWO")
            time.sleep(0.3)
            if data2 and data2.get("quarters"):
                results.append(data2)
                print(f"OK via .TWO ({len(data2['quarters'])} quarters)")
            else:
                failed.append(code)
                print(f"FAILED")
        else:
            failed.append(code)
            print("No data")

    print(f"\n  Fetched: {len(results)} stocks | Failed: {len(failed)}")
    if failed:
        print(f"  Failed codes: {', '.join(failed)}")

    # ── Generate 4Q Trend Report ──────────────────────────────────────────
    lines = [
        "# Taiwan ETF — 4Q Historical Earnings Trend",
        f"**Date:** {TODAY} | **Source:** Yahoo Finance (yfinance 1.4.1)",
        "**Quarters shown:** Up to 6 quarters (oldest→newest), revenue in thousands TWD",
        "",
        "> Note: Yahoo Finance data may differ slightly from TWSE official filings.",
        "> Net Income shown; EPS where available.",
        "",
        "---",
        "",
    ]

    for data in results:
        code  = data["code"]
        name  = NAMES.get(code, code)
        comp  = comp_map.get(code, {})
        score = comp.get("score")
        qs    = data["quarters"]

        if not qs: continue

        # Compute QoQ revenue changes
        revs     = [q.get("revenue") for q in qs]
        nets     = [q.get("net_income") for q in qs]
        eps_vals = [q.get("eps") for q in qs]

        rev_trend = trend_signal(revs)
        net_trend = trend_signal(nets)

        score_s = f"{score}/100" if score else "N/A"
        lines += [
            f"## {code} {name}",
            f"**Composite Score:** {score_s} | **Trend (Revenue):** {rev_trend} | **Trend (Net Income):** {net_trend}",
            "",
            "| Quarter | Revenue (K) | Op. Income (K) | Net Income (K) | EPS | Rev QoQ |",
            "|---------|-------------|----------------|----------------|-----|---------|",
        ]

        prev_rev = None
        for q in qs:
            rev = q.get("revenue")
            op  = q.get("operating_income")
            net = q.get("net_income")
            eps = q.get("eps")
            qoq = pct_change(rev, prev_rev)

            rev_s = f"{rev/1e3:,.0f}" if rev else "N/A"
            op_s  = f"{op/1e3:,.0f}"  if op  else "N/A"
            net_s = f"{net/1e3:,.0f}" if net  else "N/A"
            eps_s = f"{eps:.2f}"       if eps  else "N/A"
            qoq_s = f"{qoq:+.1f}%"    if qoq is not None else "—"

            lines.append(f"| {q['period']} | {rev_s} | {op_s} | {net_s} | {eps_s} | {qoq_s} |")
            prev_rev = rev

        # QoQ growth series for last 4 quarters
        if len(qs) >= 4:
            last4_revs = revs[-4:]
            qoq_series = [pct_change(last4_revs[i], last4_revs[i-1])
                         for i in range(1, 4) if last4_revs[i] and last4_revs[i-1]]
            if qoq_series:
                avg_qoq = sum(qoq_series) / len(qoq_series)
                lines.append(f"\n*Avg QoQ revenue growth (last 3 periods): {avg_qoq:+.1f}%*")

        lines.append("")

    # Trend summary table
    lines += ["---", "", "## Earnings Trend Summary", "",
              "| Code | Name | Score | Rev Trend | Net Trend | Signal |",
              "|------|------|-------|-----------|-----------|--------|"]

    for data in results:
        code = data["code"]
        name = NAMES.get(code, code)
        qs   = data["quarters"]
        if not qs: continue
        revs = [q.get("revenue") for q in qs]
        nets = [q.get("net_income") for q in qs]
        rev_t = trend_signal(revs)
        net_t = trend_signal(nets)
        score = comp_map.get(code, {}).get("score", 0)
        signal = ("🚀 BUY" if "ACCELERATING" in rev_t and "ACCELERATING" in net_t else
                  ("⚠️ WATCH" if "DECELERATING" in rev_t or "DECELERATING" in net_t else "➡ HOLD"))
        lines.append(f"| {code} | {name.split()[0]} | {score} | {rev_t} | {net_t} | {signal} |")

    lines += ["", "---",
              f"*Generated: {TODAY} | Data: Yahoo Finance | Loop: af8a5b5d | Iteration 7*"]

    out_path = OUT / "QUARTERLY_TREND.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  ✓ Saved: {out_path}")

    # Console summary
    accel = [d for d in results
             if trend_signal([q.get("revenue") for q in d["quarters"]]) == "ACCELERATING ↑"]
    decel = [d for d in results
             if trend_signal([q.get("revenue") for q in d["quarters"]]) == "DECELERATING ↓"]
    print(f"\n  Accelerating revenue trend: {[d['code'] for d in accel]}")
    print(f"  Decelerating revenue trend: {[d['code'] for d in decel]}")

    return results

if __name__ == "__main__":
    main()
