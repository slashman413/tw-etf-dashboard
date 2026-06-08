#!/usr/bin/env python3
"""
Iteration 20: Conviction Buy List — Final Synthesis
No API calls — synthesizes all prior analysis:
  composite_data.json → fundamental score + verdict
  technical_data.json → 30d MA signal + % above/below
  risk_data.json      → risk score + RA score + PEG
  price_targets.json  → upside % + fair value
  margin_data.json    → 融資融券 margin flow signal

Scoring system for conviction rank:
  +30 pts: Composite score ≥ 60
  +20 pts: Price below 30d MA (mean-reversion opportunity)
  +20 pts: Price target upside ≥ 15%
  +15 pts: Risk score ≤ 20
  +10 pts: Margin flow BULLISH
  +5 pts:  PEG < 1.0 (undervalued vs growth)

Outputs: CONVICTION_LIST.md + conviction_data.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
technical = json.loads((REPORT_DIR / "technical_data.json").read_text(encoding="utf-8"))
risk_data = json.loads((REPORT_DIR / "risk_data.json").read_text(encoding="utf-8"))
ptargets  = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
margin    = json.loads((REPORT_DIR / "margin_data.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# Build lookup maps
tech_bounce  = {x["code"]: x for x in technical.get("bounce_candidates", [])}
tech_mom     = {x["code"]: x for x in technical.get("momentum_intact", [])}
triple_conf  = set(technical.get("triple_confirmed", []))
risk_map     = {s["code"]: s for s in risk_data["all_stocks"]}
target_map   = {t["code"]: t for t in ptargets["targets"]}
margin_map   = {k: v for k,v in margin.items() if isinstance(v, dict)}

results = []
for s in composite:
    code      = s["code"]
    score     = s.get("score")
    verdict   = s.get("verdict", "—")
    name      = s["name"]
    sector    = s.get("sector", "—")
    fwd_pe    = sf(s.get("fwd_pe"))
    div_yield = sf(s.get("div_yield"))
    price     = sf(s.get("price"))
    rev_yoy   = sf(s.get("rev_yoy"))
    op_margin = sf(s.get("op_margin"))

    if score is None: continue

    # Pull from each analysis stream
    rm    = risk_map.get(code, {})
    tm    = target_map.get(code, {})
    mg    = margin_map.get(code, {})
    bc    = tech_bounce.get(code)  # below 30d MA
    mom   = tech_mom.get(code)     # above 30d MA (momentum)

    risk     = rm.get("risk", 50)
    ra_score = rm.get("ra_score")
    peg      = rm.get("peg")
    upside   = tm.get("upside")
    target   = tm.get("target")
    method   = tm.get("method", "")
    margin_sig = mg.get("sig", "N/A")
    pct_vs_ma  = bc["pct_vs_ma"] if bc else (mom["pct_vs_ma"] if mom else None)
    is_triple  = code in triple_conf

    # ── Conviction scoring ─────────────────────────────────────────────────
    conv = 0
    reasons = []

    # Fundamental quality
    if score >= 70:
        conv += 30; reasons.append(f"強基本面({score}分)")
    elif score >= 60:
        conv += 30; reasons.append(f"良好基本面({score}分)")
    elif score >= 50:
        conv += 18; reasons.append(f"中上基本面({score}分)")
    elif score >= 45:
        conv += 8; reasons.append(f"一般基本面({score}分)")

    # Mean-reversion opportunity (below 30d MA)
    if bc:
        pct = bc["pct_vs_ma"]
        if pct <= -5:
            conv += 20; reasons.append(f"深度低於30日線({pct:.1f}%)")
        elif pct <= -2:
            conv += 15; reasons.append(f"低於30日線({pct:.1f}%)")
        else:
            conv += 8; reasons.append(f"略低於30日線({pct:.1f}%)")

    # Price target upside
    if upside is not None:
        if upside >= 30:
            conv += 20; reasons.append(f"目標價上漲空間{upside:.0f}%")
        elif upside >= 15:
            conv += 20; reasons.append(f"目標價上漲空間{upside:.0f}%")
        elif upside >= 5:
            conv += 10; reasons.append(f"目標價小幅上漲{upside:.0f}%")
        elif upside < -10:
            conv -= 10; reasons.append(f"目標價下行{upside:.0f}%")

    # Risk discount
    if risk <= 10:
        conv += 15; reasons.append("極低風險")
    elif risk <= 20:
        conv += 15; reasons.append("低風險")
    elif risk <= 30:
        conv += 8; reasons.append("中等風險")
    elif risk >= 50:
        conv -= 10; reasons.append(f"高風險({risk}分)")

    # Margin flow
    if margin_sig == "BULLISH":
        conv += 10; reasons.append("融資多頭信號")
    elif margin_sig == "BEARISH":
        conv -= 5; reasons.append("融資空頭信號")

    # PEG undervalued
    if peg and peg < 0.5:
        conv += 5; reasons.append(f"PEG深度低估({peg:.2f})")
    elif peg and peg < 1.0:
        conv += 5; reasons.append(f"PEG低估({peg:.2f})")

    # Triple confirmed bonus
    if is_triple:
        conv += 5; reasons.append("三重確認✅")

    # PSMC penalty
    if code == "6770":
        conv -= 20; reasons.append("⚠ 一次性業外收入，數據不可靠")

    # Verdict adjustment
    if verdict == "REDUCE":  conv -= 5
    if verdict == "AVOID":   conv -= 10

    # Final classification
    if conv >= 65:
        action = "STRONG BUY"
    elif conv >= 45:
        action = "BUY"
    elif conv >= 25:
        action = "WATCH"
    elif conv >= 10:
        action = "HOLD"
    else:
        action = "AVOID"

    results.append({
        "code":      code,
        "name":      name,
        "sector":    sector,
        "score":     score,
        "verdict":   verdict,
        "conv":      conv,
        "action":    action,
        "risk":      risk,
        "ra_score":  ra_score,
        "peg":       peg,
        "upside":    upside,
        "target":    target,
        "margin_sig":margin_sig,
        "pct_vs_ma": pct_vs_ma,
        "is_triple": is_triple,
        "reasons":   reasons,
        "fwd_pe":    fwd_pe,
        "div_yield": div_yield,
        "price":     price,
        "rev_yoy":   rev_yoy,
        "op_margin": op_margin,
    })

results.sort(key=lambda x: -x["conv"])

# ── Buckets ────────────────────────────────────────────────────────────────────
strong_buys = [r for r in results if r["action"] == "STRONG BUY"]
buys        = [r for r in results if r["action"] == "BUY"]
watches     = [r for r in results if r["action"] == "WATCH"]
holds       = [r for r in results if r["action"] == "HOLD"]
avoids      = [r for r in results if r["action"] == "AVOID"]

# ── Generate CONVICTION_LIST.md ────────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# Conviction Buy List — Final Synthesis — {TODAY}",
    "*All 19 analysis streams combined: fundamental + technical + risk + price target + margin flow*",
    "",
    "## Conviction Scoring",
    "",
    "| Component | Max Points | Condition |",
    "|-----------|-----------|-----------|",
    "| Fundamental (composite score) | +30 | Score ≥ 60 |",
    "| Mean-reversion signal | +20 | Below 30d MA |",
    "| Price target upside | +20 | Upside ≥ 15% |",
    "| Risk quality | +15 | Risk score ≤ 20 |",
    "| Margin flow | +10 | Bullish 融資信號 |",
    "| PEG value | +5 | PEG < 1.0 |",
    "| Triple-confirmed bonus | +5 | All 3 signals |",
    "",
    f"**STRONG BUY** ≥ 65 | **BUY** 45–64 | **WATCH** 25–44 | **HOLD** 10–24 | **AVOID** < 10",
    "",
    "---",
    "",
]

if strong_buys:
    lines += [
        f"## 🔥 STRONG BUY — Highest Conviction ({len(strong_buys)} stocks)",
        "",
        "| Conv | Code | Name | Sector | Score | Risk | Upside | PEG | vs MA | Margin | Key Reasons |",
        "|------|------|------|--------|-------|------|--------|-----|-------|--------|-------------|",
    ]
    for r in strong_buys:
        reasons_short = " · ".join(r["reasons"][:3])
        lines.append(
            f"| **{r['conv']}** | **{r['code']}** | {r['name'].split()[0]} | {r['sector']} | "
            f"{r['score']} | {r['risk']} | {fmt(r['upside'],1,'+','%') if r['upside'] else '—'} | "
            f"{fmt(r['peg'],2) if r['peg'] else '—'} | "
            f"{fmt(r['pct_vs_ma'],1,'+' if (r['pct_vs_ma'] or 0)>0 else '','')}% | "
            f"{r['margin_sig']} | {reasons_short} |"
        )
    lines.append("")

if buys:
    lines += [
        f"## ✅ BUY — Good Conviction ({len(buys)} stocks)",
        "",
        "| Conv | Code | Name | Score | Risk | Upside | vs MA | Margin |",
        "|------|------|------|-------|------|--------|-------|--------|",
    ]
    for r in buys:
        lines.append(
            f"| **{r['conv']}** | **{r['code']}** | {r['name'].split()[0]} | "
            f"{r['score']} | {r['risk']} | {fmt(r['upside'],1,'+','%') if r['upside'] else '—'} | "
            f"{fmt(r['pct_vs_ma'],1,'+' if (r['pct_vs_ma'] or 0)>0 else '','')}{'%' if r['pct_vs_ma'] else '—'} | "
            f"{r['margin_sig']} |"
        )
    lines.append("")

if watches:
    codes = ", ".join(r["code"] for r in watches[:12])
    lines += [
        f"## 👀 WATCH — Monitor ({len(watches)} stocks)",
        f"*{codes}*",
        "",
    ]

if holds:
    codes = ", ".join(r["code"] for r in holds)
    lines += [
        f"## ⏸ HOLD ({len(holds)} stocks)",
        f"*{codes}*",
        "",
    ]

if avoids:
    lines += [
        f"## ❌ AVOID — Low conviction ({len(avoids)} stocks)",
        "",
        "| Conv | Code | Name | Score | Key Risk |",
        "|------|------|------|-------|---------|",
    ]
    for r in avoids:
        reasons_short = " · ".join(r["reasons"][:2]) if r["reasons"] else "Low score + no catalysts"
        lines.append(
            f"| {r['conv']} | {r['code']} | {r['name'].split()[0]} | "
            f"{r['score']} | {reasons_short} |"
        )
    lines.append("")

# Detailed breakdown for top 10
lines += [
    "---",
    "",
    "## Detailed Breakdown — Top 10 Conviction Picks",
    "",
]

for r in results[:10]:
    lines += [
        f"### {r['code']} {r['name']} — Conviction {r['conv']}/100 ({r['action']})",
        f"*Sector: {r['sector']} | Score: {r['score']} | RA Score: {r['ra_score']} | Risk: {r['risk']}*",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| 現價 | ¥{fmt(r['price'],0)} |",
        f"| 目標價 | ¥{fmt(r['target'],0)} (上漲 {fmt(r['upside'],1,'','%')}) |",
        f"| 遠期本益比 | {fmt(r['fwd_pe'],1,'','x')} |",
        f"| 股息殖利率 | {fmt(r['div_yield'],2,'','%')} |",
        f"| PEG | {fmt(r['peg'],2)} |",
        f"| 30日均線偏差 | {fmt(r['pct_vs_ma'],1,'','%')} |",
        f"| 融資信號 | {r['margin_sig']} |",
        f"| 三重確認 | {'是 ✅' if r['is_triple'] else '否'} |",
        "",
        f"**佐證因素:** {' | '.join(r['reasons'])}",
        "",
    ]

lines += [
    "---",
    "",
    "## Summary Matrix",
    "",
    f"| Action | Count | Avg Conv | Avg Score | Avg Risk |",
    f"|--------|-------|---------|-----------|---------|",
]
for bucket, label in [(strong_buys,"STRONG BUY"),(buys,"BUY"),(watches,"WATCH"),(holds,"HOLD"),(avoids,"AVOID")]:
    if not bucket: continue
    avg_conv  = sum(r["conv"]  for r in bucket) / len(bucket)
    avg_score = sum(r["score"] for r in bucket) / len(bucket)
    avg_risk  = sum(r["risk"]  for r in bucket) / len(bucket)
    lines.append(f"| **{label}** | {len(bucket)} | {avg_conv:.0f} | {avg_score:.0f} | {avg_risk:.0f} |")

lines += [
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 20 | All 19 data streams synthesized*",
]

(REPORT_DIR / "CONVICTION_LIST.md").write_text("\n".join(lines), encoding="utf-8")

# ── JSON ──────────────────────────────────────────────────────────────────────
conv_data = {
    "date": TODAY,
    "strong_buys": [{"code":r["code"],"name":r["name"].split()[0],"conv":r["conv"],
                     "score":r["score"],"risk":r["risk"],"upside":r["upside"],
                     "peg":r["peg"],"sector":r["sector"],"reasons":r["reasons"]}
                    for r in strong_buys],
    "buys":        [{"code":r["code"],"name":r["name"].split()[0],"conv":r["conv"],
                     "score":r["score"],"risk":r["risk"],"upside":r["upside"],
                     "sector":r["sector"]}
                    for r in buys],
    "all_ranked":  [{"code":r["code"],"name":r["name"].split()[0],"conv":r["conv"],
                     "action":r["action"],"score":r["score"],"risk":r["risk"],
                     "upside":r["upside"],"pct_vs_ma":r["pct_vs_ma"],
                     "margin_sig":r["margin_sig"],"is_triple":r["is_triple"],
                     "peg":r["peg"],"sector":r["sector"]}
                    for r in results],
}
(REPORT_DIR / "conviction_data.json").write_text(
    json.dumps(conv_data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ CONVICTION_LIST.md + conviction_data.json")
print(f"\n  STRONG BUY ({len(strong_buys)}): {[r['code'] for r in strong_buys]}")
print(f"  BUY        ({len(buys)}):  {[r['code'] for r in buys]}")
print(f"  WATCH      ({len(watches)}): {[r['code'] for r in watches[:8]]}")
print(f"  AVOID      ({len(avoids)}):  {[r['code'] for r in avoids]}")
print(f"\n  Top 5 conviction:")
for r in results[:5]:
    print(f"    {r['code']} {r['name'].split()[0]:12s}  conv={r['conv']:3d}  "
          f"score={r['score']:2d}  risk={r['risk']:2d}  "
          f"upside={fmt(r['upside'],1,'+','%'):8s}  {r['action']}")
