#!/usr/bin/env python3
"""
Iteration 47: Monday June 8 Open Action Plan
Synthesises grand unified, earnings quality, DNA signals, sensitivity,
peer comparison, and catalyst calendar into a prioritised Monday open list.
No API calls. Generates: monday_plan.json
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]

def _next_rev_date(ref_str: str):
    ref = datetime.strptime(ref_str, "%Y-%m-%d")
    _d = ref.replace(day=10) if ref.day < 10 else (ref.replace(day=28) + timedelta(days=4)).replace(day=10)
    while _d.weekday() >= 5:
        _d += timedelta(days=1)
    return _d

_rev_dt = _next_rev_date(TODAY)
REVENUE_DATE = _rev_dt.strftime("%Y-%m-%d")
# ROC year+month for the revenue period being published (the month before the 10th)
_rev_month = (_rev_dt.replace(day=1) - timedelta(days=1))
REVENUE_PERIOD = f"1{_rev_month.year - 1911:02d}{_rev_month.month:02d}"
REVENUE_LABEL = f"{_rev_month.month}月營收公布"
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
watch   = json.loads((REPORT_DIR / "watchlist_alerts.json").read_text(encoding="utf-8"))
sensi   = json.loads((REPORT_DIR / "score_sensitivity.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR / "earnings_quality.json").read_text(encoding="utf-8"))
apr     = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
bt      = json.loads((REPORT_DIR / "dna_backtest.json").read_text(encoding="utf-8"))
peer    = json.loads((REPORT_DIR / "peer_comparison.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
bt_map    = {r["code"]: r for r in bt.get("per_stock",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
sen_map   = {r["code"]: r for r in sensi.get("all_stocks",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

almost_triple = {r["code"]: r for r in watch.get("almost_triple",[])}
dna_5of6      = {r["code"]: r for r in watch.get("dna_5of6",[])}
near_52w      = {r["code"]: r for r in watch.get("near_52w_high",[])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def name(code): return name_map.get(code, code).split(" ")[0]

# ── Category 1: TRIPLE CONFIRMED — hold & monitor ─────────────────────────────
triple_stocks = []
for r in grand.get("triple_confirmed", []):
    code  = r["code"]
    bw    = bwi_map.get(code, {})
    mm    = mom_map.get(code, {})
    dn    = dna_map.get(code, {})
    rv    = rs_map.get(code, {})
    eq    = earq_map.get(code, {})
    close = sf(mm.get("close"))
    ma30  = sf(mm.get("ma30"))
    pe    = sf(bw.get("pe_new") or bw.get("pe_old"))
    dy    = sf(bw.get("div_new") or bw.get("div_yield"))
    rs60  = rv.get("rs_60d")
    triple_stocks.append({
        "code": code, "name": name(code),
        "grand": round(r["grand"],1), "final": r["final"],
        "close": close, "ma30": ma30,
        "pe": round(pe,1) if pe else None,
        "div_yield": round(dy,2) if dy else None,
        "bull_signs": dn.get("bull_signs",0),
        "rs_60d": rs60,
        "eq_score": eq.get("eq_score"),
        "action": "持倉追蹤 · 開盤確認MA上方 · 若跌破MA考慮減碼",
        "watch_level": f"MA30={round(ma30,1) if ma30 else '—'}",
        "priority": 1,
        "category": "🚀 TRIPLE CONFIRMED",
    })

# ── Category 2: Near-TRIPLE (≤5pts gap) ──────────────────────────────────────
near_triple = []
for s in sensi.get("near_upgrade", []):
    if not s.get("next_tier","").upper().endswith("TRIPLE CONFIRMED"): continue
    code  = s["code"]
    mm    = mom_map.get(code, {})
    dn    = dna_map.get(code, {})
    bw    = bwi_map.get(code, {})
    close = sf(mm.get("close"))
    pct_ma= sf(mm.get("pct_vs_ma"))
    top_lever = s["levers"][0] if s["levers"] else {}
    near_triple.append({
        "code": code, "name": name(code),
        "grand": s["current"]["grand"],
        "pts_gap": s["pts_to_next"],
        "dna_gap": s.get("dna_gap_to3",0),
        "bull_signs": s["current"]["bull_signs"],
        "top_lever": top_lever.get("lever",""),
        "lever_action": top_lever.get("action",""),
        "close": close, "pct_vs_ma": round(pct_ma,1) if pct_ma else None,
        "action": f"距TRIPLE {s['pts_to_next']:.1f}分 · 觀察{top_lever.get('lever','')}觸發 · 可小量佈局",
        "priority": 2,
        "category": "⚡ 近TRIPLE升評",
    })

# ── Category 3: DNA 5/6 — one signal away from 大飆股 ───────────────────────
dna56_list = []
for code, r in dna_5of6.items():
    g     = grand_map.get(code, {})
    mm    = mom_map.get(code, {})
    dn    = dna_map.get(code, {})
    bt_r  = bt_map.get(code, {})
    close = sf(mm.get("close"))
    pct_ma= sf(mm.get("pct_vs_ma"))
    avg60 = bt_r.get("avg_60d")
    win60 = bt_r.get("win_60d")
    missing = r.get("missing","?")
    dna56_list.append({
        "code": code, "name": name(code),
        "grand": round(g.get("grand",0),1),
        "bull_signs": dn.get("bull_signs",0),
        "missing_signal": missing,
        "close": close, "pct_vs_ma": round(pct_ma,1) if pct_ma else None,
        "bt_avg_60d": avg60, "bt_win_60d": win60,
        "action": f"缺 {missing} 訊號 · 6/6觸發→大飆股 · 回測60日均報酬{avg60:+.1f}%({win60:.0f}%勝率)" if avg60 else f"缺 {missing} 訊號",
        "priority": 3,
        "category": "🧬 DNA 5/6 突破觀察",
    })

# ── Category 4: Quality Dip Buys (A+ EQ + below MA or near MA) ──────────────
quality_dips = []
for r in earq.get("a_plus", []):
    code  = r["code"]
    g     = grand_map.get(code, {})
    mm    = mom_map.get(code, {})
    rv    = rs_map.get(code, {})
    close = sf(mm.get("close"))
    ma30  = sf(mm.get("ma30"))
    pct_ma= sf(mm.get("pct_vs_ma"))
    rs60  = rv.get("rs_60d")
    grand_score = g.get("grand",0) or 0
    if pct_ma is None or pct_ma > 10: continue  # skip if far above MA
    quality_dips.append({
        "code": code, "name": name(code),
        "grand": round(grand_score,1), "eq_score": r["eq_score"],
        "close": close, "ma30": ma30,
        "pct_vs_ma": round(pct_ma,1) if pct_ma else None,
        "rs_60d": rs60,
        "eps_accel": r["key_metrics"].get("eps_accel"),
        "op_margin": r["key_metrics"].get("op_margin"),
        "action": f"A+品質 EQ={r['eq_score']}/10 · 近均線{pct_ma:+.1f}% · 開盤突破MA入場",
        "priority": 4,
        "category": "💎 優質逢低買進",
    })
quality_dips.sort(key=lambda x: (-x["eq_score"], -x["grand"]))

# ── Category 5: Revenue Acceleration plays (June 10 catalyst) ─────────────────
rev_accel = []
for r in apr.get("all_results", []):
    code = r.get("code","")
    if r.get("accel") != "ACCELERATING": continue
    if sf(r.get("april_yoy","")) is None: continue
    yoy = sf(r.get("april_yoy"))
    if yoy < 10: continue  # only significant acceleration
    g   = grand_map.get(code, {})
    grand_s = g.get("grand",0) or 0
    if grand_s < 45: continue
    rev_accel.append({
        "code": code, "name": name(code),
        "grand": round(grand_s,1),
        "apr_yoy": round(yoy,1),
        "accel": r.get("accel",""),
        "action": f"4月YoY+{yoy:.0f}%加速 · 6月10日5月營收公布後更新評分",
        "priority": 5,
        "category": "📈 6月10日營收催化劑",
    })
rev_accel.sort(key=lambda x: -x["apr_yoy"])

# ── Category 6: Sector Leaders (best-in-class per sector) ────────────────────
sector_leaders = []
seen_sectors = set()
for sec in peer.get("sectors",[]):
    bg = sec.get("best_grand",{})
    if not bg: continue
    code = bg.get("code","")
    sec_name = sec["sector"]
    if sec_name in seen_sectors: continue
    seen_sectors.add(sec_name)
    g   = grand_map.get(code, {})
    mm  = mom_map.get(code, {})
    close = sf(mm.get("close"))
    pct_ma= sf(mm.get("pct_vs_ma"))
    med_pe= sec.get("medians",{}).get("pe")
    bw    = bwi_map.get(code,{})
    pe    = sf(bw.get("pe_new") or bw.get("pe_old"))
    pe_rel= round(((pe/med_pe)-1)*100,1) if (pe and med_pe) else None
    sector_leaders.append({
        "code": code, "name": name(code),
        "sector": sec_name, "grand": round(g.get("grand",0),1),
        "pe": round(pe,1) if pe else None,
        "pe_vs_sector": pe_rel,
        "close": close, "pct_vs_ma": round(pct_ma,1) if pct_ma else None,
        "n_peers": sec["n_stocks"],
        "action": f"{sec_name}行業最高Grand分 · PE{pe_rel:+.0f}%vs行業中位" if pe_rel else f"{sec_name}行業最高Grand分",
        "priority": 6,
        "category": "🏆 行業龍頭",
    })
sector_leaders.sort(key=lambda x: -x["grand"])

# ── Monday open checklist (dynamic) ──────────────────────────────────────────
_triple_codes = "/".join(s["code"] for s in triple_stocks[:4]) or "—"
_near1 = near_triple[0] if near_triple else None
_near1_desc = f"觀察{_near1['name'].split()[0]}({_near1['code']}) 開盤方向 — 差{_near1['pts_gap']:.1f}分達TRIPLE" if _near1 else "觀察近TRIPLE股開盤方向"
_qd_names = "/".join(s["code"] for s in quality_dips[:3]) if quality_dips else "—"
checklist = [
    {"time": "08:30", "task": "確認夜盤ADR走勢 (台積電/鴻海)",
     "why": "ADR與A股引領開盤方向", "type": "macro"},
    {"time": "09:00", "task": f"開盤前：設置 TRIPLE CONFIRMED {len(triple_stocks)}股價格警報",
     "why": f"{_triple_codes} 若突破前高即加碼訊號", "type": "execution"},
    {"time": "09:05", "task": _near1_desc,
     "why": "若估值訊號改善即升評至TRIPLE", "type": "alert"},
    {"time": "09:10", "task": "盤初30分鐘量價確認 DNA 5/6 突破股",
     "why": f"共{len(dna56_list)}股缺1個DNA訊號", "type": "screening"},
    {"time": "11:00", "task": "中場更新 dna_refresh.py (新收盤後)",
     "why": "S3/S4日線信號每日更新", "type": "data_update"},
    {"time": "13:30", "task": f"收盤前：觀察 A+品質 近均線股入場時機 ({_qd_names})",
     "why": "A+品質股均線回測是最優入場點", "type": "execution"},
    {"time": "收盤後", "task": "執行 daily_refresh.py → dna_refresh.py → build_dashboard.py",
     "why": "daily_refresh已包含bwibbu+taiex更新，每步需間隔≥132s避免IP封鎖", "type": "data_update"},
    {"time": REVENUE_DATE, "task": f"🔥 {REVENUE_LABEL} — 執行完整pipeline更新",
     "why": f"TWSE t187ap05_L period {REVENUE_PERIOD} 上線 — 最重要催化劑", "type": "critical"},
]

# ── Save ─────────────────────────────────────────────────────────────────────
out = {
    "date":       TODAY,
    "target_date": TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "summary": {
        "triple_count":   len(triple_stocks),
        "near_triple":    len(near_triple),
        "dna_56_count":   len(dna56_list),
        "quality_dips":   len(quality_dips),
        "rev_catalysts":  len(rev_accel),
        "sector_leaders": len(sector_leaders),
    },
    "categories": {
        "triple_confirmed": triple_stocks,
        "near_triple":      near_triple,
        "dna_56":           dna56_list,
        "quality_dips":     quality_dips,
        "rev_accel":        rev_accel,
        "sector_leaders":   sector_leaders,
    },
    "checklist": checklist,
}
(REPORT_DIR / "monday_plan.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'MONDAY JUNE 8 ACTION PLAN':=<65}")
print(f"\n  🚀 Cat 1 — TRIPLE CONFIRMED ({len(triple_stocks)} stocks)")
for s in triple_stocks:
    print(f"    {s['code']} {s['name']:<10} grand={s['grand']} DNA={s['bull_signs']}/6 MA={s['watch_level']}")

print(f"\n  ⚡ Cat 2 — Near-TRIPLE ({len(near_triple)} stocks)")
for s in near_triple:
    print(f"    {s['code']} {s['name']:<10} gap={s['pts_gap']:.1f}pts  lever={s['top_lever']}  DNA={s['bull_signs']}/6")

print(f"\n  🧬 Cat 3 — DNA 5/6 ({len(dna56_list)} stocks)")
for s in dna56_list:
    print(f"    {s['code']} {s['name']:<10} missing={s['missing_signal']}  grand={s['grand']}")

print(f"\n  💎 Cat 4 — A+ Quality Dips ({len(quality_dips)} stocks)")
for s in quality_dips:
    print(f"    {s['code']} {s['name']:<10} EQ={s['eq_score']}/10  vs MA={s['pct_vs_ma']:+.1f}%" if s['pct_vs_ma'] else
          f"    {s['code']} {s['name']:<10} EQ={s['eq_score']}/10")

print(f"\n  📈 Cat 5 — Revenue Catalysts Jun 10 ({len(rev_accel)} stocks)")
for s in rev_accel[:6]:
    print(f"    {s['code']} {s['name']:<10} 4月YoY={s['apr_yoy']:+.0f}%")

print(f"\n  ✅ Monday Checklist:")
for c in checklist:
    print(f"    [{c['time']}] {c['task']}")

print(f"\n✓ monday_plan.json saved")

