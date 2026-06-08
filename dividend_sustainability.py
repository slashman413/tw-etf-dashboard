#!/usr/bin/env python3
"""
Iteration 19: Dividend Sustainability Analysis
No API calls — uses composite_data.json + expansion_stocks.json
Computes:
  - Annual dividend per share (price × div_yield/100)
  - Payout ratio = DPS / annualized EPS (q1_eps × 4)
  - Coverage ratio = EPS / DPS (>1.5 safe, 1.0–1.5 tight, <1.0 unsustainable)
  - Q1 EPS run-rate adequacy check
  - Safety classification: SAFE / MODERATE / TIGHT / AT RISK
Generates: DIVIDEND_SUSTAINABILITY.md + dividend_sustainability.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# ── Build dividend universe ────────────────────────────────────────────────────
results = []
for s in composite:
    code      = s["code"]
    price     = sf(s.get("price"))
    div_yield = sf(s.get("div_yield"))
    q1_eps    = sf(s.get("q1_eps"))
    fwd_pe    = sf(s.get("fwd_pe"))
    op_margin = sf(s.get("op_margin"))
    rev_yoy   = sf(s.get("rev_yoy"))
    score     = s.get("score")
    verdict   = s.get("verdict","—")
    is_fin    = s.get("is_fin", False)

    if not div_yield or div_yield <= 0: continue
    if not price or price <= 0: continue

    # Annual dividend per share
    dps = price * div_yield / 100

    # Annualized EPS proxy (Q1 × 4 — seasonality not adjusted)
    ann_eps = q1_eps * 4 if q1_eps else None

    # Payout ratio and coverage
    payout = None
    coverage = None
    if ann_eps and ann_eps > 0:
        payout   = dps / ann_eps * 100   # %
        coverage = ann_eps / dps          # how many times over

    # PE-based cross-check: implied EPS = price / fwd_pe
    fwd_eps   = price / fwd_pe if fwd_pe and fwd_pe > 0 else None
    fwd_payout = dps / fwd_eps * 100 if fwd_eps and fwd_eps > 0 else None

    # ── Safety classification ─────────────────────────────────────────────
    # Use the more conservative of ann_eps and fwd_eps
    best_payout = min(p for p in [payout, fwd_payout] if p is not None) if any(
        p is not None for p in [payout, fwd_payout]) else None

    if best_payout is None:
        safety = "UNKNOWN"
    elif best_payout <= 50:
        safety = "SAFE"         # well covered, room to grow
    elif best_payout <= 80:
        safety = "MODERATE"     # comfortable
    elif best_payout <= 100:
        safety = "TIGHT"        # covered but no cushion
    elif best_payout <= 130:
        safety = "AT RISK"      # paying >100% of earnings — draw from reserves
    else:
        safety = "UNSUSTAINABLE" # >130% payout — cut likely

    # ── Yield quality bonus ───────────────────────────────────────────────
    # High yield + safe payout = "quality income"
    quality = "HIGH" if div_yield >= 4.5 and safety in ("SAFE","MODERATE") else \
              "GOOD" if div_yield >= 3.0 and safety in ("SAFE","MODERATE","TIGHT") else \
              "STRETCHED" if safety in ("AT RISK","UNSUSTAINABLE") else "OK"

    results.append({
        "code":       code,
        "name":       s["name"],
        "sector":     s.get("sector","—"),
        "score":      score,
        "verdict":    verdict,
        "price":      price,
        "div_yield":  div_yield,
        "dps":        round(dps, 2),
        "q1_eps":     q1_eps,
        "ann_eps":    round(ann_eps, 2) if ann_eps else None,
        "fwd_eps":    round(fwd_eps, 2) if fwd_eps else None,
        "payout":     round(payout, 1) if payout else None,
        "fwd_payout": round(fwd_payout, 1) if fwd_payout else None,
        "best_payout": round(best_payout, 1) if best_payout else None,
        "coverage":   round(coverage, 2) if coverage else None,
        "safety":     safety,
        "quality":    quality,
        "is_fin":     is_fin,
        "op_margin":  op_margin,
        "rev_yoy":    rev_yoy,
    })

# Add expansion stocks
for s in expansion:
    code  = s["code"]
    div   = sf(s.get("div"))
    pe    = sf(s.get("pe"))
    eps   = sf(s.get("eps"))

    if not div or div <= 0: continue

    # For expansion stocks, we only have yield; need price to compute DPS
    # Estimate price from PE × EPS if available
    price_est = pe * eps if pe and eps else None
    dps_est   = price_est * div / 100 if price_est else None
    ann_eps   = eps * 4 if eps else None
    payout    = dps_est / ann_eps * 100 if (dps_est and ann_eps and ann_eps > 0) else None
    fwd_payout = payout  # same estimate

    best_payout = payout
    if best_payout is None:
        safety = "UNKNOWN"
    elif best_payout <= 50:
        safety = "SAFE"
    elif best_payout <= 80:
        safety = "MODERATE"
    elif best_payout <= 100:
        safety = "TIGHT"
    elif best_payout <= 130:
        safety = "AT RISK"
    else:
        safety = "UNSUSTAINABLE"

    quality = "HIGH" if div >= 4.5 and safety in ("SAFE","MODERATE") else \
              "GOOD" if div >= 3.0 and safety in ("SAFE","MODERATE","TIGHT") else \
              "OK"

    results.append({
        "code":       code,
        "name":       s["name"],
        "sector":     "Financial" if s.get("is_fin") else "Various",
        "score":      None,
        "verdict":    s.get("conv","WATCH"),
        "price":      price_est,
        "div_yield":  div,
        "dps":        round(dps_est, 2) if dps_est else None,
        "q1_eps":     eps,
        "ann_eps":    round(ann_eps, 2) if ann_eps else None,
        "fwd_eps":    None,
        "payout":     round(payout, 1) if payout else None,
        "fwd_payout": None,
        "best_payout": round(best_payout, 1) if best_payout else None,
        "coverage":   round(ann_eps/dps_est, 2) if (ann_eps and dps_est and dps_est>0) else None,
        "safety":     safety,
        "quality":    quality,
        "is_fin":     s.get("is_fin", False),
        "op_margin":  None,
        "rev_yoy":    sf(s.get("yoy")),
    })

results.sort(key=lambda x: -(x["div_yield"] or 0))

# ── Statistics ────────────────────────────────────────────────────────────────
safe       = [r for r in results if r["safety"] in ("SAFE","MODERATE")]
tight      = [r for r in results if r["safety"] == "TIGHT"]
at_risk    = [r for r in results if r["safety"] in ("AT RISK","UNSUSTAINABLE")]
high_qual  = [r for r in results if r["quality"] == "HIGH"]
unknown    = [r for r in results if r["safety"] == "UNKNOWN"]

div_paying = len(results)
avg_yield  = sum(r["div_yield"] for r in results) / div_paying if div_paying else 0

# ── Generate DIVIDEND_SUSTAINABILITY.md ───────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

def safety_icon(s):
    return {"SAFE":"✅","MODERATE":"🟢","TIGHT":"🟡","AT RISK":"🔴","UNSUSTAINABLE":"💀","UNKNOWN":"❓"}.get(s,"❓")

def quality_icon(q):
    return {"HIGH":"⭐","GOOD":"✓","STRETCHED":"⚠","OK":""}.get(q,"")

lines = [
    f"# Dividend Sustainability Analysis — {TODAY}",
    "*Payout ratio = Annual DPS ÷ Annualized EPS (Q1×4). Coverage = EPS ÷ DPS.*",
    "*Best payout uses the more conservative of Q1-annualized vs Fwd P/E implied EPS.*",
    "",
    "## Summary",
    "",
    f"- **Dividend-paying stocks**: {div_paying} (of 62 universe)",
    f"- **Avg yield across payers**: {avg_yield:.2f}%",
    f"- **SAFE/MODERATE** (payout ≤ 80%): {len(safe)} stocks",
    f"- **TIGHT** (80–100% payout): {len(tight)} stocks",
    f"- **AT RISK / UNSUSTAINABLE** (payout >100%): {len(at_risk)} stocks",
    f"- **Quality income** (yield ≥4.5% + safe payout): {len(high_qual)} stocks",
    "",
    "---",
    "",
    "## ⭐ Quality Income Picks (Yield ≥ 4.5% + Payout ≤ 80%)",
    "*High yield with healthy earnings coverage — suitable for income mandate ETFs.*",
    "",
    "| Code | Name | Sector | Yield | DPS | Ann EPS | Payout | Coverage | Score | Verdict |",
    "|------|------|--------|-------|-----|---------|--------|----------|-------|---------|",
]

for r in sorted(high_qual, key=lambda x: -(x["div_yield"] or 0)):
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | {r['sector']} | "
        f"**{r['div_yield']:.2f}%** | ¥{fmt(r['dps'],2)} | "
        f"¥{fmt(r['ann_eps'],2)} | {fmt(r['best_payout'],1,'','')}% | "
        f"**{fmt(r['coverage'],2,'','')}×** | {r['score'] or '—'} | {r['verdict']} |"
    )

lines += [
    "",
    "---",
    "",
    "## Full Dividend Safety Table",
    "",
    "| Code | Name | Yield | Payout | Coverage | Safety | Quality | Score |",
    "|------|------|-------|--------|----------|--------|---------|-------|",
]

for r in results:
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | "
        f"**{r['div_yield']:.2f}%** | "
        f"{fmt(r['best_payout'],1,'','')}{'%' if r['best_payout'] else ''} | "
        f"{fmt(r['coverage'],2,'','')}{'×' if r['coverage'] else ''} | "
        f"{safety_icon(r['safety'])} **{r['safety']}** | "
        f"{quality_icon(r['quality'])} {r['quality']} | "
        f"{r['score'] or '—'} |"
    )

# AT RISK section
if at_risk:
    lines += [
        "",
        "---",
        "",
        f"## 🔴 At-Risk Dividends (Payout > 100%) — {len(at_risk)} stocks",
        "*Paying more in dividends than Q1 earnings support — risk of cut or special/one-time payout.*",
        "",
        "| Code | Name | Yield | Payout | Ann EPS | DPS | Note |",
        "|------|------|-------|--------|---------|-----|------|",
    ]
    for r in sorted(at_risk, key=lambda x: -(x["best_payout"] or 0)):
        note = ""
        if r["is_fin"]: note = "Financial — reserve-based payout common"
        elif (r["rev_yoy"] or 0) < -10: note = "Revenue declining — earnings may worsen"
        elif (r["op_margin"] or 100) < 5: note = "Thin margins — limited payout headroom"
        else: note = "Q1 seasonality may explain; verify FY EPS"
        lines.append(
            f"| **{r['code']}** | {r['name'].split()[0]} | {r['div_yield']:.2f}% | "
            f"**{fmt(r['best_payout'],1,'','')}%** | "
            f"¥{fmt(r['ann_eps'],2)} | ¥{fmt(r['dps'],2)} | {note} |"
        )

lines += [
    "",
    "---",
    "",
    "## Methodology Notes",
    "",
    "**Annualized EPS**: Q1 2026 EPS × 4. Taiwan companies are seasonal;",
    "actual FY EPS may be higher/lower (semicon/AI typically back-half loaded).",
    "",
    "**Payout ratio sources**:",
    "- Primary: price × div_yield / (Q1 EPS × 4)",
    "- Cross-check: price × div_yield / (price / Fwd P/E implied EPS)",
    "- We use the *lower* (more conservative) payout figure.",
    "",
    "**Financial sector caveat**: Banks and insurance pay dividends from",
    "regulated capital buffers, not just current-period earnings.",
    "Payout >100% is common and not always a red flag for financials.",
    "",
    "**PSMC (6770)**: Q1 EPS anomalously high (non-recurring OP); payout ratio",
    "appears artificially safe — actual sustainable payout is much higher.",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 19*",
]

(REPORT_DIR / "DIVIDEND_SUSTAINABILITY.md").write_text("\n".join(lines), encoding="utf-8")

# ── Save JSON ──────────────────────────────────────────────────────────────────
div_json = {
    "date": TODAY,
    "summary": {
        "total_payers":  div_paying,
        "avg_yield":     round(avg_yield, 2),
        "safe_count":    len(safe),
        "tight_count":   len(tight),
        "at_risk_count": len(at_risk),
        "quality_count": len(high_qual),
    },
    "quality_picks": [
        {"code": r["code"], "name": r["name"].split()[0], "sector": r["sector"],
         "yield": r["div_yield"], "payout": r["best_payout"], "coverage": r["coverage"],
         "safety": r["safety"], "score": r["score"]}
        for r in sorted(high_qual, key=lambda x: -(x["div_yield"] or 0))
    ],
    "at_risk": [
        {"code": r["code"], "name": r["name"].split()[0],
         "yield": r["div_yield"], "payout": r["best_payout"], "safety": r["safety"]}
        for r in sorted(at_risk, key=lambda x: -(x["best_payout"] or 0))
    ],
    "all_payers": [
        {"code": r["code"], "name": r["name"].split()[0], "sector": r["sector"],
         "yield": r["div_yield"], "dps": r["dps"], "ann_eps": r["ann_eps"],
         "payout": r["best_payout"], "coverage": r["coverage"],
         "safety": r["safety"], "quality": r["quality"], "score": r["score"]}
        for r in results
    ],
}
(REPORT_DIR / "dividend_sustainability.json").write_text(
    json.dumps(div_json, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ DIVIDEND_SUSTAINABILITY.md + dividend_sustainability.json")
print(f"\n  Dividend-paying stocks: {div_paying} / 62 | Avg yield: {avg_yield:.2f}%")
print(f"  SAFE/MODERATE: {len(safe)} | TIGHT: {len(tight)} | AT RISK: {len(at_risk)} | UNKNOWN: {len(unknown)}")
print(f"\n  Quality income picks (yield≥4.5% + payout≤80%):")
for r in sorted(high_qual, key=lambda x: -(x["div_yield"] or 0)):
    print(f"    {r['code']} {r['name'].split()[0]:12s}  yield={r['div_yield']:.2f}%  "
          f"payout={fmt(r['best_payout'],1,'','')}%  cov={fmt(r['coverage'],2,'','')}×  {r['safety']}")
if at_risk:
    print(f"\n  At-risk dividends (payout>100%):")
    for r in sorted(at_risk, key=lambda x: -(x["best_payout"] or 0)):
        print(f"    {r['code']} {r['name'].split()[0]:12s}  yield={r['div_yield']:.2f}%  "
              f"payout={fmt(r['best_payout'],1,'','')}%  {'[fin]' if r['is_fin'] else ''}")
