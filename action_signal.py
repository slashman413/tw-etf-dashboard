#!/usr/bin/env python3
"""
Iteration 58: Master Action Signal Board
Synthesizes Grand score + Smart Money Confluence + Q2 EPS forecast +
DNA signals + institutional flows + margin signal → single Action Score
with Buy/Accumulate/Hold/Reduce/Avoid recommendation.
No API calls. Generates: action_signal.json
"""
import json, statistics
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand  = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
smc    = json.loads((REPORT_DIR/"smart_money_confluence.json").read_text(encoding="utf-8"))
q2f    = json.loads((REPORT_DIR/"q2_eps_forecast.json").read_text(encoding="utf-8"))
flows  = json.loads((REPORT_DIR/"institutional_flows.json").read_text(encoding="utf-8"))
dna    = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
margin = json.loads((REPORT_DIR/"margin_data.json").read_text(encoding="utf-8"))
mom    = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
bwi    = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
bt     = json.loads((REPORT_DIR/"dna_backtest.json").read_text(encoding="utf-8"))
earq   = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))
comp   = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd   = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))
possize = json.loads((REPORT_DIR/"position_sizing.json").read_text(encoding="utf-8"))
peer   = json.loads((REPORT_DIR/"peer_comparison.json").read_text(encoding="utf-8"))

