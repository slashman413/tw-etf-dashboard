#!/usr/bin/env python3
"""
Iteration 60: Margin of Safety + Intrinsic Value Calculator
Modified Graham formula adapted for Taiwan market:
  Fair Value = Fwd_EPS × Fair_PE
  Fair_PE = base_pe × (1 + growth_premium) × quality_mult × sector_adj
  Margin of Safety = (Fair Value - Price) / Fair Value × 100
No API calls. Generates: margin_of_safety.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

comp   = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))
bwi    = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
grand  = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
earq   = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))
q2f    = json.loads((REPORT_DIR/"q2_eps_forecast.json").read_text(encoding="utf-8"))
peer   = json.loads((REPORT_DIR/"peer_comparison.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))

bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed", [])}
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks", [])}
q2f_map   = {r["code"]: r for r in q2f.get("all_forecasts", [])}
dna_map   = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

code_sector = {}
for sec in peer.get("sectors", []):
    for s in sec.get("stocks", []):
        code_sector[s["code"]] = sec["sector"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Sector base PE (Taiwan fair value norms) ─────────────────────────────────
# Based on TWSE long-run sector average PE ratios
SECTOR_BASE_PE = {
    "金融保險":    12.0,   # Banks/insurance: lower PE, stable
    "半導體":      22.0,   # Premium for semiconductor moats
    "電子零組件":  18.0,
    "電腦及週邊":  16.0,
    "通信網路":    20.0,
    "航運":        10.0,   # Cyclical; lower base
    "電機機械":    16.0,
    "光電":        15.0,
    "資訊科技服務":20.0,
    "汽車零件":    14.0,
    "化工":        13.0,
    "鋼鐵":        10.0,
    "其他電子":    16.0,
    "其他":        14.0,
}

# ── Sector dividend yield adjustment ─────────────────────────────────────────
# Higher yield sectors deserve PE premium for income investors
SECTOR_YIELD_ADJ = {
    "金融保險": 1.05,   # High yield → slight PE premium
    "航運":      0.95,  # Low yield, cyclical → discount
    "半導體":    1.0,
    "其他":      1.0,
}

all_stocks = comp + [s for s in expd if s["code"] not in {x["code"] for x in comp}]

results = []
for s in all_stocks:
    code    = s.get("code", "")
    name    = name_map.get(code, code)
    sector  = code_sector.get(code, "其他")
    g       = grand_map.get(code, {})
    bw      = bwi_map.get(code, {})
    eq      = earq_map.get(code, {})
    q2      = q2f_map.get(code, {})
    dn      = dna_map.get(code, {})

    # Price and earnings
    price       = sf(s.get("price"))
    q1_eps      = sf(s.get("q1_eps"))
    fwd_eps     = sf(s.get("fwd_eps"))     # Q1 × 4 annualized
    trail_eps   = sf(s.get("trail_eps"))
    eps_accel   = sf(s.get("eps_accel"))   # YoY EPS growth %
    op_margin   = sf(s.get("op_margin"))
    net_margin  = sf(s.get("net_margin"))
    div_yield   = sf(bw.get("div_new") or bw.get("div_yield") or s.get("div_yield"))
    pb          = sf(bw.get("pb_new") or s.get("pb"))
    pe_curr     = sf(bw.get("pe_new") or s.get("fwd_pe"))

    # Q2 forecast data
    q2_eps_est    = sf(q2.get("q2_eps_est"))
    q2_growth_pct = sf(q2.get("q2_eps_growth_pct"))
    fwd_pe_h1     = sf(q2.get("forward_pe_est"))   # H1 annualized PE

    # Quality signals
    grand_s   = g.get("grand", 0) or 0
    final     = g.get("final", "") or ""
    eq_score  = eq.get("eq_score", 0) or 0
    eq_grade  = (eq.get("grade","") or "").split(" ")[0]
    bull      = dn.get("bull_signs", 0) or 0

    if price is None or price <= 0:
        continue

    # Choose best EPS estimate for valuation
    # Priority: Q2-adjusted forward > Q1 annualized > trailing
    if q2_eps_est is not None and q1_eps is not None:
        best_eps = (q1_eps + q2_eps_est) * 2   # H1 annualized
    elif fwd_eps is not None and fwd_eps > 0:
        best_eps = fwd_eps
    elif trail_eps is not None and trail_eps > 0:
        best_eps = trail_eps
    else:
        best_eps = None

    if best_eps is None or best_eps <= 0:
        continue

    # ── Fair PE Calculation ───────────────────────────────────────────────────
    base_pe = SECTOR_BASE_PE.get(sector, 14.0)

    # Growth premium: EPS growth above 10% adds PE points
    # Graham growth formula: each 1pp above 0 = 0.2x PE premium, max +8x
    if eps_accel is not None:
        growth_used = min(max(eps_accel, -20), 100)
    elif q2_growth_pct is not None:
        growth_used = min(max(q2_growth_pct, -20), 100)
    else:
        growth_used = 5  # default modest growth

    growth_pe_add = min(8, max(-3, growth_used * 0.08))

    # Quality multiplier (EQ score: high quality → PE premium)
    quality_mult = 0.85 + (eq_score / 10) * 0.30  # 0.85–1.15

    # DNA bull signals premium (strong momentum adds to fair PE)
    dna_mult = 1.0 + (bull / 6) * 0.10  # 1.0–1.10

    # Sector yield adjustment
    yield_adj = SECTOR_YIELD_ADJ.get(sector, 1.0)

    # Dividend safety discount (negative yield = zero payout quality)
    if div_yield and div_yield > 3:
        div_bonus = 0.03   # high yield adds 3% to fair PE
    else:
        div_bonus = 0

    fair_pe = (base_pe + growth_pe_add) * quality_mult * dna_mult * yield_adj * (1 + div_bonus)
    fair_pe = round(max(5, min(50, fair_pe)), 1)   # cap 5–50x

    # ── Intrinsic Value ───────────────────────────────────────────────────────
    intrinsic_value = round(best_eps * fair_pe, 1)

    # ── Margin of Safety ─────────────────────────────────────────────────────
    mos_pct = round((intrinsic_value - price) / intrinsic_value * 100, 1) if intrinsic_value > 0 else 0

    # ── Graham Number (simplified for reference) ──────────────────────────────
    # Graham: √(22.5 × EPS × BVPS) — approximate BVPS from P/B
    bvps_est = price / pb if pb and pb > 0 else None
    if bvps_est and best_eps > 0:
        graham_num = round((22.5 * best_eps * bvps_est) ** 0.5, 1)
        graham_mos = round((graham_num - price) / graham_num * 100, 1)
    else:
        graham_num = None
        graham_mos = None

    # ── Safety label ──────────────────────────────────────────────────────────
    if mos_pct >= 40:    safety = "🛡 超高安全邊際"
    elif mos_pct >= 25:  safety = "✅ 高安全邊際"
    elif mos_pct >= 10:  safety = "📈 有安全邊際"
    elif mos_pct >= 0:   safety = "⚖ 合理估值"
    elif mos_pct >= -15: safety = "⚠ 略微高估"
    else:                safety = "❌ 明顯高估"

    # ── Upside/downside ───────────────────────────────────────────────────────
    upside_to_fair   = round((intrinsic_value / price - 1) * 100, 1)
    downside_to_fair = round((price / intrinsic_value - 1) * 100, 1) if intrinsic_value > 0 else 0

    results.append({
        "code":           code,
        "name":           name.split(" ")[0] if name else code,
        "sector":         sector,
        "grand":          round(grand_s, 1),
        "final":          final,
        # Inputs
        "price":          price,
        "best_eps":       round(best_eps, 2),
        "pe_curr":        round(pe_curr, 1) if pe_curr else None,
        "pb":             round(pb, 2) if pb else None,
        "div_yield":      round(div_yield, 1) if div_yield else None,
        "eq_score":       eq_score,
        "eq_grade":       eq_grade,
        "bull_signs":     bull,
        "eps_accel":      round(eps_accel, 1) if eps_accel else None,
        # Fair value components
        "base_pe":        base_pe,
        "growth_pe_add":  round(growth_pe_add, 1),
        "quality_mult":   round(quality_mult, 2),
        "dna_mult":       round(dna_mult, 2),
        "fair_pe":        fair_pe,
        # Results
        "intrinsic_value":intrinsic_value,
        "mos_pct":        mos_pct,
        "safety":         safety,
        "upside_pct":     upside_to_fair,
        "graham_num":     graham_num,
        "graham_mos":     graham_mos,
    })

# Sort by MoS descending (highest safety first)
results.sort(key=lambda x: -x["mos_pct"])

# Key groups
high_safety   = [r for r in results if r["mos_pct"] >= 25]
reasonable    = [r for r in results if 0 <= r["mos_pct"] < 25]
overvalued    = [r for r in results if r["mos_pct"] < 0]
triple_mos    = [r for r in results if "TRIPLE" in (r.get("final") or "")]
best_garp     = [r for r in results
                 if r["mos_pct"] >= 10 and (r.get("eps_accel") or 0) > 15]

# Compute sector median intrinsic values
sector_mos = {}
for r in results:
    sec = r["sector"]
    sector_mos.setdefault(sec, []).append(r["mos_pct"])
sector_median_mos = {sec: round(statistics.median(vals), 1) for sec, vals in sector_mos.items() if vals}

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'MARGIN OF SAFETY + INTRINSIC VALUE':=<65}")
print(f"  Universe: {len(results)}  High safety(≥25%): {len(high_safety)}  Overvalued(<0%): {len(overvalued)}")

print(f"\n  Top 15 最高安全邊際:")
print(f"  {'代號':<6} {'名稱':<10} {'價格':>7} {'內在價值':>9} {'MoS%':>7} {'安全':>6}  {'說明'}")
print("-"*80)
for r in results[:15]:
    print(f"  {r['code']:<6} {r['name']:<10} {r['price']:>7.1f} "
          f"{r['intrinsic_value']:>9.1f} {r['mos_pct']:>+6.1f}%  "
          f"{r['safety'][:6]}  FairPE={r['fair_pe']}x  Grand={r['grand']}")

print(f"\n  TRIPLE持倉安全邊際:")
for r in triple_mos:
    print(f"  {r['code']} {r['name']:<10} 價={r['price']:.1f}  "
          f"內在值={r['intrinsic_value']:.1f}  MoS={r['mos_pct']:+.1f}%  {r['safety']}")

print(f"\n  GARP精選 (MoS≥10% + EPS加速>15%):")
for r in best_garp[:8]:
    print(f"  {r['code']} {r['name']:<10} MoS={r['mos_pct']:+.1f}%  "
          f"EPS加速={r['eps_accel']:+.1f}%  FairPE={r['fair_pe']}x  Grand={r['grand']}")

print(f"\n  明顯高估 (MoS < -15%):")
for r in overvalued[-5:]:
    print(f"  {r['code']} {r['name']:<10} 價={r['price']:.1f}  "
          f"內在值={r['intrinsic_value']:.1f}  MoS={r['mos_pct']:+.1f}%  PE={r['pe_curr']}")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "methodology": {
        "fair_pe":   "base_pe × (1+growth_pe_add) × quality_mult × dna_mult × yield_adj",
        "base_pe":   "Sector-specific Taiwan fair PE norm (10x–22x)",
        "growth":    "EPS_accel × 0.08 (capped +8/-3)",
        "quality":   "0.85 + (EQ_score/10) × 0.30",
        "mos":       "(intrinsic_value - price) / intrinsic_value × 100",
        "eps_used":  "H1_annualized if Q2 forecast available, else fwd_eps, else trail_eps",
    },
    "aggregate": {
        "total":          len(results),
        "high_safety":    len(high_safety),
        "reasonable":     len(reasonable),
        "overvalued":     len(overvalued),
        "garp_count":     len(best_garp),
    },
    "sector_median_mos": sector_median_mos,
    "all_results":  results,
    "high_safety":  high_safety,
    "reasonable":   reasonable,
    "overvalued":   overvalued,
    "triple_mos":   triple_mos,
    "best_garp":    best_garp,
}
(REPORT_DIR/"margin_of_safety.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- margin_of_safety.json saved ({len(results)} stocks)")

