#!/usr/bin/env python3
"""
Iteration 59: DNA Signal Trigger Calculator
For each 4/6 and 5/6 stock: compute the approximate price level that would
fire the missing DNA signal and upgrade to 5/6 or TRIPLE CONFIRMED (6/6).
Uses W%R geometry and current price data.
No API calls. Generates: dna_trigger_calc.json
"""
import json, math
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

dna   = json.loads((REPORT_DIR/"dna_signals.json").read_text(encoding="utf-8"))
rs    = json.loads((REPORT_DIR/"relative_strength.json").read_text(encoding="utf-8"))
grand = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
mom   = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))
bwi   = json.loads((REPORT_DIR/"bwibbu_fresh.json").read_text(encoding="utf-8"))
comp  = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd  = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))

rs_map    = {r["code"]: r for r in rs.get("all_rs",[])}
grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Signal descriptions ───────────────────────────────────────────────────────
SIG_DESC = {
    "S1": "月DMI(+DI) > 50",
    "S2": "月RSI(4) > 77",
    "S3": "日W%R(50) < 20",    # W%R close to 50-day high (top 20% of range)
    "S4": "日RSI(60) > 57",
    "S5": "週VR(2) ≥ 150",
    "S6": "月VR(2) ≥ 150",
}

# How easy/hard each signal is to trigger with price action
SIG_PRICE_SENSITIVITY = {
    "S1": "DMI需持續多頭排列，通常需1-3週",
    "S2": "RSI月線需持續升，通常需2-4週",
    "S3": "價格突破50日高點前20%可立即觸發",  # Most price-sensitive
    "S4": "RSI(60)需維持在57以上，若已接近則1-3天",
    "S5": "週成交量比率需升至150，需量能配合",
    "S6": "月成交量比率需升至150，需1-2個月",
}

# ── Process each 4/6 and 5/6 stock ───────────────────────────────────────────
results = []

