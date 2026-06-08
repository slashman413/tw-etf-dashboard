#!/usr/bin/env python3
"""
Iteration 57: Q2 2026 EPS Forward Estimate
Projects Q2 2026 EPS per stock using:
  1. Q1 2026 EPS (from composite_data)
  2. April 2026 revenue YoY + Q1 revenue YoY + momentum signal
  3. Q1 operating margin trend vs sector
  4. Taiwan sector Q1→Q2 seasonality factors
  5. EQ reliability weighting
No API calls. Generates: q2_eps_forecast.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

comp   = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))
aprrev = json.loads((REPORT_DIR/"april_revenue.json").read_text(encoding="utf-8"))
earq   = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))
grand  = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
peer   = json.loads((REPORT_DIR/"peer_comparison.json").read_text(encoding="utf-8"))

# Build lookups
apr_map   = {r["code"]: r for r in aprrev.get("all_results", [])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks", [])}
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map   = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

code_sector = {}
for sec in peer.get("sectors", []):
    for s in sec.get("stocks", []):
        code_sector[s["code"]] = sec["sector"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Taiwan sector Q1→Q2 seasonality ──────────────────────────────────────────
SECTOR_SEASONALITY = {
    "半導體":       1.08,
    "電子零組件":    1.05,
    "資訊科技服務":  1.06,
    "金融保險":      1.04,
    "航運":          1.12,
    "電腦及週邊":    1.03,
    "電機機械":      1.04,
    "通信網路":      1.05,
    "光電":          1.02,
    "其他電子":      1.04,
    "汽車零件":      1.06,
    "鋼鐵":          0.98,
    "化工":          1.01,
}

# Sector operating leverage: revenue → earnings amplification
SECTOR_OP_LEVERAGE = {
    "半導體":    2.0,
    "航運":      2.5,
    "金融保險":  1.2,
    "電腦及週邊":1.5,
    "電子零組件":1.6,
    "光電":      1.8,
}

all_stocks = comp + [s for s in expd if s["code"] not in {x["code"] for x in comp}]

results = []
for s in all_stocks:
    code     = s["code"]
    name     = name_map.get(code, code)
    sector   = code_sector.get(code, "其他")
    g        = grand_map.get(code, {})
    dn       = dna_map.get(code, {})
    eq       = earq_map.get(code, {})
    apr      = apr_map.get(code, {})

    # Core metrics from composite
    q1_eps      = sf(s.get("q1_eps"))
    price       = sf(s.get("price"))
    fwd_pe_curr = sf(s.get("fwd_pe"))     # current Q1-annualized forward PE
    trail_pe    = sf(s.get("trail_pe"))
    eps_accel   = sf(s.get("eps_accel"))  # EPS YoY acceleration %
    op_margin   = sf(s.get("op_margin"))  # Q1 op margin %
    net_margin  = sf(s.get("net_margin")) # Q1 net margin %
    rev_yoy_q1  = sf(apr.get("q1_yoy") or s.get("rev_yoy"))  # Q1 revenue YoY %

    # April revenue data
    apr_yoy     = sf(apr.get("april_yoy"))  # April 2026 vs April 2025
    apr_accel   = sf(apr.get("accel"))      # April YoY - Q1 YoY (acceleration)
    mom_sig     = apr.get("mom_sig", "")

    # Quality
    eq_score    = eq.get("eq_score", 0) or 0
    bull        = dn.get("bull_signs", 0) or 0
    grand_s     = g.get("grand", 0) or 0

    if q1_eps is None or q1_eps <= 0:
        continue

    # ── Q2 Revenue Growth Estimate ────────────────────────────────────────────
    seasonality  = SECTOR_SEASONALITY.get(sector, 1.03)
    op_leverage  = SECTOR_OP_LEVERAGE.get(sector, 1.5)

    # Weighted blend: 60% April YoY + 40% Q1 YoY (April is more recent signal)
    if apr_yoy is not None and rev_yoy_q1 is not None:
        q2_rev_growth = (0.60 * apr_yoy + 0.40 * rev_yoy_q1) / 100
    elif apr_yoy is not None:
        q2_rev_growth = apr_yoy / 100 * 0.8   # slight haircut without Q1 context
    elif rev_yoy_q1 is not None:
        q2_rev_growth = rev_yoy_q1 / 100 * 0.7
    else:
        q2_rev_growth = 0.0

    # Apply sector seasonality uplift (additional factor for Q2)
    q2_rev_growth_adj = q2_rev_growth * (seasonality - 0.95)  # net seasonal increment
    q2_rev_growth_total = q2_rev_growth + q2_rev_growth_adj

    # ── Q2 EPS Estimate ───────────────────────────────────────────────────────
    # EPS growth ≈ revenue growth × operating leverage
    # But high-EQ (reliable) companies: more predictable; low EQ: apply discount
    reliability = 0.55 + (min(eq_score, 10) / 10) * 0.45   # 0.55–1.0

    # Base: Q1 EPS × (1 + rev_growth × leverage) × reliability
    base_eps_growth = q2_rev_growth_total * op_leverage * reliability

    # Cap extreme values: very high revenue growth gets logarithmic dampening
    # (e.g., 南亞科's 717% YoY revenue is extraordinary; EPS doesn't scale linearly)
    if abs(base_eps_growth) > 1.0:
        sign = 1 if base_eps_growth > 0 else -1
        base_eps_growth = sign * (1.0 + (abs(base_eps_growth) - 1.0) ** 0.5)

    # Seasonality base factor (e.g., shipping Q2 structurally higher)
    season_factor = seasonality

    # EPS acceleration bonus: if eps_accel > 50%, Q2 more likely to surprise
    if eps_accel and eps_accel > 50:
        accel_bonus = min(0.05, (eps_accel - 50) / 1000)   # max 5% bonus
    else:
        accel_bonus = 0

    q2_eps_est = round(q1_eps * season_factor * (1 + base_eps_growth + accel_bonus), 2)

    # ── Forward PE (H1 annualized) ─────────────────────────────────────────────
    h1_eps = q1_eps + q2_eps_est
    forward_eps_ann = h1_eps * 2
    if price and forward_eps_ann > 0:
        forward_pe_est = round(price / forward_eps_ann, 1)
    else:
        forward_pe_est = None

    # PE delta vs current
    pe_change = round(forward_pe_est - fwd_pe_curr, 1) if (forward_pe_est and fwd_pe_curr) else None

    # ── Q2 EPS growth rate ────────────────────────────────────────────────────
    q2_eps_growth = round((q2_eps_est / q1_eps - 1) * 100, 1)

    # EPS acceleration check (Q2 growth > implied Q1 growth)
    q1_implied_growth = eps_accel or 0
    eps_acc = (q2_eps_growth > q1_implied_growth + 5) and q2_eps_growth > 0
    eps_dec = (q2_eps_growth < q1_implied_growth - 5) and q2_eps_growth < 0

    # ── Valuation signal ──────────────────────────────────────────────────────
    if forward_pe_est is None or forward_pe_est <= 0:
        val_signal = "—"
    elif forward_pe_est < 8:
        val_signal = "超低估"
    elif forward_pe_est < 12:
        val_signal = "深度低估"
    elif forward_pe_est < 15:
        val_signal = "低估"
    elif forward_pe_est < 20:
        val_signal = "合理"
    elif forward_pe_est < 28:
        val_signal = "略貴"
    else:
        val_signal = "高估"

    results.append({
        "code":             code,
        "name":             name.split(" ")[0] if name else code,
        "sector":           sector,
        "grand":            round(grand_s, 1),
        "final":            g.get("final", ""),
        # Current
        "q1_eps":           q1_eps,
        "price":            price,
        "fwd_pe_curr":      round(fwd_pe_curr, 1) if fwd_pe_curr else None,
        "op_margin":        round(op_margin, 1) if op_margin else None,
        "eps_accel":        round(eps_accel, 1) if eps_accel else None,
        "apr_yoy":          round(apr_yoy, 1) if apr_yoy else None,
        "rev_yoy_q1":       round(rev_yoy_q1, 1) if rev_yoy_q1 else None,
        "apr_accel":        round(apr_accel, 1) if apr_accel else None,
        # Estimates
        "q2_rev_growth_est":round(q2_rev_growth_total * 100, 1),
        "q2_eps_est":       q2_eps_est,
        "q2_eps_growth_pct":q2_eps_growth,
        "forward_eps_ann":  round(forward_eps_ann, 2) if forward_eps_ann else None,
        "forward_pe_est":   forward_pe_est,
        "pe_change":        pe_change,
        "val_signal":       val_signal,
        # Flags
        "eps_acc":          eps_acc,
        "eps_dec":          eps_dec,
        "eq_score":         eq_score,
        "bull_signs":       bull,
        "season_factor":    round(season_factor, 2),
    })

# Sort by Q2 EPS growth desc
results.sort(key=lambda x: -(x.get("q2_eps_growth_pct") or -999))

accelerating = [r for r in results if r.get("eps_acc")]
decelerating = [r for r in results if r.get("eps_dec")]
deep_value   = [r for r in results
                if r.get("val_signal") in ("超低估","深度低估","低估")
                and (r.get("q2_eps_growth_pct") or 0) > 0]
top_growers  = [r for r in results if (r.get("q2_eps_growth_pct") or 0) > 0][:10]
triple_fcst  = [r for r in results if "TRIPLE" in (r.get("final") or "")]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'Q2 2026 EPS FORWARD ESTIMATE':=<65}")
print(f"  Modelled: {len(results)}  Accelerating: {len(accelerating)}  Decelerating: {len(decelerating)}")
print(f"  Deep value+growing: {len(deep_value)}")

print(f"\n  Top Q2 EPS Growth Forecasts:")
print(f"  {'代號':<6} {'名稱':<10} {'Q1 EPS':>8} {'Q2e EPS':>8} {'Q2e%':>7} "
      f"{'FwdPE(e)':>9} {'CurrPE':>7} {'Δ':>5} {'估值'}")
print("-"*90)
for r in top_growers:
    acc = "⬆" if r["eps_acc"] else " "
    curr = f"{r['fwd_pe_curr']:.1f}x" if r["fwd_pe_curr"] else "  —  "
    fwd  = f"{r['forward_pe_est']:.1f}x" if r["forward_pe_est"] else "  —  "
    chg  = f"{r['pe_change']:+.1f}" if r["pe_change"] else " — "
    print(f"  {r['code']:<6} {r['name']:<10} "
          f"{r['q1_eps']:>8.2f} {r['q2_eps_est']:>8.2f} "
          f"{r['q2_eps_growth_pct']:>+6.1f}% {acc}  "
          f"{fwd:>8} {curr:>8} {chg:>5}  {r['val_signal']}")

print(f"\n  TRIPLE持倉 Q2預估:")
for r in triple_fcst:
    print(f"  {r['code']} {r['name']:<10} Q2e={r['q2_eps_est']:.2f}  "
          f"成長={r['q2_eps_growth_pct']:+.1f}%  FwdPE={r['forward_pe_est'] or '—'}  {r['val_signal']}")

if accelerating:
    print(f"\n  EPS加速股:")
    for r in accelerating:
        print(f"  {r['code']} {r['name']:<10} Q2e={r['q2_eps_growth_pct']:+.1f}% > EPS加速={r['eps_accel'] or 0:+.1f}%")

q2g = [r["q2_eps_growth_pct"] for r in results if r["q2_eps_growth_pct"] is not None]
med = statistics.median(q2g) if q2g else 0
fpes = [r["forward_pe_est"] for r in results if r["forward_pe_est"] and 0 < r["forward_pe_est"] < 80]
med_fpe = statistics.median(fpes) if fpes else 0
print(f"\n  宇宙中位 Q2 EPS成長: {med:+.1f}%")
print(f"  宇宙中位 預估PE:     {med_fpe:.1f}x")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "methodology": {
        "q2_rev_growth":  "60%×Apr_YoY + 40%×Q1_YoY + sector_seasonality_adj",
        "q2_eps_formula": "Q1_EPS × seasonality × (1 + rev_growth × op_leverage × reliability)",
        "reliability":    "0.55 + (EQ/10)×0.45",
        "forward_pe":     "price / ((Q1+Q2e)×2)",
        "growth_cap":     "EPS growth >100% gets sqrt dampening",
    },
    "aggregate": {
        "stocks_modelled":     len(results),
        "accelerating":        len(accelerating),
        "decelerating":        len(decelerating),
        "deep_value_growing":  len(deep_value),
        "median_q2_growth_pct":round(med, 1),
        "median_fwd_pe":       round(med_fpe, 1),
    },
    "all_forecasts":   results,
    "accelerating":    accelerating,
    "decelerating":    decelerating,
    "deep_value":      deep_value,
    "top_growers":     top_growers,
    "triple_forecast": triple_fcst,
}
(REPORT_DIR/"q2_eps_forecast.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- q2_eps_forecast.json saved ({len(results)} stocks)")
