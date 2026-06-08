#!/usr/bin/env python3
"""
Iteration 48: CSV Export Generator
Writes clean, analysis-ready CSV files for all 62 stocks.
Outputs:
  reports/2026-06-06/STOCKS_MASTER.csv     — all metrics combined
  reports/2026-06-06/STOCKS_SCREENER.csv   — screener-ready subset
  reports/2026-06-06/STOCKS_FINANCIAL.csv  — Q1 2026 financial detail
  reports/2026-06-06/STOCKS_TECHNICAL.csv  — DNA + price technical data
No API calls.
"""
import json, csv
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

# Load all data sources
grand  = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
bwi    = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom    = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs     = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
comp   = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
apr    = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
earq   = json.loads((REPORT_DIR / "earnings_quality.json").read_text(encoding="utf-8"))
sen    = json.loads((REPORT_DIR / "score_sensitivity.json").read_text(encoding="utf-8"))
peer   = json.loads((REPORT_DIR / "peer_comparison.json").read_text(encoding="utf-8"))
bt     = json.loads((REPORT_DIR / "dna_backtest.json").read_text(encoding="utf-8"))
pt     = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
etfc   = json.loads((REPORT_DIR / "etf_comparison.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
apr_map   = {r["code"]: r for r in apr.get("all_results",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
sen_map   = {r["code"]: r for r in sen.get("all_stocks",[])}
bt_map    = {r["code"]: r for r in bt.get("per_stock",[])}
pt_map    = {t["code"]: t for t in pt.get("all_targets",[])}
comp_map  = {s["code"]: s for s in comp}
exp_map   = {s["code"]: s for s in expd}

# Peer sector lookup
code_sector = {}
code_pe_rel = {}
for sec in peer.get("sectors",[]):
    for s in sec.get("stocks",[]):
        code_sector[s["code"]] = sec["sector"]
        code_pe_rel[s["code"]] = s.get("pe_vs_sector")

# ETF membership
etf_membership = {}
for etf in etfc.get("etfs",[]):
    for h in etf.get("all_holdings",[]):
        code = h["code"]
        etf_membership.setdefault(code, []).append(etf["etf_code"])

def sf(v, decimals=2):
    if v is None: return ""
    try: return round(float(str(v).replace(",","")), decimals)
    except: return ""

def yn(v): return "Y" if v else "N"

all_codes = sorted(set(comp_map.keys()) | set(exp_map.keys()))
rows = []

for code in all_codes:
    g   = grand_map.get(code, {})
    dn  = dna_map.get(code, {})
    bw  = bwi_map.get(code, {})
    mm  = mom_map.get(code, {})
    rv  = rs_map.get(code, {})
    ar  = apr_map.get(code, {})
    eq  = earq_map.get(code, {})
    sn  = sen_map.get(code, {})
    b   = bt_map.get(code, {})
    p   = pt_map.get(code, {})
    cs  = comp_map.get(code, exp_map.get(code, {}))

    row = {
        # ── Identity ──────────────────────────────────────────────────────────
        "code":          code,
        "name":          cs.get("name",""),
        "sector":        code_sector.get(code, cs.get("sector","")),
        "etfs":          "/".join(etf_membership.get(code,[])),
        "data_date":     TODAY,
        # ── Grand Unified Score ───────────────────────────────────────────────
        "grand_score":   sf(g.get("grand")),
        "final_rating":  g.get("final",""),
        "fund_pts":      sf(g.get("fund_pts") or g.get("g_pts")),
        "tech_pts":      sf(g.get("tech_pts")),
        "val_pts":       sf(g.get("val_pts")),
        "mom_pts":       sf(g.get("mom_pts")),
        "is_triple":     yn("TRIPLE" in (g.get("final",""))),
        # ── Valuation ─────────────────────────────────────────────────────────
        "pe":            sf(bw.get("pe_new") or cs.get("fwd_pe")),
        "pb":            sf(bw.get("pb_new") or cs.get("pb")),
        "div_yield":     sf(bw.get("div_new") or bw.get("div_yield") or cs.get("div_yield")),
        "pe_vs_sector":  sf(code_pe_rel.get(code)),
        # ── Q1 2026 Financials ────────────────────────────────────────────────
        "q1_eps":        sf(cs.get("q1_eps")),
        "fwd_eps":       sf(cs.get("fwd_eps")),
        "trail_eps":     sf(cs.get("trail_eps")),
        "eps_accel_pct": sf(cs.get("eps_accel")),
        "fwd_pe":        sf(cs.get("fwd_pe")),
        "trail_pe":      sf(cs.get("trail_pe")),
        "op_margin":     sf(cs.get("op_margin")),
        "net_margin":    sf(cs.get("net_margin")),
        "rev_yoy_q1":    sf(cs.get("rev_yoy")),
        "cum_yoy":       sf(cs.get("cum_yoy")),
        # ── April 2026 Revenue ────────────────────────────────────────────────
        "apr_revenue_bn": sf(ar.get("apr_b")),
        "apr_yoy":       sf(ar.get("april_yoy")),
        "apr_mom":       sf(ar.get("mom")),
        "apr_accel":     ar.get("accel",""),
        # ── Price & Momentum ──────────────────────────────────────────────────
        "close":         sf(mm.get("close")),
        "ma30":          sf(mm.get("ma30")),
        "pct_vs_ma30":   sf(mm.get("pct_vs_ma")),
        "momentum_sig":  mm.get("signal",""),
        # ── Relative Strength ─────────────────────────────────────────────────
        "rs_20d":        sf(rv.get("rs_20d")),
        "rs_60d":        sf(rv.get("rs_60d")),
        "rs_120d":       sf(rv.get("rs_120d")),
        "ret_60d":       sf(rv.get("ret_60d")),
        "pct_52w_high":  sf(rv.get("pct_from_52w_high")),
        # ── DNA Signals ───────────────────────────────────────────────────────
        "bull_signs":    dn.get("bull_signs",""),
        "dna_verdict":   dn.get("verdict",""),
        "s1_dmi":        yn(dn.get("s1_ok")),
        "s2_rsi4m":      yn(dn.get("s2_ok")),
        "s3_wr50":       yn(dn.get("s3_ok")),
        "s4_rsi60":      yn(dn.get("s4_ok")),
        "s5_vr2w":       yn(dn.get("s5_ok")),
        "s6_vr2m":       yn(dn.get("s6_ok")),
        "s1_val":        sf(dn.get("s1_dmi"),1),
        "s2_val":        sf(dn.get("s2_rsi4m"),1),
        "s3_val":        sf(dn.get("s3_wr50"),1),
        "s4_val":        sf(dn.get("s4_rsi60"),1),
        "s5_val":        sf(dn.get("s5_vr2w"),0),
        "s6_val":        sf(dn.get("s6_vr2m"),0),
        # ── Backtest ──────────────────────────────────────────────────────────
        "bt_signals":    b.get("num_signals",""),
        "bt_avg_20d":    sf(b.get("avg_20d")),
        "bt_win_20d":    sf(b.get("win_20d")),
        "bt_avg_60d":    sf(b.get("avg_60d")),
        "bt_win_60d":    sf(b.get("win_60d")),
        # ── Earnings Quality ──────────────────────────────────────────────────
        "eq_score":      eq.get("eq_score",""),
        "eq_grade":      eq.get("grade",""),
        "eq1_eps_pos":   yn(eq.get("scores",{}).get("EQ1_eps_positive")),
        "eq2_accel_pos": yn(eq.get("scores",{}).get("EQ2_eps_accel_pos")),
        "eq3_accel_str": yn(eq.get("scores",{}).get("EQ3_accel_strong")),
        "eq4_rev_pos":   yn(eq.get("scores",{}).get("EQ4_rev_yoy_pos")),
        "eq5_rev_accel": yn(eq.get("scores",{}).get("EQ5_rev_accel")),
        # ── Upgrade Sensitivity ───────────────────────────────────────────────
        "next_tier":     sn.get("next_tier",""),
        "pts_to_next":   sf(sn.get("pts_to_next")),
        "top_lever":     sn.get("levers",[{}])[0].get("lever","") if sn.get("levers") else "",
        "max_gain_2lev": sf(sn.get("max_gain_2levers")),
        # ── Price Targets ─────────────────────────────────────────────────────
        "pt_base":       sf(p.get("base_target")),
        "pt_bull":       sf(p.get("bull_target")),
        "pt_bear":       sf(p.get("bear_target")),
        "pt_upside":     sf(p.get("base_upside")),
    }
    rows.append(row)

# Sort by grand score descending
rows.sort(key=lambda x: -(float(x["grand_score"]) if x["grand_score"] != "" else 0))

# ── Write MASTER CSV ──────────────────────────────────────────────────────────
master_path = REPORT_DIR / "STOCKS_MASTER.csv"
with open(master_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

# ── Screener CSV (key fields only) ────────────────────────────────────────────
screener_cols = ["code","name","sector","etfs","grand_score","final_rating",
                 "pe","div_yield","pe_vs_sector","apr_yoy","apr_accel",
                 "bull_signs","dna_verdict","rs_60d","pct_52w_high",
                 "eq_score","eq_grade","pts_to_next","next_tier","top_lever"]
screener_rows = [{k: r[k] for k in screener_cols} for r in rows]
scr_path = REPORT_DIR / "STOCKS_SCREENER.csv"
with open(scr_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=screener_cols)
    w.writeheader(); w.writerows(screener_rows)

# ── Financial CSV ─────────────────────────────────────────────────────────────
fin_cols = ["code","name","sector","q1_eps","fwd_eps","trail_eps","eps_accel_pct",
            "fwd_pe","trail_pe","op_margin","net_margin","rev_yoy_q1","cum_yoy",
            "apr_revenue_bn","apr_yoy","apr_mom","apr_accel",
            "pe","pb","div_yield","eq_score","eq_grade","grand_score","final_rating"]
fin_rows = [{k: r[k] for k in fin_cols} for r in rows]
fin_path = REPORT_DIR / "STOCKS_FINANCIAL.csv"
with open(fin_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fin_cols)
    w.writeheader(); w.writerows(fin_rows)

# ── Technical CSV ─────────────────────────────────────────────────────────────
tech_cols = ["code","name","close","ma30","pct_vs_ma30","momentum_sig",
             "rs_20d","rs_60d","rs_120d","ret_60d","pct_52w_high",
             "bull_signs","dna_verdict","s1_dmi","s2_rsi4m","s3_wr50",
             "s4_rsi60","s5_vr2w","s6_vr2m",
             "s1_val","s2_val","s3_val","s4_val","s5_val","s6_val",
             "bt_signals","bt_avg_20d","bt_win_20d","bt_avg_60d","bt_win_60d",
             "grand_score","final_rating"]
tech_rows = [{k: r[k] for k in tech_cols} for r in rows]
tech_path = REPORT_DIR / "STOCKS_TECHNICAL.csv"
with open(tech_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=tech_cols)
    w.writeheader(); w.writerows(tech_rows)

# ── Summary stats ─────────────────────────────────────────────────────────────
triple = [r for r in rows if r["is_triple"]=="Y"]
buy_plus= [r for r in rows if "BUY" in str(r["final_rating"])]
a_plus  = [r for r in rows if str(r["eq_grade"]).startswith("A+")]
near_up = [r for r in rows if r["pts_to_next"]!="" and float(r["pts_to_next"])<5]

print(f"=== CSV Export Complete ===")
print(f"  STOCKS_MASTER.csv:    {len(rows)} stocks × {len(rows[0])} fields")
print(f"  STOCKS_SCREENER.csv:  {len(rows)} stocks × {len(screener_cols)} fields")
print(f"  STOCKS_FINANCIAL.csv: {len(rows)} stocks × {len(fin_cols)} fields")
print(f"  STOCKS_TECHNICAL.csv: {len(rows)} stocks × {len(tech_cols)} fields")
print(f"\n  Summary:")
print(f"    TRIPLE CONFIRMED:  {len(triple)} stocks")
print(f"    BUY or better:     {len(buy_plus)} stocks")
print(f"    EQ A+:             {len(a_plus)} stocks")
print(f"    Near upgrade (<5): {len(near_up)} stocks")
print(f"\n  Files saved to: {REPORT_DIR}")

# Save manifest
manifest = {
    "date": TODAY,
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "files": [
        {"name": "STOCKS_MASTER.csv",    "rows": len(rows), "cols": len(rows[0]),     "desc": "All metrics combined"},
        {"name": "STOCKS_SCREENER.csv",  "rows": len(rows), "cols": len(screener_cols),"desc": "Key fields for screener"},
        {"name": "STOCKS_FINANCIAL.csv", "rows": len(rows), "cols": len(fin_cols),     "desc": "Q1 2026 + April revenue financials"},
        {"name": "STOCKS_TECHNICAL.csv", "rows": len(rows), "cols": len(tech_cols),    "desc": "DNA signals + price technical"},
        {"name": "FULL_REPORT.md",       "rows": len(rows), "cols": 1,                 "desc": "Markdown narrative per stock"},
    ],
    "summary": {
        "total_stocks": len(rows),
        "triple_confirmed": len(triple),
        "buy_or_better": len(buy_plus),
        "eq_a_plus": len(a_plus),
        "near_upgrade": len(near_up),
    }
}
(REPORT_DIR / "export_manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  export_manifest.json saved")
