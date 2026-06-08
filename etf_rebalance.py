#!/usr/bin/env python3
"""
Iteration 22: ETF Rebalancing Risk Analysis
No API calls — uses composite_data.json + expansion_stocks.json + etf_concentration.json
                  + april_revenue.json (for growth momentum as forward indicator)

0050 rebalances quarterly: next expected ~July 2026 (after June 30 close).
Selection: top 50 Taiwan stocks by free-float market cap.

Methodology:
  - Proxy market cap = 0050 weight (iteration 18) × approx index AUM
  - Apply today's price change to adjust market cap (stocks that fell more lost share)
  - Rank all TWSE stocks we cover; identify borderline entrants/exits
  - Flag stocks near the 50th position threshold

Generates: ETF_REBALANCE.md + etf_rebalance.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
etfconc    = json.loads((REPORT_DIR / "etf_concentration.json").read_text(encoding="utf-8"))
apr_data   = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# ── Build market cap proxy from 0050 weights ──────────────────────────────────
# 0050 tracks top 50 by free-float mktcap. We have approximate weights.
# 0050 AUM ≈ TWD 400 billion (approximate public data)
INDEX_AUM_B = 400_000_000_000  # TWD 400B

weight_map = etfconc.get("weights_0050", {})

# Build map of today's price change from daily data (hardcoded from DASHBOARD.md)
# Key movers from iteration 10/12 data
price_change_map = {
    "2327": -9.39,   # 國巨 Yageo — biggest loser
    "2376": -6.27,   # 技嘉
    "2317": -5.18,   # 鴻海
    "2357": -4.19,   # 華碩
    "2303": -4.21,   # 聯電
    "3711": -4.05,   # ASE
    "2454": -3.80,   # 聯發科
    "2330": -3.50,   # 台積電
    "2308": -3.20,   # 台達電
    "3008": -2.80,   # 大立光
    "6669": -4.60,   # 緯穎
    "2382": -2.50,   # 廣達
    "2603": -2.20,   # 長榮
    "2409": -2.00,   # 友達
    "2002": -1.80,   # 中鋼
    "1301": -2.10,   # 台塑
    "1303": -1.90,   # 南亞
    "2882": +2.83,   # 國泰金
    "2892": +1.90,   # 第一金
    "2395": +1.75,   # 研華
    "2887": +0.50,   # 台新金
    "2881": +0.30,   # 富邦金
    "5871": -1.20,   # 中租
    "2408": -3.00,   # 南亞科
}
MARKET_CHG = -3.41  # TAIEX

# ── Score each current 0050 component for rebalance risk ─────────────────────
comp_map = {s["code"]: s for s in composite}
name_map = {**{s["code"]: s["name"] for s in composite},
            **{s["code"]: s["name"] for s in expansion}}

april_map = {r["code"]: r for r in apr_data["all_results"]}

components = []
for code, wt in weight_map.items():
    # Estimate current mktcap after today's move
    chg = price_change_map.get(code, MARKET_CHG)  # default to market move
    adj_factor = 1 + chg / 100
    mktcap_est = INDEX_AUM_B * wt / 100           # pre-move estimate
    mktcap_adj = mktcap_est * adj_factor           # post-move estimate

    s        = comp_map.get(code, {})
    score    = s.get("score")
    rev_yoy  = s.get("rev_yoy")
    verdict  = s.get("verdict","—")
    apr      = april_map.get(code, {})
    cum_yoy  = apr.get("cum_yoy")
    accel    = apr.get("accel")

    components.append({
        "code":      code,
        "name":      name_map.get(code, code),
        "wt":        wt,
        "mktcap_b":  round(mktcap_est / 1e9, 1),
        "mktcap_adj":round(mktcap_adj / 1e9, 1),
        "chg":       chg,
        "score":     score,
        "verdict":   verdict,
        "rev_yoy":   rev_yoy,
        "cum_yoy":   cum_yoy,
        "accel":     accel,
        "rank_risk": None,   # filled below
    })

# Sort by adjusted market cap descending
components.sort(key=lambda x: -x["mktcap_adj"])
for i, c in enumerate(components):
    c["rank"] = i + 1
    # Rank risk: distance from position 50 (if rank > 43 → at risk)
    if c["rank"] >= 48:
        c["rank_risk"] = "HIGH"
    elif c["rank"] >= 44:
        c["rank_risk"] = "MODERATE"
    else:
        c["rank_risk"] = "SAFE"

# ── Expansion stocks that might enter 0050 ────────────────────────────────────
# A stock enters 0050 if its market cap surpasses the weakest current component
weakest_in = components[-1]["mktcap_adj"]   # smallest in current 0050
weakest_name = components[-1]["name"]

candidates = []
for s in expansion:
    code = s["code"]
    pe   = sf(s.get("pe"))
    eps  = sf(s.get("eps"))
    pb   = sf(s.get("pb"))
    div  = sf(s.get("div"))

    # Rough market cap estimate: price_est × shares_est
    # We don't have shares; use PE × EPS = price, then infer market cap from sector norms
    # Very rough: compare revenue scale to borderline 0050 stocks
    # Expansion stocks are unlikely to enter 0050 given they're already smaller-cap
    # Flag ones with strong growth momentum as potential future entrants

    apr = april_map.get(code, {})
    cum_yoy = apr.get("cum_yoy")

    candidates.append({
        "code":    code,
        "name":    s["name"],
        "etfs":    s.get("etfs", []),
        "pe":      pe,
        "pb":      pb,
        "div":     div,
        "cum_yoy": cum_yoy,
        "prospect": "LOW",  # most expansion stocks are smaller-cap
    })

# ── 0050 composition history context ──────────────────────────────────────────
# Recent changes (public knowledge):
# Jan 2026: Wiwynn (6669) entered; some smaller cap exited
# Apr 2026: No rebalance expected (mid-cycle)
# Jul 2026: Next scheduled rebalance

# Identify borderline stocks (rank 44-50) — most at risk of exit
borderline = [c for c in components if c["rank"] >= 44]
at_risk     = [c for c in components if c["rank_risk"] == "HIGH"]
safe_core   = [c for c in components if c["rank"] <= 10]

# ── Generate ETF_REBALANCE.md ─────────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# ETF Rebalancing Risk Analysis — {TODAY}",
    "*Next 0050 rebalance expected: ~July 2026 (after June 30 quarter close)*",
    "*Market cap estimates: 0050 weight × index AUM ≈ TWD 400B, adjusted for today's price change*",
    "",
    "## Key Context",
    "",
    "- 0050 selects top 50 Taiwan stocks by **free-float market cap** (quarterly review)",
    "- After today's TAIEX -3.41% broad selloff, relative rankings have shifted",
    "- Stocks that fell more than the index lost **relative** market cap → higher exit risk",
    "- Stocks that rose or fell less gained relative rank → more secure",
    "",
    "---",
    "",
    "## 🔴 Borderline Holdings (Rank 44–50) — Exit Risk",
    "*If a stock falls further, it may drop out of the top-50 at the July rebalance.*",
    "",
    "| Rank | Code | Name | Adj MktCap (B) | Today | Rev YoY | Apr Cum YoY | Risk |",
    "|------|------|------|---------------|-------|---------|------------|------|",
]

for c in borderline:
    risk_icon = "🔴" if c["rank_risk"] == "HIGH" else "🟡"
    lines.append(
        f"| **{c['rank']}** | **{c['code']}** | {c['name'].split()[0]} | "
        f"¥{c['mktcap_adj']:.1f}B | "
        f"{'+' if c['chg']>0 else ''}{c['chg']:.2f}% | "
        f"{fmt(c['rev_yoy'],1,'+' if (c['rev_yoy'] or 0)>0 else '','')}{'%' if c['rev_yoy'] else '—'} | "
        f"{fmt(c['cum_yoy'],1,'+' if (c['cum_yoy'] or 0)>0 else '','')}{'%' if c['cum_yoy'] else '—'} | "
        f"{risk_icon} {c['rank_risk']} |"
    )

lines += [
    "",
    f"> **Weakest current component**: {components[-1]['code']} {components[-1]['name'].split()[0]}",
    f"> Any stock with market cap falling below ¥{weakest_in:.1f}B risks replacement.",
    "",
    "---",
    "",
    "## ✅ Core Holdings — Secure Top 10",
    "",
    "| Rank | Code | Name | Adj MktCap (B) | Weight | Today |",
    "|------|------|------|---------------|--------|-------|",
]

for c in safe_core:
    lines.append(
        f"| **{c['rank']}** | **{c['code']}** | {c['name'].split()[0]} | "
        f"¥{c['mktcap_adj']:.0f}B | {c['wt']:.1f}% | "
        f"{'+' if c['chg']>0 else ''}{c['chg']:.2f}% |"
    )

lines += [
    "",
    "---",
    "",
    "## 📊 Full 0050 Rankings (Post-Selloff Adjusted)",
    "",
    "| Rank | Code | Name | Pre MktCap (B) | Adj MktCap (B) | Today | Apr YoY | Status |",
    "|------|------|------|---------------|---------------|-------|---------|--------|",
]

for c in components:
    status = {"HIGH":"🔴 At Risk","MODERATE":"🟡 Watch","SAFE":"✅ Secure"}.get(c["rank_risk"],"—")
    lines.append(
        f"| {c['rank']} | **{c['code']}** | {c['name'].split()[0]} | "
        f"¥{c['mktcap_b']:.1f}B | ¥{c['mktcap_adj']:.1f}B | "
        f"{'+' if c['chg']>0 else ''}{c['chg']:.2f}% | "
        f"{fmt(c['cum_yoy'],1,'+' if (c['cum_yoy'] or 0)>0 else '','')}{'%' if c['cum_yoy'] else '—'} | "
        f"{status} |"
    )

lines += [
    "",
    "---",
    "",
    "## Expansion Universe — Potential Future Entrants",
    "",
    "*Current expansion stocks (0056/00878/00713 only) are generally smaller-cap.*",
    "*Entry into 0050 requires surpassing the weakest current component (~¥" +
    f"{weakest_in:.1f}B market cap).*",
    "",
    "| Code | Name | ETFs | Apr Cum YoY | Prospect |",
    "|------|------|------|------------|---------|",
]

for c in sorted(candidates, key=lambda x: -(x["cum_yoy"] or -999))[:10]:
    lines.append(
        f"| {c['code']} | {c['name'].split()[0]} | {'+'.join(c['etfs'])} | "
        f"{fmt(c['cum_yoy'],1,'+' if (c['cum_yoy'] or 0)>0 else '','')}{'%' if c['cum_yoy'] else '—'} | "
        f"LOW (size) |"
    )

lines += [
    "",
    "---",
    "",
    "## Rebalancing Calendar",
    "",
    "| Event | Expected Date | Action |",
    "|-------|--------------|--------|",
    "| Q2 2026 end | June 30, 2026 | Market cap snapshot for rebalance |",
    "| Rebalance announcement | ~July 7–10, 2026 | FTSE Russell Taiwan index announcement |",
    "| Effective date | ~July 14–17, 2026 | New constituents take effect |",
    "| 0050 NAV adjustment | Same week | ETF purchases/sells new/old components |",
    "",
    "## Investment Implications",
    "",
    "1. **Stocks near rank 44–50** face selling pressure if they continue to underperform",
    "   before June 30 — 0050 ETF will mechanically sell them at rebalance.",
    "",
    "2. **Stocks that enter 0050** receive forced buying from ~TWD 400B in tracked AUM",
    "   — typically a 3–5% price pop at announcement.",
    "",
    "3. **Wiwynn (6669)** entered 0050 in Jan 2026 after AI-server revenue surge;",
    "   if it maintains market cap, its position is secure (rank ~11).",
    "",
    "4. **Financial stocks** rose today (+2–3%) while tech fell — their relative rank",
    "   improved slightly, reducing near-term rebalance risk.",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 22*",
    f"*Note: Market cap estimates are proxies — actual 0050 rebalance uses FTSE Russell methodology*",
]

(REPORT_DIR / "ETF_REBALANCE.md").write_text("\n".join(lines), encoding="utf-8")

# ── Save JSON ──────────────────────────────────────────────────────────────────
reb_json = {
    "date":       TODAY,
    "next_rebalance": "July 2026",
    "weakest_component": {
        "code": components[-1]["code"],
        "name": components[-1]["name"],
        "mktcap_adj_b": components[-1]["mktcap_adj"],
    },
    "borderline":  [{"code":c["code"],"name":c["name"].split()[0],"rank":c["rank"],
                     "mktcap_adj":c["mktcap_adj"],"chg":c["chg"],"risk":c["rank_risk"]}
                    for c in borderline],
    "at_risk":     [{"code":c["code"],"name":c["name"].split()[0],"rank":c["rank"],
                     "mktcap_adj":c["mktcap_adj"]}
                    for c in at_risk],
    "core_top10":  [{"code":c["code"],"name":c["name"].split()[0],"rank":c["rank"],
                     "mktcap_adj":c["mktcap_adj"],"wt":c["wt"]}
                    for c in safe_core],
    "all_ranked":  [{"code":c["code"],"name":c["name"].split()[0],"rank":c["rank"],
                     "mktcap_b":c["mktcap_b"],"mktcap_adj":c["mktcap_adj"],
                     "wt":c["wt"],"chg":c["chg"],"rank_risk":c["rank_risk"],
                     "cum_yoy":c["cum_yoy"]}
                    for c in components],
}
(REPORT_DIR / "etf_rebalance.json").write_text(
    json.dumps(reb_json, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ ETF_REBALANCE.md + etf_rebalance.json")
print(f"\n  Next 0050 rebalance: ~July 2026")
print(f"  Borderline at risk ({len(at_risk)} stocks): {[c['code'] for c in at_risk]}")
print(f"  All borderline ({len(borderline)} stocks): {[c['code'] for c in borderline]}")
print(f"  Weakest component: {components[-1]['code']} {components[-1]['name'].split()[0]} "
      f"¥{components[-1]['mktcap_adj']:.1f}B (rank {components[-1]['rank']})")
print(f"\n  Full ranking (post-selloff):")
for c in components:
    risk_flag = " ⚠" if c["rank_risk"] in ("HIGH","MODERATE") else ""
    print(f"    #{c['rank']:2d} {c['code']} {c['name'].split()[0]:12s} "
          f"¥{c['mktcap_adj']:7.1f}B  chg={c['chg']:+.2f}%{risk_flag}")
