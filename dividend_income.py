#!/usr/bin/env python3
"""
Iteration 54: Dividend Income Projection
Forward 12-month dividend schedule for the Kelly portfolio.
Taiwan stocks typically pay annual dividends in July-August.
No API calls. Generates: dividend_income.json
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

bwi     = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))
possize = json.loads((REPORT_DIR/"position_sizing.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
divsus  = json.loads((REPORT_DIR/"dividend_sustainability.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))

bwi_map  = {r["code"]: r for r in bwi.get("all_refreshed",[])}
comp_map = {s["code"]: s for s in comp}
exp_map  = {s["code"]: s for s in expd}
mom_map  = {m["code"]: m for m in mom.get("all_momentum",[])}
earq_map = {r["code"]: r for r in earq.get("all_stocks",[])}

# dividend_sustainability may have different structure; handle gracefully
divsus_map = {}
if isinstance(divsus, list):
    divsus_map = {s.get("code",""): s for s in divsus if s.get("code")}
elif isinstance(divsus, dict):
    for item in divsus.get("stocks", divsus.get("all_stocks", [])):
        if item.get("code"):
            divsus_map[item["code"]] = item

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

PORTFOLIO_SIZE = 1_000_000  # TWD

# Taiwan dividend payment calendar estimates
# Most companies pay in Jul/Aug after AGM (for FY2025 earnings)
# Financial stocks often pay in Aug/Sep
# Some companies pay interim dividends too

SECTOR_EX_MONTHS = {
    "金融保險": "2026-08",    # financials typically Aug
    "半導體":   "2026-07",    # TSMC typically July
    "科技硬體": "2026-07",    # tech hardware July
    "電信":     "2026-07",    # telecom July
    "航運":     "2026-08",    # shipping Aug
    "石化":     "2026-07",    # petrochemicals July
    "水泥":     "2026-07",    # cement July
    "其他":     "2026-07",    # default July
}

# Known specific ex-dividend dates / months (approximate, typical patterns)
KNOWN_EX_DATES = {
    "2330": "2026-07",   # TSMC typically July
    "2317": "2026-07",   # Foxconn July
    "2412": "2026-07",   # Chunghwa July
    "2882": "2026-08",   # Cathay Financial Aug
    "2881": "2026-08",   # Fubon Financial Aug
    "2883": "2026-08",   # CDIB Aug
    "2887": "2026-08",   # Taishin Financial Aug
    "6669": "2026-07",   # Wiwynn July
    "2357": "2026-07",   # ASUS July
}

results = []

for pos in possize.get("positions", []):
    alloc = pos.get("alloc_pct_norm") or 0
    if alloc < 0.5:
        continue

    code  = pos["code"]
    name  = pos["name"]
    bw    = bwi_map.get(code, {})
    cs    = comp_map.get(code, exp_map.get(code, {}))
    mm    = mom_map.get(code, {})
    eq    = earq_map.get(code, {})
    ds    = divsus_map.get(code, {})

    close     = sf(pos.get("close")) or sf(mm.get("close"))
    lots      = pos.get("lots") or 0
    actual_twd= pos.get("actual_twd") or 0
    sector    = pos.get("sector") or "其他"

    # Dividend yield from BWIBBU (most recent)
    dy = sf(bw.get("div_new") or bw.get("div_yield")) or sf(cs.get("div_yield")) or sf(cs.get("div")) or 0

    # Estimate annual dividend per share: yield * price
    div_per_share = (close * dy / 100) if (close and dy) else None

    # Total dividend from our position (lots * 1000 shares * DPS)
    if div_per_share and lots:
        total_div_income = round(lots * 1000 * div_per_share)
    elif div_per_share and actual_twd and close:
        shares = actual_twd / close
        total_div_income = round(shares * div_per_share)
    else:
        total_div_income = None

    # Effective yield on portfolio allocation
    if total_div_income and actual_twd and actual_twd > 0:
        eff_yield = total_div_income / actual_twd * 100
    else:
        eff_yield = dy

    # Ex-dividend date estimate
    ex_month = KNOWN_EX_DATES.get(code) or SECTOR_EX_MONTHS.get(sector, "2026-07")

    # Dividend sustainability assessment
    eq_score = eq.get("eq_score", 0) or 0
    eq9_div  = eq.get("scores", {}).get("EQ9_div_covered", 0)  # EQ9: dividend covered by earnings

    if dy >= 6:         yield_tier = "超高殖利率"
    elif dy >= 4.5:     yield_tier = "高殖利率"
    elif dy >= 3:       yield_tier = "中等殖利率"
    elif dy >= 1:       yield_tier = "低殖利率"
    else:               yield_tier = "近零殖利率"

    # Dividend sustainability score: EQ9 + high EQ overall + revenue growth
    if eq9_div and eq_score >= 8:       div_sustainability = "非常穩健"
    elif eq9_div and eq_score >= 6:     div_sustainability = "穩健"
    elif eq9_div:                        div_sustainability = "普通"
    elif dy > 0 and eq_score >= 6:      div_sustainability = "可能穩健"
    else:                                div_sustainability = "需觀察"

    results.append({
        "code":               code,
        "name":               name.split(" ")[0],
        "sector":             sector,
        "final":              pos.get("final", "—"),
        "grand":              pos.get("grand"),
        # Position
        "alloc_pct":          round(alloc, 2),
        "lots":               lots,
        "actual_twd":         actual_twd,
        "close":              close,
        # Dividend
        "div_yield_pct":      round(dy, 2) if dy else None,
        "div_per_share":      round(div_per_share, 2) if div_per_share else None,
        "total_div_income":   total_div_income,
        "eff_yield_on_alloc": round(eff_yield, 2) if eff_yield else None,
        "ex_month_est":       ex_month,
        "yield_tier":         yield_tier,
        "div_sustainability": div_sustainability,
        "eq9_covered":        bool(eq9_div),
        "eq_score":           eq_score,
    })

# Sort by total dividend income descending
results.sort(key=lambda x: -(x.get("total_div_income") or 0))

# ── Portfolio-level dividend stats ────────────────────────────────────────────
total_annual_income = sum(r["total_div_income"] for r in results if r["total_div_income"])
total_invested_twd  = sum(r["actual_twd"] for r in results if r["actual_twd"])
portfolio_yield     = total_annual_income / total_invested_twd * 100 if total_invested_twd else 0
monthly_income_est  = total_annual_income / 12

# By ex-month: cash flow schedule
monthly_schedule = {}
for r in results:
    if r.get("total_div_income") and r.get("ex_month_est"):
        m = r["ex_month_est"]
        monthly_schedule[m] = monthly_schedule.get(m, 0) + r["total_div_income"]

# ── High-yield picks (yield > 4%) with good EQ ───────────────────────────────
income_picks = [r for r in results
                if (r.get("div_yield_pct") or 0) >= 4
                and (r.get("eq_score") or 0) >= 6]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'DIVIDEND INCOME PROJECTION (1M TWD Kelly Portfolio)':=<65}")
print(f"\n  {'代號':<8} {'名稱':<12} {'殖利率':>7} {'每股股利':>9} {'年股息收入':>11} "
      f"{'預計除息月':>10} {'永續性':>10}")
print("-"*72)
for r in results[:20]:
    dy_s    = ("%.2f%%" % r["div_yield_pct"]) if r["div_yield_pct"] else "—"
    dps_s   = ("%.2f" % r["div_per_share"])   if r["div_per_share"] else "—"
    inc_s   = ("$%d" % r["total_div_income"]) if r["total_div_income"] else "—"
    ex_s    = r.get("ex_month_est","—")
    sus_s   = r.get("div_sustainability","—")
    print(f"  {r['code']:<8} {r['name']:<12} {dy_s:>7} {dps_s:>9} {inc_s:>11} "
          f"{ex_s:>10} {sus_s:>10}")

print(f"\n  Portfolio Summary:")
print(f"    年股息總收入:  TWD {total_annual_income:,}")
print(f"    月均股息:      TWD {monthly_income_est:,.0f}")
print(f"    投資部位殖利率: {portfolio_yield:.2f}%")
print(f"\n  除息月份現金流排程:")
for month, amt in sorted(monthly_schedule.items()):
    print(f"    {month}: TWD {amt:,}")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "portfolio_summary": {
        "total_annual_div_income": total_annual_income,
        "monthly_income_est":      round(monthly_income_est),
        "portfolio_yield_pct":     round(portfolio_yield, 2),
        "total_invested_twd":      total_invested_twd,
        "n_dividend_stocks":       sum(1 for r in results if (r.get("div_yield_pct") or 0) > 0),
        "monthly_schedule":        {k: v for k,v in sorted(monthly_schedule.items())},
    },
    "positions":     results,
    "income_picks":  income_picks,
}
(REPORT_DIR/"dividend_income.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- dividend_income.json saved ({len(results)} positions)")
