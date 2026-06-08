#!/usr/bin/env python3
"""
Iteration 43: Catalyst Calendar & Forward-Looking Intelligence
Builds upcoming catalyst timeline for all 62 stocks + macro events.
No API calls. Generates: catalyst_calendar.json
"""
import json
from pathlib import Path
from datetime import datetime, date, timedelta

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]

def _next_rev_date(ref_str: str) -> str:
    ref = datetime.strptime(ref_str, "%Y-%m-%d")
    _d = ref.replace(day=10) if ref.day < 10 else (ref.replace(day=28) + timedelta(days=4)).replace(day=10)
    while _d.weekday() >= 5:
        _d += timedelta(days=1)
    return _d.strftime("%Y-%m-%d")

REVENUE_DATE = _next_rev_date(TODAY)
REPORT_DIR = Path("reports") / TODAY

grand  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi    = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom    = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
mayp   = json.loads((REPORT_DIR / "may_preview.json").read_text(encoding="utf-8"))
apr    = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
watch  = json.loads((REPORT_DIR / "watchlist_alerts.json").read_text(encoding="utf-8"))
comp   = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
mayp_map  = {r["code"]: r for r in mayp.get("all_previews",[])}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Macro Calendar ────────────────────────────────────────────────────────────
MACRO_EVENTS = [
    {"date": TODAY, "event": "最新交易日收盤", "type": "market", "impact": "HIGH",
     "note": "收盤更新, DNA日線信號重整"},
    {"date": REVENUE_DATE, "event": "月營收公布 (預估)", "type": "revenue", "impact": "HIGH",
     "note": "TWSE t187ap05_L 最新月份 預計上線；更新信念分"},
    {"date": "2026-06-13", "event": "美國CPI (6月)", "type": "macro", "impact": "MEDIUM",
     "note": "通膨數據影響科技/出口股走向"},
    {"date": "2026-06-18", "event": "台積電法說會 (預估)", "type": "earnings", "impact": "HIGH",
     "note": "Q2 2026 展望; AI/CoWoS需求更新"},
    {"date": "2026-06-18", "event": "美聯儲FOMC", "type": "macro", "impact": "HIGH",
     "note": "利率決策; 影響匯率與資金面"},
    {"date": "2026-06-30", "event": "Q2 2026 季末", "type": "earnings", "impact": "MEDIUM",
     "note": "機構再平衡; ETF季度調整前觀察"},
    {"date": "2026-07-10", "event": "6月營收公布 (預估)", "type": "revenue", "impact": "HIGH",
     "note": "TWSE period 11506; 上半年最終確認"},
    {"date": "2026-07-15", "event": "台積電Q2財報", "type": "earnings", "impact": "VERY HIGH",
     "note": "Q2 EPS; 下半年AI伺服器訂單能見度"},
    {"date": "2026-08-01", "event": "Q2 2026 財報季開始", "type": "earnings", "impact": "HIGH",
     "note": "0050成分股Q2財報集中披露; 更新所有基本面評分"},
    {"date": "2026-08-10", "event": "7月營收公布 (預估)", "type": "revenue", "impact": "MEDIUM",
     "note": "TWSE period 11507"},
    {"date": "2026-08-31", "event": "Q2 財報季結束 (預估)", "type": "earnings", "impact": "HIGH",
     "note": "全面重算 Grand Unified Score; 重建Dashboard"},
    {"date": "2026-09-10", "event": "ETF 0056季度調整", "type": "etf", "impact": "MEDIUM",
     "note": "0056高股息成分股季度篩選; 可能影響納入/剔除股"},
    {"date": "2026-09-20", "event": "ETF 00878/00713 半年調整", "type": "etf", "impact": "MEDIUM",
     "note": "永續高股息、高息低波 成分調整"},
]

# ── Per-stock catalyst detection ──────────────────────────────────────────────
stock_catalysts = []
almost_triple = {r["code"]: r for r in watch.get("almost_triple",[])}
dna_5of6      = {r["code"]: r for r in watch.get("dna_5of6",[])}
near_52w      = {r["code"]: r for r in watch.get("near_52w_high",[])}

