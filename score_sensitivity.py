#!/usr/bin/env python3
"""
Iteration 44: Score Sensitivity & Upgrade Scenario Analysis
For every stock, computes exact gap to next conviction tier and
identifies which levers (val/mom/dna/fundamental) would trigger upgrade.
No API calls. Generates: score_sensitivity.json
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
apr     = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
watch   = json.loads((REPORT_DIR / "watchlist_alerts.json").read_text(encoding="utf-8"))

dna_map  = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map  = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map  = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map   = {r["code"]: r for r in rs.get("all_rs",[])}
comp_map = {s["code"]: s for s in comp}
exp_map  = {s["code"]: s for s in expd}
apr_map  = {r["code"]: r for r in apr.get("all_results",[])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Valuation scoring rules (from grand_unified spec) ────────────────────────
def calc_val_pts(pe, div_yield):
    """Recompute valuation points from raw PE/yield."""
    if pe is None: base = 2
    elif pe < 10:  base = 25
    elif pe < 15:  base = 22
    elif pe < 20:  base = 18
    elif pe < 30:  base = 12
    elif pe < 50:  base = 6
    else:          base = 2
    bonus = 0
    if div_yield and div_yield >= 6.0:   bonus = 2
    elif div_yield and div_yield >= 4.5: bonus = 1
    return min(25, base + bonus)

# ── Tiers ─────────────────────────────────────────────────────────────────────
TIERS = [
    ("🚀 TRIPLE CONFIRMED", 70, 3),   # grand>=70 AND bull_signs>=3
    ("✅ STRONG BUY",        65, 0),
    ("📈 BUY",               55, 0),
    ("👀 WATCH",             45, 0),
    ("⬛ HOLD",               35, 0),
    ("📉 REDUCE",             0, 0),
]

def get_tier(grand_score, bull_signs):
    if grand_score >= 70 and bull_signs >= 3: return "🚀 TRIPLE CONFIRMED"
    if grand_score >= 65: return "✅ STRONG BUY"
    if grand_score >= 55: return "📈 BUY"
    if grand_score >= 45: return "👀 WATCH"
    if grand_score >= 35: return "⬛ HOLD"
    return "📉 REDUCE"

def next_tier_info(grand_score, bull_signs, current_tier):
    """Return (next_tier_name, points_needed, description)."""
    if current_tier == "🚀 TRIPLE CONFIRMED":
        return None, 0, "已達最高評級"
    if current_tier == "✅ STRONG BUY":
        pts_gap = max(0, 70 - grand_score)
        if bull_signs < 3:
            return "🚀 TRIPLE CONFIRMED", pts_gap, f"需加 {pts_gap:.1f}分 且DNA≥3信號 (現{bull_signs}/6)"
        return "🚀 TRIPLE CONFIRMED", pts_gap, f"需加 {pts_gap:.1f}分"
    if current_tier == "📈 BUY":
        return "✅ STRONG BUY", max(0, 65 - grand_score), f"需加 {max(0,65-grand_score):.1f}分"
    if current_tier == "👀 WATCH":
        return "📈 BUY", max(0, 55 - grand_score), f"需加 {max(0,55-grand_score):.1f}分"
    if current_tier == "⬛ HOLD":
        return "👀 WATCH", max(0, 45 - grand_score), f"需加 {max(0,45-grand_score):.1f}分"
    return "⬛ HOLD", max(0, 35 - grand_score), f"需加 {max(0,35-grand_score):.1f}分"

# ── Per-stock analysis ────────────────────────────────────────────────────────
results = []

for r in grand.get("all_ranked", []):
    code  = r["code"]
    name  = r["name"]
    grand_score = r.get("grand", 0) or 0
    bull_signs  = r.get("bull_signs", 0) or 0
    fund_pts    = r.get("fund_pts") or r.get("g_pts") or 0
    tech_pts    = r.get("tech_pts", 0) or 0
    val_pts     = r.get("val_pts", 0) or 0
    mom_pts     = r.get("mom_pts", 0) or 0
    current_tier= r.get("final", get_tier(grand_score, bull_signs))

    dn = dna_map.get(code, {})
    bw = bwi_map.get(code, {})
    mm = mom_map.get(code, {})
    rv = rs_map.get(code, {})
    cs = comp_map.get(code, exp_map.get(code, {}))
    ar = apr_map.get(code, {})

    pe  = sf(bw.get("pe_new") or bw.get("pe_old"))
    dy  = sf(bw.get("div_new") or bw.get("div_yield"))
    close = sf(mm.get("close"))
    pct_ma= sf(mm.get("pct_vs_ma"))

    # Next tier gap
    next_tier, pts_needed, tier_desc = next_tier_info(grand_score, bull_signs, current_tier)

    # ── Upgrade levers ────────────────────────────────────────────────────────
    levers = []

    # 1. Valuation lever: what PE would unlock higher val_pts
    curr_val = val_pts
    if pe:
        # PE thresholds: <10=25, <15=22, <20=18, <30=12, <50=6
        if pe >= 50:
            uplift = 6 - curr_val + (1 if dy and dy >= 4.5 else 0)
            levers.append({"lever":"估值", "action":f"若PE壓縮至50以下",
                          "pts_gain": max(0, round(6-curr_val,1)),
                          "trigger":"股價下跌或EPS成長", "feasibility":"SHORT"})
        elif pe >= 30:
            uplift_20 = 18 - curr_val
            uplift_15 = 22 - curr_val
            if uplift_20 > 0:
                levers.append({"lever":"估值", "action":f"PE從{pe:.1f}x→20x (EPS成長{max(0,(pe/20-1)*100):.0f}%)",
                              "pts_gain": round(uplift_20,1), "trigger":"盈利成長或股價回落",
                              "feasibility":"MEDIUM"})
        elif pe >= 20:
            uplift = 22 - curr_val
            if uplift > 0:
                levers.append({"lever":"估值", "action":f"PE從{pe:.1f}x→15x",
                              "pts_gain": round(uplift,1), "trigger":"盈利加速或股價修正",
                              "feasibility":"MEDIUM"})
        elif pe >= 15:
            uplift = 25 - curr_val
            if uplift > 0:
                levers.append({"lever":"估值", "action":f"PE從{pe:.1f}x→10x",
                              "pts_gain": round(uplift,1), "trigger":"盈利大幅成長",
                              "feasibility":"HARD"})

    # 2. Dividend yield lever
    if dy:
        if dy < 4.5:
            bonus_gain = 1
            levers.append({"lever":"殖利率", "action":f"殖利率從{dy:.2f}%→4.5%+",
                          "pts_gain": bonus_gain, "trigger":"配息增加或股價下跌",
                          "feasibility":"MEDIUM"})
        elif dy < 6.0:
            levers.append({"lever":"殖利率", "action":f"殖利率從{dy:.2f}%→6%+",
                          "pts_gain": 1, "trigger":"配息大幅提升",
                          "feasibility":"HARD"})

    # 3. DNA / Technical lever
    missing_signals = 6 - bull_signs
    if missing_signals > 0 and missing_signals <= 3:
        missing_list = []
        for k, label in [("s1_ok","S1月DMI"),("s2_ok","S2月RSI4"),
                         ("s3_ok","S3日W%R"),("s4_ok","S4日RSI60"),
                         ("s5_ok","S5週VR2"),("s6_ok","S6月VR2")]:
            if not dn.get(k, False):
                missing_list.append(label)
        pts_per_signal = round(25 / 6, 1)
        levers.append({"lever":"技術DNA", "action":f"缺{missing_list[:2]}觸發",
                      "pts_gain": round(min(missing_signals,2) * pts_per_signal, 1),
                      "trigger":"價格動能加強", "feasibility":"SHORT"})

    # 4. Momentum lever (price vs MA)
    if pct_ma is not None and pct_ma < 5:
        gap = 5 - pct_ma
        levers.append({"lever":"動能", "action":f"股價站上月均線5%以上 (現{pct_ma:+.1f}%)",
                      "pts_gain": round(min(5, gap * 0.8), 1),
                      "trigger":"股價回升", "feasibility":"SHORT"})

    # 5. Revenue / Fundamental lever
    apr_yoy = sf(ar.get("april_yoy"))
    apr_accel = ar.get("accel","")
    if apr_accel == "DECELERATING":
        levers.append({"lever":"基本面", "action":"若5月營收恢復成長 (4月減速中)",
                      "pts_gain": 2.0, "trigger":"5月10日營收公布",
                      "feasibility":"NEAR"})
    elif fund_pts < 18:
        room = 25 - fund_pts
        levers.append({"lever":"基本面", "action":f"基本面分提升 (現{fund_pts:.0f}→目標{min(25,fund_pts+5):.0f})",
                      "pts_gain": min(5.0, round(room*0.2,1)),
                      "trigger":"Q2財報(8月)或5月營收", "feasibility":"MEDIUM"})

    # Sort by pts_gain descending, take top 3
    levers.sort(key=lambda x: -x["pts_gain"])
    top_levers = levers[:3]

    # Max theoretical upgrade (sum of top 2 levers)
    max_gain = sum(l["pts_gain"] for l in top_levers[:2])

    # Compute "to TRIPLE" scenario if not already there
    triple_gap = max(0, 70 - grand_score) if bull_signs >= 3 else None
    if bull_signs < 3:
        dna_gap = 3 - bull_signs
    else:
        dna_gap = 0

    entry = {
        "code": code, "name": name,
        "current": {
            "grand": round(grand_score, 1), "tier": current_tier,
            "fund": round(fund_pts, 1), "tech": round(tech_pts, 1),
            "val":  round(val_pts, 1),  "mom":  round(mom_pts, 1),
            "bull_signs": bull_signs, "pe": round(pe, 1) if pe else None, "div_yield": dy,
        },
        "next_tier": next_tier,
        "pts_to_next": round(pts_needed, 1),
        "tier_desc": tier_desc,
        "triple_gap": round(triple_gap, 1) if triple_gap is not None else None,
        "dna_gap_to3": dna_gap,
        "max_gain_2levers": round(max_gain, 1),
        "upgradeable_soon": max_gain >= pts_needed and pts_needed > 0,
        "levers": top_levers,
    }
    results.append(entry)

# Sort: closest to upgrade first (smallest pts_to_next, smallest gap)
results.sort(key=lambda x: (x["pts_to_next"] if x["pts_to_next"] > 0 else 999,
                             -(x["current"]["grand"])))

# Segment
near_upgrade  = [r for r in results if 0 < r["pts_to_next"] <= 5 and r["upgradeable_soon"]]
in_range      = [r for r in results if 0 < r["pts_to_next"] <= 10]
already_top   = [r for r in results if r["current"]["tier"] == "🚀 TRIPLE CONFIRMED"]

# ── Print summary ─────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"  SCORE SENSITIVITY — {len(results)} stocks")
print(f"{'='*65}")
print(f"\n  🔥 Near-upgrade (≤5pts, achievable): {len(near_upgrade)} stocks")
for r in near_upgrade[:10]:
    levers_str = " | ".join(f"{l['lever']}+{l['pts_gain']}" for l in r["levers"][:2])
    print(f"  {r['code']:6} {r['name'].split(' ')[0]:10}  grand={r['current']['grand']:.1f}"
          f"  →{r['next_tier']}  gap={r['pts_to_next']:.1f}  [{levers_str}]")

print(f"\n  📊 In-range upgrades (≤10pts): {len(in_range)} stocks")
for r in in_range[:15]:
    print(f"  {r['code']:6} {r['name'].split(' ')[0]:10}  grand={r['current']['grand']:.1f}"
          f"  gap={r['pts_to_next']:.1f}  top lever: {r['levers'][0]['lever'] if r['levers'] else '—'} "
          f"+{r['levers'][0]['pts_gain'] if r['levers'] else 0}pts")

out = {
    "date":        TODAY,
    "generated":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":       len(results),
    "near_upgrade_count": len(near_upgrade),
    "in_range_count":     len(in_range),
    "all_stocks":  results,
    "near_upgrade": near_upgrade,
    "in_range":     in_range,
    "already_triple": already_top,
}
(REPORT_DIR / "score_sensitivity.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ score_sensitivity.json saved ({len(results)} stocks)")

