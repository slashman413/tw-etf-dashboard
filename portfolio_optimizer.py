#!/usr/bin/env python3
"""
Iteration 34: Portfolio Optimizer
Uses existing correlation matrix + historical returns to find optimal allocations.
No API calls — pure computation on existing JSON data.
Generates: portfolio_optimizer.json
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
RNG        = np.random.default_rng(42)

# ── Load existing data ────────────────────────────────────────────────────────
rs    = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
grand = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna   = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
mom   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
comp  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp   = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

name_map   = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}
grand_map  = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map    = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
mom_map    = {m["code"]: m for m in mom.get("all_momentum", [])}
rs_map     = {r["code"]: r for r in rs.get("all_rs", [])}

# ── Correlation matrix (top-30 stocks) ───────────────────────────────────────
corr_codes  = rs.get("corr_codes", [])
corr_matrix = np.array(rs.get("corr_matrix", []))
print(f"Correlation matrix: {len(corr_codes)} stocks × {len(corr_codes)}")

# ── Build universe: BUY or better ────────────────────────────────────────────
universe = []
for code, gr in grand_map.items():
    final = gr.get("final", "")
    if not any(tag in final for tag in ["TRIPLE", "STRONG BUY", "BUY"]):
        continue
    r = rs_map.get(code, {})
    d = dna_map.get(code, {})
    m = mom_map.get(code, {})
    universe.append({
        "code":       code,
        "name":       name_map.get(code, code),
        "grand":      gr.get("grand", 40),
        "final":      final,
        "ret_20d":    r.get("ret_20d", 0) or 0,
        "ret_60d":    r.get("ret_60d", 0) or 0,
        "rs_60d":     r.get("rs_60d",  0) or 0,
        "pct_52w_hi": r.get("pct_from_52w_high") or 0,
        "bull_signs": d.get("bull_signs", 0) or 0,
        "pct_ma":     m.get("pct_vs_ma",  0) or 0,
    })

universe.sort(key=lambda x: -x["grand"])
print(f"Investment universe: {len(universe)} stocks")

# ── Expected return estimate ──────────────────────────────────────────────────
# Blend: 50% 60d historical return, 30% grand score convexity, 20% RS momentum
for u in universe:
    hist_ret = u["ret_60d"] / 60 * 252  # annualize 60d return
    conv_ret = (u["grand"] - 40) * 0.5  # conviction premium
    rs_boost = u["rs_60d"] * 0.3
    u["exp_ret"] = round(hist_ret * 0.5 + conv_ret * 0.3 + rs_boost * 0.2, 2)

# ── Build covariance sub-matrix for investable stocks ────────────────────────
def build_cov_matrix(codes, corr_codes, corr_mat, rs_data):
    """Build cov matrix: use correlation if available, else assume moderate corr."""
    n = len(codes)
    cov = np.zeros((n, n))
    # Individual std devs from 60d return (rough annualized vol estimate)
    stds = []
    for code in codes:
        r = rs_data.get(code, {})
        # Use 20d return volatility proxy: abs(ret_20d) * sqrt(252/20) / 100
        ret20 = abs(r.get("ret_20d", 10) or 10)
        vol   = ret20 * np.sqrt(252/20) / 100  # annualized vol
        stds.append(max(0.15, min(0.80, vol)))  # clamp to 15%-80%

    code_idx = {c: i for i, c in enumerate(corr_codes)}
    for i, ci in enumerate(codes):
        for j, cj in enumerate(codes):
            if i == j:
                cov[i, j] = stds[i] ** 2
            elif ci in code_idx and cj in code_idx:
                r_val = corr_mat[code_idx[ci], code_idx[cj]]
                cov[i, j] = r_val * stds[i] * stds[j]
            else:
                cov[i, j] = 0.35 * stds[i] * stds[j]  # assume 0.35 corr for unknowns
    return cov, stds

# Limit to top 20 by grand score (keep portfolio focused)
top20 = universe[:20]
codes = [u["code"] for u in top20]
exp_returns = np.array([u["exp_ret"] for u in top20]) / 100  # to decimal
cov, vols = build_cov_matrix(codes, corr_codes, corr_matrix, rs_map)

RISK_FREE = 0.02  # 2% risk-free rate

# ── Monte Carlo portfolio optimization ───────────────────────────────────────
N_SIM    = 50_000
n_assets = len(codes)
all_w    = RNG.dirichlet(np.ones(n_assets), N_SIM)  # random weights summing to 1

# Apply conviction floor + ceiling
# TRIPLE CONFIRMED: 5-20%, STRONG BUY: 3-15%, BUY: 2-10%
floors = []
ceils  = []
for u in top20:
    if   "TRIPLE" in u["final"]:    floors.append(0.03); ceils.append(0.20)
    elif "STRONG" in u["final"]:    floors.append(0.02); ceils.append(0.15)
    else:                           floors.append(0.01); ceils.append(0.10)
floors = np.array(floors)
ceils  = np.array(ceils)

# Project onto feasible set (clip then renormalize)
all_w = np.clip(all_w, floors, ceils)
all_w = all_w / all_w.sum(axis=1, keepdims=True)

port_ret  = all_w @ exp_returns
port_var  = np.array([w @ cov @ w for w in all_w])
port_std  = np.sqrt(np.maximum(port_var, 0))
port_sharpe = (port_ret - RISK_FREE) / (port_std + 1e-9)

idx_maxS = int(np.argmax(port_sharpe))
idx_minV = int(np.argmin(port_std))

w_maxS = all_w[idx_maxS]
w_minV = all_w[idx_minV]

# ── Risk Parity weights ───────────────────────────────────────────────────────
inv_vol = 1 / np.array(vols)
w_rp    = inv_vol / inv_vol.sum()

# ── Equal weight baseline ────────────────────────────────────────────────────
w_eq = np.ones(n_assets) / n_assets

# ── Grand-conviction weighted ─────────────────────────────────────────────────
g_scores = np.array([u["grand"] - 40 for u in top20])  # excess over threshold
g_scores = np.maximum(g_scores, 0)
w_conv   = g_scores / (g_scores.sum() + 1e-9)

# ── Portfolio metrics ─────────────────────────────────────────────────────────
def port_metrics(w, label):
    ret = float(w @ exp_returns) * 100
    std = float(np.sqrt(w @ cov @ w)) * 100
    sr  = (ret/100 - RISK_FREE) / (std/100 + 1e-9)
    return {"label": label, "ann_return_pct": round(ret,1), "ann_vol_pct": round(std,1),
            "sharpe": round(sr,2)}

portfolios_meta = [
    port_metrics(w_maxS, "最大夏普率"),
    port_metrics(w_minV, "最小波動率"),
    port_metrics(w_rp,   "風險平價"),
    port_metrics(w_conv, "信念加權"),
    port_metrics(w_eq,   "等權"),
]

# ── Build allocation tables ───────────────────────────────────────────────────
def alloc_table(w, label, top20):
    items = []
    for i, (code, wt) in enumerate(zip(codes, w)):
        u = top20[i]
        items.append({
            "code": code, "name": u["name"],
            "weight_pct": round(float(wt)*100, 1),
            "grand": u["grand"], "final": u["final"],
            "bull_signs": u["bull_signs"],
            "exp_ret_pct": u["exp_ret"],
            "vol_pct": round(vols[i]*100, 1),
        })
    items.sort(key=lambda x: -x["weight_pct"])
    return {"label": label, "allocations": items}

alloc_maxS = alloc_table(w_maxS, "最大夏普率", top20)
alloc_minV = alloc_table(w_minV, "最小波動率", top20)
alloc_rp   = alloc_table(w_rp,   "風險平價",   top20)
alloc_conv = alloc_table(w_conv, "信念加權",   top20)

# ── Efficient frontier curve (20 points) ─────────────────────────────────────
ef_pts = []
for q in np.linspace(0, 1, 20):
    idx = int(q * (N_SIM - 1))
    sorted_by_ret = np.argsort(port_ret)
    w_pt = all_w[sorted_by_ret[idx]]
    ef_pts.append({
        "ret": round(float(w_pt @ exp_returns)*100, 1),
        "vol": round(float(np.sqrt(w_pt @ cov @ w_pt))*100, 1),
    })

# ── Concentration risk analysis ───────────────────────────────────────────────
high_corr = rs.get("high_corr_pairs", [])
risk_pairs = [p for p in high_corr if p["a"] in codes and p["b"] in codes]

# ── Print summary ─────────────────────────────────────────────────────────────
print(f"\n=== Portfolio Optimization Results ===")
print(f"Universe: {len(universe)} buy candidates | Optimized: {n_assets} stocks")
print(f"\nPortfolio Comparison:")
for m in portfolios_meta:
    print(f"  {m['label']:<10} ret={m['ann_return_pct']:+5.1f}% vol={m['ann_vol_pct']:4.1f}% SR={m['sharpe']:.2f}")

print(f"\nMax Sharpe Allocation (top 10):")
for a in alloc_maxS["allocations"][:10]:
    print(f"  {a['code']} {a['name'][:8]:<8} {a['weight_pct']:5.1f}% | SR:{a['grand']:.0f} {a['final'][:15]}")

print(f"\nConcentration risks (r>0.7 in portfolio): {len(risk_pairs)}")
for p in risk_pairs[:5]:
    print(f"  {p['a']} ↔ {p['b']}: r={p['r']:.2f}")

# ── Save ──────────────────────────────────────────────────────────────────────
out = {
    "date":        TODAY,
    "fetch_ts":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "n_universe":  len(universe),
    "n_optimized": n_assets,
    "n_simulated": N_SIM,
    "risk_free":   RISK_FREE,
    "universe":    universe,
    "portfolios_meta": portfolios_meta,
    "max_sharpe":  alloc_maxS,
    "min_vol":     alloc_minV,
    "risk_parity": alloc_rp,
    "conviction":  alloc_conv,
    "efficient_frontier": ef_pts,
    "concentration_risk": risk_pairs[:20],
    "optimal_codes": codes,
}
(REPORT_DIR / "portfolio_optimizer.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ portfolio_optimizer.json saved ({n_assets} stocks, {N_SIM:,} simulations)")