grand_map  = {r["code"]: r for r in grand.get("all_ranked",[])}
smc_map    = {r["code"]: r for r in smc.get("all_results",[])}
q2f_map    = {r["code"]: r for r in q2f.get("all_forecasts",[])}
flows_map  = {r["code"]: r for r in flows.get("universe_flows",[])}
dna_map    = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
mom_map    = {m["code"]: m for m in mom.get("all_momentum",[])}
bwi_map    = {r["code"]: r for r in bwi.get("all_refreshed",[])}
bt_map     = {r["code"]: r for r in bt.get("per_stock",[])}
earq_map   = {r["code"]: r for r in earq.get("all_stocks",[])}
name_map   = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}
# Existing positions
pos_map    = {p["code"]: p for p in possize.get("positions",[])}
code_sector= {}
for sec in peer.get("sectors",[]):
    for s in sec.get("stocks",[]):
        code_sector[s["code"]] = sec["sector"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

all_codes = list(grand_map.keys())

results = []
for code in all_codes:
    g   = grand_map.get(code, {})
    sm  = smc_map.get(code, {})
    q2  = q2f_map.get(code, {})
    fl  = flows_map.get(code, {})
    dn  = dna_map.get(code, {})
    mm  = mom_map.get(code, {})
    bw  = bwi_map.get(code, {})
    btd = bt_map.get(code, {})
    eq  = earq_map.get(code, {})
    mr  = margin.get(code, {})
    pos = pos_map.get(code, {})
    name   = name_map.get(code, code)
    sector = code_sector.get(code, "其他")

    grand_s  = g.get("grand", 0) or 0
    final    = g.get("final", "") or ""
    bull     = dn.get("bull_signs", 0) or 0
    eq_score = eq.get("eq_score", 0) or 0
    eq_grade = (eq.get("grade","") or "").split(" ")[0]
    pct_ma   = sf(mm.get("pct_vs_ma"))
    close    = sf(mm.get("close"))
    pe       = sf(bw.get("pe_new")) or sf(bw.get("pe_old"))
    avg_60   = sf(btd.get("avg_60d"))
    win_60   = sf(btd.get("win_60d"))

    confluence = sm.get("confluence", 0) or 0
    inst_net   = fl.get("total_net", 0) or 0
    inst_signal= fl.get("inst_signal", "") or ""
    divergence = fl.get("divergence") or ""

    q2_growth  = sf(q2.get("q2_eps_growth_pct"))
    fwd_pe     = sf(q2.get("forward_pe_est"))
    val_signal = q2.get("val_signal", "") or ""
    eps_acc    = q2.get("eps_acc", False)

    margin_sig = mr.get("sig", "") or ""
    m_chg      = sf(mr.get("m_chg"))
    s_chg      = sf(mr.get("s_chg"))

    in_position = code in pos_map and (pos.get("alloc_pct_norm") or 0) > 0
    cur_alloc   = sf(pos.get("alloc_pct_norm")) or 0

    # ── Component A: Grand/Fundamental Score (0–35) ───────────────────────────
    comp_a = min(35, grand_s * 0.35)

    # ── Component B: Smart Money Confluence (0–25) ────────────────────────────
    comp_b = min(25, confluence * 0.25)

    # ── Component C: Forward EPS Momentum (0–20) ─────────────────────────────
    # Q2 EPS growth + EPS acceleration + valuation
    if q2_growth is not None:
        if q2_growth > 100:   q2_pts = 16
        elif q2_growth > 50:  q2_pts = 13
        elif q2_growth > 20:  q2_pts = 10
        elif q2_growth > 0:   q2_pts = 7
        elif q2_growth > -20: q2_pts = 3
        else:                  q2_pts = 0
    else:
        q2_pts = 5   # unknown → neutral
    val_pts = {"超低估": 4, "深度低估": 3, "低估": 2, "合理": 1}.get(val_signal, 0)
    comp_c = min(20, q2_pts + val_pts + (2 if eps_acc else 0))

    # ── Component D: Technical / DNA (0–20) ──────────────────────────────────
    # DNA bull signs (0-6) + MA position + divergence bonus
    dna_pts  = (bull / 6) * 10
    if pct_ma is not None:
        if pct_ma > 5:        ma_pts = 5
        elif pct_ma > 0:      ma_pts = 4
        elif pct_ma > -5:     ma_pts = 2
        else:                  ma_pts = 0
    else:
        ma_pts = 2
    div_bonus = 3 if divergence.startswith("價跌法買") else 0
    comp_d = min(20, dna_pts + ma_pts + div_bonus)

    action_score = round(comp_a + comp_b + comp_c + comp_d, 1)

    # ── Action label ──────────────────────────────────────────────────────────
    if "TRIPLE" in final:
        if action_score >= 70:  action = "🚀 立即買進"
        elif action_score >= 55: action = "✅ 積極買進"
        else:                    action = "📈 買進"
    elif action_score >= 72:    action = "🚀 立即買進"
    elif action_score >= 60:    action = "✅ 積極買進"
    elif action_score >= 48:    action = "📈 買進"
    elif action_score >= 38:    action = "👀 觀察"
    elif action_score >= 25:    action = "⚖ 持有"
    else:                        action = "❌ 減持"

    # ── Rationale (3 strongest signals) ──────────────────────────────────────
    signals = []
    if "TRIPLE" in final:         signals.append("TRIPLE確認")
    if inst_net > 2000:           signals.append("外資大買")
    elif inst_net > 500:          signals.append("法人買進")
    if divergence.startswith("價跌法買"): signals.append("看漲背離")
    if eps_acc:                   signals.append("EPS加速")
    if q2_growth and q2_growth > 50: signals.append(f"Q2e+{q2_growth:.0f}%")
    if margin_sig == "BULLISH" and s_chg and s_chg < 0: signals.append("融券回補")
    elif margin_sig == "BULLISH": signals.append("融資多頭")
    if bull >= 5:                 signals.append(f"DNA{bull}/6")
    if val_signal in ("超低估","深度低估"): signals.append(val_signal)
    if pct_ma and pct_ma > 3:    signals.append("均線強勢")
    if avg_60 and avg_60 > 8:    signals.append(f"回測+{avg_60:.0f}%")

    rationale = " | ".join(signals[:3]) if signals else "—"

    # ── Change from previous rating ──────────────────────────────────────────
    prev_final = final   # use Grand final as baseline

    results.append({
        "code":         code,
        "name":         name.split(" ")[0] if name else code,
        "sector":       sector,
        "action_score": action_score,
        "action":       action,
        "rationale":    rationale,
        # Component breakdown
        "comp_a_grand":  round(comp_a, 1),
        "comp_b_smc":    round(comp_b, 1),
        "comp_c_eps":    round(comp_c, 1),
        "comp_d_dna":    round(comp_d, 1),
        # Key data
        "grand":         round(grand_s, 1),
        "final":         final,
        "confluence":    round(confluence, 1),
        "bull_signs":    bull,
        "q2_growth":     round(q2_growth, 1) if q2_growth is not None else None,
        "fwd_pe":        fwd_pe,
        "val_signal":    val_signal,
        "inst_net":      inst_net,
        "inst_signal":   inst_signal,
        "divergence":    divergence,
        "margin_sig":    margin_sig,
        "pct_vs_ma":     round(pct_ma, 1) if pct_ma is not None else None,
        "eq_grade":      eq_grade,
        "eps_acc":       eps_acc,
        "avg_60d":       round(avg_60, 1) if avg_60 is not None else None,
        "win_60d":       round(win_60, 1) if win_60 is not None else None,
        "in_position":   in_position,
        "cur_alloc":     round(cur_alloc, 1),
        "close":         close,
        "pe":            round(pe, 1) if pe else None,
    })

results.sort(key=lambda x: -x["action_score"])

# ── Summary groups ────────────────────────────────────────────────────────────
buy_now     = [r for r in results if "立即買進" in r["action"]]
accumulate  = [r for r in results if "積極買進" in r["action"]]
buy         = [r for r in results if r["action"] == "📈 買進"]
watch       = [r for r in results if "觀察" in r["action"]]
hold        = [r for r in results if "持有" in r["action"]]
reduce      = [r for r in results if "減持" in r["action"]]

in_pos_results = [r for r in results if r["in_position"]]
not_in_pos     = [r for r in results if not r["in_position"] and "買進" in r["action"]]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'MASTER ACTION SIGNAL BOARD':=<65}")
print(f"  Universe: {len(results)}  立即買進: {len(buy_now)}  積極買進: {len(accumulate)}  買進: {len(buy)}")
print(f"  觀察: {len(watch)}  持有: {len(hold)}  減持: {len(reduce)}")

