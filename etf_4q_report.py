#!/usr/bin/env python3
"""
Generate comprehensive 4Q financial report for all ETF component stocks.
Covers 0050, 0056 (expansion), 00878, 00713, 006208.
Outputs: reports/YYYYMMDD/etf_4q_report.json + prints per-ETF summaries.
No API calls needed — uses cached data.
"""
import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

# ── Load all sources ─────────────────────────────────────────────────────────
grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
qf      = json.loads((REPORT_DIR / "quarterly_financials.json").read_text(encoding="utf-8"))
etfc    = json.loads((REPORT_DIR / "etf_concentration.json").read_text(encoding="utf-8"))
bwibbu  = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
revenue = json.loads((REPORT_DIR / "may_revenue_raw.json").read_text(encoding="utf-8"))
_mom_path = REPORT_DIR / "price_momentum.json"
mom_prices = {m["code"]: m.get("close") for m in
              (json.loads(_mom_path.read_text(encoding="utf-8")).get("all_momentum", [])
               if _mom_path.exists() else [])}

# Build lookup maps
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
comp_map  = {c["code"]: c for c in comp}
qf_map    = {c["code"]: c for c in qf.get("companies", [])}
bw_map    = {r["code"]: r for r in bwibbu.get("all_refreshed", [])}
rev_map   = {}
for r in revenue.get("raw", []):
    code = r.get("公司代號", "").strip()
    try: yoy = float(str(r.get("營業收入-去年同月增減(%)", "")).replace(",", ""))
    except: yoy = None
    try: rev = float(str(r.get("營業收入-當月營收", "")).replace(",", ""))
    except: rev = None
    rev_map[code] = {"yoy": yoy, "rev": rev, "name": r.get("公司名稱", "")}

# ── ETF component definitions ──────────────────────────────────────────────
ETF_COMPONENTS = {
    "0050": list(etfc.get("weights_0050", {}).keys()),
    "0056": [  # 元大高股息 — top high-yield components
        "2412","3045","2603","2609","2615","2882","2881","2886","2891","2884",
        "5880","2892","2887","2890","2801","2883","5876","5871","2880","2888",
        "1216","1101","1102","1301","1303","2002","2207","1590","2912","4904",
        "6488","2823","3481",
    ],
    "00878": [  # 國泰永續高股息 ESG
        "2330","2317","2382","2412","2603","2886","2892","5880","2881","2882",
        "2884","2891","2801","3711","2395","1216","2207","2308","3008","2379",
        "3034","2327","2303","1301","1303","2357","2376","2609","3231","2383",
        "6488","2049","1590",
    ],
    "00713": [  # 元大台灣高息低波
        "2412","3045","2603","2609","2615","1216","2207","2801","5880","2892",
        "2886","2884","2887","2890","2891","5876","2882","2881","5871","2883",
        "1101","1102","2002","1301","1303","2379","2395","3034","2301","2337",
        "2352","2327","2409","4938","2303","6415","6770","2376","3711","2308",
        "3008","2357","2454","6669","2382","2317","2330","2880","2344","3481",
    ],
    "006208": [  # 富邦台灣50
        "2330","2317","2454","2882","2881","2308","3008","2412","2382","2303",
        "2886","2891","2357","2603","2379","2395","2884","5880","2002","1301",
        "1303","2207","2615","2609","2892","5871","6669","3711","2327","2408",
        "2887","1216","1101","2409","3045","4938","2376","3034","6770","2801",
        "2883","2890","1102","2301","5876","2337","2352","6415","3037",
    ],
}

def get_stock_data(code):
    g  = grand_map.get(code, {})
    c  = comp_map.get(code, {})
    q  = qf_map.get(code, {})
    bw = bw_map.get(code, {})
    rv = rev_map.get(code, {})
    return {
        "code":       code,
        "name":       g.get("name") or c.get("name") or q.get("name") or rv.get("name", ""),
        "sector":     c.get("sector") or q.get("sector", ""),
        "grand":      g.get("grand"),
        "final":      g.get("final", ""),
        "eps_q1":     q.get("eps") or c.get("q1_eps"),
        "trail_eps":  c.get("trail_eps"),
        "fwd_eps":    c.get("fwd_eps"),
        "trail_pe":   c.get("trail_pe") or bw.get("pe_new"),
        "fwd_pe":     c.get("fwd_pe"),
        "pb":         bw.get("pb_new") or c.get("pb"),
        "div_yield":  bw.get("div_new") or bw.get("div_yield") or c.get("div_yield"),
        "op_margin":  q.get("op_margin") or c.get("op_margin"),
        "net_margin": q.get("net_margin") or c.get("net_margin"),
        "gross_margin": q.get("gross_margin"),
        "rev_yoy":    rv.get("yoy"),
        "price":      mom_prices.get(code) or c.get("price"),
        "verdict":    g.get("final") or c.get("verdict", ""),
    }

