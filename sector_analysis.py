#!/usr/bin/env python3
"""
Iteration 35: Sector Heatmap Analysis
Groups 62 stocks by sector, aggregates DNA/fundamental/momentum signals.
No API calls — pure computation on existing JSON data.
Generates: sector_analysis.json
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

# ── Load data ─────────────────────────────────────────────────────────────────
comp  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
grand = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna   = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
mom   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs    = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
bwi   = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map   = {s["code"]: s for s in dna.get("all_signals", dna.get("signals", [])) if "code" in s}
mom_map   = {m["code"]: m for m in mom.get("all_momentum", [])}
rs_map    = {r["code"]: r for r in rs.get("all_rs", [])}
bwi_map   = {r.get("code","").strip(): r for r in bwi.get("all_refreshed", []) if r.get("code")}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Build sector mapping ──────────────────────────────────────────────────────
# Normalize English sector names to Chinese
SECTOR_ZH = {
    "Auto":      "汽車", "Cement":   "水泥",   "Consumer":  "消費零售",
    "Display":   "面板", "Finance":  "金融保險", "Optics":    "光學",
    "Petrochem": "石化", "Semicon":  "半導體",  "Shipping":  "航運",
    "Steel":     "鋼鐵", "Tech HW":  "科技硬體", "Telecom":   "電信",
}
# Manual overrides for expansion stocks (no sector in data)
SECTOR_MANUAL = {
    "2801":"金融保險", "5871":"中租租賃", "5876":"金融保險", "5880":"金融保險",
    "2887":"金融保險", "2890":"金融保險",
    "6669":"科技硬體", "3231":"科技硬體",
}

all_stocks = []
for s in comp + exp:
    code   = s["code"]
    raw_sector = s.get("sector") or ""
    # Normalize English → Chinese, then manual overrides
    sector = SECTOR_ZH.get(raw_sector, raw_sector) or SECTOR_MANUAL.get(code, "其他")
    if sector in ("—", "", "?", None): sector = SECTOR_MANUAL.get(code, "其他")
    all_stocks.append({"code": code, "name": s["name"], "sector": sector})

# ── Aggregate per sector ──────────────────────────────────────────────────────
sectors = defaultdict(list)
for s in all_stocks:
    sectors[s["sector"]].append(s["code"])

sector_results = []
for sector_name, codes in sectors.items():
    stocks_detail = []
    grand_scores, bull_signs_list, rs60_list, pe_list, yield_list = [], [], [], [], []
    triple_ct = strong_ct = buy_ct = bear_ct = 0

    for code in codes:
        g  = grand_map.get(code, {})
        d  = dna_map.get(code, {})
        m  = mom_map.get(code, {})
        r  = rs_map.get(code, {})
        bw = bwi_map.get(code, {})

        grand_score = g.get("grand")
        bull_signs  = d.get("bull_signs", 0) or 0
        rs60        = r.get("rs_60d")
        final       = g.get("final","")
        pe          = sf(bw.get("pe_new") or bw.get("pe_old"))
        yld         = sf(bw.get("div_new") or bw.get("div_yield"))

        if grand_score: grand_scores.append(grand_score)
        bull_signs_list.append(bull_signs)
        if rs60 is not None: rs60_list.append(rs60)
        if pe and 0 < pe < 200: pe_list.append(pe)
        if yld and 0 < yld < 20: yield_list.append(yld)

        if "TRIPLE" in final: triple_ct += 1
        elif "STRONG" in final: strong_ct += 1
        elif "BUY" in final: buy_ct += 1
        elif "BEAR" in (d.get("verdict","")): bear_ct += 1

        stocks_detail.append({
            "code": code, "name": all_stocks[next(i for i,x in enumerate(all_stocks) if x["code"]==code)]["name"],
            "grand": round(grand_score,1) if grand_score else None,
            "final": final, "bull_signs": bull_signs,
            "rs_60d": round(rs60,1) if rs60 else None,
            "pe": round(pe,1) if pe else None,
            "div_yield": round(yld,2) if yld else None,
        })

    stocks_detail.sort(key=lambda x: -(x["grand"] or 0))
    n = len(codes)
    avg_grand  = round(sum(grand_scores)/len(grand_scores),1) if grand_scores else None
    avg_bull   = round(sum(bull_signs_list)/len(bull_signs_list),1) if bull_signs_list else None
    avg_rs60   = round(sum(rs60_list)/len(rs60_list),1) if rs60_list else None
    avg_pe     = round(sum(pe_list)/len(pe_list),1) if pe_list else None
    avg_yield  = round(sum(yield_list)/len(yield_list),2) if yield_list else None

    # Sector signal: STRONG if avg_grand>=60, avg_bull>=3; NEUTRAL middle; WEAK if avg_grand<45
    if   avg_grand and avg_grand >= 60 and (avg_bull or 0) >= 3: signal = "🔥 強勢"
    elif avg_grand and avg_grand >= 55:                           signal = "📈 偏多"
    elif avg_grand and avg_grand >= 45:                           signal = "⬛ 中性"
    elif avg_grand and avg_grand < 40:                            signal = "📉 偏空"
    else:                                                          signal = "⬛ 中性"

    sector_results.append({
        "sector": sector_name, "n_stocks": n,
        "avg_grand": avg_grand, "avg_bull_signs": avg_bull,
        "avg_rs_60d": avg_rs60, "avg_pe": avg_pe, "avg_yield": avg_yield,
        "triple_confirmed": triple_ct, "strong_buy": strong_ct,
        "buy": buy_ct, "signal": signal,
        "stocks": stocks_detail,
    })

sector_results.sort(key=lambda x: -(x["avg_grand"] or 0))

print("=== Sector Analysis ===")
print(f"{'Sector':<10} {'N':>3} {'AvgGrand':>9} {'AvgDNA':>7} {'AvgRS60':>8} {'AvgPE':>6} {'AvgYld':>7} {'Triple':>7} Signal")
for r in sector_results:
    print(f"  {r['sector']:<8} {r['n_stocks']:>3} "
          f"{(str(r['avg_grand']) if r['avg_grand'] else '—'):>9} "
          f"{(str(r['avg_bull_signs']) if r['avg_bull_signs'] else '—'):>7} "
          f"{(str(r['avg_rs_60d']) if r['avg_rs_60d'] else '—'):>8} "
          f"{(str(r['avg_pe']) if r['avg_pe'] else '—'):>6} "
          f"{(str(r['avg_yield']) if r['avg_yield'] else '—'):>7}% "
          f"{r['triple_confirmed']:>7}  {r['signal']}")

print(f"\nTop sector: {sector_results[0]['sector']} (avg grand={sector_results[0]['avg_grand']})")

out = {
    "date":    TODAY,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "n_sectors": len(sector_results),
    "n_stocks":  len(all_stocks),
    "sectors":   sector_results,
}
(REPORT_DIR / "sector_analysis.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ sector_analysis.json saved ({len(sector_results)} sectors, {len(all_stocks)} stocks)")