for s in dna.get("all_signals", []):
    bull = s.get("bull_signs", 0) or 0
    if bull < 4 or bull > 5:
        continue

    code  = s.get("code", "")
    name  = name_map.get(code, code)
    close = sf(mom_map.get(code, {}).get("close")) or sf(s.get("close")) or sf(s.get("close_now"))
    g     = grand_map.get(code, {})
    rv    = rs_map.get(code, {})
    mm    = mom_map.get(code, {})
    bw    = bwi_map.get(code, {})

    grand_s   = g.get("grand", 0) or 0
    final     = g.get("final", "") or ""
    pct_52h   = sf(rv.get("pct_from_52w_high"))   # negative, e.g. -12.2
    pct_52l   = sf(rv.get("pct_from_52w_low"))     # positive, e.g. 553.9
    pct_ma    = sf(mm.get("pct_vs_ma"))
    pe        = sf(bw.get("pe_new") or bw.get("pe_old"))

    # Identify missing signals
    sigs = {
        "S1": s.get("s1_ok", False),
        "S2": s.get("s2_ok", False),
        "S3": s.get("s3_ok", False),
        "S4": s.get("s4_ok", False),
        "S5": s.get("s5_ok", False),
        "S6": s.get("s6_ok", False),
    }
    missing = [k for k,v in sigs.items() if not v]

    # Current signal values
    sig_vals = {
        "S1": sf(s.get("s1_dmi")),
        "S2": sf(s.get("s2_rsi4m")),
        "S3": sf(s.get("s3_wr50")),
        "S4": sf(s.get("s4_rsi60")),
        "S5": sf(s.get("s5_vr2w")),
        "S6": sf(s.get("s6_vr2m")),
    }

    # Trigger thresholds
    THRESHOLDS = {"S1": 50.0, "S2": 77.0, "S3": 20.0, "S4": 57.0}

    # ── S3 price trigger (most actionable) ───────────────────────────────────
    s3_trigger = None
    s3_gap     = None
    s3_upside_pct = None

    if close and pct_52h is not None and pct_52l is not None:
        # Reconstruct 52-week high/low from percentages
        # pct_from_52w_high = (close - h52) / h52 × 100 → h52 = close / (1 + pct_52h/100)
        # pct_from_52w_low  = (close - l52) / l52 × 100 → l52 = close / (1 + pct_52l/100)
        h52 = close / (1 + pct_52h / 100)
        l52 = close / (1 + pct_52l / 100) if pct_52l > 0 else close * 0.5

        # 50-day range ≈ 35% of 52-week range (empirical Taiwan market estimate)
        range_52w = h52 - l52
        range_50d_est = range_52w * 0.35

        # Current W%R = s3_wr50
        cur_wr = sig_vals["S3"]

        if cur_wr is not None and range_50d_est > 0:
            # Price increase needed to drop W%R from cur_wr to 19.5 (safe margin below 20)
            # ΔClose ≈ (cur_wr - 19.5) / 100 × range_50d_est
            target_wr = 19.5
            if cur_wr > target_wr:
                delta_needed = (cur_wr - target_wr) / 100 * range_50d_est
                s3_trigger = round(close + delta_needed, 1)
                s3_gap     = round(cur_wr - 20, 1)
                s3_upside_pct = round(delta_needed / close * 100, 1)
            else:
                # Already passing
                s3_trigger = close
                s3_gap = 0
                s3_upside_pct = 0

    # ── S4 trigger context ────────────────────────────────────────────────────
    s4_gap = None
    s4_note = ""
    if sig_vals["S4"] is not None:
        s4_gap = round(57.0 - sig_vals["S4"], 1)
        if s4_gap <= 0:
            s4_note = "已超過57"
        elif s4_gap < 3:
            s4_note = f"差{s4_gap:.1f}點，1-3天可達"
        elif s4_gap < 8:
            s4_note = f"差{s4_gap:.1f}點，約1週"
        else:
            s4_note = f"差{s4_gap:.1f}點，需持續上漲"

    # ── S1 trigger context ────────────────────────────────────────────────────
    s1_gap = None
    s1_note = ""
    if sig_vals["S1"] is not None:
        s1_gap = round(50.0 - sig_vals["S1"], 1)
        if s1_gap <= 0:
            s1_note = "已超過50"
        elif s1_gap < 5:
            s1_note = f"差{s1_gap:.1f}點，接近觸發"
        else:
            s1_note = f"差{s1_gap:.1f}點，需多頭持續"

    # ── Overall upgrade difficulty ────────────────────────────────────────────
    # Score: 1 = very easy (< 3% price move), 5 = very hard (requires weeks)
    difficulty_parts = []
    for ms in missing:
        if ms == "S3" and s3_upside_pct is not None:
            if s3_upside_pct <= 1:    d = 1
            elif s3_upside_pct <= 3:  d = 2
            elif s3_upside_pct <= 8:  d = 3
            else:                      d = 4
        elif ms in ("S4",) and s4_gap is not None:
            d = 1 if s4_gap < 2 else (2 if s4_gap < 5 else 3)
        elif ms == "S1":
            d = 3 if (s1_gap or 99) < 5 else 4
        elif ms in ("S5", "S6"):
            d = 5   # volume-based, hard to force
        elif ms == "S2":
            d = 4   # monthly RSI, needs sustained run
        else:
            d = 3
        difficulty_parts.append(d)

    avg_difficulty = round(sum(difficulty_parts) / len(difficulty_parts), 1) if difficulty_parts else 3
    upgrade_label = ["", "🟢 極易觸發", "🟡 易觸發", "🟠 中等", "🔴 較難", "⚫ 困難"][int(avg_difficulty)]

    # ── Monday priority ───────────────────────────────────────────────────────
    # Priority for Monday action based on how close to upgrade
    if bull == 5 and avg_difficulty <= 2:
        monday_priority = "P1 — 周一重點監控，接近TRIPLE"
    elif bull == 5 and avg_difficulty <= 3:
        monday_priority = "P2 — 5/6強勢持倉，升評在望"
    elif bull == 5:
        monday_priority = "P3 — 5/6需時間醞釀"
    elif bull == 4 and avg_difficulty <= 2:
        monday_priority = "P3 — 4/6有快速上升潛力"
    else:
        monday_priority = "P4 — 4/6觀察等待"

    results.append({
        "code":         code,
        "name":         name.split(" ")[0] if name else code,
        "bull_signs":   bull,
        "grand":        round(grand_s, 1),
        "final":        final,
        "close":        close,
        "pct_vs_ma":    round(pct_ma, 1) if pct_ma is not None else None,
        "missing":      missing,
        "sig_vals": {
            "S1_dmi":  round(sig_vals["S1"], 1) if sig_vals["S1"] else None,
            "S2_rsi4m":round(sig_vals["S2"], 1) if sig_vals["S2"] else None,
            "S3_wr50": round(sig_vals["S3"], 1) if sig_vals["S3"] else None,
            "S4_rsi60":round(sig_vals["S4"], 1) if sig_vals["S4"] else None,
        },
        "s3_trigger_price":  s3_trigger,
        "s3_gap_pts":        s3_gap,
        "s3_upside_pct":     s3_upside_pct,
        "s4_gap_pts":        s4_gap,
        "s4_note":           s4_note,
        "s1_gap_pts":        s1_gap,
        "s1_note":           s1_note,
        "avg_difficulty":    avg_difficulty,
        "upgrade_label":     upgrade_label,
        "monday_priority":   monday_priority,
        "pe":                round(pe, 1) if pe else None,
    })

