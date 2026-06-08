#!/usr/bin/env python3
"""
Compute/update trailing 4Q EPS estimates for all 62 tracked stocks.
Sources (in priority):
  1. composite_data.json trail_eps (computed earlier from Yahoo Finance for 0050)
  2. grand_unified.json trail_eps (if available)
  3. Q1 2026 EPS × 4 annualized (rough estimate, flagged as such)
Saves: reports/YYYYMMDD/trail_eps_estimates.json
Updates: grand_unified.json with trail_eps field
"""
import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

grand = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
comp  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
bwi   = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
comp_map  = {c["code"]: c for c in comp}
bw_map    = {r["code"]: r for r in bwi.get("all_refreshed", [])}

print(f"[{datetime.now():%H:%M:%S}] === Trailing 4Q EPS Estimates ===")

results = []
for code, g in grand_map.items():
    cs = comp_map.get(code, {})
    bw = bw_map.get(code, {})

    # Priority 1: composite_data trail_eps (actual historical from Yahoo Finance)
    trail_actual = cs.get("trail_eps")

    # Priority 2: any existing trail_eps in grand_unified
    trail_grand = g.get("trail_eps")

    # Priority 3: Q1 × 4 annualized
    eps_q1 = g.get("eps_q1") or cs.get("q1_eps")
    trail_annualized = round(eps_q1 * 4, 2) if eps_q1 is not None else None

    # Choose best estimate
    if trail_actual and abs(trail_actual) < 9999:
        trail_eps = round(trail_actual, 2)
        source = "actual"
    elif trail_grand and abs(trail_grand) < 9999:
        trail_eps = round(trail_grand, 2)
        source = "grand"
    elif trail_annualized is not None:
        trail_eps = trail_annualized
        source = "annualized_4x"
    else:
        trail_eps = None
        source = "none"

    # Compute trailing P/E
    pe_live = bw.get("pe_new") or g.get("pe")
    trail_pe = None
    if trail_eps and trail_eps > 0 and pe_live and pe_live > 0:
        price = pe_live * (cs.get("fwd_eps") or eps_q1 or 1)  # rough
        # Use BWIBBU PE as proxy for current trailing PE
        trail_pe = round(pe_live, 1)  # BWIBBU already reflects trailing PE

    entry = {
        "code":       code,
        "name":       g.get("name", ""),
        "eps_q1":     eps_q1,
        "trail_eps":  trail_eps,
        "source":     source,
        "trail_pe":   trail_pe,
        "div_yield":  bw.get("div_new") or bw.get("div_yield"),
        "grand":      g.get("grand"),
        "final":      g.get("final", ""),
    }
    results.append(entry)

    # Update grand_unified with trail_eps if missing
    if g.get("trail_eps") is None and trail_eps is not None:
        g["trail_eps"] = trail_eps
        g["trail_eps_source"] = source

# Save
results.sort(key=lambda x: -(x.get("grand") or 0))
out = {
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total": len(results),
    "with_actual_trail": sum(1 for r in results if r["source"] == "actual"),
    "with_annualized":   sum(1 for r in results if r["source"] == "annualized_4x"),
    "stocks": results,
}
(REPORT_DIR / "trail_eps_estimates.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# Update grand_unified
grand["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "grand_unified.json").write_text(
    json.dumps(grand, ensure_ascii=False, indent=2), encoding="utf-8")

# Print summary
print(f"  Total stocks: {len(results)}")
print(f"  With actual trailing EPS: {out['with_actual_trail']}")
print(f"  With annualized estimate: {out['with_annualized']}")
print(f"\n  {'代號':<6} {'名稱':<10} {'Q1 EPS':>8} {'4Q Trail':>10} {'Source':<14} {'PE':>8} {'Grand':>7}")
print("  " + "─" * 68)
for r in results[:20]:
    q1  = f"{r['eps_q1']:.2f}" if r['eps_q1'] else "—"
    tr  = f"{r['trail_eps']:.2f}" if r['trail_eps'] else "—"
    pe  = f"{r['trail_pe']:.1f}x" if r['trail_pe'] else "—"
    gr  = f"{r['grand']:.1f}" if r['grand'] else "—"
    print(f"  {r['code']:<6} {r['name'][:8]:<10} {q1:>8} {tr:>10} {r['source']:<14} {pe:>8} {gr:>7}")

print(f"\n  ✅ Saved: {REPORT_DIR}/trail_eps_estimates.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
