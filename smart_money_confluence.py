#!/usr/bin/env python3
"""
Iteration 56: Smart Money Confluence + Short Squeeze Radar
Combines institutional flows (T86) + margin data (融資融券) + Grand score + DNA.
No API calls. Generates: smart_money_confluence.json
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
margin  = json.loads((REPORT_DIR/"margin_data.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
instf   = json.loads((REPORT_DIR/"institutional_flows.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
flows_map = {r["code"]: r for r in instf.get("universe_flows",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Build confluence data per stock ──────────────────────────────────────────
all_stocks = list(grand_map.keys())
results = []

for code in all_stocks:
    g  = grand_map.get(code, {})
    mr = margin.get(code, {})
    dn = dna_map.get(code, {})
    fl = flows_map.get(code, {})
    eq = earq_map.get(code, {})
    mm = mom_map.get(code, {})
    bw = bwi_map.get(code, {})
    name = name_map.get(code, code)

    grand_s  = g.get("grand", 0) or 0
    final    = g.get("final", "") or ""
    bull     = dn.get("bull_signs", 0) or 0
    eq_score = eq.get("eq_score", 0) or 0
    eq_grade = (eq.get("grade","") or "").split(" ")[0]
    pct_ma   = sf(mm.get("pct_vs_ma"))
    close    = sf(mm.get("close"))
    pe       = sf(bw.get("pe_new") or bw.get("pe_old"))

    # ── Margin data ───────────────────────────────────────────────────────────
    m_today  = sf(mr.get("m_today"))  # 融資餘額 (張)
    m_chg    = sf(mr.get("m_chg"))    # 融資變化
    s_today  = sf(mr.get("s_today"))  # 融券餘額 (張)
    s_chg    = sf(mr.get("s_chg"))    # 融券變化
    margin_sig = mr.get("sig", "")

    # Short interest ratio: 融券 / 融資 (高 = 多空對立激烈)
    short_ratio = (s_today / m_today * 100) if (m_today and m_today > 0 and s_today) else 0

    # ── Institutional flow data ───────────────────────────────────────────────
    total_net  = fl.get("total_net", 0) or 0
    foreign_net= fl.get("foreign_net", 0) or 0
    trust_net  = fl.get("trust_net", 0) or 0
    inst_signal= fl.get("inst_signal", "") or ""
    divergence = fl.get("divergence") or ""

    # ── Smart Money Confluence Score (0-100) ──────────────────────────────────
    # Component 1: Institutional Flow (0-30)
    #   >5000  = 30; >2000=25; >500=18; >0=10; <0=0; <-2000=-5
    if   total_net > 5000:  flow_pts = 30
    elif total_net > 2000:  flow_pts = 25
    elif total_net > 500:   flow_pts = 18
    elif total_net > 0:     flow_pts = 10
    elif total_net > -2000: flow_pts = 2
    else:                    flow_pts = 0

    # Component 2: Fundamental Quality (0-25)
    #   Weighted: EQ (0-10) + Grand (0-10) + DNA bull (0-5)
    eq_pts    = min(10, eq_score)
    grand_pts = min(10, (grand_s / 10))
    dna_pts   = min(5, bull)
    fund_pts  = eq_pts + grand_pts + dna_pts

    # Component 3: Margin Position (0-20)
    #   Bullish: margin↑ + short↓ = 20; margin↑ = 12; neutral = 8; bearish = 0
    if margin_sig == "BULLISH":
        if s_chg is not None and s_chg < 0:
            margin_pts = 20   # margin buying + short covering
        else:
            margin_pts = 14
    elif margin_sig == "NEUTRAL":
        margin_pts = 8
    else:
        margin_pts = 2

    # Component 4: Technical Position (0-15)
    #   Below MA but institutions buying = divergence bonus (10); above MA = 8; below = 4
    if divergence.startswith("價跌法買"):
        tech_pts = 10   # bullish divergence — highest reward
    elif pct_ma is not None and pct_ma > 0:
        tech_pts = 8    # above MA
    elif pct_ma is not None and pct_ma > -5:
        tech_pts = 5    # slightly below
    else:
        tech_pts = 3    # deep below

    # Component 5: Valuation (0-10)
    #   PE < 12 = 10; < 15 = 8; < 20 = 5; > 20 = 2
    if pe is None:        val_pts = 5
    elif pe <= 0:         val_pts = 3
    elif pe < 12:         val_pts = 10
    elif pe < 15:         val_pts = 8
    elif pe < 20:         val_pts = 5
    else:                 val_pts = 2

    confluence = round(flow_pts + fund_pts + margin_pts + tech_pts + val_pts, 1)

    # ── Squeeze Potential Score ───────────────────────────────────────────────
    # High squeeze potential: high 融券 ratio + institutional buying + grand > 60
    if s_today and s_today > 50 and total_net > 200 and grand_s >= 60:
        squeeze_score = min(100, short_ratio * 2 + (total_net / 1000) * 5)
        squeeze_label = "高擠壓潛力" if squeeze_score > 30 else "中擠壓潛力"
    elif s_today and s_today > 20 and total_net > 0:
        squeeze_score = min(50, short_ratio + 10)
        squeeze_label = "低擠壓潛力"
    else:
        squeeze_score = 0
        squeeze_label = ""

    # ── Crowded Long Risk ─────────────────────────────────────────────────────
    # Risk: very high 融資 + institutions selling + below MA
    if m_today and m_today > 5000 and total_net < -500 and (pct_ma or 0) < -2:
        crowded_risk = "高擁擠風險"
    elif m_today and m_today > 2000 and total_net < 0:
        crowded_risk = "中擁擠風險"
    else:
        crowded_risk = ""

    # ── Signal label ──────────────────────────────────────────────────────────
    if confluence >= 70:
        signal = "🔥 強勢匯合"
    elif confluence >= 55:
        signal = "⭐ 多力聚焦"
    elif confluence >= 40:
        signal = "📊 中性偏多"
    elif confluence >= 25:
        signal = "⚠ 混合信號"
    else:
        signal = "❄ 弱勢"

    results.append({
        "code":          code,
        "name":          name.split(" ")[0] if name else code,
        "grand":         round(grand_s, 1),
        "final":         final,
        "confluence":    confluence,
        "signal":        signal,
        # Components
        "flow_pts":      flow_pts,
        "fund_pts":      round(fund_pts, 1),
        "margin_pts":    margin_pts,
        "tech_pts":      tech_pts,
        "val_pts":       val_pts,
        # Raw data
        "total_net":     total_net,
        "foreign_net":   foreign_net,
        "trust_net":     trust_net,
        "inst_signal":   inst_signal,
        "divergence":    divergence,
        "m_today":       m_today,
        "m_chg":         m_chg,
        "s_today":       s_today,
        "s_chg":         s_chg,
        "short_ratio":   round(short_ratio, 2),
        "margin_sig":    margin_sig,
        "bull_signs":    bull,
        "eq_score":      eq_score,
        "eq_grade":      eq_grade,
        "pct_vs_ma":     round(pct_ma, 1) if pct_ma is not None else None,
        "pe":            round(pe, 1) if pe else None,
        "close":         close,
        "squeeze_score": round(squeeze_score, 1),
        "squeeze_label": squeeze_label,
        "crowded_risk":  crowded_risk,
    })

# Sort by confluence score desc
results.sort(key=lambda x: -x["confluence"])

# ── Key groups ────────────────────────────────────────────────────────────────
top_confluence   = [r for r in results if r["confluence"] >= 55]
divergence_buys  = [r for r in results if r.get("divergence","").startswith("價跌法買")]
squeeze_cands    = [r for r in results if r["squeeze_score"] > 0]
squeeze_cands.sort(key=lambda x: -x["squeeze_score"])
crowded_longs    = [r for r in results if r["crowded_risk"]]
triple_cf        = [r for r in results if "TRIPLE" in (r.get("final") or "")]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'SMART MONEY CONFLUENCE ANALYSIS':=<65}")
print(f"  Universe: {len(results)} stocks | Top confluence(≥55): {len(top_confluence)}")

print(f"\n  Top 15 Smart Money Confluence:")
print(f"  {'代號':<6} {'名稱':<10} {'Conf':>5} {'Grand':>6} {'Flow':>5} {'Fund':>5} {'Mrg':>4} {'Tech':>5} {'Signal'}")
print("-"*85)
for r in results[:15]:
    print(f"  {r['code']:<6} {r['name']:<10} {r['confluence']:>5.1f} "
          f"{r['grand']:>6.1f} {r['flow_pts']:>5} {r['fund_pts']:>5.1f} "
          f"{r['margin_pts']:>4} {r['tech_pts']:>5}  {r['signal']}")

print(f"\n  TRIPLE持倉匯合分數:")
for r in triple_cf:
    print(f"  {r['code']} {r['name']:<10} Conf={r['confluence']:.1f}  {r['signal']}  "
          f"法人={r['inst_signal']}  融資={r['margin_sig']}")

if squeeze_cands[:5]:
    print(f"\n  擠壓候選 (融券高+法人買進):")
    for r in squeeze_cands[:5]:
        print(f"  {r['code']} {r['name']:<10} 擠壓分={r['squeeze_score']:.1f}  "
              f"融券={r['s_today']}張  融券比={r['short_ratio']:.1f}%  法人={r['total_net']:+,}  [{r['squeeze_label']}]")

if crowded_longs:
    print(f"\n  擁擠多頭風險:")
    for r in crowded_longs:
        print(f"  {r['code']} {r['name']:<10} 融資={r['m_today']}張  法人={r['total_net']:+,}  [{r['crowded_risk']}]")

# ── Save ──────────────────────────────────────────────────────────────────────
out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "universe_count": len(results),
    "summary": {
        "top_confluence_count":   len(top_confluence),
        "divergence_buy_count":   len(divergence_buys),
        "squeeze_candidate_count": len(squeeze_cands),
        "crowded_long_count":     len(crowded_longs),
    },
    "scoring_methodology": {
        "flow_pts":    "機構淨買賣超 (0-30): >5000=30, >2000=25, >500=18, >0=10, neutral=2",
        "fund_pts":    "基本面品質 (0-25): EQ(0-10) + Grand/10(0-10) + DNA(0-5)",
        "margin_pts":  "融資信號 (0-20): BULLISH+short_down=20, BULLISH=14, NEUTRAL=8",
        "tech_pts":    "技術位置 (0-15): 看漲背離=10, 均線上=8, 微跌=5, 深跌=3",
        "val_pts":     "估值 (0-10): PE<12=10, <15=8, <20=5, ≥20=2",
    },
    "all_results":      results,
    "top_confluence":   top_confluence,
    "divergence_buys":  divergence_buys,
    "squeeze_candidates": squeeze_cands,
    "crowded_longs":    crowded_longs,
    "triple_confluence": triple_cf,
}
(REPORT_DIR/"smart_money_confluence.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- smart_money_confluence.json saved ({len(results)} stocks)")


