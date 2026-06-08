#!/usr/bin/env python3
"""Rebuild technical_data.json from authoritative live sources.

Sources:
  - triple_confirmed: grand_unified.json (grand>=70, bull_signs>=3)
  - MA data: ma_refresh.json (above_list / below_list / all_results)
  - TAIEX: taiex_ohlc.json (current.close)
  - dividend quality: composite_data.json + bwibbu_fresh.json
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
DIR   = Path("reports") / TODAY

grand_d   = json.loads((DIR / "grand_unified.json").read_text(encoding="utf-8"))
ma_d      = json.loads((DIR / "ma_refresh.json").read_text(encoding="utf-8"))
taiex_d   = json.loads(Path("taiex_ohlc.json").read_text(encoding="utf-8"))
bwi_d     = json.loads((DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))
mom_d     = json.loads((DIR / "price_momentum.json").read_text(encoding="utf-8"))

# TRIPLE: grand>=70 AND bull_signs>=3
triple_confirmed = [
    r["code"] for r in grand_d.get("all_ranked", [])
    if (r.get("grand") or 0) >= 70 and (r.get("bull_signs") or 0) >= 3
]

# TAIEX from taiex_ohlc
taiex_close = taiex_d.get("current", {}).get("close")
taiex_pct   = taiex_d.get("current", {}).get("pct_change")
if taiex_pct is None:
    hist = taiex_d.get("history", [])
    if len(hist) >= 2 and hist[-1].get("close") and hist[-2].get("close"):
        prev = hist[-2]["close"]
        taiex_pct = round((taiex_close - prev) / prev * 100, 2) if prev else None
taiex = {"close": taiex_close, "pct": taiex_pct}

# MA data from ma_refresh
above_list  = ma_d.get("above_list", [])
below_list  = ma_d.get("below_list", [])
all_ma      = ma_d.get("all_results", [])
above_ma    = ma_d.get("above_ma", len(above_list))
below_ma    = ma_d.get("below_ma", len(below_list))
matched     = ma_d.get("valid", above_ma + below_ma)

# Name map from momentum
name_map = {m["code"]: m.get("name", m["code"]) for m in mom_d.get("all_momentum", [])}
# Also from grand
for r in grand_d.get("all_ranked", []):
    if r.get("code") and r.get("name"):
        name_map.setdefault(r["code"], r["name"])

# Grand score map
grand_map = {r["code"]: r.get("grand", 0) for r in grand_d.get("all_ranked", [])}

# Build bounce candidates: below MA + grand>=55
bounce_candidates = []
for row in below_list:
    code = row.get("code", "")
    g = grand_map.get(code, 0)
    if g >= 55:
        bounce_candidates.append({
            "code":      code,
            "name":      name_map.get(code, code),
            "score":     round(g, 1),
            "pct_vs_ma": round(row.get("pct_vs_ma", 0), 1),
            "tech_sig":  row.get("signal", row.get("tech_sig", "BELOW")),
        })
bounce_candidates.sort(key=lambda x: x["score"] - abs(x["pct_vs_ma"]), reverse=True)

# Momentum intact: above MA + grand>=55
momentum_intact = []
for row in above_list:
    code = row.get("code", "")
    g = grand_map.get(code, 0)
    if g >= 55:
        momentum_intact.append({
            "code":      code,
            "name":      name_map.get(code, code),
            "score":     round(g, 1),
            "pct_vs_ma": round(row.get("pct_vs_ma", 0), 1),
            "tech_sig":  row.get("signal", row.get("tech_sig", "ABOVE")),
        })
momentum_intact.sort(key=lambda x: -x["pct_vs_ma"])

# High div quality from bwibbu (div yield >= 3.5%)
bwi_map = {b["code"]: b for b in bwi_d.get("all_refreshed", [])}
high_div_quality = []
for code, b in bwi_map.items():
    div = b.get("div_new") or b.get("yield_pct")
    if div and div >= 3.5:
        g = grand_map.get(code, 0)
        high_div_quality.append({
            "code":  code,
            "name":  name_map.get(code, code),
            "div":   round(div, 2),
            "score": round(g, 1),
        })
high_div_quality.sort(key=lambda x: -x["div"])

out = {
    "date":             TODAY,
    "generated":        datetime.now().strftime("%Y-%m-%d %H:%M"),
    "taiex":            taiex,
    "summary":          {"above_ma": above_ma, "below_ma": below_ma, "matched": matched},
    "triple_confirmed": triple_confirmed,
    "bounce_candidates": bounce_candidates[:15],
    "momentum_intact":   momentum_intact[:15],
    "high_div_quality":  high_div_quality[:10],
}

(DIR / "technical_data.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"technical_data.json rebuilt for {TODAY}")
pct_str = f"{taiex_pct:+.2f}%" if taiex_pct is not None else "n/a"
print(f"  TAIEX: {taiex_close:,.2f} ({pct_str})")
print(f"  Above MA: {above_ma}  Below MA: {below_ma}  Matched: {matched}")
print(f"  TRIPLE ({len(triple_confirmed)}): {triple_confirmed}")
print(f"  Bounce candidates: {len(bounce_candidates)}")
print(f"  Momentum intact: {len(momentum_intact)}")
print(f"  High div quality: {len(high_div_quality)}")
