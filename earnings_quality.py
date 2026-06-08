#!/usr/bin/env python3
"""
Iteration 46: Earnings Quality Score
Synthesises Q4 2025 + Q1 2026 financial data into a 0-10 quality score.
Components (each 0-1 point, total 10):
  EQ1  EPS positive & growing (q1_eps > 0)
  EQ2  EPS acceleration (eps_accel > 0)
  EQ3  EPS acceleration strong (eps_accel > 10%)
  EQ4  Revenue YoY positive (april_yoy > 0)
  EQ5  Revenue acceleration (accel == ACCELERATING)
  EQ6  Operating margin healthy (op_margin > 15%)
  EQ7  Net margin quality (net_margin / op_margin > 0.60)
  EQ8  Forward cheaper than trailing (fwd_pe < trail_pe)
  EQ9  Dividend sustainable (div_yield > 0 and q1_eps * 4 > expected_div)
  EQ10 Sequential Q4→Q1 improvement implied (fwd_eps > trail_eps)
No API calls. Generates: earnings_quality.json
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

comp   = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
apr    = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
bwi    = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
grand  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

comp_map  = {s["code"]: s for s in comp}
exp_map   = {s["code"]: s for s in expd}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

results = []

all_codes = sorted(set(comp_map.keys()) | set(exp_map.keys()))

for code in all_codes:
    cs = comp_map.get(code, exp_map.get(code, {}))
    ar = apr_map.get(code, {})
    bw = bwi_map.get(code, {})
    g  = grand_map.get(code, {})

    name = cs.get("name", code)

    # Raw data
    q1_eps    = sf(cs.get("q1_eps"))
    fwd_eps   = sf(cs.get("fwd_eps"))
    trail_eps = sf(cs.get("trail_eps"))
    eps_accel = sf(cs.get("eps_accel"))
    fwd_pe    = sf(cs.get("fwd_pe"))
    trail_pe  = sf(cs.get("trail_pe"))
    op_margin = sf(cs.get("op_margin"))
    net_margin= sf(cs.get("net_margin"))
    rev_yoy   = sf(cs.get("rev_yoy"))
    apr_yoy   = sf(ar.get("april_yoy"))
    apr_accel = ar.get("accel", "")
    div_yield = sf(bw.get("div_new") or bw.get("div_yield")) or sf(cs.get("div_yield"))
    price     = sf(cs.get("price"))

    # Infer dividend per share from yield and price
    # Infer if dividend is sustainable: annual_div ≈ price * dy/100
    # Compare to fwd_eps (annualized from q1)
    ann_div = (price * div_yield / 100) if (price and div_yield) else None
    div_covered = (fwd_eps and ann_div and fwd_eps > ann_div * 0.7) if (fwd_eps and ann_div) else None

    # Implied average Q2–Q4 2025 EPS
    prior_q_avg = ((trail_eps - q1_eps) / 3) if (trail_eps and q1_eps) else None

    # ── Score components ──────────────────────────────────────────────────────
    scores = {}

    # EQ1: EPS positive & growing
    scores["EQ1_eps_positive"] = 1 if (q1_eps and q1_eps > 0) else 0

    # EQ2: EPS acceleration positive (q1 above prior average)
    if eps_accel is not None:
        scores["EQ2_eps_accel_pos"] = 1 if eps_accel > 0 else 0
    elif prior_q_avg and q1_eps:
        scores["EQ2_eps_accel_pos"] = 1 if q1_eps > prior_q_avg else 0
    else:
        scores["EQ2_eps_accel_pos"] = 0

    # EQ3: Strong EPS acceleration (>10%)
    scores["EQ3_accel_strong"] = 1 if (eps_accel and eps_accel > 10) else 0

    # EQ4: Revenue YoY positive (use april as latest, fallback to composite)
    yoy_to_use = apr_yoy if apr_yoy is not None else rev_yoy
    scores["EQ4_rev_yoy_pos"] = 1 if (yoy_to_use and yoy_to_use > 0) else 0

    # EQ5: Revenue ACCELERATING
    scores["EQ5_rev_accel"] = 1 if apr_accel == "ACCELERATING" else 0

    # EQ6: Operating margin healthy
    if op_margin is not None:
        if cs.get("is_fin") or cs.get("sector","").lower() in ("finance","financial"):
            scores["EQ6_margin_healthy"] = 1 if op_margin > 20 else 0
        else:
            scores["EQ6_margin_healthy"] = 1 if op_margin > 15 else 0
    else:
        scores["EQ6_margin_healthy"] = 0

    # EQ7: Net margin quality (net >= 60% of operating, indicating low financial expense drag)
    if net_margin is not None and op_margin and op_margin > 0:
        scores["EQ7_margin_quality"] = 1 if (net_margin / op_margin) >= 0.60 else 0
    else:
        scores["EQ7_margin_quality"] = 0

    # EQ8: Forward cheaper than trailing (earnings growing into next year)
    if fwd_pe and trail_pe and trail_pe > 0 and fwd_pe > 0:
        scores["EQ8_fwd_lt_trail"] = 1 if fwd_pe < trail_pe else 0
    else:
        scores["EQ8_fwd_lt_trail"] = 0

    # EQ9: Dividend sustainable (covered by forward earnings)
    if div_covered is not None:
        scores["EQ9_div_covered"] = 1 if div_covered else 0
    elif div_yield and div_yield > 0 and q1_eps and q1_eps > 0:
        # Rough check: if yield < 8% and EPS positive, assume sustainable
        scores["EQ9_div_covered"] = 1 if div_yield < 8 else 0
    else:
        scores["EQ9_div_covered"] = 0  # no dividend or can't assess

    # EQ10: Sequential Q4→Q1 improvement (fwd_eps > trail_eps means Q1 above prior-4Q average)
    if fwd_eps and trail_eps and trail_eps > 0:
        scores["EQ10_fwd_gt_trail"] = 1 if fwd_eps > trail_eps else 0
    elif q1_eps and prior_q_avg:
        scores["EQ10_fwd_gt_trail"] = 1 if q1_eps > prior_q_avg else 0
    else:
        scores["EQ10_fwd_gt_trail"] = 0

    eq_score = sum(scores.values())

    # Grade
    if eq_score >= 9:   grade = "A+ 最優質"
    elif eq_score >= 7: grade = "A  優質"
    elif eq_score >= 5: grade = "B  良好"
    elif eq_score >= 3: grade = "C  普通"
    else:               grade = "D  偏弱"

    grand_score = g.get("grand", 0) or 0
    final       = g.get("final", "—")

    results.append({
        "code":       code,
        "name":       name,
        "eq_score":   eq_score,
        "grade":      grade,
        "scores":     scores,
        "grand":      round(grand_score, 1),
        "final":      final,
        "key_metrics": {
            "q1_eps":      q1_eps,
            "fwd_eps":     round(fwd_eps,2) if fwd_eps else None,
            "trail_eps":   round(trail_eps,2) if trail_eps else None,
            "eps_accel":   round(eps_accel,1) if eps_accel else None,
            "fwd_pe":      round(fwd_pe,1) if fwd_pe else None,
            "trail_pe":    round(trail_pe,1) if trail_pe else None,
            "op_margin":   round(op_margin,1) if op_margin else None,
            "net_margin":  round(net_margin,1) if net_margin else None,
            "rev_yoy":     round(apr_yoy,1) if apr_yoy else (round(rev_yoy,1) if rev_yoy else None),
            "rev_accel":   apr_accel,
            "div_yield":   round(div_yield,2) if div_yield else None,
            "div_covered": div_covered,
        },
        "q4_q1_analysis": {
            "prior_q_avg_eps": round(prior_q_avg,2) if prior_q_avg else None,
            "q1_vs_prior": round(((q1_eps/prior_q_avg)-1)*100,1)
                           if (q1_eps and prior_q_avg and prior_q_avg>0) else None,
            "yoy_rev_growth": round(apr_yoy,1) if apr_yoy else None,
            "accel_status": apr_accel,
            "margin_trend": "改善" if (net_margin and op_margin and net_margin/max(0.01,op_margin)>0.6) else "待觀察",
        }
    })

results.sort(key=lambda x: (-x["eq_score"], -x["grand"]))

# Grade buckets
a_plus = [r for r in results if r["eq_score"] >= 9]
a_grad  = [r for r in results if 7 <= r["eq_score"] < 9]
b_grad  = [r for r in results if 5 <= r["eq_score"] < 7]
c_or_d  = [r for r in results if r["eq_score"] < 5]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'EARNINGS QUALITY SCORES':=<65}")
print(f"  A+({len(a_plus)})  A({len(a_grad)})  B({len(b_grad)})  C/D({len(c_or_d)})")
print(f"\n  {'代號':<8} {'名稱':<12} {'EQ':>4} {'Grade':<14} {'Grand':>7} {'評級'}")
print("-"*65)
for r in results[:25]:
    bar = "█"*r["eq_score"] + "░"*(10-r["eq_score"])
    print(f"  {r['code']:<8} {r['name'].split(' ')[0]:<12} "
          f"{r['eq_score']:>4}  {r['grade']:<14} {r['grand']:>7.1f}  {r['final']}")

print(f"\n  A+ 最優質 stocks:")
for r in a_plus:
    m = r["key_metrics"]
    print(f"    {r['code']} {r['name'].split(' ')[0]}: EPS加速={m['eps_accel']}% "
          f"營業利益率={m['op_margin']}% 殖利率={m['div_yield']}%")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":      len(results),
    "grade_counts": {
        "A+": len(a_plus), "A": len(a_grad), "B": len(b_grad), "C_D": len(c_or_d)
    },
    "all_stocks": results,
    "a_plus":     a_plus,
    "a_grade":    a_grad,
    "methodology": {
        "EQ1":  "Q1 2026 EPS > 0",
        "EQ2":  "EPS acceleration positive (q1 > prior avg)",
        "EQ3":  "Strong EPS acceleration > 10%",
        "EQ4":  "April 2026 revenue YoY > 0",
        "EQ5":  "Revenue ACCELERATING (April vs prior months)",
        "EQ6":  "Operating margin > 15% (general) or > 20% (financial)",
        "EQ7":  "Net margin >= 60% of operating margin (low financial drag)",
        "EQ8":  "Forward PE < trailing PE (growing earnings)",
        "EQ9":  "Dividend yield covered by forward earnings",
        "EQ10": "Forward EPS > trailing EPS (sequential Q4→Q1 improvement)",
    }
}
(REPORT_DIR / "earnings_quality.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ earnings_quality.json saved ({len(results)} stocks)")
