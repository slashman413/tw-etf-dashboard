#!/usr/bin/env python3
"""
Generate OTC market Q1 2026 analysis report.
Saves: reports/YYYY-MM-DD/otc_analysis.json
Uses only existing data from full_market.json — no API calls.
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
otc = [c for c in fm["companies"] if c.get("market") == "OTC"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === OTC Market Q1 2026 Analysis ===")
print(f"  OTC companies: {len(otc)}")

# Overall stats
eps_list  = [c["eps_q1"] for c in otc if c.get("eps_q1") is not None]
yoy_list  = [c["rev_yoy"] for c in otc if c.get("rev_yoy") is not None and abs(c["rev_yoy"]) < 500]
gm_list   = [c["gross_margin"] for c in otc if c.get("gross_margin") is not None]
om_list   = [c["op_margin"]    for c in otc if c.get("op_margin") is not None]
pe_list   = [c["pe"] for c in otc if c.get("pe") and 0 < c["pe"] < 200]

def median(lst):
    if not lst: return None
    s = sorted(lst)
    m = len(s)//2
    return (s[m-1]+s[m])/2 if len(s)%2==0 else s[m]

def avg(lst):
    return sum(lst)/len(lst) if lst else None

overall = {
    "total": len(otc),
    "profitable": sum(1 for c in otc if (c.get("eps_q1") or 0) > 0),
    "loss":       sum(1 for c in otc if (c.get("eps_q1") or 0) < 0),
    "median_eps": round(median(eps_list), 2) if eps_list else None,
    "avg_eps":    round(avg(eps_list), 2)    if eps_list else None,
    "median_rev_yoy": round(median(yoy_list), 1) if yoy_list else None,
    "pct_rev_growth": round(sum(1 for y in yoy_list if y > 0) / len(yoy_list) * 100, 1) if yoy_list else None,
    "median_gross_margin": round(median(gm_list), 1) if gm_list else None,
    "median_op_margin":    round(median(om_list), 1) if om_list else None,
    "median_pe":  round(median(pe_list), 1)  if pe_list else None,
}
print(f"\n  Overall OTC Q1 stats:")
for k, v in overall.items():
    print(f"    {k}: {v}")

# Sector breakdown
sector_map = defaultdict(list)
for c in otc:
    sec = c.get("sector") or "其他"
    sector_map[sec].append(c)

sectors_out = []
for sec, stocks in sorted(sector_map.items()):
    eps_s  = [s["eps_q1"] for s in stocks if s.get("eps_q1") is not None]
    yoy_s  = [s["rev_yoy"] for s in stocks if s.get("rev_yoy") is not None and abs(s["rev_yoy"]) < 500]
    gm_s   = [s["gross_margin"] for s in stocks if s.get("gross_margin") is not None]
    prof   = sum(1 for s in stocks if (s.get("eps_q1") or 0) > 0)

    # Top 3 by EPS in sector
    top3 = sorted([s for s in stocks if s.get("eps_q1") is not None],
                  key=lambda x: -(x["eps_q1"] or 0))[:3]

    sectors_out.append({
        "sector":        sec,
        "count":         len(stocks),
        "profitable":    prof,
        "median_eps":    round(median(eps_s), 2) if eps_s else None,
        "median_rev_yoy": round(median(yoy_s), 1) if yoy_s else None,
        "median_gm":     round(median(gm_s), 1)  if gm_s else None,
        "top_eps":       [{"code":s["code"],"name":s.get("name",""),"eps":s["eps_q1"]} for s in top3],
    })

# Top performers
top_eps = sorted([c for c in otc if c.get("eps_q1") is not None],
                 key=lambda x: -(x["eps_q1"] or 0))[:20]
top_gm  = sorted([c for c in otc if c.get("gross_margin") is not None and (c.get("rev_now") or 0) > 50000],
                 key=lambda x: -(x["gross_margin"] or 0))[:20]
top_yoy = sorted([c for c in otc if c.get("rev_yoy") is not None and 0 < c["rev_yoy"] < 500],
                 key=lambda x: -(x["rev_yoy"] or 0))[:20]

result = {
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "period":     "115Q1 (2026 Q1)",
    "data_source": "TPEX t187ap14_O + t187ap06_O_ci + t187ap05_O",
    "overall":    overall,
    "sectors":    sorted(sectors_out, key=lambda x: -(x.get("median_eps") or -999)),
    "top_eps":    [{"code":c["code"],"name":c.get("name",""),"eps":c["eps_q1"],
                    "gross_margin":c.get("gross_margin"),"sector":c.get("sector")} for c in top_eps],
    "top_gross_margin": [{"code":c["code"],"name":c.get("name",""),"gross_margin":c["gross_margin"],
                          "eps":c.get("eps_q1"),"sector":c.get("sector")} for c in top_gm],
    "top_rev_yoy": [{"code":c["code"],"name":c.get("name",""),"rev_yoy":c["rev_yoy"],
                     "eps":c.get("eps_q1"),"sector":c.get("sector")} for c in top_yoy],
}

(REPORT_DIR / "otc_analysis.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  Top 10 OTC by Q1 EPS:")
for c in top_eps[:10]:
    print(f"    {c['code']} {c.get('name','?')[:10]:<12} eps={c['eps_q1']:.2f} gm={c.get('gross_margin','—')}")

print(f"\n  Top 5 OTC sectors by median EPS:")
for s in sectors_out[:5]:
    print(f"    {s['sector']}: {s['count']}家, profit={s['profitable']}, med_eps={s['median_eps']}")

print(f"\n  ✅ Saved {REPORT_DIR}/otc_analysis.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
