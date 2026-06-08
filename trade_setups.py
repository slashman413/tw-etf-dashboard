#!/usr/bin/env python3
"""
Iteration 23: Trade Setup Cards — Actionable Investment Instructions
No API calls — synthesizes conviction_data.json + price_targets.json +
               risk_data.json + technical_data.json + margin_data.json

For each STRONG BUY / BUY stock:
  - Entry zone: current price ± bid-ask buffer (0.5%)
  - Stop-loss: max(10% below entry, nearest technical support proxy)
  - Price target: from PEG model (iteration 17)
  - Risk/Reward ratio: (target − entry) / (entry − stop)
  - Position size: 2% portfolio risk rule
    position_pct = 2% / stop_loss_pct  (% of portfolio in this stock)
  - Expected holding period: months to reach target assuming EPS-growth-rate price appreciation
  - Catalysts to watch

Generates: TRADE_SETUPS.md + trade_setups.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

conviction = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))
ptargets   = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
riskdata   = json.loads((REPORT_DIR / "risk_data.json").read_text(encoding="utf-8"))
technical  = json.loads((REPORT_DIR / "technical_data.json").read_text(encoding="utf-8"))
margin     = json.loads((REPORT_DIR / "margin_data.json").read_text(encoding="utf-8"))
composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))

def sf(v):
    try: return float(v) if v is not None else None
    except: return None

# Build lookup maps
target_map    = {t["code"]: t for t in ptargets["targets"]}
risk_map      = {s["code"]: s for s in riskdata["all_stocks"]}
comp_map      = {s["code"]: s for s in composite}
margin_map    = {k: v for k, v in margin.items() if isinstance(v, dict)}
bounce_map    = {x["code"]: x for x in technical.get("bounce_candidates", [])}
momentum_map  = {x["code"]: x for x in technical.get("momentum_intact", [])}
triple_set    = set(technical.get("triple_confirmed", []))

# ── Catalysts database ─────────────────────────────────────────────────────────
CATALYSTS = {
    "2376": ["Q2 2026 server GPU分銷業績", "AI PC/工作站需求加速", "股息記錄日(推估7月)"],
    "2357": ["Q2 EPS確認(DRAM/AI PC)", "GameFest新品發表", "技術性超賣反彈機會"],
    "2887": ["Q2淨利息收入成長", "Fed利率決策(維持或降息)", "金融股殖利率配息(7月)"],
    "5871": ["Q2租賃業務量增長", "台灣利率環境", "殖利率5%+支撐評價"],
    "2408": ["DRAM現貨價格趨勢", "三星/SK Hynix減產效果", "AI記憶體規格升級"],
    "5876": ["Q2存款/放款利差", "台灣利率維持高位", "特殊殖利率高達4.9%"],
    "1303": ["石化品景氣復甦時程", "原油價格走勢", "下半年需求改善預期"],
    "2801": ["Q2利差收入", "金融改革紅利", "殖利率4.9% + 目標價+53%"],
    "2883": ["Q2淨利改善", "資本利得強勁", "IFRS17比較基期"],
    "3008": ["iPhone 17系列採購", "Vision Pro 2鏡頭規格", "Apple供應鏈動向"],
    "2615": ["貨運市況Q3展望", "台灣港口吞吐量", "航運指數回升"],
    "6770": ["⚠ Q2業外收入是否持續", "非經常性損益確認", "不建議追高"],
}

setups = []

# Process STRONG BUY + BUY stocks
buy_codes = [r["code"] for r in conviction["strong_buys"]] + \
            [r["code"] for r in conviction["buys"] if r["code"] != "6770"]

for code in buy_codes:
    s       = comp_map.get(code, {})
    t       = target_map.get(code, {})
    r       = risk_map.get(code, {})
    mg      = margin_map.get(code, {})
    bc      = bounce_map.get(code)
    mom     = momentum_map.get(code)
    is_sb   = code in [x["code"] for x in conviction["strong_buys"]]

    price    = sf(s.get("price"))
    target   = sf(t.get("target"))
    upside   = sf(t.get("upside"))
    risk_sc  = r.get("risk", 30)
    peg      = r.get("peg")
    score    = s.get("score", 40)
    div      = sf(s.get("div_yield"))
    fwd_pe   = sf(s.get("fwd_pe"))
    eps_g    = sf(s.get("eps_accel"))
    is_fin   = s.get("is_fin", False)
    ms       = mg.get("sig", "N/A")
    pct_ma   = bc["pct_vs_ma"] if bc else (mom["pct_vs_ma"] if mom else None)
    is_tri   = code in triple_set

    if not price or price <= 0: continue
    if not target or target <= 0: continue
    if not upside or upside < 10: continue   # skip if target price < 10% upside

    # ── Entry zone ────────────────────────────────────────────────────────────
    # Limit order range: current price ± 0.5% bid-ask
    entry_lo = round(price * 0.995, 1)
    entry_hi = round(price * 1.005, 1)
    entry_mid = price

    # ── Stop-loss ─────────────────────────────────────────────────────────────
    # Base: 10% below entry (standard risk management)
    # Adjust: high-risk stocks get tighter stop (8%), low-risk wider (12%)
    # Technical: if below 30d MA, use MA as reference support
    if risk_sc <= 15:
        stop_pct = 0.88   # wider stop for high-quality names
    elif risk_sc <= 30:
        stop_pct = 0.90   # standard
    else:
        stop_pct = 0.92   # tighter for riskier names

    stop_price = round(entry_mid * stop_pct, 1)
    stop_loss_pct = (1 - stop_pct) * 100   # e.g. 10%

    # ── Risk / Reward ─────────────────────────────────────────────────────────
    gain = (target / entry_mid - 1) * 100
    loss = stop_loss_pct
    rr   = gain / loss if loss > 0 else 0

    # ── Position size (2% portfolio risk rule) ────────────────────────────────
    # Max loss per position = 2% of portfolio
    # If price drops to stop, position loses stop_loss_pct
    # So max position size = 2% / stop_loss_pct
    # 1% portfolio-risk rule: position = 1% / stop_loss_pct; cap at 10%
    position_pct = min(1.0 / (stop_loss_pct / 100) * 100, 10.0)
    if risk_sc > 30: position_pct *= 0.7   # reduce for higher-risk stocks
    if risk_sc <= 10: position_pct = min(position_pct * 1.2, 10.0)  # allow slightly more for safest
    position_pct = round(position_pct, 1)

    # ── Holding period estimate ───────────────────────────────────────────────
    # Assume price appreciates at: max(eps_growth, 15%) per year
    annual_return = max(abs(eps_g) if eps_g else 15, 15) / 100
    months = round(upside / (annual_return * 100 / 12)) if upside and annual_return else None

    # ── Catalysts ─────────────────────────────────────────────────────────────
    cats = CATALYSTS.get(code, ["Q2 EPS發布", "產業景氣動向"])

    # ── Verdict ──────────────────────────────────────────────────────────────
    action = "STRONG BUY" if is_sb else "BUY"

    setups.append({
        "code":        code,
        "name":        s.get("name",""),
        "sector":      s.get("sector","—"),
        "action":      action,
        "score":       score,
        "risk":        risk_sc,
        "is_triple":   is_tri,
        "price":       price,
        "entry_lo":    entry_lo,
        "entry_hi":    entry_hi,
        "stop_price":  stop_price,
        "stop_pct":    stop_loss_pct,
        "target":      target,
        "upside":      upside,
        "rr":          round(rr, 1),
        "position_pct":position_pct,
        "months":      months,
        "div":         div,
        "fwd_pe":      fwd_pe,
        "peg":         peg,
        "margin_sig":  ms,
        "pct_vs_ma":   pct_ma,
        "is_fin":      is_fin,
        "catalysts":   cats,
        "is_tri":      is_tri,
    })

setups.sort(key=lambda x: (0 if x["action"]=="STRONG BUY" else 1, -x["rr"]))

# ── Generate TRADE_SETUPS.md ───────────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

lines = [
    f"# Trade Setup Cards — {TODAY}",
    "*Actionable buy setups for STRONG BUY / BUY conviction stocks.*",
    "*Stop-loss based on risk score. Position size based on 2% portfolio-risk rule.*",
    "*These are research-based setups, not financial advice. Verify before acting.*",
    "",
    "## Setup Summary",
    "",
    "| Action | Code | Name | Price | Target | Upside | Stop | R/R | Position% |",
    "|--------|------|------|-------|--------|--------|------|-----|-----------|",
]

for s in setups:
    lines.append(
        f"| **{s['action']}** | **{s['code']}** | {s['name'].split()[0]} | "
        f"¥{s['price']:,.0f} | ¥{s['target']:,.0f} | **{s['upside']:+.1f}%** | "
        f"¥{s['stop_price']:,.0f} ({s['stop_pct']:.0f}%) | **{s['rr']:.1f}×** | "
        f"{s['position_pct']:.1f}% |"
    )

lines += ["", "---", ""]

for s in setups:
    tri_badge = " ⭐ 三重確認" if s["is_triple"] else ""
    fin_note  = " (金融股)" if s["is_fin"] else ""
    lines += [
        f"## {s['code']} {s['name']}{fin_note} — {s['action']}{tri_badge}",
        f"*{s['sector']} | 綜合分 {s['score']} | 風險 {s['risk']} | "
        f"融資: {s['margin_sig']} | vs 30d MA: {fmt(s['pct_vs_ma'],1,'','%')}*",
        "",
        "```",
        f"  現價      ¥{s['price']:>10,.0f}",
        f"  進場區間  ¥{s['entry_lo']:>10,.1f} – ¥{s['entry_hi']:,.1f}",
        f"  停損      ¥{s['stop_price']:>10,.1f}  (-{s['stop_pct']:.0f}%)",
        f"  目標價    ¥{s['target']:>10,.0f}  (+{s['upside']:.1f}%)",
        f"  風險/報酬  {s['rr']:.1f}× 每承擔1元風險獲得{s['rr']:.1f}元報酬",
        f"  建議倉位  ≤ {s['position_pct']:.1f}% 投資組合",
        f"  預計持有  {'~'+str(s['months'])+'個月' if s['months'] else '視業績而定'}",
        f"  遠期本益比 {fmt(s['fwd_pe'],1,'','x')}",
        f"  PEG      {fmt(s['peg'],2)}",
        f"  股息殖利率 {fmt(s['div'],2,'','%')}",
        "```",
        "",
        f"**催化劑:** {' | '.join(s['catalysts'])}",
        "",
        "---",
        "",
    ]

# Summary stats
avg_rr     = sum(s["rr"] for s in setups) / len(setups) if setups else 0
avg_pos    = sum(s["position_pct"] for s in setups) / len(setups) if setups else 0
best_rr    = max(setups, key=lambda x: x["rr"]) if setups else None
total_pos  = sum(s["position_pct"] for s in setups)

lines += [
    "## Portfolio Construction",
    "",
    f"| Metric | Value |",
    f"|--------|-------|",
    f"| 建議買進股票 | {len(setups)} 支 |",
    f"| 平均風險/報酬 | {avg_rr:.1f}× |",
    f"| 最佳R/R | {best_rr['code']} {best_rr['name'].split()[0]} {best_rr['rr']:.1f}× |"
    if best_rr else "",
    f"| 合計建議倉位 | {total_pos:.1f}% (剩餘{100-total_pos:.1f}%現金/其他) |",
    f"| 平均單股倉位 | {avg_pos:.1f}% |",
    "",
    "**分散投資原則:**",
    "- 單一股票不超過15–20%投資組合",
    "- 科技/半導體不超過50%",
    "- 金融股不超過30%",
    "- 保留20–30%現金以應對回調加碼機會",
    "",
    "**停損紀律:**",
    "- 若股價跌破停損位，無條件執行停損",
    "- 不要用「等反彈」心態持有虧損部位",
    "- 每季重新評估業績後再決定是否繼續持有",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 23*",
    f"*免責聲明: 以上為研究分析輸出，非投資建議。投資前請自行評估風險承受能力。*",
]

(REPORT_DIR / "TRADE_SETUPS.md").write_text("\n".join(lines), encoding="utf-8")

# ── JSON ──────────────────────────────────────────────────────────────────────
(REPORT_DIR / "trade_setups.json").write_text(
    json.dumps({"date": TODAY, "setups": setups,
                "avg_rr": round(avg_rr,2), "total_position_pct": round(total_pos,1)},
               ensure_ascii=False, indent=2), encoding="utf-8")

print(f"✓ TRADE_SETUPS.md + trade_setups.json")
print(f"\n  {len(setups)} trade setups | avg R/R: {avg_rr:.1f}× | total position: {total_pos:.1f}%")
print(f"\n  Setup cards:")
for s in setups:
    print(f"    {s['action']:11s} {s['code']} {s['name'].split()[0]:12s} "
          f"¥{s['price']:>7,.0f} → ¥{s['target']:>7,.0f}  "
          f"stop=¥{s['stop_price']:>7,.0f}  R/R={s['rr']:.1f}×  "
          f"pos={s['position_pct']:.1f}%")