print(f"\n  🚀 立即買進 (Top Action):")
print(f"  {'代號':<6} {'名稱':<10} {'Score':>6} {'Grand':>6} {'Conf':>5} {'Q2e%':>6} {'Action':<12}  {'Key Signals'}")
print("-"*95)
for r in buy_now[:12]:
    q2g = f"{r['q2_growth']:+.0f}%" if r["q2_growth"] is not None else "  —"
    print(f"  {r['code']:<6} {r['name']:<10} {r['action_score']:>6.1f} "
          f"{r['grand']:>6.1f} {r['confluence']:>5.1f} {q2g:>6}  "
          f"{r['action']:<14}  {r['rationale']}")

print(f"\n  現有持倉行動建議:")
print(f"  {'代號':<6} {'名稱':<10} {'Score':>6} {'配置%':>6} {'Action':<14}  {'Key Signals'}")
for r in in_pos_results[:15]:
    print(f"  {r['code']:<6} {r['name']:<10} {r['action_score']:>6.1f} "
          f"{r['cur_alloc']:>5.1f}%  {r['action']:<16}  {r['rationale']}")

print(f"\n  未持有但評為買進的股票 ({len(not_in_pos)}支):")
for r in not_in_pos[:8]:
    q2g = f"{r['q2_growth']:+.0f}%" if r["q2_growth"] is not None else "  —"
    print(f"  {r['code']} {r['name']:<10} Score={r['action_score']:.1f} Q2e={q2g}  {r['rationale']}")

out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "methodology": {
        "comp_a": "Grand/Fundamental (35%): grand_score × 0.35",
        "comp_b": "Smart Money Confluence (25%): confluence × 0.25",
        "comp_c": "EPS Momentum (20%): Q2 growth tier + valuation + accel bonus",
        "comp_d": "Technical/DNA (20%): DNA signals + MA position + divergence",
    },
    "summary": {
        "total":       len(results),
        "buy_now":     len(buy_now),
        "accumulate":  len(accumulate),
        "buy":         len(buy),
        "watch":       len(watch),
        "hold":        len(hold),
        "reduce":      len(reduce),
        "new_buys":    len(not_in_pos),
    },
    "all_signals":      results,
    "buy_now":          buy_now,
    "accumulate":       accumulate,
    "buy":              buy,
    "watch":            watch,
    "hold":             hold,
    "reduce":           reduce,
    "in_position":      in_pos_results,
    "new_buy_signals":  not_in_pos,
}
(REPORT_DIR/"action_signal.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- action_signal.json saved ({len(results)} stocks)")