for code, g in grand_map.items():
    name  = name_map.get(code, code)
    final = g.get("final","")
    grand_s = g.get("grand",0) or 0
    dn    = dna_map.get(code,{})
    mm    = mom_map.get(code,{})
    bw    = bwi_map.get(code,{})
    mp    = mayp_map.get(code,{})
    ar    = apr_map.get(code,{})

    cats = []

    # TRIPLE CONFIRMED → watch for price breakout
    if "TRIPLE" in final:
        cats.append({"trigger": "TRIPLE CONFIRMED 持倉追蹤",
                     "date": TODAY,
                     "priority": "🚀 CRITICAL",
                     "action": f"確認 grand={grand_s:.0f} 維持; 監控S3/S4日線"})

    # Almost TRIPLE
    if code in almost_triple:
        gap = almost_triple[code].get("grand_gap",0)
        cats.append({"trigger": f"差 {gap:.1f} 分達TRIPLE",
                     "date": TODAY,
                     "priority": "⚠️ HIGH",
                     "action": f"收盤後重算; 若估值升 {gap:.1f}pts 則升級"})

    # DNA 5/6
    if code in dna_5of6:
        missing = dna_5of6[code].get("missing","?")
        cats.append({"trigger": f"DNA 5/6 — 缺少 {missing}",
                     "date": TODAY,
                     "priority": "⚠️ HIGH",
                     "action": f"觀察 {missing} 是否觸發; 若全6信號 → 升為大飆股"})

    # Near 52w high
    if code in near_52w:
        hi = near_52w[code].get("pct_from_52w_high",0)
        cats.append({"trigger": f"近52週高點 ({hi:+.1f}%)",
                     "date": TODAY,
                     "priority": "👀 MEDIUM",
                     "action": "突破52週高→ 追蹤; 量縮確認"})

    # Revenue acceleration → May catalyst
    apr_yoy   = sf(ar.get("april_yoy"))
    apr_accel = ar.get("accel","")
    if apr_accel == "ACCELERATING" and (apr_yoy or 0) > 10:
        cats.append({"trigger": f"4月YoY +{apr_yoy:.0f}% ACCELERATING → 5月預告",
                     "date": REVENUE_DATE,
                     "priority": "📈 HIGH",
                     "action": "5月營收公布後更新conviction分; 若持續加速→升評"})

    # PE compression opportunity (high fundamental but low valuation)
    pe  = sf(bw.get("pe_new") or bw.get("pe_old"))
    fun_pts = g.get("fund_pts") or g.get("g_pts") or 0
    if pe and pe < 12 and fun_pts >= 15:
        cats.append({"trigger": f"深度低估 PE={pe:.1f}x 基本面={fun_pts:.0f}pts",
                     "date": REVENUE_DATE,
                     "priority": "💎 HIGH",
                     "action": "5月營收後重算估值分; 估值最大上調空間"})

    # Dividend yield catalyst (ex-date season — next Q3 start)
    _ref_dt = datetime.strptime(TODAY, "%Y-%m-%d")
    _q3_year = _ref_dt.year if _ref_dt.month <= 9 else _ref_dt.year + 1
    _q3_start = f"{_q3_year}-07-01"
    if _q3_start <= TODAY:
        _q3_start = f"{_q3_year + 1}-07-01"
    dy = sf(bw.get("div_new") or bw.get("div_yield"))
    if dy and dy >= 5.0:
        cats.append({"trigger": f"高殖利率 {dy:.2f}% — 除息追蹤",
                     "date": _q3_start,
                     "priority": "💰 MEDIUM",
                     "action": "Q3除息季前確認持有; 除息後觀察填息能力"})

    # May revenue outlook
    may_view = mp.get("outlook","")
    rev_score= mp.get("rev_score",0)
    if rev_score and rev_score >= 4:
        cats.append({"trigger": f"5月展望優異 ({may_view})",
                     "date": REVENUE_DATE,
                     "priority": "📊 MEDIUM",
                     "action": "5月確認後作為加碼依據"})

    if cats:
        stock_catalysts.append({
            "code": code,
            "name": name.split(" ")[0],
            "grand": round(grand_s,1),
            "final": final,
            "catalysts": cats,
        })

# Sort by earliest catalyst date, then by grand score
stock_catalysts.sort(key=lambda x: (min(c["date"] for c in x["catalysts"]), -x["grand"]))

# ── Summary stats ─────────────────────────────────────────────────────────────
by_date = {}
for sc in stock_catalysts:
    for c in sc["catalysts"]:
        by_date.setdefault(c["date"], []).append({
            "code": sc["code"],
            "name": sc["name"],
            "trigger": c["trigger"],
            "action": c["action"],
            "priority": c["priority"],
            "grand": sc["grand"],
        })

timeline = [
    {"date": d, "events": sorted(v, key=lambda x: -x["grand"])}
    for d, v in sorted(by_date.items())
]

# Merge macro into timeline
macro_by_date = {e["date"]: e for e in MACRO_EVENTS}
for t in timeline:
    if t["date"] in macro_by_date:
        t["macro"] = macro_by_date[t["date"]]

macro_only = [{"date": e["date"], "macro": e, "events": []}
              for e in MACRO_EVENTS if e["date"] not in by_date]
timeline = sorted(timeline + macro_only, key=lambda x: x["date"])

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"  CATALYST CALENDAR — {len(stock_catalysts)} stocks, {sum(len(t['events']) for t in timeline)} events")
print(f"{'='*65}")
for t in timeline[:12]:
    macro = t.get("macro")
    print(f"\n📅 {t['date']}" + (f"  ← {macro['event']} [{macro['impact']}]" if macro else ""))
    for e in t["events"][:5]:
        print(f"  {e['priority']} {e['code']} {e['name']}: {e['trigger']}")
        print(f"     → {e['action']}")

out = {
    "date":           TODAY,
    "generated":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "macro_events":   MACRO_EVENTS,
    "stock_catalysts": stock_catalysts,
    "timeline":       timeline,
    "summary": {
        "stocks_with_catalysts": len(stock_catalysts),
        "critical_june8":  sum(1 for t in timeline if t["date"]==TODAY for e in t["events"] if "CRITICAL" in e.get("priority","")),
        "high_june8":      sum(1 for t in timeline if t["date"]==TODAY for e in t["events"]),
        "revenue_plays":   sum(1 for sc in stock_catalysts for c in sc["catalysts"] if "5月" in c["trigger"] or "4月" in c["trigger"]),
    },
}
(REPORT_DIR / "catalyst_calendar.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ catalyst_calendar.json saved ({len(stock_catalysts)} stocks, {len(MACRO_EVENTS)} macro events)")

