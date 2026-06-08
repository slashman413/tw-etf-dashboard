#!/usr/bin/env python3
"""
Conviction Matrix: synthesize ALL analyses into final conviction rank.
Combines: Grand + Smart Money + Action Signal + MoS + Q2 EPS + DNA signals
No API calls. Generates: conviction_matrix.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
smc    = json.loads((REPORT_DIR / "smart_money_confluence.json").read_text(encoding="utf-8"))
act    = json.loads((REPORT_DIR / "action_signal.json").read_text(encoding="utf-8"))
mos    = json.loads((REPORT_DIR / "margin_of_safety.json").read_text(encoding="utf-8"))
q2f    = json.loads((REPORT_DIR / "q2_eps_forecast.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
inst   = json.loads((REPORT_DIR / "institutional_flows.json").read_text(encoding="utf-8"))
dnatrig= json.loads((REPORT_DIR / "dna_trigger_calc.json").read_text(encoding="utf-8"))
earq   = json.loads((REPORT_DIR / "earnings_quality.json").read_text(encoding="utf-8"))
comp   = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

grand_map  = {r["code"]: r for r in grand.get("all_ranked", [])}
smc_map    = {r["code"]: r for r in smc.get("all_results", [])}
act_map    = {r["code"]: r for r in act.get("all_signals", [])}
mos_map    = {r["code"]: r for r in mos.get("all_results", [])}
q2f_map    = {r["code"]: r for r in q2f.get("all_forecasts", [])}
dna_map    = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
inst_map   = {r["code"]: r for r in inst.get("universe_flows", [])}
trig_map   = {r["code"]: r for r in dnatrig.get("all_results", [])}
earq_map   = {r["code"]: r for r in earq.get("all_stocks", [])}
name_map   = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

codes = sorted(grand_map.keys())
results = []

for code in codes:
    g   = grand_map.get(code, {})
    sm  = smc_map.get(code, {})
    ac  = act_map.get(code, {})
    mo  = mos_map.get(code, {})
    q2  = q2f_map.get(code, {})
    dn  = dna_map.get(code, {})
    fl  = inst_map.get(code, {})
    tg  = trig_map.get(code, {})
    eq  = earq_map.get(code, {})
    name = name_map.get(code, code).split(" ")[0]

    grand_s   = sf(g.get("grand")) or 0
    final     = g.get("final", "") or ""
    confluence= sf(sm.get("confluence")) or 0
    act_score = sf(ac.get("action_score")) or 0
    mos_pct   = sf(mo.get("mos_pct"))
    q2_growth = sf(q2.get("q2_eps_growth_pct"))
    bull      = (dn.get("bull_signs") or 0)
    inst_net  = sf(fl.get("total_net")) or 0
    eq_score  = (eq.get("eq_score") or 0)
    eq_grade  = (eq.get("grade","") or "").split(" ")[0]
    difficulty= sf(tg.get("avg_difficulty"))

    # ── Factor 1: Grand Score (0–30 pts) ─────────────────────────────────────
    f1 = min(30, grand_s * 0.30)

    # ── Factor 2: Smart Money Confluence (0–20 pts) ───────────────────────────
    f2 = min(20, confluence * 0.20)

    # ── Factor 3: Action Signal (0–20 pts) ───────────────────────────────────
    f3 = min(20, act_score * 0.20)

    # ── Factor 4: Margin of Safety (0–15 pts) ────────────────────────────────
    # MoS ≥40% → 15; ≥25% → 12; ≥10% → 8; ≥0% → 4; <0% → 0
    if mos_pct is None:       f4 = 5  # unknown
    elif mos_pct >= 40:       f4 = 15
    elif mos_pct >= 25:       f4 = 12
    elif mos_pct >= 10:       f4 = 8
    elif mos_pct >= 0:        f4 = 4
    else:                     f4 = 0

    # ── Factor 5: Q2 EPS Momentum (0–10 pts) ─────────────────────────────────
    if q2_growth is None:     f5 = 3
    elif q2_growth > 80:      f5 = 10
    elif q2_growth > 40:      f5 = 8
    elif q2_growth > 15:      f5 = 6
    elif q2_growth > 0:       f5 = 4
    elif q2_growth > -20:     f5 = 2
    else:                     f5 = 0

    # ── Factor 6: DNA Signal Completeness (0–5 pts) ───────────────────────────
    f6 = round((bull / 6) * 5, 1)

    conviction = round(f1 + f2 + f3 + f4 + f5 + f6, 1)

    # ── Bonuses ───────────────────────────────────────────────────────────────
    bonus = 0
    bonus_reasons = []
    if "TRIPLE" in final:
        bonus += 5; bonus_reasons.append("TRIPLE+5")
    if inst_net > 2000:
        bonus += 3; bonus_reasons.append(f"外資大買+3")
    elif inst_net > 500:
        bonus += 1; bonus_reasons.append("法人買進+1")
    if eq_grade == "A+":
        bonus += 2; bonus_reasons.append("EQ=A++2")
    elif eq_grade == "A":
        bonus += 1; bonus_reasons.append("EQ=A+1")
    if difficulty is not None and difficulty <= 1.5 and bull >= 5:
        bonus += 2; bonus_reasons.append("近TRIPLE升評+2")

    final_score = min(100, round(conviction + bonus, 1))

    # ── Conviction label ──────────────────────────────────────────────────────
    if final_score >= 85:   label = "🔥 極高確信"
    elif final_score >= 72: label = "💎 高確信"
    elif final_score >= 58: label = "✅ 中高確信"
    elif final_score >= 44: label = "📊 中確信"
    elif final_score >= 30: label = "⚖ 低確信"
    else:                   label = "❌ 不確定"

    # Tier for position sizing guidance
    if final_score >= 85 and "TRIPLE" in final:
        tier = "TIER1-CORE"
        size_guide = "核心倉位 6-10%"
    elif final_score >= 72:
        tier = "TIER2-HIGH"
        size_guide = "主力倉位 4-6%"
    elif final_score >= 58:
        tier = "TIER3-MED"
        size_guide = "標準倉位 2-4%"
    elif final_score >= 44:
        tier = "TIER4-LOW"
        size_guide = "輕倉觀察 1-2%"
    else:
        tier = "TIER5-WATCH"
        size_guide = "等待觀望 0-1%"

    results.append({
        "code":          code,
        "name":          name,
        "final_score":   final_score,
        "conviction":    conviction,
        "bonus":         round(bonus, 1),
        "bonus_reasons": bonus_reasons,
        "label":         label,
        "tier":          tier,
        "size_guide":    size_guide,
        "grand":         round(grand_s, 1),
        "final":         final,
        "confluence":    round(confluence, 1),
        "action_score":  round(act_score, 1),
        "mos_pct":       round(mos_pct, 1) if mos_pct is not None else None,
        "q2_growth":     round(q2_growth, 1) if q2_growth is not None else None,
        "bull_signs":    bull,
        "eq_grade":      eq_grade,
        "inst_net":      inst_net,
        "factors": {
            "f1_grand":    round(f1, 1),
            "f2_smc":      round(f2, 1),
            "f3_action":   round(f3, 1),
            "f4_mos":      round(f4, 1),
            "f5_q2":       round(f5, 1),
            "f6_dna":      round(f6, 1),
        },
    })

results.sort(key=lambda x: -x["final_score"])

# Groups
tier1 = [r for r in results if r["tier"] == "TIER1-CORE"]
tier2 = [r for r in results if r["tier"] == "TIER2-HIGH"]
tier3 = [r for r in results if r["tier"] == "TIER3-MED"]
tier4 = [r for r in results if r["tier"] == "TIER4-LOW"]

scores = [r["final_score"] for r in results]
med_s  = round(statistics.median(scores), 1)

# Print
print(f"\n{'CONVICTION MATRIX — FINAL RANKING':=<65}")
print(f"  Universe: {len(results)} | Tier1 Core: {len(tier1)} | Tier2 High: {len(tier2)} | Tier3 Med: {len(tier3)}")
print(f"  Median conviction: {med_s}")

print(f"\n  🔥 TIER 1 — 核心倉位 (≥85 分):")
header = f"  {'代號':<6} {'名稱':<10} {'Score':>6} {'Grand':>6} {'Conf':>5} {'ActSig':>7} {'MoS%':>6} {'Q2%':>6} {'Tier'}"
print(header); print("-"*80)
for r in tier1 + tier2[:8]:
    mos = f"{r['mos_pct']:+.0f}%" if r['mos_pct'] is not None else "  —"
    q2  = f"{r['q2_growth']:+.0f}%" if r['q2_growth'] is not None else "  —"
    bonus_str = f" (+{r['bonus']})" if r['bonus'] else ""
    print(f"  {r['code']:<6} {r['name']:<10} {r['final_score']:>6.1f}{bonus_str:<5} "
          f"{r['grand']:>6.1f} {r['confluence']:>5.1f} {r['action_score']:>7.1f} "
          f"{mos:>6} {q2:>6}  {r['tier']}")
    if tier1 and r == tier1[-1] and tier2: print()

print(f"\n  Factor breakdown for TIER1 stocks:")
print(f"  {'代號':<6} {'名稱':<8} {'F1':>5} {'F2':>5} {'F3':>5} {'F4':>5} {'F5':>5} {'F6':>5} {'Bonus':>6} = {'Total':>6}")
for r in tier1 + tier2[:4]:
    f = r["factors"]
    print(f"  {r['code']:<6} {r['name']:<8} {f['f1_grand']:>5.1f} {f['f2_smc']:>5.1f} "
          f"{f['f3_action']:>5.1f} {f['f4_mos']:>5.1f} {f['f5_q2']:>5.1f} "
          f"{f['f6_dna']:>5.1f} {r['bonus']:>6.1f} = {r['final_score']:>6.1f}  {r['label']}")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "methodology": {
        "f1_grand":  "Grand score × 0.30 (max 30)",
        "f2_smc":    "Smart Money confluence × 0.20 (max 20)",
        "f3_action": "Action signal score × 0.20 (max 20)",
        "f4_mos":    "Margin of Safety tiers 0/4/8/12/15",
        "f5_q2":     "Q2 EPS growth tiers 0/2/4/6/8/10",
        "f6_dna":    "(DNA bull signs / 6) × 5 (max 5)",
        "bonuses":   "TRIPLE+5, 外資大買+3, EQ=A++2, 近升評+2",
    },
    "aggregate": {
        "total":      len(results),
        "tier1_core": len(tier1),
        "tier2_high": len(tier2),
        "tier3_med":  len(tier3),
        "tier4_low":  len(tier4),
        "median_score": med_s,
    },
    "all_results": results,
    "tier1": tier1,
    "tier2": tier2,
    "tier3": tier3,
    "tier4": tier4,
}
(REPORT_DIR / "conviction_matrix.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- conviction_matrix.json saved ({len(results)} stocks)")

