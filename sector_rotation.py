#!/usr/bin/env python3
"""
Iteration 50: Sector Rotation Signal
Aggregates individual stock RS, momentum, and DNA data to sector level.
Identifies which sectors are gaining vs losing relative strength and
produces rotation trade recommendations. No API calls.
Generates: sector_rotation.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
apr     = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
peer    = json.loads((REPORT_DIR / "peer_comparison.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR / "earnings_quality.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

code_sector = {}
for sec in peer.get("sectors",[]):
    for s in sec.get("stocks",[]):
        code_sector[s["code"]] = sec["sector"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def med(lst): return statistics.median(lst) if lst else None
def avg(lst): return sum(lst)/len(lst) if lst else None

sector_data = defaultdict(list)
all_rs60 = []

for code, sector in code_sector.items():
    g   = grand_map.get(code, {})
    rv  = rs_map.get(code, {})
    mm  = mom_map.get(code, {})
    dn  = dna_map.get(code, {})
    bw  = bwi_map.get(code, {})
    ar  = apr_map.get(code, {})
    eq  = earq_map.get(code, {})
    rs20  = sf(rv.get("rs_20d"))
    rs60  = sf(rv.get("rs_60d"))
    rs120 = sf(rv.get("rs_120d"))
    ret60 = sf(rv.get("ret_60d"))
    pct_ma  = sf(mm.get("pct_vs_ma"))
    pct_52w = sf(rv.get("pct_from_52w_high"))
    grand_s = g.get("grand", 0) or 0
    bull    = dn.get("bull_signs", 0) or 0
    apr_yoy = sf(ar.get("april_yoy"))
    accel   = ar.get("accel","")
    pe      = sf(bw.get("pe_new") or bw.get("pe_old"))
    dy      = sf(bw.get("div_new") or bw.get("div_yield"))
    eq_score= eq.get("eq_score", 0) or 0
    if rs60 is not None: all_rs60.append(rs60)
    sector_data[sector].append({
        "code":code,"name":name_map.get(code,code),"grand":grand_s,
        "final":g.get("final","—"),"rs_20":rs20,"rs_60":rs60,"rs_120":rs120,
        "ret_60":ret60,"pct_ma":pct_ma,"pct_52w":pct_52w,"bull":bull,
        "apr_yoy":apr_yoy,"accel":accel,"pe":pe,"dy":dy,"eq_score":eq_score,
    })

sectors_out = []
all_rs60_sorted = sorted([x for x in all_rs60 if x is not None])
n_all = len(all_rs60_sorted)

for sector_name, members in sector_data.items():
    if len(members) < 2: continue
    rs20s  = [m["rs_20"]  for m in members if m["rs_20"]  is not None]
    rs60s  = [m["rs_60"]  for m in members if m["rs_60"]  is not None]
    rs120s = [m["rs_120"] for m in members if m["rs_120"] is not None]
    ret60s = [m["ret_60"] for m in members if m["ret_60"] is not None]
    pct_mas= [m["pct_ma"] for m in members if m["pct_ma"] is not None]
    pct52ws= [m["pct_52w"] for m in members if m["pct_52w"] is not None]
    grands = [m["grand"]  for m in members]
    bulls  = [m["bull"]   for m in members]
    apryoys= [m["apr_yoy"] for m in members if m["apr_yoy"] is not None]
    pes    = [m["pe"]     for m in members if m["pe"] and 0 < m["pe"] < 200]
    dys    = [m["dy"]     for m in members if m["dy"] and 0 < m["dy"] < 30]
    eqs    = [m["eq_score"] for m in members]

    med_rs20  = med(rs20s)
    med_rs60  = med(rs60s)
    med_rs120 = med(rs120s)
    med_ret60 = med(ret60s)
    med_pct_ma= med(pct_mas)
    med_pct52w= med(pct52ws)
    avg_grand = avg(grands)
    avg_bull  = avg(bulls)
    med_apr_yoy=med(apryoys)
    med_pe    = med(pes)
    med_dy    = med(dys)
    avg_eq    = avg(eqs)

    if med_rs20 and med_rs60:
        if med_rs20 > med_rs60 + 5:   rs_accel = "加速"
        elif med_rs20 > med_rs60:      rs_accel = "持穩"
        elif med_rs20 < med_rs60 - 5:  rs_accel = "減速"
        else:                           rs_accel = "中性"
    else: rs_accel = None

    if med_rs60 is not None and n_all > 0:
        percentile = sum(1 for x in all_rs60_sorted if x <= med_rs60) / n_all
        rs_pts = percentile * 40
    else: rs_pts = 20
    if med_rs20 and med_rs60:
        mom_pts = min(20, max(0, 10 + (med_rs20 - med_rs60) * 2))
    else: mom_pts = 10
    if med_pct_ma is not None:
        ma_pts = min(20, max(0, 10 + med_pct_ma * 0.5))
    else: ma_pts = 10
    if med_apr_yoy is not None:
        rev_pts = min(20, max(0, 10 + med_apr_yoy * 0.2))
    else: rev_pts = 10
    rotation_score = round(rs_pts + mom_pts + ma_pts + rev_pts, 1)

    if rotation_score >= 70:   phase = "領漲"
    elif rotation_score >= 55: phase = "改善中"
    elif rotation_score >= 45: phase = "中性"
    elif rotation_score >= 35: phase = "落後"
    else:                       phase = "弱勢"

    rs_trend_delta = None
    if med_rs20 and med_rs120:
        rs_trend_delta = med_rs20 - med_rs120
        if rs_trend_delta > 10:    rs_trend = "強力升溫"
        elif rs_trend_delta > 3:   rs_trend = "升溫"
        elif rs_trend_delta > -3:  rs_trend = "平穩"
        elif rs_trend_delta > -10: rs_trend = "降溫"
        else:                       rs_trend = "急速降溫"
    else: rs_trend = "—"

    if phase in ("領漲","改善中") and rs_accel in ("加速","持穩"):
        rotation_signal = "BUY → 增持"; signal_color = "#15803d"
    elif phase == "中性" and rs_accel == "加速":
        rotation_signal = "WATCH → 觀察建倉"; signal_color = "#0891b2"
    elif phase in ("落後","弱勢") and rs_accel in ("減速",None):
        rotation_signal = "REDUCE → 減持"; signal_color = "#dc2626"
    elif phase in ("落後","弱勢"):
        rotation_signal = "HOLD → 持觀望"; signal_color = "#d97706"
    else:
        rotation_signal = "NEUTRAL → 維持"; signal_color = "#64748b"

    tags = []
    if med_pe and med_pe < 15:   tags.append("低估值")
    if med_dy and med_dy > 4:    tags.append("高殖利率")
    if med_apr_yoy and med_apr_yoy > 20: tags.append("營收強勁")
    if rs_trend in ("強力升溫","升溫"): tags.append("動能升溫")
    n_triple = sum(1 for m in members if "TRIPLE" in m["final"])
    n_buy    = sum(1 for m in members if "BUY" in m["final"])
    n_above_ma = sum(1 for m in members if m["pct_ma"] is not None and m["pct_ma"] >= 0)
    if n_triple > 0: tags.append(f"{n_triple}TRIPLE")
    if avg_grand and avg_grand > 60: tags.append("高Grand分")

    best     = max(members, key=lambda x: x["grand"])
    best_rs  = max([m for m in members if m["rs_60"] is not None], key=lambda x: x["rs_60"], default=None)

    sectors_out.append({
        "sector": sector_name, "n_stocks": len(members),
        "rotation_score": rotation_score, "phase": phase,
        "rotation_signal": rotation_signal, "signal_color": signal_color,
        "rs_trend": rs_trend,
        "rs_trend_delta": round(rs_trend_delta,1) if rs_trend_delta is not None else None,
        "rs_accel": rs_accel, "tags": tags,
        "medians": {
            "rs_20":  round(med_rs20,1)  if med_rs20  is not None else None,
            "rs_60":  round(med_rs60,1)  if med_rs60  is not None else None,
            "rs_120": round(med_rs120,1) if med_rs120 is not None else None,
            "ret_60d": round(med_ret60,1) if med_ret60 is not None else None,
            "pct_vs_ma30": round(med_pct_ma,1) if med_pct_ma is not None else None,
            "pct_from_52w": round(med_pct52w,1) if med_pct52w is not None else None,
            "grand":  round(avg_grand,1) if avg_grand is not None else None,
            "bull_signs": round(avg_bull,1) if avg_bull is not None else None,
            "apr_yoy": round(med_apr_yoy,1) if med_apr_yoy is not None else None,
            "pe":  round(med_pe,1) if med_pe is not None else None,
            "div_yield": round(med_dy,2) if med_dy is not None else None,
            "eq_score": round(avg_eq,1) if avg_eq is not None else None,
        },
        "best_grand": {"code":best["code"],"name":best["name"].split(" ")[0],"grand":best["grand"],"final":best["final"]},
        "best_rs60":  {"code":best_rs["code"],"name":best_rs["name"].split(" ")[0],"rs_60":best_rs["rs_60"]} if best_rs else None,
        "n_triple": n_triple, "n_buy_plus": n_buy, "n_above_ma": n_above_ma,
        "stocks": sorted(members, key=lambda x: -(x["rs_60"] or 0)),
    })

sectors_out.sort(key=lambda x: -x["rotation_score"])

buy_sectors    = [s for s in sectors_out if "BUY" in s["rotation_signal"]]
reduce_sectors = [s for s in sectors_out if "REDUCE" in s["rotation_signal"]]
watch_sectors  = [s for s in sectors_out if "WATCH" in s["rotation_signal"]]
rotation_trades = []
for buy in buy_sectors[:3]:
    for reduce in reduce_sectors[:3]:
        rotation_trades.append({
            "rotate_from": reduce["sector"], "rotate_to": buy["sector"],
            "rationale": f"{reduce['sector']}({reduce['phase']},{reduce['rs_trend']}) → {buy['sector']}({buy['phase']},{buy['rs_trend']})",
            "confidence": "高" if abs((buy["rotation_score"]-reduce["rotation_score"])) > 20 else "中",
        })

print(f"\n{'SECTOR ROTATION SIGNALS':=<65}")
print(f"\n  {'產業':<14} {'旋轉分':>6} {'Phase':>7} {'RS20':>6} {'RS60':>6} {'RS120':>6} {'趨勢':>8}  訊號")
print("-"*75)
for s in sectors_out:
    m = s["medians"]
    r20  = ("%.1f" % m["rs_20"])  if m["rs_20"]  is not None else "—"
    r60  = ("%.1f" % m["rs_60"])  if m["rs_60"]  is not None else "—"
    r120 = ("%.1f" % m["rs_120"]) if m["rs_120"] is not None else "—"
    print(f"  {s['sector']:<14} {s['rotation_score']:>6.1f} {s['phase']:>7} "
          f"{r20:>6} {r60:>6} {r120:>6} {s['rs_trend']:>8}  {s['rotation_signal']}")
print(f"\n  Rotation Trades:")
for t in rotation_trades[:4]:
    print(f"    {t['rotate_from']} → {t['rotate_to']}  [{t['confidence']}信心]")

out = {
    "date": TODAY, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "sectors": sectors_out, "buy_sectors": buy_sectors,
    "reduce_sectors": reduce_sectors, "watch_sectors": watch_sectors,
    "rotation_trades": rotation_trades,
    "summary": {
        "n_sectors": len(sectors_out), "n_buy": len(buy_sectors),
        "n_reduce": len(reduce_sectors),
        "n_neutral": len([s for s in sectors_out if s["phase"] == "中性"]),
        "top_sector":    sectors_out[0]["sector"] if sectors_out else None,
        "bottom_sector": sectors_out[-1]["sector"] if sectors_out else None,
    }
}
(REPORT_DIR / "sector_rotation.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- sector_rotation.json saved ({len(sectors_out)} sectors)")