# Sort: 5/6 first, then by difficulty (easiest first)
results.sort(key=lambda x: (-x["bull_signs"], x["avg_difficulty"]))

# ── Key groups ────────────────────────────────────────────────────────────────
near_triple     = [r for r in results if r["bull_signs"] == 5 and r["avg_difficulty"] <= 2]
five_six        = [r for r in results if r["bull_signs"] == 5]
four_six        = [r for r in results if r["bull_signs"] == 4]
s3_only_missing = [r for r in results if r["missing"] == ["S3"]]  # only S3 missing

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'DNA SIGNAL TRIGGER CALCULATOR':=<65}")
print(f"  5/6 stocks: {len(five_six)}  4/6 stocks: {len(four_six)}")
print(f"  Near-TRIPLE (5/6, easy trigger): {len(near_triple)}")

print(f"\n  5/6 升評路徑 (一個信號缺失):")
print(f"  {'代號':<6} {'名稱':<8} {'缺失':>4} {'難度':>5} {'S3觸發':>10} {'S3漲幅%':>8}  {'說明'}")
print("-"*85)
for r in five_six:
    s3t = f"TWD {r['s3_trigger_price']:.1f}" if r['s3_trigger_price'] else "  N/A   "
    s3u = f"+{r['s3_upside_pct']:.1f}%" if r['s3_upside_pct'] else "  — "
    extra = r['s4_note'] if r['missing'] == ['S4'] else r['s1_note'] if r['missing'] == ['S1'] else ""
    print(f"  {r['code']:<6} {r['name']:<8} {','.join(r['missing']):>5}  {r['upgrade_label'][:6]}  "
          f"{s3t:>12} {s3u:>8}  {r['monday_priority'][:30]}  {extra}")

print(f"\n  S3唯一缺失股 (最易觸發 — 漲到50日高點前20%即可):")
for r in s3_only_missing:
    if r['s3_trigger_price']:
        print(f"  {r['code']} {r['name']:<8}  現價={r['close']:>8.1f}  "
              f"S3觸發價≈{r['s3_trigger_price']:>8.1f}  需漲+{r['s3_upside_pct']:.1f}%  "
              f"W%R現值={r['sig_vals']['S3_wr50']:.1f}  {r['upgrade_label']}")

# ── Summary table ─────────────────────────────────────────────────────────────
out = {
    "date":       TODAY,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "methodology": {
        "s3_trigger": "W%R = (HH_50-close)/(HH_50-LL_50)×100 < 20; range_50d ≈ 35% of 52w range",
        "difficulty": "1=極易(≤1%漲), 2=易(≤3%), 3=中等, 4=較難, 5=困難(量能)",
    },
    "summary": {
        "five_six_count":    len(five_six),
        "four_six_count":    len(four_six),
        "near_triple_count": len(near_triple),
        "s3_only_count":     len(s3_only_missing),
    },
    "all_results":     results,
    "near_triple":     near_triple,
    "five_six":        five_six,
    "four_six":        four_six,
    "s3_only_missing": s3_only_missing,
}
(REPORT_DIR/"dna_trigger_calc.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- dna_trigger_calc.json saved ({len(results)} stocks)")

