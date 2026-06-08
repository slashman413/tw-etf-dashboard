#!/usr/bin/env python3
"""
Iteration 52: Pre-Market Price Level Checklist
Synthesises position sizing, stop-loss, DNA signals, and score sensitivity
into a concrete Monday June 8 trade execution guide.
No API calls. Generates: premarket_checklist.json + PREMARKET.txt
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
TRADE_DATE = TODAY
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
possize = json.loads((REPORT_DIR/"position_sizing.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR/"relative_strength.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
sensi   = json.loads((REPORT_DIR/"score_sensitivity.json").read_text(encoding="utf-8"))
earq    = json.loads((REPORT_DIR/"earnings_quality.json").read_text(encoding="utf-8"))
watch   = json.loads((REPORT_DIR/"watchlist_alerts.json").read_text(encoding="utf-8"))
bt      = json.loads((REPORT_DIR/"dna_backtest.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
dna_map   = {s["code"]: s for s in dna.get("all_signals",[]) if s.get("code")}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
sen_map   = {r["code"]: r for r in sensi.get("all_stocks",[])}
earq_map  = {r["code"]: r for r in earq.get("all_stocks",[])}
bt_map    = {r["code"]: r for r in bt.get("per_stock",[])}
pos_list  = possize.get("positions",[])

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def fv(v, d=1):
    if v is None: return "—"
    return f"{v:.{d}f}"

# ── DNA missing signals reference ─────────────────────────────────────────────
dna_5of6 = {r["code"]: r for r in watch.get("dna_5of6",[])}
almost_triple = {r["code"]: r for r in watch.get("almost_triple",[])}

checklist = []

for pos in pos_list:
    alloc = pos.get("alloc_pct_norm") or 0
    if alloc < 0.5:
        continue   # only positions worth acting on

    code   = pos["code"]
    name   = pos["name"].split(" ")[0]
    g      = grand_map.get(code, {})
    dn     = dna_map.get(code, {})
    mm     = mom_map.get(code, {})
    rv     = rs_map.get(code, {})
    bw     = bwi_map.get(code, {})
    sn     = sen_map.get(code, {})
    eq     = earq_map.get(code, {})
    b      = bt_map.get(code, {})

    close   = sf(pos.get("close"))
    ma30    = sf(pos.get("ma30"))
    stop    = sf(pos.get("stop_level"))
    pe      = sf(bw.get("pe_new") or bw.get("pe_old"))
    dy      = sf(bw.get("div_new") or bw.get("div_yield"))
    rs60    = rv.get("rs_60d")
    pct_ma  = sf(mm.get("pct_vs_ma"))
    bull    = dn.get("bull_signs", 0) or 0
    grand_s = g.get("grand", 0) or 0
    final   = g.get("final", "—")

    # ── Entry strategy ────────────────────────────────────────────────────────
    risk_tier = pos.get("risk_tier","—")

    if "TRIPLE" in final:
        # TRIPLE: confirm MA on open, add on breakout above last week's high
        entry_note   = "確認MA上方開盤即可持倉"
        entry_level  = close  # already in position
        add_level    = round(close * 1.02, 1) if close else None  # add on +2% breakout
        entry_action = "持倉 (已持有)" if alloc >= 5 else "建倉"
    elif grand_s >= 65:
        # STRONG BUY: enter on MA touch or 0.5% above MA
        entry_level  = round(ma30 * 1.005, 1) if ma30 else close
        add_level    = round(close * 1.015, 1) if close else None
        entry_note   = "MA30附近建倉"
        entry_action = "建倉"
    elif grand_s >= 55:
        # BUY: wait for pullback to MA before entry
        entry_level  = round(ma30 * 0.995, 1) if ma30 else close
        add_level    = round(ma30 * 1.01, 1) if ma30 else None
        entry_note   = "等待回踩MA建倉"
        entry_action = "條件建倉"
    else:
        entry_level  = round(ma30 * 0.99, 1) if ma30 else close
        add_level    = None
        entry_note   = "觀察訊號確認後建倉"
        entry_action = "觀察"

    # ── Take-profit levels ────────────────────────────────────────────────────
    # Based on backtest avg return and ATR proxy (pct from 52w high)
    avg_60d = sf(b.get("avg_60d"))
    if avg_60d and close:
        tp1 = round(close * (1 + avg_60d/200), 1)  # half of avg 60d return
        tp2 = round(close * (1 + avg_60d/100), 1)  # full avg 60d return
    elif close:
        tp1 = round(close * 1.05, 1)
        tp2 = round(close * 1.10, 1)
    else:
        tp1 = tp2 = None

    # ── Key price levels ──────────────────────────────────────────────────────
    stop_pct = ((stop/close)-1)*100 if (stop and close) else None

    # ── DNA signals to monitor ────────────────────────────────────────────────
    missing_dna = []
    if code in dna_5of6:
        missing_dna = [dna_5of6[code].get("missing","?")]
    s1_val = sf(dn.get("s1_dmi"))
    s2_val = sf(dn.get("s2_rsi4m"))
    s3_val = sf(dn.get("s3_wr50"))
    s4_val = sf(dn.get("s4_rsi60"))
    s5_val = sf(dn.get("s5_vr2w"))
    s6_val = sf(dn.get("s6_vr2m"))

    # S3日W%R threshold: need < 20 to trigger
    s3_note = None
    if not dn.get("s3_ok") and s3_val is not None:
        s3_note = f"S3日W%R={s3_val:.1f} (需<20，差{s3_val-20:.1f}點)"

    # ── Score upgrade potential ───────────────────────────────────────────────
    pts_gap  = sf(sn.get("pts_to_next"))
    next_tier = sn.get("next_tier","")
    top_lever = (sn.get("levers",[{}])[0].get("lever","")) if sn.get("levers") else ""

    # ── Monday priority ───────────────────────────────────────────────────────
    if "TRIPLE" in final:                           priority = 1
    elif grand_s >= 65 or code in almost_triple:    priority = 2
    elif code in dna_5of6:                          priority = 3
    elif grand_s >= 55:                             priority = 4
    else:                                            priority = 5

    priority_label = {1:"🔴 P1-TRIPLE", 2:"🟠 P2-near升評", 3:"🟡 P3-DNA5/6",
                      4:"🟢 P4-BUY建倉", 5:"⚪ P5-觀察"}.get(priority,"—")

    checklist.append({
        "priority":       priority,
        "priority_label": priority_label,
        "code":           code,
        "name":           name,
        "final":          final,
        "grand":          round(grand_s, 1),
        "bull_signs":     bull,
        "alloc_pct":      round(alloc, 2),
        "lots":           pos.get("lots"),
        "risk_tier":      risk_tier,
        # Price levels
        "close":          close,
        "ma30":           round(ma30, 1) if ma30 else None,
        "stop":           stop,
        "stop_pct":       round(stop_pct, 1) if stop_pct else None,
        "stop_buffer_pct": round(-stop_pct, 1) if stop_pct else None,
        "entry_level":    entry_level,
        "entry_action":   entry_action,
        "entry_note":     entry_note,
        "add_level":      add_level,
        "tp1":            tp1,
        "tp2":            tp2,
        # DNA
        "missing_dna":    missing_dna,
        "s3_note":        s3_note,
        "dna_values":     {
            "S1_DMI+DI": round(s1_val,1) if s1_val else None,
            "S2_RSI4m":  round(s2_val,1) if s2_val else None,
            "S3_WR50":   round(s3_val,1) if s3_val else None,
            "S4_RSI60":  round(s4_val,1) if s4_val else None,
            "S5_VR2w":   round(s5_val,0) if s5_val else None,
            "S6_VR2m":   round(s6_val,0) if s6_val else None,
        },
        # Context
        "pe":             round(pe,1) if pe else None,
        "div_yield":      round(dy,2) if dy else None,
        "rs_60d":         rs60,
        "pct_vs_ma":      round(pct_ma,1) if pct_ma else None,
        "eq_score":       eq.get("eq_score"),
        "eq_grade":       (eq.get("grade","") or "").split(" ")[0],
        "pts_to_upgrade": round(pts_gap,1) if pts_gap else None,
        "next_tier":      next_tier,
        "top_lever":      top_lever,
        "win_60d":        b.get("win_60d"),
        "avg_60d":        round(avg_60d,1) if avg_60d else None,
    })

checklist.sort(key=lambda x: (x["priority"], -x["grand"]))

# ── Generate printable text checklist ────────────────────────────────────────
lines = []
lines.append("=" * 70)
lines.append(f"  台灣 ETF — 週一 {TRADE_DATE} 開盤行動卡")
lines.append(f"  生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}  (數據：{TODAY})")
lines.append("=" * 70)
lines.append("")

for priority_group in [1, 2, 3, 4, 5]:
    group = [c for c in checklist if c["priority"] == priority_group]
    if not group: continue
    label = group[0]["priority_label"]
    lines.append(f"\n{'─'*70}")
    lines.append(f"  {label}")
    lines.append(f"{'─'*70}")
    for c in group:
        close_s = fv(c["close"],1) if c["close"] else "—"
        ma_s    = fv(c["ma30"],1) if c["ma30"] else "—"
        stop_s  = fv(c["stop"],1) if c["stop"] else "—"
        tp1_s   = fv(c["tp1"],1) if c["tp1"] else "—"
        entry_s = fv(c["entry_level"],1) if c["entry_level"] else "—"
        buf_s   = (f"+{c['stop_buffer_pct']:.1f}%") if c.get("stop_buffer_pct") else "—"
        lines.append(f"\n  [{c['code']}] {c['name']:<10} Grand={c['grand']:.1f}  DNA={c['bull_signs']}/6  "
                     f"EQ={c.get('eq_score','—')}  建議={c['alloc_pct']:.2f}%")
        lines.append(f"    收盤={close_s}  MA30={ma_s}  止損={stop_s}({buf_s})")
        lines.append(f"    入場={entry_s} [{c['entry_action']}]  TP1={tp1_s}")
        lines.append(f"    行動：{c['entry_note']}")
        if c.get("s3_note"):
            lines.append(f"    ⚠ {c['s3_note']}")
        if c.get("pts_to_upgrade") and c["pts_to_upgrade"] < 5:
            lines.append(f"    ↑ 距{c['next_tier']} {c['pts_to_upgrade']:.1f}分  槓桿：{c['top_lever']}")

lines.append("\n" + "=" * 70)
lines.append("  關鍵日期：06-08開市 / 06-10五月營收 / 06-18 FOMC+TSMC法說")
lines.append("=" * 70)
txt = "\n".join(lines)

(REPORT_DIR / "PREMARKET.txt").write_text(txt, encoding="utf-8")
(REPORT_DIR / "premarket_checklist.json").write_text(
    json.dumps({"date": TODAY, "trade_date": TRADE_DATE,
                "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "checklist": checklist,
                "summary": {
                    "total_positions": len(checklist),
                    "p1_triple":  len([c for c in checklist if c["priority"]==1]),
                    "p2_near":    len([c for c in checklist if c["priority"]==2]),
                    "p3_dna56":   len([c for c in checklist if c["priority"]==3]),
                    "p4_buy":     len([c for c in checklist if c["priority"]==4]),
                    "p5_watch":   len([c for c in checklist if c["priority"]==5]),
                }}, ensure_ascii=False, indent=2), encoding="utf-8")

print(txt[:2000])
print(f"\n-- premarket_checklist.json + PREMARKET.txt saved ({len(checklist)} positions)")

