#!/usr/bin/env python3
"""
Iteration 42: Individual Stock Report Generator
Creates per-stock analysis files for all 62 ETF components.
Outputs:
  reports/2026-06-06/stocks/[CODE]_report.json  — machine-readable per stock
  reports/2026-06-06/FULL_REPORT.md             — consolidated markdown summary
"""

import json, math
from pathlib import Path
from datetime import datetime

def _clean(obj):
    """Recursively replace NaN/Inf with None for valid JSON output."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    return obj

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
STOCKS_DIR = REPORT_DIR / "stocks"
STOCKS_DIR.mkdir(exist_ok=True)

# ── Load all data ─────────────────────────────────────────────────────────────
grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
bt      = json.loads((REPORT_DIR / "dna_backtest.json").read_text(encoding="utf-8"))
mayp    = json.loads((REPORT_DIR / "may_preview.json").read_text(encoding="utf-8"))
apr     = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
sector  = json.loads((REPORT_DIR / "sector_analysis.json").read_text(encoding="utf-8"))
pt      = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp_d   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
_trail_raw = (REPORT_DIR / "trail_eps_estimates.json")
trail_data = json.loads(_trail_raw.read_text(encoding="utf-8")) if _trail_raw.exists() else {}
trail_map  = {s["code"]: s for s in trail_data.get("stocks", [])}
margin  = json.loads((REPORT_DIR / "margin_data.json").read_text(encoding="utf-8"))
watch   = json.loads((REPORT_DIR / "watchlist_alerts.json").read_text(encoding="utf-8"))
portopt = json.loads((REPORT_DIR / "portfolio_optimizer.json").read_text(encoding="utf-8"))

grand_map  = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map    = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
mom_map    = {m["code"]: m for m in mom.get("all_momentum", [])}
rs_map     = {r["code"]: r for r in rs.get("all_rs", [])}
bwi_map    = {r["code"]: r for r in bwi.get("all_refreshed", [])}
bt_map     = {r["code"]: r for r in bt.get("per_stock", [])}
mayp_map   = {r["code"]: r for r in mayp.get("all_previews", [])}
apr_map    = {r["code"]: r for r in apr.get("all_results", [])}
pt_map     = {t["code"]: t for t in pt.get("all_targets", [])}
comp_map   = {s["code"]: s for s in comp}
exp_map    = {s["code"]: s for s in exp_d}
margin_map = {code: v for code, v in margin.items() if isinstance(v, dict)}
po_map     = {a["code"]: a for a in portopt.get("max_sharpe",{}).get("allocations",[])}

# Alert lookups
almost_triple = {r["code"]: r for r in watch.get("almost_triple",[])}
dna_5of6      = {r["code"]: r for r in watch.get("dna_5of6",[])}
near_52w      = {r["code"]: r for r in watch.get("near_52w_high",[])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def get_sector(code):
    for sec in sector.get("sectors",[]):
        if any(s["code"]==code for s in sec.get("stocks",[])):
            return sec["sector"]
    return "其他"

all_codes = sorted({**comp_map, **exp_map}.keys())

# ── Generate per-stock report ──────────────────────────────────────────────────
generated = 0
report_lines = [
    f"# 台灣 ETF 成分股分析報告",
    f"**日期**: {TODAY} | **涵蓋股票**: {len(all_codes)} 支",
    f"**資料來源**: TWSE OpenAPI + Yahoo Finance | **更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
    "---",
    "",
    "## 目錄",
    "| 排名 | 代碼 | 名稱 | 信念分 | 建議 | DNA | 殖利率 |",
    "|------|------|------|--------|------|-----|--------|",
]

# Table of contents
for i, r in enumerate(grand.get("all_ranked",[])[:30], 1):
    bw = bwi_map.get(r["code"],{})
    dy = sf(bw.get("div_new") or bw.get("div_yield"))
    dn = dna_map.get(r["code"],{})
    dy_str = ("%.2f%%" % dy) if dy else "—"
    report_lines.append(
        f"| {i} | {r['code']} | {r['name'].split(' ')[0]} | {r['grand']:.0f} | {r['final']} "
        f"| {dn.get('bull_signs','?')}/6 | {dy_str} |"
    )
report_lines += ["", "---", ""]

for code in all_codes:
    g   = grand_map.get(code, {})
    dn  = dna_map.get(code, {})
    mm  = mom_map.get(code, {})
    rv  = rs_map.get(code, {})
    bw  = bwi_map.get(code, {})
    bt_r= bt_map.get(code, {})
    mp  = mayp_map.get(code, {})
    ar  = apr_map.get(code, {})
    pt_r= pt_map.get(code, {})
    cs  = comp_map.get(code, exp_map.get(code, {}))
    mg  = margin_map.get(code, {})
    po  = po_map.get(code, {})
    sec = get_sector(code)

    name  = cs.get("name", code)
    final = g.get("final", "—")
    grand_score = g.get("grand", 0) or 0
    bull_signs  = dn.get("bull_signs", 0) or 0

    pe  = sf(bw.get("pe_new")) or sf(bw.get("pe_old")) or sf(cs.get("fwd_pe")) or sf(cs.get("pe"))
    pb  = sf(bw.get("pb_new"))  or sf(cs.get("pb"))
    dy  = sf(bw.get("div_new") or bw.get("div_yield")) or sf(cs.get("div")) or sf(cs.get("div_yield"))
    close = sf(mm.get("close"))
    ma30  = sf(mm.get("ma30"))
    pct_ma= sf(mm.get("pct_vs_ma"))
    pct_pr= sf(mm.get("pct_vs_prior"))

    rs60   = rv.get("rs_60d")
    hi52   = rv.get("pct_from_52w_high")
    ret_60 = rv.get("ret_60d")

    apr_yoy  = sf(ar.get("april_yoy"))
    apr_accel= ar.get("accel","")
    may_view = mp.get("outlook","—")

    # Alerts
    alerts = []
    if code in almost_triple: alerts.append(f"⚠️ 差{almost_triple[code].get('grand_gap',0):.1f}分達TRIPLE")
    if code in dna_5of6:      alerts.append(f"🧬 DNA5/6缺{dna_5of6[code].get('missing','?')}")
    if code in near_52w:      alerts.append(f"🏔 近52週高點RS={near_52w[code].get('rs_60d',0):+.1f}%")

    # Score components
    fund_pts = g.get("fund_pts") or g.get("g_pts") or 0
    tech_pts = g.get("tech_pts", 0) or 0
    val_pts  = g.get("val_pts", 0) or 0
    mom_pts  = g.get("mom_pts", 0) or 0

    # Build JSON report
    report = {
        "code": code, "name": name, "sector": sec,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "recommendation": {
            "final": final, "grand_score": round(grand_score, 1),
            "score_breakdown": {
                "fundamental": round(fund_pts,1), "technical": round(tech_pts,1),
                "valuation": round(val_pts,1), "momentum": round(mom_pts,1),
            }
        },
        "market_data": {
            "close": close, "ma30": ma30,
            "pct_vs_ma": round(pct_ma,1) if pct_ma else None,
            "pct_vs_baseline": round(pct_pr,1) if pct_pr else None,
        },
        "valuation": {
            "pe": round(pe,1) if pe else None,
            "pb": round(pb,2) if pb else None,
            "div_yield": round(dy,2) if dy else None,
        },
        "technical_dna": {
            "bull_signs": bull_signs,
            "signals": {
                "s1_monthly_dmi": {"ok": dn.get("s1_ok",False), "val": dn.get("s1_dmi")},
                "s2_monthly_rsi4": {"ok": dn.get("s2_ok",False), "val": dn.get("s2_rsi4m")},
                "s3_daily_wr50":   {"ok": dn.get("s3_ok",False), "val": dn.get("s3_wr50")},
                "s4_daily_rsi60":  {"ok": dn.get("s4_ok",False), "val": dn.get("s4_rsi60")},
                "s5_weekly_vr2":   {"ok": dn.get("s5_ok",False), "val": dn.get("s5_vr2w")},
                "s6_monthly_vr2":  {"ok": dn.get("s6_ok",False), "val": dn.get("s6_vr2m")},
            },
            "verdict": dn.get("verdict","—"),
        },
        "relative_strength": {
            "rs_60d": rs60, "ret_60d": ret_60, "pct_from_52w_high": hi52,
        },
        "fundamental": {
            "apr_yoy": round(apr_yoy,1) if apr_yoy else None,
            "apr_accel": apr_accel,
            "may_outlook": may_view,
            "q1_eps": sf(cs.get("q1_eps")) or sf(cs.get("eps")) or sf(g.get("eps_q1")),
            "trail_eps": trail_map.get(code, {}).get("trail_eps"),
            "trail_eps_source": trail_map.get(code, {}).get("source"),
            "rev_yoy": sf(cs.get("rev_yoy")),
            "op_margin": sf(cs.get("op_margin")),
        },
        "backtest": {
            "avg_20d": bt_r.get("avg_20d"), "win_20d": bt_r.get("win_20d"),
            "avg_60d": bt_r.get("avg_60d"), "win_60d": bt_r.get("win_60d"),
            "num_signals": bt_r.get("num_signals", 0),
        },
        "portfolio_weight_pct": po.get("weight_pct"),
        "alerts": alerts,
    }

    # Save individual JSON (sanitize NaN/Inf → null for valid JSON)
    (STOCKS_DIR / f"{code}_report.json").write_text(
        json.dumps(_clean(report), ensure_ascii=False, indent=2), encoding="utf-8")
    generated += 1

    # Add to markdown report
    close_s  = ("%.1f"  % close)        if close   else "—"
    ma30_s   = ("%.1f"  % ma30)         if ma30    else "—"
    pct_ma_s = ("%+.1f%%" % pct_ma)     if pct_ma  else "—"
    pe_s     = ("%.1fx" % pe)           if pe      else "—"
    dy_s     = ("%.2f%%" % dy)          if dy      else "—"
    rs60_s   = ("%+.1f%%" % rs60)       if rs60 is not None else "—"
    yoy_s    = ("%+.0f%%" % apr_yoy)    if apr_yoy is not None else "—"
    star = "⭐" if "TRIPLE" in final else ("★" if "STRONG" in final else "")
    report_lines += [
        f"## {star} {code} {name.split(' ')[0]}  `{sec}`",
        f"**建議**: {final} | **信念分**: {grand_score:.0f}/100",
        "",
        "| 指標 | 數值 |",
        "|------|------|",
        f"| 收盤價 | {close_s} |",
        f"| 月均線 | {ma30_s} ({pct_ma_s}) |",
        f"| PE | {pe_s} |",
        f"| 殖利率 | {dy_s} |",
        f"| DNA訊號 | {bull_signs}/6 |",
        f"| 60日RS | {rs60_s} |",
        f"| 4月YoY | {yoy_s} ({apr_accel}) |",
        f"| 5月展望 | {may_view} |",
    ]
    if alerts:
        report_lines.append(f"\n**警示**: {' | '.join(alerts)}")
    report_lines.append("")

    # Score bar
    bars = " | ".join([
        f"基本面:{fund_pts:.0f}",
        f"技術:{tech_pts:.0f}",
        f"估值:{val_pts:.0f}",
        f"動能:{mom_pts:.0f}",
    ])
    report_lines.append(f"*分解: {bars}*")
    report_lines.append("\n---\n")

# ── Write consolidated markdown ──────────────────────────────────────────────
md_path = REPORT_DIR / "FULL_REPORT.md"
md_path.write_text("\n".join(report_lines), encoding="utf-8")

print(f"=== Stock Report Generation ===")
print(f"  Individual JSON reports: {generated} → {STOCKS_DIR}")
print(f"  Consolidated markdown:   {md_path}")
print(f"\n  TRIPLE CONFIRMED:")
for r in grand.get("triple_confirmed",[]):
    print(f"    ✅ {r['code']} {r['name'][:10]}: {r['grand']:.1f}")
print(f"\n  STRONG BUY ({len(grand.get('strong_buy',[]))}):")
for r in grand.get("strong_buy",[]):
    print(f"    ★  {r['code']} {r['name'][:10]}: {r['grand']:.1f}")
print(f"\n  Total BUY or better: {len(grand.get('triple_confirmed',[]))+len(grand.get('strong_buy',[]))+len(grand.get('buy',[]))}")
