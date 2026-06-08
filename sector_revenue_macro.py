#!/usr/bin/env python3
"""
Sector Revenue Macro Analysis: full TWSE 1,078-company April 2026 revenue.
Groups by 產業別, computes median YoY growth, identifies hot/cold sectors.
Cross-references with our 62-stock universe.
No API calls. Generates: sector_revenue_macro.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

raw_file = REPORT_DIR / "may_revenue_raw.json"
comp     = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd     = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
grand    = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

raw_data = json.loads(raw_file.read_text(encoding="utf-8"))
records  = raw_data.get("raw", [])

universe_codes = {s["code"] for s in comp + expd}
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# Build sector → list of YoY growths
sector_data = defaultdict(list)
code_data   = {}

for r in records:
    code     = r.get("公司代號","").strip()
    sector   = r.get("產業別","其他").strip()
    yoy_pct  = sf(r.get("營業收入-去年同月增減(%)"))
    cum_yoy  = sf(r.get("累計營業收入-前期比較增減(%)"))
    rev_now  = sf(r.get("營業收入-當月營收"))
    rev_prev = sf(r.get("營業收入-上月營收"))
    mom_pct  = sf(r.get("營業收入-上月比較增減(%)"))

    if yoy_pct is not None:
        sector_data[sector].append(yoy_pct)

    code_data[code] = {
        "code":    code,
        "name":    r.get("公司名稱",""),
        "sector":  sector,
        "yoy":     yoy_pct,
        "cum_yoy": cum_yoy,
        "mom":     mom_pct,
        "in_universe": code in universe_codes,
    }

# Compute sector stats
sector_stats = []
for sector, yoys in sector_data.items():
    if not yoys: continue
    pos = [y for y in yoys if y > 0]
    neg = [y for y in yoys if y < 0]
    med = statistics.median(yoys)
    avg = sum(yoys) / len(yoys)
    beat_rate = len(pos) / len(yoys) * 100

    # Classify sector momentum
    if med > 20:   momentum = "🔥 強勁"
    elif med > 5:  momentum = "✅ 正成長"
    elif med > -5: momentum = "⚖ 持平"
    elif med > -20:momentum = "⚠ 微衰退"
    else:          momentum = "❌ 衰退"

    sector_stats.append({
        "sector":    sector,
        "count":     len(yoys),
        "median_yoy":round(med, 1),
        "avg_yoy":   round(avg, 1),
        "beat_rate": round(beat_rate, 1),
        "max_yoy":   round(max(yoys), 1),
        "min_yoy":   round(min(yoys), 1),
        "pos_count": len(pos),
        "neg_count": len(neg),
        "momentum":  momentum,
    })

sector_stats.sort(key=lambda x: -x["median_yoy"])

# Universe stock vs sector median
universe_vs_sector = []
for code in sorted(universe_codes):
    cd = code_data.get(code)
    if not cd: continue
    sec_stat = next((s for s in sector_stats if s["sector"] == cd.get("sector")), None)
    sec_med  = sec_stat["median_yoy"] if sec_stat else None
    alpha    = round((cd["yoy"] or 0) - (sec_med or 0), 1) if (cd["yoy"] is not None and sec_med is not None) else None
    gr       = grand_map.get(code, {})
    universe_vs_sector.append({
        "code":       code,
        "name":       cd["name"].split(" ")[0][:6],
        "sector":     cd["sector"],
        "yoy":        cd["yoy"],
        "sector_med": sec_med,
        "vs_sector":  alpha,
        "outperform": (alpha or 0) > 5,
        "grand":      round(gr.get("grand", 0), 1),
        "final":      gr.get("final",""),
    })

universe_vs_sector.sort(key=lambda x: -(x.get("vs_sector") or -999))

# Top-5 / bottom-5 sectors
top5    = sector_stats[:5]
bot5    = sector_stats[-5:]
total   = len(records)
pos_all = sum(1 for r in records if sf(r.get("營業收入-去年同月增減(%)","0")) and sf(r.get("營業收入-去年同月增減(%)","0")) > 0)
beat_rate_all = round(pos_all / total * 100, 1) if total else 0

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'SECTOR REVENUE MACRO — April 2026':=<65}")
print(f"  Total companies: {total}  Sectors: {len(sector_stats)}")
print(f"  市場整體正成長比率: {beat_rate_all}%  (正成長家數: {pos_all}/{total})")

print(f"\n  🔥 Top 5 產業 (中位數YoY最高):")
print(f"  {'產業別':<14} {'家數':>4} {'中位YoY':>8} {'平均YoY':>8} {'正成長率':>8} {'動能'}")
print("-"*70)
for s in top5:
    print(f"  {s['sector']:<14} {s['count']:>4}  {s['median_yoy']:>+7.1f}%  {s['avg_yoy']:>+7.1f}%  {s['beat_rate']:>7.1f}%  {s['momentum']}")

print(f"\n  ❌ Bottom 5 產業 (中位數YoY最低):")
for s in bot5:
    print(f"  {s['sector']:<14} {s['count']:>4}  {s['median_yoy']:>+7.1f}%  {s['avg_yoy']:>+7.1f}%  {s['beat_rate']:>7.1f}%  {s['momentum']}")

print(f"\n  📊 投資組合 vs 產業中位 (Alpha排名):")
outperformers = [r for r in universe_vs_sector if r["outperform"]]
print(f"  超越產業中位(>+5%)的持倉: {len(outperformers)}支")
print(f"  {'代號':<6} {'名稱':<8} {'YoY':>7} {'產業中位':>8} {'vs產業':>8} {'Grand':>6} {'評級'}")
print("-"*75)
for r in universe_vs_sector[:12]:
    yoy = f"{r['yoy']:+.1f}%" if r["yoy"] is not None else "  —"
    sm  = f"{r['sector_med']:+.1f}%" if r["sector_med"] is not None else "  —"
    vs  = f"{r['vs_sector']:+.1f}%" if r["vs_sector"] is not None else "  —"
    print(f"  {r['code']:<6} {r['name']:<8} {yoy:>7} {sm:>8} {vs:>8}  {r['grand']:>5.1f}  {r.get('final','')[:15]}")

out = {
    "date":      TODAY,
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "data_period": "11504 (April 2026)",
    "aggregate": {
        "total_companies":    total,
        "total_sectors":      len(sector_stats),
        "beat_rate_all":      beat_rate_all,
        "pos_growth_count":   pos_all,
    },
    "sector_stats":      sector_stats,
    "top5_sectors":      top5,
    "bottom5_sectors":   bot5,
    "universe_vs_sector":universe_vs_sector,
    "outperformers":     outperformers,
}
(REPORT_DIR / "sector_revenue_macro.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- sector_revenue_macro.json saved")
