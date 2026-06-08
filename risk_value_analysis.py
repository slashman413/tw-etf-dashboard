#!/usr/bin/env python3
"""
Iteration 16: PEG Ratio + Risk Scoring Overlay
No API calls — uses composite_data.json + daily_scores.json + margin_data.json
Adds:
  - PEG ratio (Fwd P/E ÷ EPS growth %) — <1 = undervalued vs growth
  - Risk score (0–100, lower = safer): valuation, quality, leverage, momentum risks
  - Risk-adjusted conviction: combine composite score with risk score
Generates: RISK_VALUE_ANALYSIS.md + risk_data.json
"""

import json, math
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
margin    = json.loads((REPORT_DIR / "margin_data.json").read_text(encoding="utf-8"))
tech      = json.loads((REPORT_DIR / "technical_data.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# ── Build enriched universe ───────────────────────────────────────────────────
stocks = []
for s in composite:
    code      = s["code"]
    m         = margin.get(code, {})
    fwd_pe    = sf(s.get("fwd_pe"))
    eps_accel = sf(s.get("eps_accel"))   # % EPS acceleration Q1×4 vs TTM
    rev_yoy   = sf(s.get("rev_yoy"))
    op_margin = sf(s.get("op_margin"))
    pb        = sf(s.get("pb"))
    div       = sf(s.get("div_yield"))
    price     = sf(s.get("price"))
    score     = s.get("score")
    is_fin    = s.get("is_fin", False)

    # ── PEG ratio ──────────────────────────────────────────────────────────
    # Use EPS acceleration as growth rate proxy; cap growth at 200% to avoid distortion
    peg = None
    growth_rate = None
    if fwd_pe and eps_accel and eps_accel > 0:
        growth_rate = min(abs(eps_accel), 200.0)
        peg = fwd_pe / growth_rate
    elif fwd_pe and rev_yoy and rev_yoy > 0 and not is_fin:
        # Fallback: use revenue YoY as growth proxy (less reliable)
        growth_rate = min(abs(rev_yoy), 200.0)
        peg = fwd_pe / growth_rate
        peg = peg * 1.5   # penalize: revenue growth ≠ EPS growth

    # ── Risk scoring (0 = no risk, 100 = max risk) ─────────────────────────
    risk = 0

    # Valuation risk (0–35 pts)
    if fwd_pe:
        if fwd_pe > 80:   risk += 35
        elif fwd_pe > 50: risk += 25
        elif fwd_pe > 30: risk += 15
        elif fwd_pe > 20: risk += 8
        elif fwd_pe > 15: risk += 3
    elif not is_fin:      risk += 10   # unknown P/E = uncertain

    # Quality risk (0–25 pts)
    if op_margin is not None and not is_fin:
        if op_margin < 0:    risk += 25  # operating loss
        elif op_margin < 3:  risk += 18
        elif op_margin < 7:  risk += 10
        elif op_margin < 12: risk += 5

    # Revenue trend risk (0–20 pts)
    if rev_yoy is not None:
        if rev_yoy < -10:  risk += 20
        elif rev_yoy < -5: risk += 12
        elif rev_yoy < 0:  risk += 6
        elif rev_yoy < 3:  risk += 3

    # Leverage/valuation risk via P/B (0–15 pts)
    if pb:
        if pb > 15:  risk += 15
        elif pb > 8: risk += 8
        elif pb > 5: risk += 4

    # Margin flow risk (0–5 pts)
    sig = m.get("sig","")
    if sig == "BEARISH":   risk += 5
    elif sig == "MIXED":   risk += 2

    # PSMC anomaly flag
    if code == "6770": risk += 20  # non-recurring one-time OP

    risk = min(risk, 100)

    # ── Risk-adjusted score ────────────────────────────────────────────────
    # Penalize composite score by risk: ra_score = score × (1 - risk/200)
    ra_score = round(score * (1 - risk / 200)) if score else None

    stocks.append({
        "code":       code,
        "name":       s["name"],
        "sector":     s.get("sector","—"),
        "score":      score,
        "verdict":    s.get("verdict","—"),
        "fwd_pe":     fwd_pe,
        "pb":         pb,
        "div":        div,
        "rev_yoy":    rev_yoy,
        "op_margin":  op_margin,
        "eps_accel":  eps_accel,
        "peg":        peg,
        "growth_rate": growth_rate,
        "risk":       risk,
        "ra_score":   ra_score,
        "margin_sig": m.get("sig","N/A"),
        "is_fin":     is_fin,
    })

# Sort by risk-adjusted score
stocks.sort(key=lambda x: -(x["ra_score"] or 0))

# ── Classify PEG ──────────────────────────────────────────────────────────────
def peg_label(peg):
    if peg is None:   return "N/A"
    if peg < 0.5:     return "Deep Value"
    if peg < 1.0:     return "Undervalued"
    if peg < 1.5:     return "Fair Value"
    if peg < 2.5:     return "Slightly Rich"
    return            "Overvalued"

def risk_label(r):
    if r <= 15:  return "LOW ✅"
    if r <= 30:  return "MODERATE ⚠"
    if r <= 50:  return "ELEVATED ⚠⚠"
    return              "HIGH 🔴"

# ── Best PEG stocks ───────────────────────────────────────────────────────────
peg_stocks = sorted([s for s in stocks if s["peg"] and s["peg"] < 2.0 and s["score"] and s["score"] >= 40],
                    key=lambda x: x["peg"])

low_risk    = sorted([s for s in stocks if s["risk"] <= 20 and s["score"] and s["score"] >= 45],
                     key=lambda x: -(x["ra_score"] or 0))

high_risk   = sorted([s for s in stocks if s["risk"] >= 40],
                     key=lambda x: -(x["risk"]))

# ── Generate RISK_VALUE_ANALYSIS.md ──────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# Risk & PEG Value Analysis — {TODAY}",
    "*PEG = Forward P/E ÷ EPS growth rate. <1.0 = undervalued vs growth.*",
    "*Risk score 0–100: valuation + quality + revenue + leverage + margin flow.*",
    "",
    "---",
    "",
    "## 🏆 Risk-Adjusted Rankings (Top 20)",
    "*RA Score = Composite Score × (1 − Risk/200)*",
    "",
    "| RA Score | Score | Risk | Code | Name | Sector | PEG | Verdict |",
    "|----------|-------|------|------|------|--------|-----|---------|",
]

for s in stocks[:20]:
    peg_str = f"{s['peg']:.2f}" if s["peg"] else "—"
    lines.append(
        f"| **{s['ra_score']}** | {s['score']} | {risk_label(s['risk'])} | "
        f"**{s['code']}** | {s['name'].split()[0]} | {s['sector']} | "
        f"{peg_str} | {s['verdict']} |"
    )

lines += [
    "",
    "---",
    "",
    "## 💎 PEG < 1.0 — Undervalued Relative to Growth",
    "*Strong growth at cheap multiple — classic value-growth sweet spot.*",
    "",
    "| Code | Name | PEG | Fwd P/E | EPS Growth | Rev YoY | Score | PEG Label |",
    "|------|------|-----|---------|-----------|---------|-------|-----------|",
]

for s in peg_stocks:
    g = s["growth_rate"]
    lines.append(
        f"| **{s['code']}** | {s['name'].split()[0]} | **{s['peg']:.3f}** | "
        f"{fmt(s['fwd_pe'],1,'','x')} | {fmt(g,0,'+','%')} | "
        f"{fmt(s['rev_yoy'],1,'+' if (s['rev_yoy'] or 0)>0 else '','')}% | "
        f"{s['score']} | **{peg_label(s['peg'])}** |"
    )

if not peg_stocks:
    lines.append("*No stocks with PEG < 2.0 and score ≥ 40 today.*")

lines += [
    "",
    "---",
    "",
    "## ✅ Low-Risk Picks (Risk ≤ 20, Score ≥ 45)",
    "",
    "| Code | Name | Score | RA Score | Risk | Fwd P/E | Op Margin | Div% |",
    "|------|------|-------|----------|------|---------|----------|------|",
]

for s in low_risk[:12]:
    lines.append(
        f"| **{s['code']}** | {s['name'].split()[0]} | {s['score']} | **{s['ra_score']}** | "
        f"{risk_label(s['risk'])} | {fmt(s['fwd_pe'],1,'','x')} | "
        f"{fmt(s['op_margin'],1,'','%')} | {fmt(s['div'],2,'','%')} |"
    )

lines += [
    "",
    "---",
    "",
    "## 🔴 High-Risk Flags (Risk ≥ 40)",
    "",
    "| Code | Name | Risk | Score | Key Risk Factor | Fwd P/E | Op Margin |",
    "|------|------|------|-------|----------------|---------|----------|",
]

for s in high_risk[:10]:
    # Explain primary risk
    reasons = []
    if s["fwd_pe"] and s["fwd_pe"] > 50:      reasons.append(f"P/E {s['fwd_pe']:.0f}x")
    if s["op_margin"] is not None and s["op_margin"] < 0: reasons.append("Op Loss")
    if s["rev_yoy"] and s["rev_yoy"] < -5:    reasons.append(f"Rev {s['rev_yoy']:.0f}%")
    if s["pb"] and s["pb"] > 10:              reasons.append(f"P/B {s['pb']:.1f}x")
    if s["code"] == "6770":                   reasons.append("Non-recurring OP")
    reason_str = " | ".join(reasons[:2]) if reasons else "Multiple"
    lines.append(
        f"| **{s['code']}** | {s['name'].split()[0]} | **{s['risk']}** | {s['score']} | "
        f"{reason_str} | {fmt(s['fwd_pe'],1,'','x')} | {fmt(s['op_margin'],1,'','%')} |"
    )

lines += [
    "",
    "---",
    "",
    "## Full Risk + PEG Table",
    "",
    "| Code | Name | Score | RA Score | Risk | PEG | Fwd P/E | Op Mgn | Rev YoY |",
    "|------|------|-------|----------|------|-----|---------|--------|---------|",
]

for s in sorted(stocks, key=lambda x: -(x["score"] or 0)):
    peg_str = f"{s['peg']:.2f}" if s["peg"] else "—"
    yoy_pre = "+" if (s["rev_yoy"] or 0) > 0 else ""
    lines.append(
        f"| {s['code']} | {s['name'].split()[0]} | {s['score']} | {s['ra_score'] or '—'} | "
        f"{s['risk']} | {peg_str} | {fmt(s['fwd_pe'],1,'','x')} | "
        f"{fmt(s['op_margin'],1,'','%')} | {fmt(s['rev_yoy'],1,yoy_pre,'%')} |"
    )

lines += [
    "",
    "---",
    "",
    "## Methodology Notes",
    "",
    "**PEG Calculation:**",
    "- Primary: Fwd P/E ÷ EPS acceleration (Q1×4 vs TTM EPS, capped at 200%)",
    "- Fallback: Fwd P/E ÷ Revenue YoY × 1.5 penalty (revenue ≠ earnings growth)",
    "- PEG not computed when EPS growth ≤ 0 or P/E unavailable",
    "",
    "**Risk Score Components (0–100):**",
    "- Valuation risk: 0–35 pts (Fwd P/E bands)",
    "- Quality risk: 0–25 pts (operating margin)",
    "- Revenue trend: 0–20 pts (YoY growth)",
    "- Leverage (P/B): 0–15 pts",
    "- Margin flow: 0–5 pts (BEARISH = +5)",
    "- PSMC anomaly: +20 pts (non-recurring operating profit)",
    "",
    "**Risk-Adjusted Score:** `RA = Composite × (1 − Risk/200)`",
    "- A stock with score 80 and risk 40 → RA = 80 × 0.80 = 64",
    "- Penalizes high-risk stocks without fully discarding them",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 16*",
]

out_md = REPORT_DIR / "RISK_VALUE_ANALYSIS.md"
out_md.write_text("\n".join(lines), encoding="utf-8")

# ── Save risk_data.json ───────────────────────────────────────────────────────
risk_data = {
    "date": TODAY,
    "top_ra": [{"code":s["code"],"name":s["name"].split()[0],"score":s["score"],
                "ra_score":s["ra_score"],"risk":s["risk"],"peg":s["peg"],
                "verdict":s["verdict"],"sector":s["sector"],
                "fwd_pe":s["fwd_pe"],"div":s["div"],"rev_yoy":s["rev_yoy"]}
               for s in stocks[:20]],
    "peg_undervalued": [{"code":s["code"],"name":s["name"].split()[0],"peg":s["peg"],
                          "fwd_pe":s["fwd_pe"],"growth_rate":s["growth_rate"],
                          "score":s["score"],"label":peg_label(s["peg"])}
                         for s in peg_stocks],
    "low_risk":  [{"code":s["code"],"name":s["name"].split()[0],"score":s["score"],
                   "ra_score":s["ra_score"],"risk":s["risk"]}
                  for s in low_risk[:10]],
    "high_risk": [{"code":s["code"],"name":s["name"].split()[0],"score":s["score"],
                   "risk":s["risk"]}
                  for s in high_risk[:10]],
    "all_stocks": [{"code":s["code"],"name":s["name"].split()[0],"score":s["score"],
                    "ra_score":s["ra_score"],"risk":s["risk"],"peg":s["peg"],
                    "fwd_pe":s["fwd_pe"],"op_margin":s["op_margin"],
                    "rev_yoy":s["rev_yoy"],"verdict":s["verdict"],"sector":s["sector"]}
                   for s in stocks],
}
(REPORT_DIR / "risk_data.json").write_text(
    json.dumps(risk_data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ RISK_VALUE_ANALYSIS.md")
print(f"✓ risk_data.json")
print(f"\nTop 10 Risk-Adjusted:")
for s in stocks[:10]:
    peg_str = f"{s['peg']:.2f}" if s['peg'] else "—"
    print(f"  {s['code']} {s['name'].split()[0]:12s}  score={s['score']:3d}  risk={s['risk']:3d}  "
          f"ra={s['ra_score']:3d}  peg={peg_str:6s}  {s['verdict']}")
print(f"\nPEG undervalued (<1.0, score≥40): {[s['code'] for s in peg_stocks if s['peg']<1.0]}")
print(f"Low risk + good score:            {[s['code'] for s in low_risk[:6]]}")
print(f"High risk flags:                  {[s['code'] for s in high_risk[:6]]}")
