#!/usr/bin/env python3
"""
Iteration 41: ETF Comparison Analysis
Compares 0050 / 0056 / 006208 / 00713 / 00878 across:
- Weighted grand score, DNA, valuation, momentum, RS
- Dividend yield, PE, sector breakdown
- TRIPLE/STRONG BUY exposure
- DNA signal alignment per ETF
No API calls. Generates: etf_comparison.json
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

etfc    = json.loads((REPORT_DIR / "etf_concentration.json").read_text(encoding="utf-8"))
grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
mayp    = json.loads((REPORT_DIR / "may_preview.json").read_text(encoding="utf-8"))
sector  = json.loads((REPORT_DIR / "sector_analysis.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp     = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map   = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed", [])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum", [])}
rs_map    = {r["code"]: r for r in rs.get("all_rs", [])}
mayp_map  = {r["code"]: r for r in mayp.get("all_previews", [])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def get_sector(code):
    for sec in sector.get("sectors", []):
        if any(s["code"] == code for s in sec.get("stocks", [])):
            return sec["sector"]
    return "其他"

# ── Build ETF membership maps ─────────────────────────────────────────────────
# From blended_top20 we know which ETFs contain each stock
etf_members = defaultdict(set)
blended = etfc.get("blended_top20", [])
for r in blended:
    code = r["code"]
    for e in r.get("etfs", []):
        etf_members[e].add(code)

# From expansion stocks and composite, also tag ETFs
for s in comp:
    if s.get("etf_0050") or s.get("source") == "0050":
        etf_members["0050"].add(s["code"])
for s in exp:
    src = s.get("source","")
    for etf_code in ["0056","00878","00713","006208"]:
        if etf_code in src:
            etf_members[etf_code].add(s["code"])

# Add all composite stocks to 0050
for s in comp:
    etf_members["0050"].add(s["code"])

# 0050 exact weights
w_0050 = etfc.get("weights_0050", {})

# For other ETFs, use equal weights
def get_weights(etf_code, members):
    if etf_code == "0050" and w_0050:
        # Use known weights, normalize to 100
        wts = {c: sf(w_0050.get(c, 0)) or 0 for c in members}
        total = sum(wts.values()) or 1
        return {c: w/total*100 for c,w in wts.items()}
    else:
        n = len(members)
        return {c: 100/n for c in members} if n > 0 else {}

ETF_NAMES = {
    "0050":   "元大台灣50",
    "0056":   "元大高股息",
    "006208": "富邦台50",
    "00713":  "元大台灣高息低波",
    "00878":  "國泰永續高股息",
}
ETF_THEMES = {
    "0050":   "大市值市值加權",
    "0056":   "高殖利率篩選",
    "006208": "台灣50追蹤",
    "00713":  "高息低波因子",
    "00878":  "ESG永續高股息",
}

# ── Per-ETF analysis ──────────────────────────────────────────────────────────
etf_results = []

for etf_code in ["0050", "0056", "006208", "00713", "00878"]:
    members = sorted(etf_members.get(etf_code, set()))
    if not members:
        print(f"  {etf_code}: no member data")
        continue

    weights = get_weights(etf_code, members)
    total_w = sum(weights.values())

    # Weighted aggregates
    grand_vals, pe_vals, dy_vals, bs_vals, rs60_vals = [], [], [], [], []
    mom_pos = mom_neg = 0
    triple_ct = strong_ct = buy_ct = 0
    beat_ct   = 0
    sector_ct = defaultdict(float)
    top_holdings = []

    for code in members:
        w  = weights.get(code, 0) / total_w  # normalized fraction
        g  = grand_map.get(code, {})
        dn = dna_map.get(code, {})
        bw = bwi_map.get(code, {})
        mm = mom_map.get(code, {})
        rv = rs_map.get(code, {})
        mp = mayp_map.get(code, {})

        grand_score = g.get("grand") or 0
        bull_signs  = dn.get("bull_signs") or 0
        pe          = sf(bw.get("pe_new") or bw.get("pe_old"))
        dy          = sf(bw.get("div_new") or bw.get("div_yield")) or 0
        rs60        = rv.get("rs_60d")
        pct_ma      = sf(mm.get("pct_vs_ma")) or 0
        final       = g.get("final","")
        rev_score   = mp.get("rev_score") or 0

        grand_vals.append(grand_score * w)
        bs_vals.append(bull_signs * w)
        if pe and 0 < pe < 200: pe_vals.append(pe * w)
        if dy and 0 < dy < 20:  dy_vals.append(dy * w)
        if rs60 is not None:    rs60_vals.append(rs60 * w)
        if pct_ma > 0:          mom_pos += w
        else:                   mom_neg += w
        if "TRIPLE" in final:   triple_ct += 1
        elif "STRONG" in final: strong_ct += 1
        elif "BUY" in final:    buy_ct += 1
        if rev_score >= 3:      beat_ct += 1

        sec = get_sector(code)
        sector_ct[sec] += w * 100

        top_holdings.append({
            "code": code, "name": name_map.get(code, code),
            "weight_pct": round(weights.get(code,0), 2),
            "grand": round(grand_score, 1), "final": final,
            "bull_signs": bull_signs, "pe": pe, "div_yield": dy,
            "rs_60d": rv.get("rs_60d"),
        })

    top_holdings.sort(key=lambda x: -x["weight_pct"])

    # Sector breakdown (top 3)
    top_sectors = sorted(sector_ct.items(), key=lambda x:-x[1])[:4]

    # ETF-level score
    avg_grand  = round(sum(grand_vals), 1)
    avg_dna    = round(sum(bs_vals), 2)
    wt_pe      = round(sum(pe_vals), 1)  if pe_vals    else None
    wt_dy      = round(sum(dy_vals), 2)  if dy_vals    else None
    avg_rs60   = round(sum(rs60_vals),1) if rs60_vals  else None
    pct_above_ma = round(mom_pos * 100, 1)

    # ETF rating
    if   avg_grand >= 60 and avg_dna >= 3:  rating = "🔥 強力推薦"
    elif avg_grand >= 55 and avg_dna >= 2.5: rating = "📈 積極看多"
    elif avg_grand >= 50:                    rating = "⬛ 中性偏多"
    else:                                    rating = "📉 偏空謹慎"

    result = {
        "etf_code": etf_code,
        "etf_name": ETF_NAMES.get(etf_code, etf_code),
        "theme":    ETF_THEMES.get(etf_code, ""),
        "n_holdings": len(members),
        "avg_grand":  avg_grand,
        "avg_dna_signals": avg_dna,
        "wt_pe":    wt_pe, "wt_div_yield": wt_dy,
        "avg_rs_60d": avg_rs60,
        "pct_above_ma": pct_above_ma,
        "triple_holdings":  triple_ct,
        "strongbuy_holdings": strong_ct,
        "buy_holdings":       buy_ct,
        "beat_revenue_ct":    beat_ct,
        "rating": rating,
        "top_sectors": [{"sector": s, "pct": round(p,1)} for s,p in top_sectors],
        "top_holdings": top_holdings[:10],
        "all_holdings": top_holdings,
    }
    etf_results.append(result)

etf_results.sort(key=lambda x: -x["avg_grand"])

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'ETF':<8} {'名稱':<12} {'n':>4} {'Grand':>7} {'DNA':>5} {'PE':>6} {'殖利率':>7} {'RS60':>7} {'MA%':>6}  Rating")
print("-"*85)
for e in etf_results:
    pe  = f"{e['wt_pe']:.1f}x"  if e['wt_pe']  else "—"
    dy  = f"{e['wt_div_yield']:.2f}%" if e['wt_div_yield'] else "—"
    rs  = f"{e['avg_rs_60d']:+.1f}%" if e['avg_rs_60d'] is not None else "—"
    print(f"  {e['etf_code']:<6} {e['etf_name']:<12} {e['n_holdings']:>4} "
          f"{e['avg_grand']:>7.1f} {e['avg_dna_signals']:>5.1f} {pe:>6} {dy:>7} {rs:>7} "
          f"{e['pct_above_ma']:>5.1f}%  {e['rating']}")

print(f"\n  Best grand score: {etf_results[0]['etf_code']} ({etf_results[0]['avg_grand']})")
print(f"  Best yield:       {max(etf_results, key=lambda x: x['wt_div_yield'] or 0)['etf_code']}")
print(f"  Best DNA:         {max(etf_results, key=lambda x: x['avg_dna_signals'])['etf_code']}")

# TRIPLE CONFIRMED coverage
print(f"\n  TRIPLE CONFIRMED holdings per ETF:")
for e in etf_results:
    triple = [h for h in e["top_holdings"] if "TRIPLE" in h.get("final","")]
    codes = [h["code"] for h in e["all_holdings"] if "TRIPLE" in h.get("final","")]
    print(f"    {e['etf_code']}: {len(codes)} | {codes}")

out = {
    "date":     TODAY,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "etf_count": len(etf_results),
    "etfs":      etf_results,
    "best_grand":     etf_results[0]["etf_code"] if etf_results else None,
    "best_yield":     max(etf_results, key=lambda x: x["wt_div_yield"] or 0)["etf_code"] if etf_results else None,
    "best_dna":       max(etf_results, key=lambda x: x["avg_dna_signals"])["etf_code"] if etf_results else None,
}
(REPORT_DIR / "etf_comparison.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ etf_comparison.json saved ({len(etf_results)} ETFs)")

