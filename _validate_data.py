#!/usr/bin/env python3
"""
Quick data validation: checks coverage and key metrics across all JSON files.
Run anytime to verify report dir is consistent. No API calls, no side effects.
"""
import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
rd = _dirs[0]
print(f"[{datetime.now():%H:%M:%S}] Validating: {rd}")

def chk(path):
    p = rd / path
    if not p.exists(): return None, f"❌ MISSING"
    size = p.stat().st_size / 1024
    return json.loads(p.read_text(encoding="utf-8")), f"✅ {size:.0f}KB"

fm,   s = chk("full_market.json");       print(f"  full_market.json       {s}")
qf,   s = chk("quarterly_financials.json"); print(f"  quarterly_financials.json {s}")
gu,   s = chk("grand_unified.json");     print(f"  grand_unified.json     {s}")
oa,   s = chk("otc_analysis.json");      print(f"  otc_analysis.json      {s}")
pm,   s = chk("price_momentum.json");    print(f"  price_momentum.json    {s}")
bw,   s = chk("bwibbu_fresh.json");      print(f"  bwibbu_fresh.json      {s}")

if fm:
    cos = fm["companies"]
    otc = [c for c in cos if c.get("market") == "OTC"]
    tse = [c for c in cos if c.get("market") != "OTC"]
    print(f"\n  Full Market: {len(cos)} total | TSE={len(tse)} OTC={len(otc)}")
    # full_market fields (actual names used by the pipeline)
    fields = [("pe","pe"), ("pb","pb"), ("yield","yield"), ("rev_yoy","rev_yoy"), ("rev_now","rev_now"), ("sector","sector")]
    for fname, key in fields:
        tse_c = sum(1 for c in tse if c.get(key) is not None)
        otc_c = sum(1 for c in otc if c.get(key) is not None)
        print(f"    {fname:<16} TSE:{tse_c:>5}/{len(tse)}  OTC:{otc_c:>4}/{len(otc)}")
    score_dist = {}
    for c in cos:
        s2 = c.get("quick_score",0)
        score_dist[s2] = score_dist.get(s2,0) + 1
    print(f"\n  Score distribution: {dict(sorted(score_dist.items()))}")
    top_pe = sorted([c for c in cos if c.get("pe") and c["pe"] > 0], key=lambda x: x["pe"])[:3]
    print(f"  Lowest PE: {[(c['code'], round(c['pe'],1)) for c in top_pe]}")

if qf:
    cos2 = qf["companies"]
    otc2 = [c for c in cos2 if c.get("market") == "OTC"]
    print(f"\n  Quarterly: {len(cos2)} total | OTC={len(otc2)}")
    with_eps = sum(1 for c in cos2 if c.get("eps") is not None)
    pos_eps  = sum(1 for c in cos2 if (c.get("eps") or 0) > 0)
    print(f"    with EPS: {with_eps} | profitable: {pos_eps}")

if gu:
    ranked = gu.get("all_ranked",[])
    triple = [r for r in ranked if "TRIPLE" in r.get("final","")]
    sbuy   = [r for r in ranked if r.get("final","") == "✅ STRONG BUY"]
    print(f"\n  Grand Unified: {len(ranked)} ranked | 🚀 TRIPLE={len(triple)} | STRONG_BUY={len(sbuy)}")
    print(f"  Data date: {gu.get('date') or gu.get('data_date','?')}")

if oa:
    ov = oa.get("overall",{})
    print(f"\n  OTC Analysis: {ov.get('total','?')} companies | profitable={ov.get('profitable','?')}")
    print(f"  Median EPS={ov.get('median_eps','?')} | Median GrossMargin={ov.get('median_gross_margin','?')}%")

if pm:
    print(f"\n  Price Momentum: data_date={pm.get('data_date','?')} | tracked={pm.get('total_tracked','?')}")
    print(f"  Signals: {pm.get('signal_counts',{})}")

print(f"\n[{datetime.now():%H:%M:%S}] Done")
