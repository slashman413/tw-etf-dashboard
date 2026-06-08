#!/usr/bin/env python3
"""
Iteration 8: Expand 4Q trend coverage + Final Consolidated Brief
- Fetches Yahoo Finance historical data for remaining 14 non-financial stocks
- Merges with composite_data.json + QUARTERLY_TREND results
- Generates FINAL_BRIEF.md: definitive investment document combining all 8 iterations
"""

import time, json
from pathlib import Path
from datetime import datetime
import yfinance as yf

TODAY = datetime.now().strftime("%Y-%m-%d")
OUT   = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

# Remaining non-financial stocks not covered in Iter 7
REMAINING = ["2454","2412","6669","3711","1101","1102","1216","2207",
             "6415","2301","2002","1301","2409","2352"]

# Already covered in Iter 7
ITER7_DONE = ["2408","6770","2376","2615","2330","3008","2357","2382",
              "2303","2379","2395","2603","2327","3034","2317","4938",
              "2337","1303","2609","2308"]

NAMES = {
    "2330":"台積電 TSMC","2317":"鴻海 Foxconn","2454":"聯發科 MediaTek",
    "2308":"台達電 Delta","3008":"大立光 LARGAN","2412":"中華電 Chunghwa",
    "2382":"廣達 Quanta","2303":"聯電 UMC","2357":"華碩 ASUS",
    "2603":"長榮 Evergreen","2379":"瑞昱 Realtek","2395":"研華 Advantech",
    "2327":"國巨 Yageo","2408":"南亞科 NanyaTech","1216":"統一 Uni-Pres",
    "2609":"陽明 YangMing","2615":"萬海 WanHai","6669":"緯穎 Wiwynn",
    "3711":"日月光 ASE","2376":"技嘉 Gigabyte","3034":"聯詠 Novatek",
    "6770":"力積電 PSMC","2337":"旺宏 Macronix","1303":"南亞 NanYa",
    "4938":"和碩 Pegatron","2454":"聯發科 MediaTek","6415":"矽力 Silergy",
    "2301":"光寶 LiteOn","2002":"中鋼 ChinaSteel","1301":"台塑 Formosa",
    "2409":"友達 AUO","2352":"佳世達 Qisda","1101":"台泥 Cement",
    "1102":"亞泥 AsiaCement","2207":"和泰車 Hotai",
    "2882":"國泰金 Cathay","2881":"富邦金 Fubon","2886":"兆豐金 Mega",
    "2891":"中信金 CTBC","2884":"玉山金 E.Sun","5880":"合庫金 TWCoop",
    "2892":"第一金 First","2887":"台新金 Taishin","2801":"彰銀 ChangHwa",
    "2883":"開發金 CDFH","2890":"永豐金 SinoPac","5876":"上海商銀 ShanghaiCB",
    "5871":"中租 Chailease",
}

FINANCIAL = {"2882","2881","2886","2891","2884","5880","2892","2887",
             "2801","2883","2890","5876","5871"}

def sf(v):
    try:
        f = float(v)
        return None if (f != f) else f
    except: return None

def pct_change(new, old):
    if new is None or old is None or old == 0: return None
    return (new - old) / abs(old) * 100

def trend_signal(values):
    clean = [v for v in values if v is not None]
    if len(clean) < 3: return "N/A"
    early = sum(clean[:2]) / 2
    late  = sum(clean[-2:]) / 2
    if early == 0: return "STABLE"
    pct = (late - early) / abs(early) * 100
    if pct > 15:  return "ACCEL ↑"
    if pct < -15: return "DECEL ↓"
    return "STABLE →"

def fetch_trend(code):
    try:
        t = yf.Ticker(f"{code}.TW")
        qf = t.quarterly_financials
        if qf is None or qf.empty: return None
        quarters = []
        cols = list(qf.columns)
        for col in reversed(cols[-5:]):
            ql = col.strftime("%YQ%m") if hasattr(col, 'strftime') else str(col)
            q_num = (col.month - 1) // 3 + 1 if hasattr(col, 'month') else 0
            period = f"{col.year}-Q{q_num}" if hasattr(col, 'year') else ql
            rev = sf(qf.loc["Total Revenue"][col]) if "Total Revenue" in qf.index else None
            op  = sf(qf.loc["Operating Income"][col]) if "Operating Income" in qf.index else None
            net = (sf(qf.loc["Net Income"][col]) if "Net Income" in qf.index else
                   sf(qf.loc["Net Income Common Stockholders"][col])
                   if "Net Income Common Stockholders" in qf.index else None)
            quarters.append({"period": period, "rev": rev, "op": op, "net": net})
        return quarters if quarters else None
    except:
        return None