# ── Generate per-ETF analysis ─────────────────────────────────────────────
print(f"[{datetime.now():%H:%M:%S}] === ETF 4Q Financial Report ===")
print(f"  Report dir: {REPORT_DIR}\n")

etf_reports = {}
for etf_code, codes in ETF_COMPONENTS.items():
    codes = list(dict.fromkeys(codes))  # deduplicate
    stocks = [get_stock_data(c) for c in codes]

    # Compute ETF-level metrics
    with_eps  = [s for s in stocks if s.get("eps_q1") is not None]
    with_pe   = [s for s in stocks if s.get("trail_pe") and s["trail_pe"] > 0]
    with_div  = [s for s in stocks if s.get("div_yield") and s["div_yield"] > 0]
    with_yoy  = [s for s in stocks if s.get("rev_yoy") is not None]

    avg_pe  = sum(s["trail_pe"] for s in with_pe) / len(with_pe) if with_pe else None
    avg_div = sum(s["div_yield"] for s in with_div) / len(with_div) if with_div else None
    avg_yoy = sum(s["rev_yoy"] for s in with_yoy) / len(with_yoy) if with_yoy else None
    avg_eps = sum(s["eps_q1"] for s in with_eps) / len(with_eps) if with_eps else None

    top_eps  = sorted(with_eps, key=lambda x: -(x["eps_q1"] or 0))[:5]
    top_div  = sorted(with_div, key=lambda x: -(x["div_yield"] or 0))[:5]
    buys     = [s for s in stocks if "BUY" in (s.get("verdict") or "") or "STRONG" in (s.get("verdict") or "")]
    triple   = [s for s in stocks if "TRIPLE" in (s.get("final") or "")]

    etf_reports[etf_code] = {
        "etf": etf_code,
        "stock_count": len(stocks),
        "eps_coverage": f"{len(with_eps)}/{len(stocks)}",
        "avg_pe": round(avg_pe, 1) if avg_pe else None,
        "avg_div_yield": round(avg_div, 2) if avg_div else None,
        "avg_rev_yoy": round(avg_yoy, 1) if avg_yoy else None,
        "avg_eps_q1": round(avg_eps, 2) if avg_eps else None,
        "top_eps": [{"code": s["code"], "name": s["name"][:8], "eps": s["eps_q1"]} for s in top_eps],
        "top_div": [{"code": s["code"], "name": s["name"][:8], "yield": s["div_yield"]} for s in top_div],
        "triple_confirmed": [{"code": s["code"], "name": s["name"][:8], "grand": s["grand"]} for s in triple],
        "buy_count": len(buys),
        "stocks": stocks,
    }

    # Print summary
    etf_names = {"0050":"元大台灣50","0056":"元大高股息","00878":"國泰永續高股息","00713":"元大台灣高息低波","006208":"富邦台灣50"}
    print(f"  ══ {etf_code} {etf_names.get(etf_code,'')} ══")
    print(f"     成份股: {len(stocks)}  EPS覆蓋: {len(with_eps)}/{len(stocks)}  買入: {len(buys)}")
    if avg_pe:   print(f"     平均本益比: {avg_pe:.1f}x  平均殖利率: {avg_div:.2f}%  平均營收YoY: {avg_yoy:+.1f}%")
    print(f"     Q1 EPS Top 3: {[(s['code'], round(s['eps_q1'],2)) for s in top_eps[:3]]}")
    if triple:   print(f"     TRIPLE CONFIRMED: {[(s['code'], s['name'][:6]) for s in triple]}")
    print()

# ── Save report ────────────────────────────────────────────────────────────
out = {
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "data_period": "115Q1 (Q1 2026)",
    "etfs": etf_reports,
}
out_path = REPORT_DIR / "etf_4q_report.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved: {out_path} ({out_path.stat().st_size//1024} KB)")
print(f"\n[{datetime.now():%H:%M:%S}] === Done ===")
