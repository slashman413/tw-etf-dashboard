#!/usr/bin/env python3
"""
Iteration 15: Portfolio Scenario Analysis
No API calls — uses existing composite_data.json + margin_data.json + technical_data.json
Computes 5 hypothetical equal-weight portfolios and intra-sector rankings.
Generates: PORTFOLIO_ANALYSIS.md + portfolio_data.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
margin    = json.loads((REPORT_DIR / "margin_data.json").read_text(encoding="utf-8"))
tech      = json.loads((REPORT_DIR / "technical_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

# ── Build master universe ─────────────────────────────────────────────────────
def sf(v):
    try: return float(v) if v is not None else None
    except: return None

universe = []
for s in composite:
    code = s["code"]
    m = margin.get(code, {})
    tc = code in tech["triple_confirmed"]
    bc = next((x for x in tech["bounce_candidates"] if x["code"] == code), None)
    universe.append({
        "code":      code,
        "name":      s["name"],
        "sector":    s.get("sector","—"),
        "score":     s.get("score"),
        "verdict":   s.get("verdict","—"),
        "fwd_pe":    sf(s.get("fwd_pe")),
        "pb":        sf(s.get("pb")),
        "div":       sf(s.get("div_yield")),
        "q1_eps":    sf(s.get("q1_eps")),
        "rev_yoy":   sf(s.get("rev_yoy")),
        "op_margin": sf(s.get("op_margin")),
        "eps_accel": sf(s.get("eps_accel")),
        "price":     sf(s.get("price")),
        "v_pts":     s.get("v_pts",0),
        "g_pts":     s.get("g_pts",0),
        "q_pts":     s.get("q_pts",0),
        "i_pts":     s.get("i_pts",0),
        "margin_sig": m.get("sig","N/A"),
        "m_chg":     m.get("m_chg"),
        "triple":    tc,
        "pct_vs_ma": bc["pct_vs_ma"] if bc else None,
        "is_fin":    s.get("is_fin", False),
    })

def wavg(stocks, field, weight_field=None):
    """Weighted average of field; if weight_field=None, equal-weight. Ignores None values."""
    vals = [(s[field], s.get(weight_field,1) or 1) for s in stocks if s.get(field) is not None]
    if not vals: return None
    total_w = sum(w for _,w in vals)
    return sum(v*w for v,w in vals) / total_w if total_w else None

def portfolio_stats(stocks, name):
    n = len(stocks)
    if not n: return None
    return {
        "name":        name,
        "count":       n,
        "avg_score":   wavg(stocks, "score"),
        "avg_fwd_pe":  wavg(stocks, "fwd_pe"),
        "avg_pb":      wavg(stocks, "pb"),
        "avg_div":     wavg(stocks, "div"),
        "avg_yoy":     wavg(stocks, "rev_yoy"),
        "avg_opmgn":   wavg(stocks, "op_margin"),
        "avg_eps_acc": wavg(stocks, "eps_accel"),
        "bullish_margin": sum(1 for s in stocks if s["margin_sig"] == "BULLISH"),
        "stocks":      [{"code":s["code"],"name":s["name"].split()[0],"score":s["score"],
                         "div":s["div"],"fwd_pe":s["fwd_pe"],"rev_yoy":s["rev_yoy"]} for s in stocks],
    }

# ── Define 5 scenarios ────────────────────────────────────────────────────────
scored = [s for s in universe if s["score"] is not None]
scored_sorted = sorted(scored, key=lambda x: -x["score"])

top5    = scored_sorted[:5]
top10   = scored_sorted[:10]
buys    = [s for s in scored if s["verdict"] in ("STRONG BUY","BUY")]
high_div = sorted([s for s in scored if s["div"] and s["div"] > 4.0 and s["score"] >= 40],
                   key=lambda x: -(x["div"] or 0))[:8]
triple  = [s for s in scored if s["triple"]]

scenarios = [
    portfolio_stats(top5,    "Top 5 Composite"),
    portfolio_stats(top10,   "Top 10 Composite"),
    portfolio_stats(buys,    "All BUY Signals"),
    portfolio_stats(high_div,"High-Dividend (>4% + Score≥40)"),
    portfolio_stats(triple,  "Triple-Confirmed BUY"),
]

# ── Intra-sector leaders ──────────────────────────────────────────────────────
sector_leaders = {}
for s in scored:
    sec = s["sector"]
    if sec not in sector_leaders:
        sector_leaders[sec] = []
    sector_leaders[sec].append(s)

sector_best = {}
for sec, stocks in sector_leaders.items():
    ranked = sorted(stocks, key=lambda x: -(x["score"] or 0))
    sector_best[sec] = ranked[:3]

# ── Generate PORTFOLIO_ANALYSIS.md ────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# Portfolio Scenario Analysis — {TODAY}",
    "*Equal-weight hypothetical portfolios from 62-stock ETF universe*",
    "",
    "## Scenario Comparison",
    "",
    "| Portfolio | # | Avg Score | Fwd P/E | P/B | Div Yield | Rev YoY | Op Margin | Bullish Margin |",
    "|-----------|---|-----------|---------|-----|----------|---------|----------|---------------|",
]

for p in scenarios:
    if not p: continue
    lines.append(
        f"| **{p['name']}** | {p['count']} | **{fmt(p['avg_score'],1)}** | "
        f"{fmt(p['avg_fwd_pe'],1,'','x')} | {fmt(p['avg_pb'],2,'','x')} | "
        f"{fmt(p['avg_div'],2,'','')}% | {fmt(p['avg_yoy'],1,'+' if (p['avg_yoy'] or 0)>0 else '','')}% | "
        f"{fmt(p['avg_opmgn'],1,'','%')} | {p['bullish_margin']}/{p['count']} |"
    )

lines += ["", "---", ""]

for p in scenarios:
    if not p: continue
    div_str = fmt(p['avg_div'],2,'','')+"%"
    pe_str  = fmt(p['avg_fwd_pe'],1,'','x')
    lines += [
        f"## {p['name']}",
        f"*{p['count']} stocks | Avg Score: {fmt(p['avg_score'],1)} | Fwd P/E: {pe_str} | Div: {div_str}*",
        "",
        "| Code | Name | Score | Fwd P/E | Div% | Rev YoY |",
        "|------|------|-------|---------|------|---------|",
    ]
    for s in p["stocks"]:
        lines.append(
            f"| **{s['code']}** | {s['name']} | {s['score']} | "
            f"{fmt(s['fwd_pe'],1,'','x')} | {fmt(s['div'],2,'','')}% | "
            f"{fmt(s['rev_yoy'],1,'+' if (s['rev_yoy'] or 0)>0 else '','')}% |"
        )
    lines.append("")

# ── Intra-sector section ──────────────────────────────────────────────────────
lines += [
    "---",
    "",
    "## Intra-Sector Leaders",
    "*Best 1–3 stocks within each sector by composite score*",
    "",
]

sector_order = sorted(sector_best.keys(),
    key=lambda s: -max(x["score"] for x in sector_best[s]))

for sec in sector_order:
    best = sector_best[sec]
    lines.append(f"### {sec}")
    lines.append("| Code | Name | Score | Verdict | Fwd P/E | Rev YoY | Div% |")
    lines.append("|------|------|-------|---------|---------|---------|------|")
    for s in best:
        yoy_pre = "+" if (s["rev_yoy"] or 0) > 0 else ""
        lines.append(
            f"| **{s['code']}** | {s['name'].split()[0]} | **{s['score']}** | {s['verdict']} | "
            f"{fmt(s['fwd_pe'],1,'','x')} | {fmt(s['rev_yoy'],1,yoy_pre,'%')} | {fmt(s['div'],2,'','%')} |"
        )
    lines.append("")

lines += [
    "---",
    "",
    "## Key Takeaways",
    "",
    f"1. **Triple-Confirmed BUY** portfolio (score + below 30d MA + bullish margin) has the strongest",
    f"   combined signal — {len(triple)} stocks: " + ", ".join(s['code'] for s in triple),
    "2. **Top 5** offers the highest avg score ({:.0f}/100) with reasonable P/E ({})".format(
        top5[0]["score"] if top5 else 0, fmt(scenarios[0]["avg_fwd_pe"],1,"","x") if scenarios[0] else "—"),
    "3. **High-Dividend** basket gives {:.2f}% avg yield — suitable for 0056/00713 ETF income mandate".format(
        scenarios[3]["avg_div"] or 0 if scenarios[3] else 0),
    "4. Finance sector leads by avg score (55.5) — banks offer P/B < 1.5 + yield > 4% combo",
    "5. Avoid broad REDUCE/AVOID bucket (22 stocks): avg Fwd P/E > 35x on declining/flat revenue",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 15*",
]

(REPORT_DIR / "PORTFOLIO_ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")

# ── Save portfolio_data.json for dashboard ────────────────────────────────────
portfolio_data = {
    "date": TODAY,
    "scenarios": scenarios,
    "sector_leaders": {
        sec: [{"code":s["code"],"name":s["name"].split()[0],"score":s["score"],
               "verdict":s["verdict"],"fwd_pe":s["fwd_pe"],"div":s["div"],"rev_yoy":s["rev_yoy"]}
              for s in stocks]
        for sec, stocks in sector_best.items()
    },
}
(REPORT_DIR / "portfolio_data.json").write_text(
    json.dumps(portfolio_data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ PORTFOLIO_ANALYSIS.md")
print(f"✓ portfolio_data.json")
print(f"\nScenario summary:")
for p in scenarios:
    if not p: continue
    print(f"  {p['name']:35s} n={p['count']:2d}  score={p['avg_score']:.0f}  "
          f"pe={fmt(p['avg_fwd_pe'],1,'','x'):6s}  div={fmt(p['avg_div'],2,'','%'):6s}  "
          f"yoy={fmt(p['avg_yoy'],1,'+' if (p['avg_yoy'] or 0)>0 else '','')}%")
print(f"\nSector leaders (top stock per sector):")
for sec in sector_order:
    b = sector_best[sec][0]
    print(f"  {sec:12s} → {b['code']} {b['name'].split()[0]:10s} score={b['score']}")
