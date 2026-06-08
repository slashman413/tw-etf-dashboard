#!/usr/bin/env python3
"""
Iteration 53: Portfolio Scenario Analysis & Stress Test
Computes bull/base/bear case return projections for the Kelly portfolio
and stress tests: financial sector shock, DNA reversal, correlation spike.
No API calls. Generates: scenario_analysis.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
possize = json.loads((REPORT_DIR/"position_sizing.json").read_text(encoding="utf-8"))
bt      = json.loads((REPORT_DIR/"dna_backtest.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR/"relative_strength.json").read_text(encoding="utf-8"))
peer    = json.loads((REPORT_DIR/"peer_comparison.json").read_text(encoding="utf-8"))
secrot  = json.loads((REPORT_DIR/"sector_rotation.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))

bt_map    = {r["code"]: r for r in bt.get("per_stock",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}

code_sector = {}
for sec in peer.get("sectors",[]):
    for s in sec.get("stocks",[]):
        code_sector[s["code"]] = sec["sector"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Active positions (alloc >= 0.5%) ─────────────────────────────────────────
positions = [p for p in possize.get("positions",[]) if (p.get("alloc_pct_norm") or 0) >= 0.5]
total_invested = sum(p.get("alloc_pct_norm",0) for p in positions) / 100  # as fraction

# ── Per-position scenario data ────────────────────────────────────────────────
pos_scenarios = []
for pos in positions:
    code    = pos["code"]
    alloc   = (pos.get("alloc_pct_norm") or 0) / 100  # fraction of portfolio
    b       = bt_map.get(code, {})
    dn      = dna_map.get(code, {})
    mm      = mom_map.get(code, {})
    rv      = rs_map.get(code, {})
    bw      = bwi_map.get(code, {})
    eq      = earq_map.get(code, {})
    g       = grand_map.get(code, {})
    sector  = code_sector.get(code, "其他")

    avg_60  = sf(b.get("avg_60d"))   # historical avg 60d return when DNA signal
    win_60  = sf(b.get("win_60d"))   # win rate %
    avg_20  = sf(b.get("avg_20d"))
    win_20  = sf(b.get("win_20d"))
    bull    = dn.get("bull_signs", 0) or 0
    close   = sf(pos.get("close"))
    stop    = sf(pos.get("stop_level"))
    pct_ma  = sf(mm.get("pct_vs_ma"))
    pct_52w = sf(rv.get("pct_from_52w_high"))
    pe      = sf(bw.get("pe_new") or bw.get("pe_old"))
    grand_s = g.get("grand", 0) or 0
    eq_score= eq.get("eq_score", 0) or 0

    # ── Base case: use backtest avg_60d adjusted for current DNA strength ──
    if avg_60 is not None:
        dna_adj  = 0.7 + (bull / 6) * 0.6    # 0.7 at 0/6, 1.3 at 6/6
        base_ret = avg_60 * dna_adj
    else:
        base_ret = 3.0   # conservative default

    # ── Bull case: all 6 DNA signals, revenue beats, PE compression ──────
    # Bull adds: DNA 6/6 premium (historical 6/6 signals outperform by ~40%)
    # + revenue acceleration premium (A+ EQ adds ~20% to return)
    # + MA breakout premium (already above MA adds ~15%)
    bull_premium = 0
    bull_premium += (6 - bull) * 1.5       # each missing DNA signal = 1.5% upside if triggered
    bull_premium += (eq_score / 10) * 3    # EQ quality premium max 3%
    bull_premium += 2 if (pct_ma and pct_ma > 0) else 0  # already above MA
    bull_ret = base_ret + bull_premium

    # ── Bear case: DNA signals fade, sector headwinds ────────────────────
    # Bear: stop-loss triggers → cap loss at stop distance
    if stop and close and close > 0:
        max_loss = (stop / close - 1) * 100   # negative number
    else:
        max_loss = -8.0
    # Bear also considers: if win_rate < 50%, expect negative avg
    if win_60 and win_60 < 50:
        bear_ret = max_loss * 0.5   # expect partial stop hit
    else:
        bear_ret = max_loss * 0.4   # less severe bear, strong quality stocks

    # ── Stress scenarios ──────────────────────────────────────────────────
    # 1. Financial sector shock (-15% sector): affects 金融保險 stocks
    fin_shock = -15.0 if sector == "金融保險" else -3.0

    # 2. DNA signal reversal: if all 6 signals flip off
    dna_reversal = -avg_60 * 0.8 if avg_60 else -5.0

    # 3. Correlation spike (2015-style): all stocks drop to -20% max loss
    corr_spike = max(max_loss, -20.0)

    # 4. May revenue miss: -10% for high-revenue-expectation stocks
    high_rev_exp = ["2881","2882","2883","2887","6669","2330","2376"]
    rev_miss = -10.0 if code in high_rev_exp else -3.0

    pos_scenarios.append({
        "code":     code,
        "name":     pos["name"].split(" ")[0],
        "sector":   sector,
        "alloc":    round(alloc * 100, 2),
        "base_ret": round(base_ret, 2),
        "bull_ret": round(bull_ret, 2),
        "bear_ret": round(bear_ret, 2),
        # Stress
        "stress_fin":    round(fin_shock, 2),
        "stress_dna":    round(dna_reversal, 2),
        "stress_corr":   round(corr_spike, 2),
        "stress_rev":    round(rev_miss, 2),
        # Context
        "bull_signs":    bull,
        "eq_score":      eq_score,
        "win_60d":       win_60,
        "avg_60d":       avg_60,
        "grand":         grand_s,
        "final":         g.get("final","—"),
        "pe":            round(pe,1) if pe else None,
        "max_loss_pct":  round(max_loss, 2),
    })

# ── Portfolio-level scenario returns (weighted average) ──────────────────────
def port_ret(key):
    return sum(p["alloc"]/100 * p[key] for p in pos_scenarios) / total_invested

p_base = port_ret("base_ret")
p_bull = port_ret("bull_ret")
p_bear = port_ret("bear_ret")
p_fin  = port_ret("stress_fin")
p_dna  = port_ret("stress_dna")
p_corr = port_ret("stress_corr")
p_rev  = port_ret("stress_rev")

# Cash drag: 20% cash earns 0%
p_base_with_cash = p_base * total_invested
p_bull_with_cash = p_bull * total_invested
p_bear_with_cash = p_bear * total_invested
p_fin_with_cash  = p_fin  * total_invested
p_dna_with_cash  = p_dna  * total_invested
p_corr_with_cash = p_corr * total_invested
p_rev_with_cash  = p_rev  * total_invested

# ── Scenario narratives ───────────────────────────────────────────────────────
scenarios = [
    {
        "name":        "🐂 牛市情境",
        "name_en":     "Bull Case",
        "description": "所有DNA信號觸發 + 5月營收超預期 + 金融股PE擴張",
        "triggers":    ["DNA 5/6股票S3信號全部觸發", "5月營收YoY>20%", "金融股PE擴張至16x", "半導體ADR+3%"],
        "probability": "25%",
        "port_return": round(p_bull_with_cash, 2),
        "invested_return": round(p_bull, 2),
        "timeline":    "60日",
        "key_drivers": ["華碩DNA觸發→TRIPLE", "金融TRIPLE股加碼", "台積電ADR帶動"],
    },
    {
        "name":        "📊 基本情境",
        "name_en":     "Base Case",
        "description": "維持現有DNA信號 + 5月營收符合預期 + 板塊輪動正常",
        "triggers":    ["DNA維持5/6", "5月營收YoY+10-15%", "市場緩步向上", "FOMC中性"],
        "probability": "50%",
        "port_return": round(p_base_with_cash, 2),
        "invested_return": round(p_base, 2),
        "timeline":    "60日",
        "key_drivers": ["金融TRIPLE股穩健上漲", "日W%R信號逐步改善", "earnings quality支撐"],
    },
    {
        "name":        "🐻 熊市情境",
        "name_en":     "Bear Case",
        "description": "部分止損觸發 + DNA信號衰減 + 市場修正",
        "triggers":    ["MA30跌破", "RS60下滑", "外資賣超", "FOMC偏鷹"],
        "probability": "25%",
        "port_return": round(p_bear_with_cash, 2),
        "invested_return": round(p_bear, 2),
        "timeline":    "60日",
        "key_drivers": ["止損紀律執行", "20%現金緩衝作用", "高EQ股相對抗跌"],
    },
]

stress_tests = [
    {
        "name":        "💥 金融板塊衝擊 -15%",
        "description": "金融保險板塊整體下跌15% (監管政策、利率倒掛等)",
        "port_impact": round(p_fin_with_cash, 2),
        "affected_stocks": [p["code"] for p in pos_scenarios if p["sector"]=="金融保險"],
        "mitigation":  "金融股均有止損設置；20%現金緩衝；半導體/科技股逆相關",
        "probability": "低 (10%)",
    },
    {
        "name":        "🧬 DNA信號全面衰退",
        "description": "大飆股6個DNA信號同步轉為熊市排列",
        "port_impact": round(p_dna_with_cash, 2),
        "affected_stocks": [p["code"] for p in pos_scenarios if p["bull_signs"] >= 4],
        "mitigation":  "分散於多個板塊；高EQ(A+)股基本面支撐；每日dna_refresh.py監控",
        "probability": "極低 (5%)",
    },
    {
        "name":        "📉 相關性飆升 (2015式閃崩)",
        "description": "台股急跌，所有持倉同向下跌，最大損失觸達止損",
        "port_impact": round(p_corr_with_cash, 2),
        "affected_stocks": [p["code"] for p in pos_scenarios],
        "mitigation":  "止損紀律；20%現金；Kelly半倉設計；TRIPLE股止損在MA30×0.98",
        "probability": "極低 (3%)",
    },
    {
        "name":        "📊 5月營收大幅不如預期",
        "description": "5月營收YoY<5%，市場大幅下修評估",
        "port_impact": round(p_rev_with_cash, 2),
        "affected_stocks": ["2881","2882","2883","2887","6669","2330","2376"],
        "mitigation":  "6月10日公布後立即更新模型；已設止損；EQ高分股相對抗跌",
        "probability": "低 (15%)",
    },
]

# ── Expected value calculation ────────────────────────────────────────────────
ev = 0.25 * p_bull_with_cash + 0.50 * p_base_with_cash + 0.25 * p_bear_with_cash
ev_invested = 0.25 * p_bull + 0.50 * p_base + 0.25 * p_bear

# ── Risk metrics ──────────────────────────────────────────────────────────────
all_bear_returns = [p["bear_ret"] for p in pos_scenarios]
var_95 = sorted(all_bear_returns)[int(len(all_bear_returns)*0.05)] if all_bear_returns else -10
max_drawdown_estimate = p_corr_with_cash   # worst stress scenario

# ── Sharpe-like ratio (using base return and bear as risk proxy) ──────────────
risk_estimate = abs(p_bear_with_cash - p_base_with_cash)
sharpe_proxy = (p_base_with_cash / risk_estimate) if risk_estimate else 0

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'PORTFOLIO SCENARIO ANALYSIS':=<65}")
print(f"\n  {'情境':<20} {'持倉部分':>9} {'含現金':>9} {'機率':>7}")
print("-"*55)
for sc in scenarios:
    print(f"  {sc['name']:<20} {sc['invested_return']:>+8.2f}%  {sc['port_return']:>+8.2f}%  {sc['probability']:>7}")
print(f"\n  期望值(EV):  持倉={ev_invested:+.2f}%  含現金={ev:+.2f}%")
print(f"  Sharpe代理: {sharpe_proxy:.2f}")

print(f"\n  壓力測試:")
for st in stress_tests:
    print(f"  {st['name']:<30} 組合影響={st['port_impact']:+.2f}%  [{st['probability']}]")

print(f"\n  最大回撤估計: {max_drawdown_estimate:+.2f}%")
print(f"  VaR (5%分位): {var_95:+.2f}%")

out = {
    "date": TODAY, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "portfolio_summary": {
        "n_positions": len(pos_scenarios),
        "total_invested_pct": round(total_invested*100, 1),
        "cash_pct": round((1-total_invested)*100, 1),
    },
    "scenarios": scenarios,
    "stress_tests": stress_tests,
    "risk_metrics": {
        "expected_value_invested": round(ev_invested, 2),
        "expected_value_with_cash": round(ev, 2),
        "sharpe_proxy": round(sharpe_proxy, 2),
        "var_5pct": round(var_95, 2),
        "max_drawdown_estimate": round(max_drawdown_estimate, 2),
    },
    "position_scenarios": pos_scenarios,
}
(REPORT_DIR/"scenario_analysis.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- scenario_analysis.json saved ({len(pos_scenarios)} positions)")

