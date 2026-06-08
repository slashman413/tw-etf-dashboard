#!/usr/bin/env python3
"""
Iteration 38b: May Revenue Impact Preview
No API calls — projects May 2026 revenue outcomes using April trend data.
Uses: april_revenue.json, composite_data.json, grand_unified.json, dna_signals.json
Generates: may_preview.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

apr   = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
comp  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
grand = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna   = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
mom   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map   = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
mom_map   = {m["code"]: m for m in mom.get("all_momentum", [])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Parse April revenue records ───────────────────────────────────────────────
apr_map = {}
for r in apr.get("all_results", []):
    code = r.get("code")
    if code: apr_map[code] = r

print(f"April revenue data: {len(apr_map)} stocks")
if apr_map:
    sample = next(iter(apr_map.values()))
    print(f"  Sample keys: {list(sample.keys())[:10]}")

# ── Build May preview for each stock ─────────────────────────────────────────
previews = []

for code, name in sorted(name_map.items()):
    ar = apr_map.get(code, {})
    gr = grand_map.get(code, {})
    dn = dna_map.get(code, {})
    mm = mom_map.get(code, {})

    # April revenue metrics
    apr_yoy  = sf(ar.get("april_yoy"))
    apr_mom  = sf(ar.get("mom"))
    apr_cum  = sf(ar.get("cum_yoy"))
    apr_rev  = sf(ar.get("apr_b"))        # already in 億元
    apr_accel= ar.get("accel", "")        # ACCELERATING / DECELERATING / STABLE

    # Trend extrapolation for May
    # Use: April YoY + momentum signal + DNA signal + sector trend
    bull_signs  = dn.get("bull_signs", 0) or 0
    pct_vs_ma   = sf(mm.get("pct_vs_ma"))
    pct_prior   = sf(mm.get("pct_vs_prior"))

    # Score the revenue outlook
    rev_score = 0
    signals   = []

    if apr_yoy is not None:
        if apr_yoy > 30:   rev_score += 3; signals.append(f"4月YoY+{apr_yoy:.0f}%強勢")
        elif apr_yoy > 10: rev_score += 2; signals.append(f"4月YoY+{apr_yoy:.0f}%成長")
        elif apr_yoy > 0:  rev_score += 1; signals.append(f"4月YoY+{apr_yoy:.0f}%微增")
        elif apr_yoy > -10: rev_score -= 1; signals.append(f"4月YoY{apr_yoy:.0f}%小幅衰退")
        else:               rev_score -= 2; signals.append(f"4月YoY{apr_yoy:.0f}%衰退")

    if apr_mom is not None:
        if apr_mom > 10:  rev_score += 1; signals.append(f"月增率+{apr_mom:.0f}%")
        elif apr_mom < -10: rev_score -= 1; signals.append(f"月增率{apr_mom:.0f}%")

    if apr_accel == "ACCELERATING":   rev_score += 1; signals.append("累積加速成長")
    elif apr_accel == "DECELERATING": rev_score -= 1; signals.append("累積成長減速")

    if bull_signs >= 4: rev_score += 1; signals.append(f"DNA {bull_signs}/6訊號強")
    elif bull_signs <= 1: rev_score -= 1; signals.append(f"DNA弱({bull_signs}/6)")

    if (pct_vs_ma or 0) > 5:  rev_score += 1; signals.append("股價強於月均")
    elif (pct_vs_ma or 0) < -10: rev_score -= 1; signals.append("股價弱於月均")

    # Verdict
    if   rev_score >= 4: outlook = "🔥 超預期強勢"
    elif rev_score >= 2: outlook = "📈 可望優於預期"
    elif rev_score >= 0: outlook = "⬛ 符合預期"
    elif rev_score >= -2: outlook = "📉 可能低於預期"
    else:                 outlook = "❌ 警示衰退"

    # Estimate May rev range (Apr rev in 億 * (1 + yoy%) ± 5% seasonal)
    may_est_low = may_est_high = None
    apr_rev_bn  = round(apr_rev, 2) if apr_rev else None
    if apr_rev and apr_yoy is not None:
        trend_factor = 1 + max(-0.5, min(2.0, apr_yoy/100))
        base         = apr_rev * trend_factor
        may_est_low  = round(base * 0.95, 2)
        may_est_high = round(base * 1.05, 2)

    previews.append({
        "code":       code,
        "name":       name,
        "apr_yoy":    round(apr_yoy,1) if apr_yoy is not None else None,
        "apr_mom":    round(apr_mom,1) if apr_mom is not None else None,
        "apr_cum_yoy":round(apr_cum,1) if apr_cum is not None else None,
        "apr_rev_bn":  apr_rev_bn,
        "apr_accel":   apr_accel,
        "may_est_low_bn":  may_est_low,
        "may_est_high_bn": may_est_high,
        "rev_score":  rev_score,
        "outlook":    outlook,
        "signals":    signals,
        "grand":      gr.get("grand"),
        "final":      gr.get("final",""),
        "bull_signs": bull_signs,
    })

previews.sort(key=lambda x: -(x["rev_score"]))

# ── Segment ───────────────────────────────────────────────────────────────────
beat      = [p for p in previews if p["rev_score"] >= 2]
in_line   = [p for p in previews if p["rev_score"] in (0, 1)]
miss      = [p for p in previews if p["rev_score"] < 0]

# TRIPLE CONFIRMED stocks — May outlook matters most
triple_preview = [p for p in previews
                  if p["final"] and "TRIPLE" in p["final"]]

print(f"\n=== May Revenue Impact Preview ===")
print(f"Total: {len(previews)} | Beat: {len(beat)} | In-line: {len(in_line)} | Miss: {len(miss)}")

print(f"\n🔥 Top Beat Candidates (rev_score ≥ 2):")
for p in beat[:10]:
    yoy = f"YoY={p['apr_yoy']:+.0f}%" if p['apr_yoy'] is not None else "YoY=?"
    print(f"  {p['code']} {p['name'][:10]}: {yoy} | score={p['rev_score']} | {p['outlook']}")

print(f"\n❌ Warning: Potential Misses (rev_score < -1):")
for p in [x for x in miss if x['rev_score'] < -1][:5]:
    yoy = f"YoY={p['apr_yoy']:+.0f}%" if p['apr_yoy'] is not None else "YoY=?"
    print(f"  {p['code']} {p['name'][:10]}: {yoy} | score={p['rev_score']} | {p['outlook']}")

print(f"\n💎 TRIPLE CONFIRMED May Outlook:")
for p in triple_preview:
    yoy = f"YoY={p['apr_yoy']:+.0f}%" if p['apr_yoy'] is not None else "no apr data"
    print(f"  {p['code']} {p['name'][:10]}: {yoy} | {p['outlook']}")

out = {
    "date":     TODAY,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "expected_release": "2026-06-10 (estimated)",
    "total":    len(previews),
    "beat_candidates":  beat,
    "in_line":          in_line,
    "miss_risks":       miss,
    "triple_preview":   triple_preview,
    "all_previews":     previews,
    "summary": {
        "beat": len(beat), "in_line": len(in_line), "miss": len(miss)
    }
}
(REPORT_DIR / "may_preview.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ may_preview.json saved ({len(previews)} stocks)")