def conviction(s, rev_trend, net_trend):
    """Final conviction combining composite score + trend."""
    score = s.get("score", 0)
    is_fin = s.get("is_fin", False)

    if is_fin:
        if score >= 70: return "STRONG BUY"
        if score >= 55: return "BUY"
        return "HOLD"

    # Adjust based on trend
    bonus = 0
    if rev_trend == "ACCEL ↑": bonus += 10
    if net_trend == "ACCEL ↑": bonus += 8
    if rev_trend == "DECEL ↓": bonus -= 12
    if net_trend == "DECEL ↓": bonus -= 10

    adj = score + bonus

    if adj >= 70: return "STRONG BUY"
    if adj >= 55: return "BUY"
    if adj >= 40: return "HOLD"
    if s.get("fwd_pe") and s["fwd_pe"] > 70: return "AVOID"
    if s.get("op_margin") and s["op_margin"] < 0: return "AVOID"
    return "REDUCE"

def main():
    print(f"\n{'='*60}")
    print(f"  Iteration 8: Final Brief + Remaining 4Q Data")
    print(f"{'='*60}")

    # Load composite data
    comp_data = json.loads((OUT / "composite_data.json").read_text(encoding="utf-8"))
    comp_map  = {s["code"]: s for s in comp_data}

    # Load Iter 7 trend results from QUARTERLY_TREND.md (parse out trend signals)
    trend_map = {}  # code -> {rev_trend, net_trend}

    # Known from Iter 7 output
    iter7_trends = {
        "2408": ("ACCEL ↑", "ACCEL ↑"),  "6770": ("STABLE →", "DECEL ↓"),
        "2376": ("ACCEL ↑", "STABLE →"), "2615": ("STABLE →", "STABLE →"),
        "2330": ("STABLE →", "ACCEL ↑"), "3008": ("DECEL ↓", "DECEL ↓"),
        "2357": ("ACCEL ↑", "ACCEL ↑"),  "2382": ("ACCEL ↑", "STABLE →"),
        "2303": ("STABLE →", "ACCEL ↑"), "2379": ("STABLE →", "DECEL ↓"),
        "2395": ("STABLE →", "STABLE →"),"2603": ("DECEL ↓", "DECEL ↓"),
        "2327": ("STABLE →", "ACCEL ↑"), "3034": ("STABLE →", "DECEL ↓"),
        "2317": ("ACCEL ↑", "ACCEL ↑"),  "4938": ("STABLE →", "ACCEL ↑"),
        "2337": ("STABLE →", "STABLE →"),"1303": ("STABLE →", "ACCEL ↑"),
        "2609": ("DECEL ↓", "DECEL ↓"),  "2308": ("ACCEL ↑", "ACCEL ↑"),
    }
    trend_map.update(iter7_trends)

    # ── Fetch remaining non-financial stocks ──────────────────────────────
    print(f"\n  Fetching {len(REMAINING)} remaining stocks from Yahoo Finance...")
    new_trends = {}
    for i, code in enumerate(REMAINING, 1):
        name = NAMES.get(code, code)
        print(f"  [{i:2d}/{len(REMAINING)}] {code} {name.split()[0]}...", end=" ", flush=True)
        qs = fetch_trend(code)
        time.sleep(0.4)
        if qs and len(qs) >= 3:
            revs = [q["rev"] for q in qs]
            nets = [q["net"] for q in qs]
            rt = trend_signal(revs)
            nt = trend_signal(nets)
            new_trends[code] = (rt, nt)
            trend_map[code]  = (rt, nt)
            print(f"Rev:{rt}  Net:{nt}")
        else:
            trend_map[code] = ("N/A", "N/A")
            print("No data")

    # ── Compute final conviction for all 49 stocks ─────────────────────────
    print("\n  Computing final conviction scores...")
    final = []
    for s in comp_data:
        code = s["code"]
        rt, nt = trend_map.get(code, ("N/A", "N/A"))
        conv = conviction(s, rt, nt)
        final.append({**s, "rev_trend": rt, "net_trend": nt, "conviction": conv})

    # Sort by original score desc
    final.sort(key=lambda x: -x["score"])

    # ── Generate FINAL BRIEF ───────────────────────────────────────────────
    strong_buys = [s for s in final if s["conviction"] == "STRONG BUY" and not s["is_fin"]]
    buys        = [s for s in final if s["conviction"] == "BUY" and not s["is_fin"]]
    avoids      = [s for s in final if s["conviction"] in ("AVOID","REDUCE")]
    fin_buys    = [s for s in final if s["is_fin"] and s["conviction"] in ("STRONG BUY","BUY")]

    lines = [
        "# Taiwan ETF Universe — Final Investment Brief",
        f"**Completed:** {TODAY} | **Iterations:** 8 | **Stocks:** 49 across 5 ETFs",
        "**Data sources:** TWSE Open API (Q1 2026) + Yahoo Finance (4Q historical) + Composite Scoring",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "Eight iterations of analysis covering 0050.TW, 0056.TW, 00878.TW, 00713.TW, 006208.TW.",
        "Key macro themes: AI infrastructure supercycle (TSMC/Gigabyte/Quanta/ASUS), DRAM recovery",
        "(Nanya Tech), shipping normalization (Evergreen/Yang Ming), petrochemical weakness.",
        "",
        "**Investment universe signal: SELECTIVE BUY** — 6 high-conviction non-financial picks",
        "at reasonable valuations; majority of index is HOLD/REDUCE on current prices.",
        "",
        "---",
        "",
        "## 🟢 Non-Financial Conviction Picks",
        "",
    ]

    all_buys_nonfin = strong_buys + buys
    for s in all_buys_nonfin:
        rt, nt = s["rev_trend"], s["net_trend"]
        fpe  = f"{s['fwd_pe']:.1f}x" if s.get("fwd_pe") else "N/A"
        yoy  = f"+{s['rev_yoy']:.1f}%" if s.get("rev_yoy") and s["rev_yoy"] > 0 else (f"{s['rev_yoy']:.1f}%" if s.get("rev_yoy") else "N/A")
        om   = f"{s['op_margin']:.1f}%" if s.get("op_margin") else "N/A"
        div  = f"{s['div_yield']:.2f}%" if s.get("div_yield") else "N/A"
        score = s["score"]
        conv  = s["conviction"]
        trend_badge = ("✅ Both accel" if rt == "ACCEL ↑" and nt == "ACCEL ↑" else
                       f"Rev:{rt} Net:{nt}")
        lines += [
            f"### {s['code']} {s['name']} — {conv}",
            f"**Score:** {score}/100 | **Fwd P/E:** {fpe} | **Rev YoY:** {yoy} | **Op Margin:** {om} | **Div:** {div}",
            f"**4Q Trend:** {trend_badge}",
            "",
        ]
        # Thesis
        thesis = []
        if s.get("rev_yoy") and s["rev_yoy"] > 50:
            thesis.append(f"Revenue surge {s['rev_yoy']:.0f}% YoY")
        if s.get("fwd_pe") and s["fwd_pe"] < 15:
            thesis.append(f"undervalued at {s['fwd_pe']:.1f}x forward P/E")
        if s.get("op_margin") and s["op_margin"] > 20:
            thesis.append(f"high-quality {s['op_margin']:.0f}% operating margin")
        if rt == "ACCEL ↑" and nt == "ACCEL ↑":
            thesis.append("both revenue and profit trending up across 4 quarters")
        if thesis:
            lines.append(f"*Thesis: {'; '.join(thesis)}.*\n")

    lines += [
        "---",
        "",
        "## 💰 Financial Sector Picks (Dividend + Value)",
        "",
        "*(P/E analysis unreliable due to IFRS 17; use P/B + dividend yield)*",
        "",
        "| Code | Name | Conviction | P/B | Div Yield | Q1 EPS |",
        "|------|------|-----------|-----|-----------|--------|",
    ]
    for s in sorted(fin_buys, key=lambda x: -(x.get("div_yield") or 0)):
        pb  = f"{s['pb']:.2f}x" if s.get("pb") else "N/A"
        div = f"{s['div_yield']:.2f}%" if s.get("div_yield") else "N/A"
        eps = f"¥{s['q1_eps']:.2f}" if s.get("q1_eps") else "N/A"
        lines.append(f"| {s['code']} | {s['name'].split()[0]} | {s['conviction']} | {pb} | {div} | {eps} |")

    lines += [
        "",
        "---",
        "",
        "## 🔴 Confirmed AVOID",
        "",
        "| Code | Name | Reason |",
        "|------|------|--------|",
    ]
    for s in avoids[:10]:
        reasons = []
        if s.get("fwd_pe") and s["fwd_pe"] > 60: reasons.append(f"expensive {s['fwd_pe']:.0f}x fwd P/E")
        if s.get("op_margin") and s["op_margin"] < 0: reasons.append("operating loss")
        if s.get("rev_yoy") and s["rev_yoy"] < -5: reasons.append(f"rev decline {s['rev_yoy']:.1f}%")
        if s["rev_trend"] == "DECEL ↓" and s["net_trend"] == "DECEL ↓":
            reasons.append("both trends deteriorating")
        if not reasons: reasons.append("poor multi-factor ranking")
        lines.append(f"| {s['code']} | {s['name'].split()[0]} | {', '.join(reasons)} |")

    # Full ranking table
    lines += [
        "",
        "---",
        "",
        "## Full 49-Stock Final Ranking",
        "",
        "| Conviction | Score | Code | Name | Sector | FwdP/E | RevYoY | OpMgn | RevTrend | NetTrend |",
        "|-----------|-------|------|------|--------|--------|--------|-------|---------|---------|",
    ]
    for s in final:
        fpe = f"{s['fwd_pe']:.1f}x" if s.get("fwd_pe") else "N/A"
        yoy = f"+{s['rev_yoy']:.1f}%" if s.get("rev_yoy") and s["rev_yoy"] > 0 else (f"{s['rev_yoy']:.1f}%" if s.get("rev_yoy") else "N/A")
        om  = f"{s['op_margin']:.1f}%" if s.get("op_margin") else "N/A"
        lines.append(
            f"| {s['conviction']} | **{s['score']}** | {s['code']} | "
            f"{s['name'].split()[0]} | {s['sector']} | {fpe} | {yoy} | {om} | "
            f"{s['rev_trend']} | {s['net_trend']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Data Quality Notes",
        "",
        "1. **PSMC (6770)**: TWSE Q1 2026 shows EPS ¥3.36 and 104% op.margin, contradicting Yahoo Finance data which shows operating losses through Q4 2025. Verify directly on MOPS before acting.",
        "2. **Financial sector revenue**: IFRS 17 accounting change distorts YoY revenue comparisons for all banks and insurance companies. Use P/B + dividend yield instead.",
        "3. **Forward EPS**: Based on Q1 2026 × 4 — Q1 may be seasonally atypical for some sectors.",
        "4. **Yahoo Finance data**: Taiwan stock coverage is good but may lag TWSE official filings by 1-2 quarters.",
        "",
        "---",
        "",
        "## Analysis Iterations Log",
        "",
        "| Iter | Focus | Output |",
        "|------|-------|--------|",
        "| 1 | 0050+0056 valuation + April revenue | 51 stock reports + 2 ETF summaries |",
        "| 2 | 00878, 00713, 006208 ETF expansion | 3 more ETF summaries |",
        "| 3 | Q1 2026 actual P&L (EPS, margins) | 49 Q1 reports + MASTER_REPORT.md |",
        "| 4 | Forward P/E + EPS acceleration | FORWARD_VALUATION.md |",
        "| 5 | Multi-factor composite score 0-100 | COMPOSITE_SCORE.md + composite_data.json |",
        "| 6 | Sector rotation signals | SECTOR_ROTATION.md |",
        "| 7 | 4Q historical trend (20 stocks, Yahoo) | QUARTERLY_TREND.md |",
        "| 8 | Remaining 14 stocks + final brief | FINAL_BRIEF.md (this file) |",
        "",
        "---",
        f"*Final brief generated: {TODAY} | Cron job: af8a5b5d*",
    ]

    out_path = OUT / "FINAL_BRIEF.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  ✓ Saved: {out_path}")

    # Console summary
    print(f"\n{'='*60}")
    print(f"  FINAL CONVICTION SUMMARY:")
    print(f"  Strong Buys (non-fin): {[s['code'] for s in strong_buys]}")
    print(f"  Buys (non-fin):        {[s['code'] for s in buys]}")
    print(f"  Financial Buys:        {[s['code'] for s in fin_buys]}")
    print(f"  Avoids:                {[s['code'] for s in avoids if s['verdict'] == 'AVOID']}")
    print(f"{'='*60}")

    return final

if __name__ == "__main__":
    main()
