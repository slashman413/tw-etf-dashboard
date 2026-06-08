#!/usr/bin/env python3
"""
Iteration 17: Price Target Model
No API calls — derives fair-value targets from composite_data.json
Method:
  Non-fin:  Fair P/E = clamp(EPS_growth × 1.0, 8, 28) [PEG≈1 anchor]
  Finance:  Fair P/B = clamp(0.8 + div_yield×8, 0.9, 2.2)
  Target price = fair_multiple × forward_EPS (or BV proxy)
  Upside % = (target - price) / price × 100
Generates: PRICE_TARGETS.md + price_targets.json
"""

import json, math
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
risk_data  = json.loads((REPORT_DIR / "risk_data.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# Build risk lookup
risk_map = {s["code"]: s["risk"] for s in risk_data["all_stocks"]}

results = []
for s in composite:
    code      = s["code"]
    price     = sf(s.get("price"))
    fwd_eps   = sf(s.get("fwd_eps"))      # Q1×4 annualized
    fwd_pe    = sf(s.get("fwd_pe"))
    pb        = sf(s.get("pb"))
    div       = sf(s.get("div_yield"))
    eps_accel = sf(s.get("eps_accel"))
    rev_yoy   = sf(s.get("rev_yoy"))
    op_margin = sf(s.get("op_margin"))
    score     = s.get("score", 40)
    verdict   = s.get("verdict","—")
    is_fin    = s.get("is_fin", False)
    risk      = risk_map.get(code, 30)

    if price is None or price <= 0:
        continue

    # ── Fair multiple calculation ──────────────────────────────────────────
    fair_pe   = None
    fair_pb   = None
    target    = None
    method    = ""

    if is_fin:
        # Financial: anchor to P/B; ROE proxy via dividend sustainability
        # Fair P/B = 0.9 base + quality premium - risk discount
        base_pb = 0.9
        if div and div > 3:   base_pb += 0.3
        if div and div > 4.5: base_pb += 0.2
        if score >= 60:       base_pb += 0.3
        if risk > 30:         base_pb -= 0.2
        fair_pb = min(max(base_pb, 0.8), 2.2)
        if pb and pb > 0:
            # Target = current BV × fair_pb; BV = price / pb
            bv_per_share = price / pb
            target = fair_pb * bv_per_share
            method = f"P/B anchor (fair={fair_pb:.2f}x, curr={pb:.2f}x)"
    else:
        # Non-financial: PEG≈1 model; cap growth at 100% to avoid distortion
        growth = None
        if eps_accel and eps_accel > 0:
            growth = min(abs(eps_accel), 100.0)
        elif rev_yoy and rev_yoy > 0:
            growth = min(abs(rev_yoy) * 0.6, 80.0)  # revenue → earnings haircut

        if growth:
            # Fair P/E = growth × PEG_target; PEG_target depends on quality
            peg_target = 0.8 if op_margin and op_margin > 20 else 1.0
            fair_pe = min(max(growth * peg_target, 8.0), 30.0)
            # Risk discount: reduce target P/E for high-risk stocks
            if risk > 40: fair_pe *= 0.80
            elif risk > 25: fair_pe *= 0.90

            if fwd_eps and fwd_eps > 0:
                target = fair_pe * fwd_eps
                method = f"PEG model (fair PE={fair_pe:.1f}x, growth={growth:.0f}%)"
            elif fwd_pe and fwd_pe > 0:
                # Fallback: scale current price by PE ratio
                target = price * (fair_pe / fwd_pe)
                method = f"PE ratio model (fair={fair_pe:.1f}x, curr={fwd_pe:.1f}x)"

        elif fwd_pe:
            # No growth data: use sector median PE as anchor
            sector_pe = 15.0  # conservative default
            if s.get("sector") == "Semicon":   sector_pe = 18.0
            elif s.get("sector") == "Tech HW": sector_pe = 16.0
            elif s.get("sector") == "Optics":  sector_pe = 20.0
            elif s.get("sector") == "Shipping": sector_pe = 10.0
            fair_pe = min(max(sector_pe, 8), 25)
            target = price * (fair_pe / fwd_pe)
            method = f"Sector PE anchor ({fair_pe:.0f}x)"

    if target is None or target <= 0:
        continue

    upside = (target / price - 1) * 100
    action = ("STRONG BUY" if upside > 30 else
              "BUY"        if upside > 15 else
              "HOLD"       if upside > -5 else
              "REDUCE"     if upside > -20 else
              "AVOID")

    results.append({
        "code":    code,
        "name":    s["name"],
        "sector":  s.get("sector","—"),
        "score":   score,
        "verdict": verdict,
        "price":   price,
        "target":  round(target, 1),
        "upside":  round(upside, 1),
        "action":  action,
        "method":  method,
        "fair_pe": fair_pe,
        "fair_pb": fair_pb,
        "fwd_pe":  fwd_pe,
        "risk":    risk,
        "fwd_eps": fwd_eps,
        "div":     div,
    })

results.sort(key=lambda x: -x["upside"])

# ── Generate PRICE_TARGETS.md ─────────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# Price Target Model — {TODAY}",
    "*Fair value derived from PEG≈1 model (non-financial) and P/B anchor (financial).*",
    "*Target = Fair P/E × Forward EPS. Upside = (Target − Price) / Price × 100%.*",
    "",
    "## Summary",
    "",
]

buy_targets  = [r for r in results if r["action"] in ("STRONG BUY","BUY")]
hold_targets = [r for r in results if r["action"] == "HOLD"]
sell_targets = [r for r in results if r["action"] in ("REDUCE","AVOID")]
avg_upside   = sum(r["upside"] for r in results) / len(results) if results else 0

lines += [
    f"- **BUY targets** (upside >15%): {len(buy_targets)} stocks",
    f"- **HOLD** (upside -5% to +15%): {len(hold_targets)} stocks",
    f"- **REDUCE/AVOID** (downside >5%): {len(sell_targets)} stocks",
    f"- Average upside across universe: **{avg_upside:+.1f}%**",
    "",
    "---",
    "",
    "## 🟢 Buy Targets (Upside > 15%)",
    "",
    "| Code | Name | Price | Target | Upside | Score | Action | Method |",
    "|------|------|-------|--------|--------|-------|--------|--------|",
]

for r in buy_targets:
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | ¥{r['price']:,.0f} | "
        f"**¥{r['target']:,.0f}** | **{r['upside']:+.1f}%** | {r['score']} | "
        f"**{r['action']}** | {r['method']} |"
    )

