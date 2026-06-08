#!/usr/bin/env python3
"""
Iteration 45: Sector Peer Comparison Analysis
Within each sector, ranks stocks on key metrics and identifies
relative value vs. sector median. No API calls.
Generates: peer_comparison.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi    = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom    = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs     = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
comp   = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
apr    = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
sector_d = json.loads((REPORT_DIR / "sector_analysis.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
comp_map  = {s["code"]: s for s in comp}
exp_map   = {s["code"]: s for s in expd}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def med(lst): return statistics.median(lst) if lst else None
def q1(lst):  return sorted(lst)[len(lst)//4] if lst else None
def q3(lst):  return sorted(lst)[3*len(lst)//4] if lst else None

# ── Build sector membership from sector_analysis ─────────────────────────────
code_sector = {}
for sec in sector_d.get("sectors",[]):
    for s in sec.get("stocks",[]):
        code_sector[s["code"]] = sec["sector"]

# Assign "其他" for any unmapped code
all_codes = set(comp_map.keys()) | set(exp_map.keys())
for code in all_codes:
    if code not in code_sector:
        code_sector[code] = "其他"

# ── Collect per-stock metrics ─────────────────────────────────────────────────
stock_metrics = {}
for code in all_codes:
    g  = grand_map.get(code, {})
    dn = dna_map.get(code, {})
    bw = bwi_map.get(code, {})
    mm = mom_map.get(code, {})
    rv = rs_map.get(code, {})
    cs = comp_map.get(code, exp_map.get(code, {}))
    ar = apr_map.get(code, {})

    pe      = sf(bw.get("pe_new") or bw.get("pe_old"))  or sf(cs.get("fwd_pe"))
    pb      = sf(bw.get("pb_new"))  or sf(cs.get("pb"))
    dy      = sf(bw.get("div_new") or bw.get("div_yield")) or sf(cs.get("div_yield"))
    grand_s = g.get("grand") or 0
    bs      = dn.get("bull_signs", 0) or 0
    rev_yoy = sf(ar.get("april_yoy")) or sf(cs.get("rev_yoy"))
    eps_accel= sf(cs.get("eps_accel"))
    op_margin= sf(cs.get("op_margin"))
    rs60    = rv.get("rs_60d")
    pct_ma  = sf(mm.get("pct_vs_ma"))
    final   = g.get("final","—")
    name    = cs.get("name", code)

    stock_metrics[code] = {
        "code": code, "name": name, "sector": code_sector.get(code,"其他"),
        "pe": pe, "pb": pb, "div_yield": dy,
        "grand": grand_s, "bull_signs": bs, "final": final,
        "rev_yoy": rev_yoy, "eps_accel": eps_accel,
        "op_margin": op_margin, "rs_60d": rs60, "pct_vs_ma": pct_ma,
        "fund_pts": g.get("fund_pts") or g.get("g_pts") or 0,
        "tech_pts": g.get("tech_pts", 0) or 0,
        "val_pts":  g.get("val_pts",  0) or 0,
        "mom_pts":  g.get("mom_pts",  0) or 0,
    }

# ── Per-sector analysis ───────────────────────────────────────────────────────
sectors_out = []
sector_groups = defaultdict(list)
for code, m in stock_metrics.items():
    sector_groups[m["sector"]].append(m)

for sector_name, members in sorted(sector_groups.items()):
    if len(members) < 2:
        continue  # skip singletons

    # Collect valid metric lists
    pes   = [m["pe"]        for m in members if m["pe"] and 0 < m["pe"] < 200]
    dys   = [m["div_yield"] for m in members if m["div_yield"] and 0 < m["div_yield"] < 30]
    grands= [m["grand"]     for m in members if m["grand"]]
    yoys  = [m["rev_yoy"]   for m in members if m["rev_yoy"] is not None]
    rs60s = [m["rs_60d"]    for m in members if m["rs_60d"] is not None]
    ops   = [m["op_margin"] for m in members if m["op_margin"] is not None]

    med_pe  = med(pes)
    med_dy  = med(dys)
    med_gd  = med(grands)
    med_yoy = med(yoys)
    med_rs  = med(rs60s)
    med_op  = med(ops)

    # Per-stock relative metrics
    enriched = []
    for m in members:
        pe_rel  = ((m["pe"] / med_pe - 1) * 100)  if (m["pe"] and med_pe) else None
        dy_rel  = (m["div_yield"] - med_dy)         if (m["div_yield"] is not None and med_dy) else None
        rs_rel  = (m["rs_60d"] - med_rs)            if (m["rs_60d"] is not None and med_rs) else None

        # Peer rank score: lower PE → better; higher yield → better; higher grand → better
        rank_score = (
            (100 - (m["pe"] / med_pe * 50) if (m["pe"] and med_pe) else 50) +
            ((m["div_yield"] / med_dy * 20) if (m["div_yield"] and med_dy) else 10) +
            (m["grand"] / max(grands) * 30 if (m["grand"] and grands) else 15)
        )

        # Cheap vs expensive vs peers
        if pe_rel is not None:
            if pe_rel < -20:   pe_status = "深度折價"
            elif pe_rel < -10: pe_status = "折價"
            elif pe_rel > 20:  pe_status = "溢價"
            elif pe_rel > 10:  pe_status = "小溢價"
            else:              pe_status = "合理"
        else:
            pe_status = "—"

        enriched.append({**m,
            "pe_vs_sector": round(pe_rel, 1) if pe_rel is not None else None,
            "pe_status":    pe_status,
            "dy_vs_sector": round(dy_rel, 2) if dy_rel is not None else None,
            "rs_vs_sector": round(rs_rel, 1) if rs_rel is not None else None,
            "peer_rank_score": round(rank_score, 1),
        })

    enriched.sort(key=lambda x: -x["peer_rank_score"])

    # Best/worst in class
    best_value  = min([m for m in enriched if m["pe"]], key=lambda x: x["pe"], default=None) if pes else None
    best_grand  = max(enriched, key=lambda x: x["grand"]) if enriched else None
    best_yield  = max([m for m in enriched if m["div_yield"]], key=lambda x: x["div_yield"], default=None) if dys else None
    best_growth = max([m for m in enriched if m["rev_yoy"] is not None], key=lambda x: x["rev_yoy"], default=None) if yoys else None

    sectors_out.append({
        "sector":     sector_name,
        "n_stocks":   len(members),
        "medians":    {
            "pe": round(med_pe, 1) if med_pe else None,
            "div_yield": round(med_dy, 2) if med_dy else None,
            "grand": round(med_gd, 1) if med_gd else None,
            "rev_yoy": round(med_yoy, 1) if med_yoy else None,
            "rs_60d": round(med_rs, 1) if med_rs else None,
            "op_margin": round(med_op, 1) if med_op else None,
        },
        "best_value":  {"code":best_value["code"],  "name":best_value["name"].split(" ")[0],  "pe":best_value["pe"]}  if best_value  else None,
        "best_grand":  {"code":best_grand["code"],  "name":best_grand["name"].split(" ")[0],  "grand":best_grand["grand"]} if best_grand  else None,
        "best_yield":  {"code":best_yield["code"],  "name":best_yield["name"].split(" ")[0],  "dy":best_yield["div_yield"]}  if best_yield  else None,
        "best_growth": {"code":best_growth["code"], "name":best_growth["name"].split(" ")[0], "yoy":best_growth["rev_yoy"]} if best_growth else None,
        "stocks":      enriched,
    })

sectors_out.sort(key=lambda x: -(x["medians"].get("grand") or 0))

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'SECTOR PEER COMPARISON':=<65}")
print(f"{'產業':<14} {'n':>3} {'中位PE':>8} {'中位殖':>8} {'中位Grand':>10} {'最佳價值':<10} {'最佳評級':<10}")
print("-"*65)
for sec in sectors_out:
    m = sec["medians"]
    bv = sec["best_value"]["code"] if sec["best_value"] else "—"
    bg = sec["best_grand"]["code"] if sec["best_grand"] else "—"
    print(f"  {sec['sector']:<12} {sec['n_stocks']:>3} "
          f"{(str(round(m['pe'],1))+'x') if m['pe'] else '—':>8} "
          f"{(str(round(m['div_yield'],2))+'%') if m['div_yield'] else '—':>8} "
          f"{m['grand'] or '—':>10} "
          f"{bv:<10} {bg:<10}")

print(f"\n  Best-in-class highlights:")
for sec in sectors_out[:6]:
    bv = sec["best_value"]
    bg = sec["best_grand"]
    if bv and bg:
        print(f"  {sec['sector']}: 最低PE={bv['code']}({bv['pe']:.1f}x)  "
              f"最高Grand={bg['code']}({bg['grand']:.1f})")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "n_sectors":  len(sectors_out),
    "sectors":    sectors_out,
}
(REPORT_DIR / "peer_comparison.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ peer_comparison.json saved ({len(sectors_out)} sectors)")

