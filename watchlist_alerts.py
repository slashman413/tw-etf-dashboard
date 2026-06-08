#!/usr/bin/env python3
"""
Iteration 37: Watchlist Alert Scanner
Pure computation — no API calls.
Identifies:
  A) Stocks one signal away from TRIPLE CONFIRMED
  B) DNA bull_signs == 5/6 (one away from full sweep)
  C) Stocks approaching MA30 from below (momentum turning)
  D) Stocks near 52-week high with positive RS
  E) TRIPLE CONFIRMED ranked by upside to price target
Generates: watchlist_alerts.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

grand   = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
dna     = json.loads((REPORT_DIR / "dna_signals.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
rs      = json.loads((REPORT_DIR / "relative_strength.json").read_text(encoding="utf-8"))
pt      = json.loads((REPORT_DIR / "price_targets.json").read_text(encoding="utf-8"))
bwi     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp     = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp}}
grand_map = {r["code"]: r for r in grand.get("all_ranked", [])}
dna_map   = {s["code"]: s for s in dna.get("all_signals", []) if s.get("code")}
mom_map   = {m["code"]: m for m in mom.get("all_momentum", [])}
rs_map    = {r["code"]: r for r in rs.get("all_rs", [])}
pt_map    = {t["code"]: t for t in pt.get("all_targets", [])}
bwi_map   = {r["code"]: r for r in bwi.get("all_refreshed", [])}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

all_codes = set(name_map.keys())

# ── Alert A: One signal away from TRIPLE CONFIRMED ────────────────────────────
# TRIPLE = grand >= 70 AND bull_signs >= 3
# "Almost TRIPLE" = grand between 60-70 OR (grand >= 70 but bull_signs == 2)
alert_a = []
for code in all_codes:
    g  = grand_map.get(code, {})
    d  = dna_map.get(code, {})
    grand_score = g.get("grand", 0) or 0
    bull_signs  = d.get("bull_signs", 0) or 0
    final       = g.get("final", "")

    if "TRIPLE" in final: continue  # already confirmed

    grand_gap  = 70 - grand_score
    signs_gap  = 3 - bull_signs

    # Score gap < 8 points OR one more DNA signal would push over
    is_close = (0 < grand_gap <= 8) or (grand_score >= 65 and signs_gap == 1)
    if is_close:
        # What's needed?
        needs = []
        if grand_gap > 0: needs.append(f"Grand需+{grand_gap:.1f}分")
        if signs_gap > 0: needs.append(f"DNA需+{signs_gap}訊號")

        alert_a.append({
            "code": code, "name": name_map.get(code, code),
            "grand": round(grand_score,1), "grand_gap": round(grand_gap,1),
            "bull_signs": bull_signs, "signs_gap": signs_gap,
            "final": final, "needs": " + ".join(needs) if needs else "接近達標",
            "pe": bwi_map.get(code, {}).get("pe_new"),
            "div": bwi_map.get(code, {}).get("div_new") or bwi_map.get(code, {}).get("div_yield"),
        })

alert_a.sort(key=lambda x: x["grand_gap"])

# ── Alert B: DNA 5/6 — one away from full sweep ──────────────────────────────
alert_b = []
for code in all_codes:
    d = dna_map.get(code, {})
    bs = d.get("bull_signs", 0) or 0
    if bs == 5:
        # Find missing signal
        missing = []
        for k, label in [("s1_ok","S1月DMI"),("s2_ok","S2月RSI4"),
                          ("s3_ok","S3日W%R"),("s4_ok","S4日RSI60"),
                          ("s5_ok","S5週VR"),("s6_ok","S6月VR")]:
            if not d.get(k, False): missing.append(label)
        alert_b.append({
            "code": code, "name": name_map.get(code, code),
            "bull_signs": bs, "missing": ", ".join(missing),
            "verdict": d.get("verdict",""),
            "grand": grand_map.get(code,{}).get("grand"),
            "final": grand_map.get(code,{}).get("final",""),
        })

alert_b.sort(key=lambda x: -(x["grand"] or 0))

# ── Alert C: MA30 crossing — pct_vs_ma improving from below ──────────────────
alert_c = []
for code in all_codes:
    m = mom_map.get(code, {})
    pct_ma    = sf(m.get("pct_vs_ma"))
    pct_prior = sf(m.get("pct_vs_prior"))
    close     = sf(m.get("close"))
    ma30      = sf(m.get("ma30"))
    # Near MA30 from below: pct_ma between -5% and 0%, overall trend up
    if pct_ma is not None and -5 <= pct_ma < 0 and (pct_prior or 0) > 5:
        alert_c.append({
            "code": code, "name": name_map.get(code, code),
            "close": close, "ma30": ma30,
            "pct_vs_ma": round(pct_ma,1), "pct_vs_prior": round(pct_prior,1),
            "grand": grand_map.get(code,{}).get("grand"),
            "final": grand_map.get(code,{}).get("final",""),
            "bull_signs": dna_map.get(code,{}).get("bull_signs",0),
        })

alert_c.sort(key=lambda x: -(x["grand"] or 0))

# ── Alert D: Near 52-week high + positive RS ─────────────────────────────────
alert_d = []
for code in all_codes:
    r = rs_map.get(code, {})
    hi_pct = r.get("pct_from_52w_high")
    rs60   = r.get("rs_60d")
    g      = grand_map.get(code, {})
    # Within 5% of 52w high AND outperforming index by 10%+
    if hi_pct is not None and -5 <= hi_pct <= 2 and (rs60 or 0) > 10:
        alert_d.append({
            "code": code, "name": name_map.get(code, code),
            "pct_from_52w_high": round(hi_pct,1),
            "rs_60d": round(rs60,1),
            "ret_60d": r.get("ret_60d"),
            "grand": g.get("grand"), "final": g.get("final",""),
            "bull_signs": dna_map.get(code,{}).get("bull_signs",0),
        })

alert_d.sort(key=lambda x: -(x["rs_60d"] or 0))

# ── Alert E: TRIPLE CONFIRMED — upside to price target ───────────────────────
alert_e = []
for r in grand.get("triple_confirmed", []):
    code = r["code"]
    t    = pt_map.get(code, {})
    m    = mom_map.get(code, {})
    close = sf(m.get("close"))
    target = sf(t.get("target")) if t else None
    upside = round((target/close - 1)*100, 1) if target and close and close > 0 else None
    alert_e.append({
        "code": code, "name": name_map.get(code, code),
        "grand": r["grand"], "final": r["final"],
        "bull_signs": r.get("bull_signs",0),
        "close": close, "target": target, "upside_pct": upside,
        "pe": bwi_map.get(code,{}).get("pe_new"),
        "div": bwi_map.get(code,{}).get("div_new") or bwi_map.get(code,{}).get("div_yield"),
        "rs_60d": rs_map.get(code,{}).get("rs_60d"),
    })

alert_e.sort(key=lambda x: -(x["upside_pct"] or -99))

# ── Print summary ─────────────────────────────────────────────────────────────
print(f"=== Watchlist Alert Scanner ===")
print(f"\nA) Almost TRIPLE CONFIRMED ({len(alert_a)} stocks):")
for a in alert_a[:8]:
    print(f"  {a['code']} {a['name'][:10]}: grand={a['grand']} DNA={a['bull_signs']}/6 | {a['needs']}")

print(f"\nB) DNA 5/6 — missing 1 signal ({len(alert_b)} stocks):")
for b in alert_b[:5]:
    print(f"  {b['code']} {b['name'][:10]}: missing={b['missing']}")

print(f"\nC) Approaching MA30 from below ({len(alert_c)} stocks):")
for c in alert_c[:5]:
    print(f"  {c['code']} {c['name'][:10]}: {c['pct_vs_ma']:+.1f}% vs MA | Trend:{c['pct_vs_prior']:+.1f}%")

print(f"\nD) Near 52w high + strong RS ({len(alert_d)} stocks):")
for d in alert_d[:5]:
    print(f"  {d['code']} {d['name'][:10]}: {d['pct_from_52w_high']:+.1f}% from 52wH | RS60={d['rs_60d']:+.1f}%")

print(f"\nE) TRIPLE CONFIRMED — upside analysis ({len(alert_e)} stocks):")
for e in alert_e:
    up = f"+{e['upside_pct']:.1f}%" if e.get('upside_pct') else "—"
    print(f"  {e['code']} {e['name'][:10]}: grand={e['grand']} | target upside={up} | PE={e.get('pe','?')} Yield={e.get('div','?')}%")

out = {
    "date":     TODAY,
    "fetch_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "almost_triple": alert_a,
    "dna_5of6":      alert_b,
    "ma_crossing":   alert_c,
    "near_52w_high": alert_d,
    "triple_upside": alert_e,
    "summary": {
        "almost_triple": len(alert_a),
        "dna_5of6":      len(alert_b),
        "ma_crossing":   len(alert_c),
        "near_52w_high": len(alert_d),
        "triple_confirmed": len(alert_e),
    }
}
(REPORT_DIR / "watchlist_alerts.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ watchlist_alerts.json saved")
