#!/usr/bin/env python3
"""
Iteration 28: Grand Unified Ranking
Combines ALL analysis streams into one master score per stock:
  - Fundamental composite score (0–100)
  - Conviction score (0–100)
  - DNA technical signals (bull_signs 0–6, core_met 0–3)
  - Fresh BWIBBU valuation (P/E, div yield)
  - Price momentum vs baseline
  - 30d MA position
Generates: grand_unified.json
"""

import json
from pathlib import Path
from datetime import datetime

# Auto-detect latest report directory
_reports = sorted([d for d in (Path("reports")).iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)
TODAY      = _reports[0].name if _reports else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
print(f"[grand_unified] Using report dir: {REPORT_DIR}")

composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
conviction = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))
dna        = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwibbu     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
momentum   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
ma_data    = json.loads((REPORT_DIR / "ma_refresh.json").read_text(encoding="utf-8"))
ptargets   = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
# Prefer May revenue when available; fall back to April
_may_rev_path = REPORT_DIR / "may_revenue.json"
if _may_rev_path.exists():
    _may_rev = json.loads(_may_rev_path.read_text(encoding="utf-8"))
    if _may_rev.get("updates"):
        aprdata = {"all_results": _may_rev["updates"], "_source": "may_revenue"}
        print(f"  Using May revenue ({_may_rev.get('period','?')}) for scoring")
    else:
        aprdata = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
else:
    aprdata = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))

# Build lookup maps
name_map   = {**{s["code"]: s["name"] for s in composite},
              **{s["code"]: s["name"] for s in expansion}}
fund_map   = {s["code"]: s for s in composite}
exp_map    = {s["code"]: s for s in expansion}
conv_map   = {r["code"]: r for r in conviction.get("all_ranked", [])}
dna_map    = {s["code"]: s for s in dna.get("all_signals", dna.get("signals", [])) if "code" in s}
bwi_map    = {r["code"]: r for r in bwibbu.get("all_refreshed", [])}
mom_map    = {m["code"]: m for m in momentum.get("all_momentum", [])}
ma_map     = {r["code"]: r for r in ma_data.get("all_results", [])}
pt_map     = {r["code"]: r for r in ptargets.get("all_targets", [])}
apr_map    = {r["code"]: r for r in (aprdata.get("all_results") or aprdata.get("stocks", []))}

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v is not None else None
    except: return None

results = []

