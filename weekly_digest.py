#!/usr/bin/env python3
"""
Iteration 51: Weekly Digest — Self-Contained HTML Report
Generates reports/2026-06-06/WEEKLY_DIGEST.html
No server needed. All data embedded. Printable.
No API calls.
"""
import json, html
from pathlib import Path
from datetime import datetime, timedelta

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR/"relative_strength.json").read_text(encoding="utf-8"))
apr     = json.loads((REPORT_DIR/"april_revenue.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))
sensi   = json.loads((REPORT_DIR/"score_sensitivity.json").read_text(encoding="utf-8"))
peer    = json.loads((REPORT_DIR/"peer_comparison.json").read_text(encoding="utf-8"))
secrot  = json.loads((REPORT_DIR/"sector_rotation.json").read_text(encoding="utf-8"))
possize = json.loads((REPORT_DIR/"position_sizing.json").read_text(encoding="utf-8"))
monday  = json.loads((REPORT_DIR/"monday_plan.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
sen_map   = {r["code"]: r for r in sensi.get("all_stocks",[])}
pos_map   = {r["code"]: r for r in possize.get("positions",[])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def fv(v, d=1, s="", plus=False):
    if v is None: return "—"
    f = round(float(v), d)
    prefix = "+" if plus and f >= 0 else ""
    return f"{prefix}{f:.{d}f}{s}"

def verdict_style(v):
    if "TRIPLE" in str(v): return "background:#fef2f2;color:#c2410c;font-weight:700"
    if "STRONG BUY" in str(v): return "background:#f0fdf4;color:#15803d;font-weight:700"
    if "BUY" in str(v): return "background:#eff6ff;color:#1d4ed8;font-weight:700"
    if "WATCH" in str(v): return "background:#fffbeb;color:#92400e;font-weight:600"
    return "background:#f8fafc;color:#64748b"

# Build master row list
rows = []
for r in grand.get("all_ranked",[]):
    code  = r["code"]
    g     = r
    dn    = dna_map.get(code,{})
    bw    = bwi_map.get(code,{})
    mm    = mom_map.get(code,{})
    rv    = rs_map.get(code,{})
    ar    = apr_map.get(code,{})
    eq    = earq_map.get(code,{})
    sn    = sen_map.get(code,{})
    ps    = pos_map.get(code,{})
    rows.append({
        "code": code,
        "name": g.get("name", code),
        "sector": g.get("sector","—"),
        "grand": g.get("grand",0) or 0,
        "final": g.get("final","—"),
        "bull_signs": dn.get("bull_signs",0) or 0,
        "pe": sf(bw.get("pe_new")) or sf(bw.get("pe_old")),
        "dy": sf(bw.get("div_new") or bw.get("div_yield")),
        "close": sf(mm.get("close")),
        "pct_ma": sf(mm.get("pct_vs_ma")),
        "rs_60": rv.get("rs_60d"),
        "pct_52w": sf(rv.get("pct_from_52w_high")),
        "apr_yoy": sf(ar.get("april_yoy")),
        "accel": ar.get("accel",""),
        "eq_score": eq.get("eq_score",0) or 0,
        "eq_grade": (eq.get("grade","") or "").split(" ")[0],
        "pts_next": sf(sn.get("pts_to_next")),
        "next_tier": sn.get("next_tier",""),
        "alloc_pct": sf(ps.get("alloc_pct_norm")),
        "risk_tier": ps.get("risk_tier","—"),
        "stop_level": sf(ps.get("stop_level")),
    })
rows.sort(key=lambda x: -x["grand"])

triple = [r for r in rows if "TRIPLE" in r["final"]]
sbuy   = [r for r in rows if "STRONG BUY" in r["final"]]
buy    = [r for r in rows if r["final"].strip() == "BUY" or "📈 BUY" == r["final"]]
top30  = rows[:30]

# ── HTML generation ───────────────────────────────────────────────────────────
def stock_row(r, i):
    grand_color = "#c2410c" if r["grand"]>=70 else "#1d4ed8" if r["grand"]>=60 else "#374151"
    eq_color    = "#15803d" if r["eq_grade"]=="A+" else "#0891b2" if r["eq_grade"].startswith("A") else "#64748b"
    accel_sym   = "↑↑" if r["accel"]=="ACCELERATING" else ("↑" if r["accel"]=="STABLE" else ("↓" if r["accel"] else "—"))
    alloc_s     = (fv(r["alloc_pct"],2)+"%") if r["alloc_pct"] else "—"
    stop_s      = (fv(r["stop_level"],1)) if r["stop_level"] else "—"
    return f"""<tr class="stock-row">
      <td style="text-align:center;color:#94a3b8;font-size:12px">{i}</td>
      <td><b>{html.escape(r["code"])}</b></td>
      <td style="white-space:nowrap">{html.escape(r["name"].split(" ")[0])}</td>
      <td style="font-size:12px;color:#64748b">{html.escape(r["sector"])}</td>
      <td><span style="{verdict_style(r["final"])};padding:2px 7px;border-radius:5px;font-size:12px;white-space:nowrap">{html.escape(str(r["final"]))}</span></td>
      <td style="text-align:right;font-weight:700;color:{grand_color}">{fv(r["grand"],1)}</td>
      <td style="text-align:center">{r["bull_signs"]}/6</td>
      <td style="text-align:right">{fv(r["pe"],1,"x")}</td>
      <td style="text-align:right">{fv(r["dy"],2,"%")}</td>
      <td style="text-align:right;color:{"#16a34a" if (r["pct_ma"] or 0)>=0 else "#dc2626"}">{fv(r["pct_ma"],1,"%",True)}</td>
      <td style="text-align:right;color:{"#16a34a" if (r["rs_60"] or 0)>=0 else "#dc2626"}">{fv(r["rs_60"],1)}</td>
      <td style="text-align:right">{accel_sym} {fv(r["apr_yoy"],1,"%",True)}</td>
      <td style="text-align:center;color:{eq_color};font-weight:700">{html.escape(r["eq_grade"])}</td>
      <td style="text-align:right;color:#0369a1">{alloc_s}</td>
      <td style="text-align:right;color:#dc2626;font-size:12px">{stop_s}</td>
    </tr>"""

table_rows = "\n".join(stock_row(r, i+1) for i, r in enumerate(top30))

# Monday checklist HTML
checklist_html = ""
for c in monday.get("checklist",[]):
    bg = {"critical":"#fee2e2","data_update":"#eff6ff","execution":"#f0fdf4","alert":"#fffbeb"}.get(c["type"],"#f8fafc")
    bl = {"critical":"#dc2626","data_update":"#3b82f6","execution":"#22c55e","alert":"#f59e0b"}.get(c["type"],"#94a3b8")
    checklist_html += f"""<div style="background:{bg};border-left:3px solid {bl};border-radius:0 6px 6px 0;
        padding:8px 14px;margin-bottom:6px;display:flex;gap:12px;align-items:flex-start">
      <span style="font-weight:700;color:#374151;min-width:75px;font-size:13px">{html.escape(c["time"])}</span>
      <div><div style="font-weight:600;font-size:13px">{html.escape(c["task"])}</div>
        <div style="font-size:12px;color:#64748b;margin-top:2px">{html.escape(c["why"])}</div></div>
    </div>"""

# Sector rotation HTML
secrot_html = ""
for sec in secrot.get("sectors",[]):
    m = sec.get("medians",{})
    phase_colors = {"領漲":"#15803d","改善中":"#0891b2","中性":"#374151","落後":"#d97706","弱勢":"#dc2626"}
    pc = phase_colors.get(sec["phase"],"#374151")
    tags_html = " ".join(f'<span style="font-size:11px;padding:1px 5px;background:#f1f5f9;border-radius:3px">{t}</span>' for t in sec.get("tags",[]))
    secrot_html += f"""<tr>
      <td style="font-weight:600">{html.escape(sec["sector"])}</td>
      <td style="text-align:center;font-weight:700;color:{pc}">{html.escape(sec["phase"])}</td>
      <td style="text-align:right">{fv(m.get("rs_20"),1)}</td>
      <td style="text-align:right">{fv(m.get("rs_60"),1)}</td>
      <td style="text-align:right">{fv(m.get("rs_120"),1)}</td>
      <td style="text-align:right">{fv(m.get("apr_yoy"),1,"%")}</td>
      <td style="color:{pc};font-weight:600;font-size:13px">{html.escape(sec["rotation_signal"])}</td>
      <td>{tags_html}</td>
    </tr>"""

# EQ summary
eq_grades = {"A+":[],"A":[],"B":[],"C":[],"D":[]}
for r in rows:
    k = r["eq_grade"] if r["eq_grade"] in eq_grades else "D"
    eq_grades[k].append(r)

# Pre-compute EQ distribution HTML (avoids nested f-string with dict literal)
_eq_colors = {"A+":"#15803d","A":"#0891b2","B":"#374151","C":"#d97706","D":"#dc2626"}
_eq_ranges  = {"A+":"9-10分","A":"7-8分","B":"5-6分","C":"3-4分","D":"<3分"}
eq_dist_html = ""
for _g, _v in eq_grades.items():
    _c = _eq_colors.get(_g,"#374151")
    _r = _eq_ranges.get(_g,"—")
    eq_dist_html += (f'<div class="section-card">'
        f'<div style="font-size:12px;color:#64748b">Grade {_g}</div>'
        f'<div style="font-size:24px;font-weight:700;color:{_c}">{len(_v)}</div>'
        f'<div style="font-size:11px;color:#94a3b8">{_r}</div></div>')

# Position sizing top picks
pos_rows = ""
for r in possize.get("positions",[]):
    if (r.get("alloc_pct_norm") or 0) < 0.5: continue
    tc = {"核心持倉":"#c2410c","主要持倉":"#1d4ed8","衛星持倉":"#7c3aed"}.get(r.get("risk_tier",""),"#64748b")
    lots_s = (str(r["lots"])+"張") if r.get("lots") else "—"
    twd_s  = (fv(r.get("actual_twd",0)/10000,1)+"萬") if r.get("actual_twd") else "—"
    pos_rows += f"""<tr>
      <td><b>{html.escape(r["code"])}</b></td>
      <td>{html.escape(r["name"].split(" ")[0])}</td>
      <td style="color:{tc};font-weight:700;font-size:12px">{html.escape(r.get("risk_tier","—"))}</td>
      <td style="text-align:right;font-weight:700;color:#0369a1">{fv(r.get("alloc_pct_norm"),2)}%</td>
      <td style="text-align:right">{twd_s}</td>
      <td style="text-align:right">{lots_s}</td>
      <td style="text-align:right;color:#64748b;font-size:12px">{fv(r.get("kelly_half"),1)}%</td>
      <td style="text-align:right;color:#16a34a;font-size:12px">{fv(r.get("win_60d"),0)}%</td>
      <td style="text-align:right;font-size:12px;color:{"#16a34a" if (r.get("avg_60d") or 0) >= 0 else "#dc2626"}">{fv(r.get("avg_60d"),1,"%",True)}</td>
      <td style="text-align:right;color:#dc2626;font-size:12px">{fv(r.get("stop_level"),1)}</td>
    </tr>"""

gen_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# Dynamic date helpers
from datetime import timedelta
_price_date_roc = mom.get("data_date", "")
if _price_date_roc and len(_price_date_roc) == 7 and _price_date_roc[:3].isdigit():
    _yr = int(_price_date_roc[:3]) + 1911
    DATA_DATE_DISPLAY = f"{_yr}-{_price_date_roc[3:5]}-{_price_date_roc[5:]}"
else:
    DATA_DATE_DISPLAY = TODAY
_today_dt = datetime.strptime(TODAY, "%Y-%m-%d")
_next_weekday = _today_dt + timedelta(days=1)
while _next_weekday.weekday() >= 5:
    _next_weekday += timedelta(days=1)
NEXT_TRADING_DAY = _next_weekday.strftime("%Y-%m-%d")
_rev_date_dt = _today_dt + timedelta(days=1)
while _rev_date_dt.weekday() >= 5:
    _rev_date_dt += timedelta(days=1)
# Revenue typically published ~10th of next month; compute dynamically as fallback
def _next_revenue_date(ref: datetime) -> str:
    if ref.day < 10:
        _d = ref.replace(day=10)
    else:
        _d = (ref.replace(day=28) + timedelta(days=4)).replace(day=10)
    while _d.weekday() >= 5:
        _d += timedelta(days=1)
    return _d.strftime("%Y-%m-%d")

_checklist = monday.get("checklist", [])
REVENUE_DATE = _checklist[-1].get("time", "") if _checklist else ""
if not REVENUE_DATE or REVENUE_DATE <= TODAY:
    REVENUE_DATE = _next_revenue_date(_today_dt)

# Next FOMC decision date (2026 schedule)
_FOMC_DATES = ["2026-06-18","2026-07-29","2026-09-16","2026-10-28","2026-12-16"]
FOMC_DATE = next((d for d in _FOMC_DATES if d > TODAY), _FOMC_DATES[-1])
_fomc_label = "FOMC利率決策" if FOMC_DATE > TODAY else "FOMC利率決策 (已過)"

doc = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>台灣 ETF 週報 — {TODAY}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans TC',sans-serif;
    background:#fff;color:#1a2332;font-size:14px;line-height:1.5}}
  .page{{max-width:1200px;margin:0 auto;padding:24px 20px}}
  h1{{font-size:26px;font-weight:800;color:#1a2332}}
  h2{{font-size:18px;font-weight:700;color:#1a2332;margin:28px 0 10px;
     padding-bottom:6px;border-bottom:2px solid #e2e8f0}}
  h3{{font-size:15px;font-weight:700;margin:16px 0 8px}}
  .meta{{font-size:13px;color:#64748b;margin:6px 0 20px}}
  .kpi-row{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:16px 0}}
  @media(max-width:900px){{.kpi-row{{grid-template-columns:repeat(3,1fr)}}}}
  .kpi{{background:#f8fafc;border-radius:8px;padding:12px 14px;border:1px solid #e2e8f0}}
  .kpi-label{{font-size:11px;color:#64748b;font-weight:500;text-transform:uppercase}}
  .kpi-val{{font-size:22px;font-weight:700;margin-top:2px;line-height:1.1}}
  .kpi-sub{{font-size:11px;color:#94a3b8;margin-top:2px}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th{{background:#f1f5f9;padding:8px 10px;text-align:left;font-weight:600;
     color:#374151;border-bottom:2px solid #e2e8f0;white-space:nowrap}}
  td{{padding:7px 10px;border-bottom:1px solid #f1f5f9}}
  tr:hover td{{background:#fafafa}}
  .badge{{display:inline-block;padding:2px 7px;border-radius:4px;font-size:12px}}
  .alert-box{{background:#fef3c7;border:1px solid #fbbf24;border-radius:8px;
    padding:12px 16px;margin:12px 0;font-size:13px}}
  .section-card{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
    padding:16px;margin-bottom:16px}}
  @media print{{
    h2{{page-break-before:always}}
    h2:first-of-type{{page-break-before:avoid}}
    .no-print{{display:none}}
    table{{font-size:11px}}
  }}
</style>
</head>
<body>
<div class="page">

<!-- ── Header ── -->
<div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:8px">
  <div>
    <h1>🇹🇼 台灣 ETF 週報</h1>
    <div class="meta">0050/0056/00878/00713/006208 成分股全面分析 · 分析日期：{TODAY} · 生成：{gen_time}</div>
  </div>
  <div class="no-print" style="display:flex;gap:8px">
    <button onclick="window.print()" style="padding:8px 16px;background:#1a2332;color:#fff;
      border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600">🖨 列印</button>
  </div>
</div>

<!-- ── Alert ── -->
<div class="alert-box">
  ⚠️ <b>報告提醒</b>：本報告基於 {DATA_DATE_DISPLAY} 收盤數據（{TODAY} 生成）。
  下一交易日 {NEXT_TRADING_DAY} 開盤為執行本報告建議的最早時機。
  <b>{REVENUE_DATE}</b> 為5月營收公布日 — 最重要近期催化劑。
</div>

<!-- ── KPIs ── -->
<div class="kpi-row">
  <div class="kpi"><div class="kpi-label">分析股票</div><div class="kpi-val" style="color:#1a2332">{len(rows)}</div><div class="kpi-sub">62支成分股</div></div>
  <div class="kpi"><div class="kpi-label">TRIPLE CONFIRMED</div><div class="kpi-val" style="color:#c2410c">{len(triple)}</div><div class="kpi-sub">≥70分 DNA≥3</div></div>
  <div class="kpi"><div class="kpi-label">STRONG BUY</div><div class="kpi-val" style="color:#15803d">{len(sbuy)}</div><div class="kpi-sub">≥65分</div></div>
  <div class="kpi"><div class="kpi-label">BUY評級</div><div class="kpi-val" style="color:#1d4ed8">{len(buy)}</div><div class="kpi-sub">≥55分</div></div>
  <div class="kpi"><div class="kpi-label">A+盈利品質</div><div class="kpi-val" style="color:#0891b2">{len([r for r in rows if r["eq_grade"]=="A+"])}</div><div class="kpi-sub">EQ 9-10分</div></div>
  <div class="kpi"><div class="kpi-label">預期60日報酬</div><div class="kpi-val" style="color:#7c3aed">{fv(possize.get("portfolio_summary",{}).get("expected_60d_return"),2,"%",True)}</div><div class="kpi-sub">Kelly組合加權</div></div>
</div>

<!-- ── TRIPLE CONFIRMED ── -->
<h2>🚀 TRIPLE CONFIRMED — 最高優先持倉</h2>
<p style="color:#64748b;font-size:13px;margin-bottom:10px">大飆股DNA≥3 + Grand≥70 + 基本面確認。所有TRIPLE股均符合3重條件認證。</p>
<table>
  <thead><tr>
    <th>#</th><th>代號</th><th>名稱</th><th>產業</th><th>評級</th>
    <th style="text-align:right">Grand</th><th style="text-align:center">DNA</th>
    <th style="text-align:right">PE</th><th style="text-align:right">殖利率</th>
    <th style="text-align:right">vs MA</th><th style="text-align:right">RS60</th>
    <th style="text-align:right">4月YoY</th><th>EQ</th>
    <th style="text-align:right">建議%</th><th style="text-align:right">止損</th>
  </tr></thead>
  <tbody>
    {"".join(stock_row(r,i+1) for i,r in enumerate([r for r in rows if "TRIPLE" in r["final"]]))}
  </tbody>
</table>

<!-- ── Top 30 ── -->
<h2>📊 綜合排名 Top 30</h2>
<p style="color:#64748b;font-size:13px;margin-bottom:10px">
  Grand Unified Score = 基本面(25) + 技術DNA(25) + 估值(25) + 動能(25)。
  回測勝率以60日持有期計算，止損為MA30×0.98或收盤×0.92取較低值。
</p>
<table>
  <thead><tr>
    <th>#</th><th>代號</th><th>名稱</th><th>產業</th><th>評級</th>
    <th style="text-align:right">Grand</th><th style="text-align:center">DNA</th>
    <th style="text-align:right">PE</th><th style="text-align:right">殖利率</th>
    <th style="text-align:right">vs MA</th><th style="text-align:right">RS60</th>
    <th style="text-align:right">4月YoY</th><th>EQ</th>
    <th style="text-align:right">建議%</th><th style="text-align:right">止損</th>
  </tr></thead>
  <tbody>{table_rows}</tbody>
</table>

<!-- ── Kelly Position Sizing ── -->
<h2>📐 Kelly倉位建議 (100萬TWD參考)</h2>
<table>
  <thead><tr>
    <th>代號</th><th>名稱</th><th>風險層</th>
    <th style="text-align:right">建議%</th><th style="text-align:right">金額</th>
    <th style="text-align:right">張數</th><th style="text-align:right">Kelly%</th>
    <th style="text-align:right">勝率60d</th><th style="text-align:right">均報60d</th>
    <th style="text-align:right">止損</th>
  </tr></thead>
  <tbody>{pos_rows}</tbody>
</table>
<p style="font-size:12px;color:#94a3b8;margin-top:6px">
  Half-Kelly × Grand評分乘數 × EQ品質乘數 × DNA乘數 × 風險調整。核心≥10%，主要6-10%，衛星1-6%。總投入80%，現金20%。
</p>

<!-- ── Sector Rotation ── -->
<h2>🔄 板塊輪動信號</h2>
<table>
  <thead><tr>
    <th>板塊</th><th style="text-align:center">Phase</th>
    <th style="text-align:right">RS20</th><th style="text-align:right">RS60</th><th style="text-align:right">RS120</th>
    <th style="text-align:right">4月YoY</th><th>輪動訊號</th><th>標籤</th>
  </tr></thead>
  <tbody>{secrot_html}</tbody>
</table>

<!-- ── Earnings Quality ── -->
<h2>📊 盈利品質 (EQ) 分布</h2>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:12px">
  {eq_dist_html}
</div>
<p style="font-size:13px;color:#374151">
  <b>A+最優質 ({len(eq_grades["A+"])}股)：</b>
  {", ".join(r["code"]+" "+r["name"].split(" ")[0] for r in eq_grades["A+"][:8])}
</p>

<!-- ── Monday Plan ── -->
<h2>🗓 {NEXT_TRADING_DAY} 開盤行動計劃</h2>
<div>{checklist_html}</div>

<!-- ── Catalysts ── -->
<h2>📅 關鍵日期催化劑</h2>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">
  <div class="section-card" style="border-left:4px solid #22c55e">
    <div style="font-weight:700;color:#15803d">{NEXT_TRADING_DAY}</div>
    <div style="font-size:13px;margin-top:4px">下一交易日開市</div>
    <div style="font-size:12px;color:#64748b;margin-top:4px">S3日W%R信號可能觸發 DNA-5/6 股票</div>
  </div>
  <div class="section-card" style="border-left:4px solid #dc2626">
    <div style="font-weight:700;color:#dc2626">{REVENUE_DATE} 🔥 最重要</div>
    <div style="font-size:13px;margin-top:4px">5月營收公布日</div>
    <div style="font-size:12px;color:#64748b;margin-top:4px">TWSE t187ap05_L period 11505 — 執行完整pipeline更新</div>
  </div>
  <div class="section-card" style="border-left:4px solid #f59e0b">
    <div style="font-weight:700;color:#92400e">{FOMC_DATE}</div>
    <div style="font-size:13px;margin-top:4px">{_fomc_label}</div>
    <div style="font-size:12px;color:#64748b;margin-top:4px">聯準會利率決策 — 重大方向性事件</div>
  </div>
</div>

<!-- ── Footer ── -->
<div style="margin-top:32px;padding-top:16px;border-top:1px solid #e2e8f0;
     font-size:12px;color:#94a3b8;text-align:center">
  台灣 ETF 分析週報 · {TODAY} · 數據來源：TWSE Open API · 僅供學術研究參考，不構成投資建議
  <br>分析架構：Grand Unified Score (34層分析) · 大飆股DNA信號 · Kelly Criterion倉位計算 · 板塊輪動訊號
  <br>互動式儀表板：<code>python -m http.server 8765</code> 後開啟 <code>http://localhost:8765/dashboard.html</code>
</div>

</div>
</body>
</html>"""

out_path = REPORT_DIR / "WEEKLY_DIGEST.html"
out_path.write_text(doc, encoding="utf-8")
size_kb = out_path.stat().st_size // 1024
print(f"-- WEEKLY_DIGEST.html saved ({size_kb} KB)")
print(f"   Path: {out_path.resolve()}")
print(f"   Stocks: {len(rows)} | Triple: {len(triple)} | Top30 rows: 30")
print(f"   Sections: Header / KPIs / TRIPLE / Top30 / Kelly / Sector Rotation / EQ / Monday / Catalysts")
