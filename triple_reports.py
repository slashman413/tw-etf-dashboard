#!/usr/bin/env python3
"""
Iteration 40: TRIPLE CONFIRMED Deep-Dive Reports
Generates a comprehensive 1-pager for each TRIPLE CONFIRMED stock combining:
fundamental, technical, valuation, momentum, relative strength, and outlook.
No API calls. Generates: triple_reports.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
bt      = json.loads((REPORT_DIR / "dna_backtest.json").read_text(encoding="utf-8"))
watch   = json.loads((REPORT_DIR / "watchlist_alerts.json").read_text(encoding="utf-8"))
mayp    = json.loads((REPORT_DIR / "may_preview.json").read_text(encoding="utf-8"))
sector  = json.loads((REPORT_DIR / "sector_analysis.json").read_text(encoding="utf-8"))
pt      = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp     = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
portopt = json.loads((REPORT_DIR / "portfolio_optimizer.json").read_text(encoding="utf-8"))

dna_map  = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
mom_map  = {m["code"]: m for m in mom.get("all_momentum", [])}
rs_map   = {r["code"]: r for r in rs.get("all_rs", [])}
bwi_map  = {r["code"]: r for r in bwi.get("all_refreshed", [])}
bt_map   = {r["code"]: r for r in bt.get("per_stock", [])}
mayp_map = {r["code"]: r for r in mayp.get("all_previews", [])}
pt_map   = {t["code"]: t for t in pt.get("all_targets", [])}
comp_map = {s["code"]: s for s in comp}
exp_map  = {s["code"]: s for s in exp}

# Port opt — find weight in max_sharpe portfolio
portopt_w = {a["code"]: a for a in portopt.get("max_sharpe", {}).get("allocations", [])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def score_bar(pts, max_pts=25):
    filled = round(pts / max_pts * 5)
    return "█" * filled + "░" * (5 - filled)

# ── Sector info ──────────────────────────────────────────────────────────────
def get_sector(code):
    for sec in sector.get("sectors", []):
        if any(s["code"] == code for s in sec.get("stocks", [])):
            return sec["sector"]
    return "—"

# ── Generate report per TRIPLE CONFIRMED ─────────────────────────────────────
reports = []

for r in grand.get("triple_confirmed", []):
    code  = r["code"]
    name  = r["name"]
    g     = r  # grand record
    dn    = dna_map.get(code, {})
    mm    = mom_map.get(code, {})
    rv    = rs_map.get(code, {})
    bw    = bwi_map.get(code, {})
    bt_r  = bt_map.get(code, {})
    may_r = mayp_map.get(code, {})
    pt_r  = pt_map.get(code, {})
    cs    = comp_map.get(code, exp_map.get(code, {}))
    po    = portopt_w.get(code, {})
    sec   = get_sector(code)

    # ── Grand score breakdown ─────────────────────────────────────────────────
    fund_pts = g.get("fund_pts") or g.get("g_pts") or g.get("score_fundamental", 0) or 0
    tech_pts = g.get("tech_pts", 0) or 0
    val_pts  = g.get("val_pts",  0) or 0
    mom_pts  = g.get("mom_pts",  0) or 0
    grand_total = g["grand"]

    # ── Valuation ──────────────────────────────────────────────────────────────
    pe  = bw.get("pe_new")  or sf(cs.get("fwd_pe"))
    pb  = bw.get("pb_new")  or sf(cs.get("pb"))
    div = bw.get("div_new") or bw.get("div_yield") or sf(cs.get("div"))
    close = sf(mm.get("close"))

    # ── Momentum ───────────────────────────────────────────────────────────────
    pct_ma    = sf(mm.get("pct_vs_ma"))
    pct_prior = sf(mm.get("pct_vs_prior"))
    ma30      = sf(mm.get("ma30"))

    # ── Relative strength ──────────────────────────────────────────────────────
    rs_20d  = rv.get("rs_20d")
    rs_60d  = rv.get("rs_60d")
    rs_120d = rv.get("rs_120d")
    hi52_pct= rv.get("pct_from_52w_high")
    ret_60d = rv.get("ret_60d")

    # ── DNA signals ────────────────────────────────────────────────────────────
    dna_signals = []
    for k, label, threshold in [
        ("s1_ok","S1 月DMI>50",  dn.get("s1_dmi")),
        ("s2_ok","S2 月RSI4>77", dn.get("s2_rsi4m")),
        ("s3_ok","S3 日W%R<20",  dn.get("s3_wr50")),
        ("s4_ok","S4 日RSI60>57",dn.get("s4_rsi60")),
        ("s5_ok","S5 週VR2≥150", dn.get("s5_vr2w")),
        ("s6_ok","S6 月VR2≥150", dn.get("s6_vr2m")),
    ]:
        ok  = dn.get(k, False)
        val = threshold
        dna_signals.append({"signal": label, "ok": ok, "value": round(val, 1) if val else None})

    bull_signs = dn.get("bull_signs", 0) or 0

    # ── Backtest ───────────────────────────────────────────────────────────────
    bt_20d_avg = bt_r.get("avg_20d")
    bt_20d_win = bt_r.get("win_20d")
    bt_60d_avg = bt_r.get("avg_60d")
    bt_60d_win = bt_r.get("win_60d")
    bt_nsig    = bt_r.get("num_signals", 0)

    # ── May revenue outlook ───────────────────────────────────────────────────
    may_outlook = may_r.get("outlook", "—")
    apr_yoy     = may_r.get("apr_yoy")
    apr_accel   = may_r.get("apr_accel", "—")

    # ── Portfolio optimizer weight ─────────────────────────────────────────────
    port_weight = po.get("weight_pct")

    # ── Investment thesis ─────────────────────────────────────────────────────
    thesis_parts = []
    if pe and pe < 16:    thesis_parts.append(f"估值合理 PE {pe:.1f}x")
    if div and div > 3.5: thesis_parts.append(f"殖利率 {div:.2f}%")
    if bull_signs >= 4:   thesis_parts.append(f"技術面 {bull_signs}/6 訊號齊發")
    if (rs_60d or 0) > 0: thesis_parts.append(f"60日超額報酬 {rs_60d:+.1f}%")
    if (pct_ma or 0) > 0: thesis_parts.append(f"股價站上月均線 +{pct_ma:.1f}%")
    if apr_yoy and apr_yoy > 10: thesis_parts.append(f"4月YoY +{apr_yoy:.0f}%")
    thesis = " · ".join(thesis_parts[:4]) if thesis_parts else "多因子強勢"

    report = {
        "code": code, "name": name, "sector": sec,
        "grand_total": grand_total, "final": g["final"],
        "score_breakdown": {
            "fundamental": round(fund_pts, 1), "technical": round(tech_pts, 1),
            "valuation":   round(val_pts, 1),  "momentum":   round(mom_pts, 1),
            "fund_bar": score_bar(fund_pts), "tech_bar": score_bar(tech_pts),
            "val_bar":  score_bar(val_pts),  "mom_bar":  score_bar(mom_pts),
        },
        "valuation": {"pe": pe, "pb": pb, "div_yield": div, "close": close, "ma30": ma30},
        "momentum": {
            "pct_vs_ma": pct_ma, "pct_vs_prior": pct_prior,
            "signal": mm.get("signal", "NEUTRAL"),
        },
        "relative_strength": {
            "rs_20d": rs_20d, "rs_60d": rs_60d, "rs_120d": rs_120d,
            "ret_60d": ret_60d, "pct_from_52w_high": hi52_pct,
        },
        "dna_signals": dna_signals, "bull_signs": bull_signs,
        "backtest": {
            "avg_20d": bt_20d_avg, "win_20d": bt_20d_win,
            "avg_60d": bt_60d_avg, "win_60d": bt_60d_win,
            "num_signals": bt_nsig,
        },
        "may_outlook": {
            "verdict": may_outlook, "apr_yoy": apr_yoy, "accel": apr_accel,
            "est_range": f"{may_r.get('may_est_low_bn','?')}–{may_r.get('may_est_high_bn','?')} 億"
                         if may_r.get("may_est_low_bn") else "N/A",
        },
        "portfolio_weight": port_weight,
        "thesis": thesis,
    }
    reports.append(report)

    # ── Print ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  {code} {name}  [{sec}]  Grand: {grand_total:.1f} / 100")
    print(f"{'='*60}")
    print(f"  Score: Fund{score_bar(fund_pts)}({fund_pts:.0f}) Tech{score_bar(tech_pts)}({tech_pts:.0f})"
          f" Val{score_bar(val_pts)}({val_pts:.0f}) Mom{score_bar(mom_pts)}({mom_pts:.0f})")
    print(f"  PE: {pe:.1f}x  PB: {pb:.2f}x  殖利率: {div:.2f}%" if pe and pb and div else
          f"  PE: {pe}  PB: {pb}  殖利率: {div}%")
    print(f"  Close: {close}  MA30: {ma30}  vs MA: {pct_ma:+.1f}%" if close and ma30 and pct_ma else "")
    print(f"  DNA: {bull_signs}/6 | " +
          " ".join(("✅" if s["ok"] else "—") + s["signal"].split()[0] for s in dna_signals))
    if rs_60d is not None: print(f"  RS60: {rs_60d:+.1f}%  RS120: {rs_120d or 0:+.1f}%  52wH: {hi52_pct or 0:+.1f}%")
    if bt_20d_avg: print(f"  Backtest 20d: avg {bt_20d_avg:+.1f}% win {bt_20d_win:.0f}% (n={bt_nsig})")
    print(f"  May outlook: {may_outlook} (4月YoY: {apr_yoy:+.0f}%)" if apr_yoy else f"  May outlook: {may_outlook}")
    if port_weight: print(f"  Portfolio weight (max Sharpe): {port_weight:.1f}%")
    print(f"  Thesis: {thesis}")

out = {
    "date":     TODAY,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "count":    len(reports),
    "reports":  reports,
}
(REPORT_DIR / "triple_reports.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ triple_reports.json saved ({len(reports)} reports)")
