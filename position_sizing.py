#!/usr/bin/env python3
"""
Iteration 49: Position Sizing & Kelly Criterion Analysis
Combines backtest win rates, grand scores, and risk metrics into
concrete position size recommendations for a TWD 1M portfolio.
No API calls. Generates: position_sizing.json
"""
import json, math
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
PORTFOLIO_SIZE = 1_000_000   # TWD 1M reference portfolio

grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
bt      = json.loads((REPORT_DIR / "dna_backtest.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR / "earnings_quality.json").read_text(encoding="utf-8"))
sensi   = json.loads((REPORT_DIR / "score_sensitivity.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
peer    = json.loads((REPORT_DIR / "peer_comparison.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
bt_map    = {r["code"]: r for r in bt.get("per_stock",[])}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
sen_map   = {r["code"]: r for r in sensi.get("all_stocks",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}
code_sector = {}
for sec in peer.get("sectors",[]):
    for s in sec.get("stocks",[]):
        code_sector[s["code"]] = sec["sector"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def kelly(win_rate, avg_win_pct, avg_loss_pct):
    """Kelly criterion: f = (p*b - q) / b where b = avg_win/avg_loss"""
    if not win_rate or not avg_win_pct or not avg_loss_pct: return 0
    p = win_rate / 100
    q = 1 - p
    b = abs(avg_win_pct) / abs(avg_loss_pct) if avg_loss_pct else abs(avg_win_pct)
    k = (p * b - q) / b
    return max(0, k)

results = []

all_codes = sorted(set(grand_map.keys()))

for code in all_codes:
    g   = grand_map.get(code, {})
    b   = bt_map.get(code, {})
    bw  = bwi_map.get(code, {})
    rv  = rs_map.get(code, {})
    mm  = mom_map.get(code, {})
    dn  = dna_map.get(code, {})
    eq  = earq_map.get(code, {})
    sn  = sen_map.get(code, {})

    name      = name_map.get(code, code)
    grand_s   = g.get("grand", 0) or 0
    final     = g.get("final", "—")
    sector    = code_sector.get(code, "其他")

    # ── Backtest stats ────────────────────────────────────────────────────────
    win_60  = sf(b.get("win_60d"))   # win rate %
    avg_60  = sf(b.get("avg_60d"))   # avg return % per signal
    n_sigs  = sf(b.get("num_signals"))

    # Estimate avg loss: if avg return is positive with given win rate,
    # back out implied avg loss from: avg = wr*avg_win + (1-wr)*avg_loss
    # We'll use avg_20d as shorter-term estimate for loss sizing
    avg_20  = sf(b.get("avg_20d"))
    win_20  = sf(b.get("win_20d"))

    # Estimate avg_win and avg_loss from aggregate stats
    # avg = win_rate*avg_win + (1-win_rate)*avg_loss
    # Use 60d stats. Assume avg_win / avg_loss ratio ~2:1 for initial estimate
    if win_60 and avg_60 is not None and n_sigs and n_sigs >= 3:
        p = win_60 / 100
        # Solve for avg_win: avg_60 = p*avg_win + (1-p)*(-|loss|)
        # Assume avg_loss = avg_win / 2 (conservative 2:1 reward:risk)
        # Then: avg_60 = p*w - (1-p)*(w/2) → avg_60 = w*(p - (1-p)/2) → w = avg_60 / (p - (1-p)/2)
        denominator = p - (1-p)/2
        if denominator > 0.01:
            est_avg_win  = avg_60 / denominator
            est_avg_loss = est_avg_win / 2
        else:
            # Can't reliably estimate; use simple 1:1 assumption
            est_avg_win  = max(avg_60, 2.0)
            est_avg_loss = est_avg_win
        kelly_f = kelly(win_60, est_avg_win, est_avg_loss)
    else:
        est_avg_win  = None
        est_avg_loss = None
        kelly_f = 0.0

    # Half-Kelly for practical use (reduces overconfidence)
    half_kelly = kelly_f / 2

    # ── Grand-score conviction multiplier ─────────────────────────────────────
    # Scale 0–1 based on grand score:  ≥70→1.0, 60-70→0.8, 50-60→0.6, 40-50→0.4, <40→0.2
    if grand_s >= 70:       conv_mult = 1.0
    elif grand_s >= 65:     conv_mult = 0.9
    elif grand_s >= 60:     conv_mult = 0.8
    elif grand_s >= 55:     conv_mult = 0.65
    elif grand_s >= 50:     conv_mult = 0.5
    elif grand_s >= 45:     conv_mult = 0.35
    elif grand_s >= 40:     conv_mult = 0.2
    else:                    conv_mult = 0.1

    # EQ quality multiplier: A+→1.1, A→1.0, B→0.9, C/D→0.8
    eq_grade = eq.get("grade","") or ""
    if "A+" in eq_grade:    eq_mult = 1.1
    elif eq_grade.startswith("A"): eq_mult = 1.0
    elif eq_grade.startswith("B"): eq_mult = 0.9
    else:                          eq_mult = 0.8

    # DNA bull signal multiplier
    bull_signs = dn.get("bull_signs", 0) or 0
    dna_mult = 0.7 + (bull_signs / 6) * 0.6   # 0.7 at 0/6, 1.3 at 6/6

    # ── Risk adjustment ────────────────────────────────────────────────────────
    pct_52w = sf(rv.get("pct_from_52w_high"))
    pct_ma  = sf(mm.get("pct_vs_ma"))
    pe      = sf(bw.get("pe_new") or bw.get("pe_old"))

    # Distance from 52w high — deeper = higher risk = smaller position
    if pct_52w is None:     risk_52w = 1.0
    elif pct_52w > -5:      risk_52w = 1.0   # near high → momentum, no discount
    elif pct_52w > -15:     risk_52w = 0.95
    elif pct_52w > -30:     risk_52w = 0.85
    elif pct_52w > -50:     risk_52w = 0.7
    else:                    risk_52w = 0.5

    # PE risk: very high PE = higher risk
    if pe is None:          pe_risk = 1.0
    elif pe < 15:           pe_risk = 1.1
    elif pe < 25:           pe_risk = 1.0
    elif pe < 40:           pe_risk = 0.9
    elif pe < 60:           pe_risk = 0.8
    else:                    pe_risk = 0.7

    # Backtest sample size reliability
    if n_sigs is None:          bt_rely = 0.5
    elif n_sigs >= 10:          bt_rely = 1.0
    elif n_sigs >= 5:           bt_rely = 0.85
    elif n_sigs >= 3:           bt_rely = 0.65
    else:                        bt_rely = 0.4

    # ── Combined position size ─────────────────────────────────────────────────
    # Base: half_kelly adjusted by conviction, EQ, DNA, risk, and backtest reliability
    base_alloc = half_kelly * conv_mult * eq_mult * dna_mult * risk_52w * pe_risk * bt_rely

    # Cap at 15% per position; minimum 0.5% to appear in portfolio
    base_alloc = min(base_alloc, 0.15)

    # For non-BUY stocks, further cap
    if "TRIPLE" in final:   max_alloc = 0.15
    elif "STRONG BUY" in final: max_alloc = 0.12
    elif "BUY" in final:    max_alloc = 0.08
    elif "WATCH" in final:  max_alloc = 0.04
    else:                    max_alloc = 0.02

    final_alloc = min(base_alloc, max_alloc)

    # Size in TWD
    size_twd = round(final_alloc * PORTFOLIO_SIZE)

    # Suggested lot size (台股1張=1000股)
    close = sf(mm.get("close"))
    if close and close > 0 and size_twd > 0:
        lots = max(1, round(size_twd / (close * 1000)))
        actual_twd = lots * close * 1000
        actual_alloc = actual_twd / PORTFOLIO_SIZE
    else:
        lots = None
        actual_twd = None
        actual_alloc = final_alloc

    # ── Risk tier ─────────────────────────────────────────────────────────────
    if final_alloc >= 0.10:    risk_tier = "核心持倉"
    elif final_alloc >= 0.06:  risk_tier = "主要持倉"
    elif final_alloc >= 0.03:  risk_tier = "衛星持倉"
    elif final_alloc >= 0.01:  risk_tier = "觀察倉位"
    else:                       risk_tier = "不建議"

    # ── Stop-loss level ───────────────────────────────────────────────────────
    # Use MA30 as primary stop; -8% from current as hard stop
    ma30 = sf(mm.get("ma30"))
    if close and ma30:
        stop_ma    = round(ma30 * 0.98, 1)    # 2% below MA30
        stop_hard  = round(close * 0.92, 1)    # 8% below current
        stop_level = min(stop_ma, stop_hard)   # more conservative (lower)
    elif close:
        stop_level = round(close * 0.92, 1)
    else:
        stop_level = None

    results.append({
        "code": code,
        "name": name,
        "sector": sector,
        "final": final,
        "grand": round(grand_s, 1),
        "bull_signs": bull_signs,
        "eq_grade": eq_grade.split(" ")[0] if eq_grade else "—",
        # Backtest
        "win_60d":   round(win_60, 1) if win_60 else None,
        "avg_60d":   round(avg_60, 2) if avg_60 is not None else None,
        "n_signals": int(n_sigs) if n_sigs else None,
        "est_avg_win":  round(est_avg_win, 2)  if est_avg_win else None,
        "est_avg_loss": round(est_avg_loss, 2) if est_avg_loss else None,
        "kelly_full":   round(kelly_f * 100, 2),
        "kelly_half":   round(half_kelly * 100, 2),
        # Risk factors
        "conv_mult":  round(conv_mult, 2),
        "eq_mult":    round(eq_mult, 2),
        "dna_mult":   round(dna_mult, 2),
        "risk_52w":   round(risk_52w, 2),
        "pe_risk":    round(pe_risk, 2),
        "bt_rely":    round(bt_rely, 2),
        # Final allocation
        "alloc_pct":  round(final_alloc * 100, 2),
        "size_twd":   size_twd,
        "lots":       lots,
        "actual_twd": actual_twd,
        "actual_alloc_pct": round(actual_alloc * 100, 2),
        "risk_tier":  risk_tier,
        # Stop
        "close":      close,
        "ma30":       ma30,
        "stop_level": stop_level,
        "stop_pct":   round((stop_level/close - 1)*100, 1) if (stop_level and close) else None,
        "pe":         pe,
        "pct_52w_high": pct_52w,
    })

# Sort by alloc_pct descending
results.sort(key=lambda x: -(x["alloc_pct"] or 0))

# ── Portfolio-level stats ─────────────────────────────────────────────────────
investable = [r for r in results if r["alloc_pct"] >= 0.5]
core       = [r for r in results if r["risk_tier"] == "核心持倉"]
major      = [r for r in results if r["risk_tier"] == "主要持倉"]
satellite  = [r for r in results if r["risk_tier"] == "衛星持倉"]
watch_pos  = [r for r in results if r["risk_tier"] == "觀察倉位"]

total_alloc = sum(r["alloc_pct"] for r in investable)
# Normalize to 100% if exceeds; keep cash buffer of 20%
MAX_INVESTED = 80   # max 80% invested
if total_alloc > MAX_INVESTED:
    scale = MAX_INVESTED / total_alloc
    for r in results:
        r["alloc_pct_norm"] = round(r["alloc_pct"] * scale, 2)
        r["size_twd_norm"]  = round(r["alloc_pct"] * scale / 100 * PORTFOLIO_SIZE)
else:
    for r in results:
        r["alloc_pct_norm"] = r["alloc_pct"]
        r["size_twd_norm"]  = r["size_twd"]

total_norm = sum(r["alloc_pct_norm"] for r in investable)
cash_pct   = 100 - total_norm

# Expected portfolio return (weighted average of backtest avg_60d)
weighted_return = sum(
    (r["alloc_pct_norm"]/100) * (r["avg_60d"] or 0)
    for r in investable
)

# Sector concentration
sector_alloc = {}
for r in investable:
    sec = r["sector"]
    sector_alloc[sec] = sector_alloc.get(sec, 0) + r["alloc_pct_norm"]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'POSITION SIZING (Kelly Criterion)':=<65}")
print(f"{'代號':<8} {'名稱':<12} {'分配%':>6} {'Kelly%':>7} {'風險層':>8} {'勝率':>6} {'均報':>7} {'止損':>7}")
print("-"*65)
for r in results[:20]:
    wl = ("%.0f%%" % r["win_60d"]) if r["win_60d"] else "—"
    ar = ("%+.1f%%" % r["avg_60d"]) if r["avg_60d"] is not None else "—"
    sl = ("%.1f(%.0f%%)" % (r["stop_level"], r["stop_pct"])) if r["stop_level"] else "—"
    print(f"  {r['code']:<8} {r['name'].split(' ')[0]:<12} "
          f"{r['alloc_pct_norm']:>6.2f}% "
          f"{r['kelly_half']:>6.2f}% "
          f"{r['risk_tier']:>8} "
          f"{wl:>6} {ar:>7} {sl}")

print(f"\n  Portfolio summary:")
print(f"    Core positions:      {len(core)} stocks")
print(f"    Major positions:     {len(major)} stocks")
print(f"    Satellite positions: {len(satellite)} stocks")
print(f"    Total invested:      {total_norm:.1f}%")
print(f"    Cash reserve:        {cash_pct:.1f}%")
print(f"    Expected 60d return: {weighted_return:+.2f}%")
print(f"\n  Sector allocation:")
for sec, pct in sorted(sector_alloc.items(), key=lambda x: -x[1])[:6]:
    print(f"    {sec:<16}: {pct:.1f}%")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "portfolio_size_twd": PORTFOLIO_SIZE,
    "methodology": {
        "kelly": "Full Kelly = (p*b-q)/b; Half-Kelly used for practical sizing",
        "conviction": "Grand score multiplier: ≥70→1.0, 60-70→0.8, 50-60→0.6, <50→0.2",
        "eq_mult": "EQ grade: A+→1.1, A→1.0, B→0.9, C/D→0.8",
        "dna_mult": "DNA bull signs: 0/6→0.7, 3/6→1.0, 6/6→1.3",
        "risk_52w": "Distance from 52w high: near→1.0, -30%→0.85, -50%→0.7",
        "bt_rely":  "Backtest reliability: n≥10→1.0, n≥5→0.85, n≥3→0.65",
        "cap": "Max 15% per position; TRIPLE→15%, STRONG BUY→12%, BUY→8%",
        "stop": "Stop = min(MA30×0.98, close×0.92)",
    },
    "portfolio_summary": {
        "total_invested_pct": round(total_norm, 1),
        "cash_reserve_pct":   round(cash_pct, 1),
        "n_positions":        len(investable),
        "core_positions":     len(core),
        "major_positions":    len(major),
        "satellite_positions": len(satellite),
        "expected_60d_return": round(weighted_return, 2),
        "sector_allocation":   {k: round(v,2) for k,v in sector_alloc.items()},
    },
    "positions": results,
    "investable": investable,
    "core":     core,
    "major":    major,
    "satellite": satellite,
}
(REPORT_DIR / "position_sizing.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ position_sizing.json saved ({len(results)} stocks)")