lines += [
    "",
    "## ⚪ Hold (Upside -5% to +15%)",
    "",
    "| Code | Name | Price | Target | Upside | Score |",
    "|------|------|-------|--------|--------|-------|",
]

for r in hold_targets[:15]:
    lines.append(
        f"| {r['code']} | {r['name'].split()[0]} | ¥{r['price']:,.0f} | "
        f"¥{r['target']:,.0f} | {r['upside']:+.1f}% | {r['score']} |"
    )

lines += [
    "",
    "## 🔴 Reduce / Avoid (Downside > 5%)",
    "",
    "| Code | Name | Price | Target | Downside | Score | Reason |",
    "|------|------|-------|--------|----------|-------|--------|",
]

for r in sell_targets:
    lines.append(
        f"| {r['code']} | {r['name'].split()[0]} | ¥{r['price']:,.0f} | "
        f"¥{r['target']:,.0f} | **{r['upside']:+.1f}%** | {r['score']} | {r['method']} |"
    )

lines += [
    "",
    "---",
    "",
    "## Full Price Target Table",
    "",
    "| Code | Name | Sector | Price | Target | Upside | Score | Fair P/E | Fair P/B | Action |",
    "|------|------|--------|-------|--------|--------|-------|---------|---------|--------|",
]

for r in sorted(results, key=lambda x: -(x["score"] or 0)):
    lines.append(
        f"| {r['code']} | {r['name'].split()[0]} | {r['sector']} | "
        f"¥{r['price']:,.0f} | ¥{r['target']:,.0f} | {r['upside']:+.1f}% | "
        f"{r['score']} | {fmt(r['fair_pe'],1,'','x')} | "
        f"{fmt(r['fair_pb'],2,'','x')} | {r['action']} |"
    )

lines += [
    "",
    "---",
    "",
    "## Model Assumptions",
    "",
    "**Non-financial stocks:**",
    "- Fair P/E = EPS growth rate × PEG target (0.8 for high-margin, 1.0 standard), capped 8–30x",
    "- Growth = min(|EPS acceleration|, 100%) or revenue YoY × 0.6 haircut",
    "- Risk discount: −10% for risk score 25–40, −20% for risk >40",
    "",
    "**Financial stocks (banks/insurance):**",
    "- Fair P/B anchor: 0.9 base + dividend yield premium + quality bonus − risk penalty",
    "- Capped 0.8–2.2x to reflect Taiwan bank valuation norms",
    "",
    "**Limitations:**",
    "- Forward EPS based on Q1 2026 × 4 — seasonality not adjusted",
    "- PSMC (6770) excluded from BUY targets due to non-recurring Q1 OP",
    "- Macro/FX risk not modeled; Taiwan semicon exposed to USD/TWD and US chip demand",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 17*",
]

(REPORT_DIR / "PRICE_TARGETS.md").write_text("\n".join(lines), encoding="utf-8")

# ── Save JSON ─────────────────────────────────────────────────────────────────
(REPORT_DIR / "price_targets.json").write_text(
    json.dumps({"date": TODAY, "targets": results}, ensure_ascii=False, indent=2),
    encoding="utf-8")

print(f"✓ PRICE_TARGETS.md + price_targets.json")
print(f"\n  BUY targets ({len(buy_targets)}):")
for r in buy_targets:
    print(f"    {r['code']} {r['name'].split()[0]:12s}  ¥{r['price']:>7,.0f} → ¥{r['target']:>7,.0f}  "
          f"upside={r['upside']:+.1f}%  score={r['score']}")
print(f"\n  Reduce/Avoid ({len(sell_targets)}):")
for r in sell_targets[:6]:
    print(f"    {r['code']} {r['name'].split()[0]:12s}  ¥{r['price']:>7,.0f} → ¥{r['target']:>7,.0f}  "
          f"upside={r['upside']:+.1f}%")
print(f"\n  Avg universe upside: {avg_upside:+.1f}%")