for code, name in sorted(name_map.items()):
    f   = fund_map.get(code, {})
    cr  = conv_map.get(code, {})
    dn  = dna_map.get(code, {})
    bw  = bwi_map.get(code, {})
    mo  = mom_map.get(code, {})
    mar = ma_map.get(code, {})
    pt  = pt_map.get(code, {})
    apr = apr_map.get(code, {})

    # ── Raw scores ───────────────────────────────────────────────────────────
    ex  = exp_map.get(code, {})
    fund_score  = sf(f.get("score"))          # 0–100 composite
    conv_score  = sf(cr.get("conviction"))    # 0–100 conviction
    bull_signs  = sf(dn.get("bull_signs"))    # 0–6 DNA
    core_met    = sf(dn.get("core_met"))      # 0–3 DNA core
    pct_ma      = sf(mar.get("pct_vs_ma"))    # % vs 30d MA
    pct_prior   = sf(mo.get("pct_vs_prior"))  # % change since baseline
    pe          = sf(bw.get("pe_new")) or sf(bw.get("pe_old")) or sf(ex.get("pe"))
    div_yield   = sf(bw.get("div_new") or bw.get("div_yield")) or sf(ex.get("div"))
    upside      = sf(pt.get("upside_pct"))
    apr_yoy     = sf(apr.get("cum_yoy") or apr.get("april_yoy") or apr.get("yoy_pct"))

    # ── Normalize to 0–25 points each ────────────────────────────────────────

    # 1) Fundamental (0–25): direct from composite score
    fund_pts = (fund_score / 100 * 25) if fund_score is not None else 12.5

    # 2) Technical DNA (0–25): bull_signs/6 * 15 + core_met/3 * 10
    if bull_signs is not None and core_met is not None:
        tech_pts = (bull_signs / 6 * 15) + (core_met / 3 * 10)
    else:
        tech_pts = 0

    # 3) Valuation (0–25): PE < 15 = 25pts, PE 15–25 = 20, PE 25–40 = 12, PE > 40 = 5
    # Bonus for high div yield
    if pe is not None and pe > 0:
        if pe < 10:   val_pts = 25
        elif pe < 15: val_pts = 22
        elif pe < 20: val_pts = 18
        elif pe < 30: val_pts = 12
        elif pe < 50: val_pts = 6
        else:         val_pts = 2
    else:
        val_pts = 10  # unknown

    if div_yield is not None and div_yield >= 4.5: val_pts = min(25, val_pts + 3)
    if div_yield is not None and div_yield >= 6.0: val_pts = min(25, val_pts + 2)

    # 4) Momentum (0–25): MA position + price change + upside
    mom_pts = 12.5  # neutral base
    if pct_ma is not None:
        mom_pts += min(8, max(-8, pct_ma * 0.5))   # ±8 pts from MA
    if pct_prior is not None:
        mom_pts += min(5, max(-5, pct_prior * 0.3)) # ±5 pts from momentum
    if upside is not None and upside > 0:
        mom_pts += min(5, upside / 30)              # up to +5 pts for upside
    mom_pts = max(0, min(25, mom_pts))

    # ── Grand score ──────────────────────────────────────────────────────────
    grand = round(fund_pts + tech_pts + val_pts + mom_pts, 1)

    # ── Action ───────────────────────────────────────────────────────────────
    action = cr.get("action", "WATCH")
    dna_verdict = dn.get("verdict", "—")

    # Final verdict
    if grand >= 70 and bull_signs is not None and bull_signs >= 3:
        final = "🚀 TRIPLE CONFIRMED"
    elif grand >= 65:
        final = "✅ STRONG BUY"
    elif grand >= 55:
        final = "📈 BUY"
    elif grand >= 40:
        final = "👀 WATCH"
    elif grand >= 25:
        final = "⬛ HOLD"
    else:
        final = "❌ REDUCE"

    results.append({
        "code":       code,
        "name":       name,
        "grand":      grand,
        "fund_pts":   round(fund_pts, 1),
        "tech_pts":   round(tech_pts, 1),
        "val_pts":    round(val_pts, 1),
        "mom_pts":    round(mom_pts, 1),
        "fund_score": fund_score,
        "conv_score": conv_score,
        "bull_signs": int(bull_signs) if bull_signs is not None else None,
        "core_met":   int(core_met)   if core_met   is not None else None,
        "pe":         pe,
        "div_yield":  div_yield,
        "pct_ma":     pct_ma,
        "pct_prior":  pct_prior,
        "upside":     upside,
        "apr_yoy":    apr_yoy,
        "action":     action,
        "dna_verdict":dna_verdict,
        "final":      final,
    })

results.sort(key=lambda x: -x["grand"])

# Print top results
print("=== Grand Unified Ranking ===")
print(f"{'Code':<6} {'Name':<12} {'Grand':>6} {'Fund':>5} {'Tech':>5} {'Val':>5} {'Mom':>5} {'Final'}")
print("-" * 75)
for r in results[:20]:
    print(f"{r['code']:<6} {r['name'][:10]:<12} {r['grand']:>6.1f} "
          f"{r['fund_pts']:>5.1f} {r['tech_pts']:>5.1f} {r['val_pts']:>5.1f} {r['mom_pts']:>5.1f}  "
          f"{r['final']}")

triple = [r for r in results if "TRIPLE" in r["final"]]
strong = [r for r in results if r["final"] == "✅ STRONG BUY"]
buy    = [r for r in results if r["final"] == "📈 BUY"]
print(f"\nTriple Confirmed: {len(triple)} | STRONG BUY: {len(strong)} | BUY: {len(buy)}")

# Save
out = {
    "date":          TODAY,
    "data_date":     momentum.get("data_date"),
    "fetch_ts":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":         len(results),
    "triple_confirmed": triple,
    "strong_buy":    strong,
    "buy":           buy,
    "all_ranked":    results,
}
(REPORT_DIR / "grand_unified.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ grand_unified.json written")
