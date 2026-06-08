#!/usr/bin/env python3
"""
Iteration 27b: 大飆股DNA Screen
Computes available signals from existing data for each stock.
6 criteria from the system:
  1. 月DMI +DI > 50         ← needs history (N/A)
  2. 月RSI4 > 77            ← proxy: strong cumulative YoY momentum
  3. 日W%R50 < 20           ← proxy: close in lower 20% of recent range (oversold)
  4. 日RSI60 > 57           ← proxy: price significantly above baseline
  5. 週VR2 ≥ 150            ← needs history (N/A)
  6. 月VR2 ≥ 150            ← needs history (N/A)

Additional from system:
  A. 日MACD四箭頭向上       ← proxy: price trend + above MA
  B. 日DMI ADX向上          ← proxy: strong MA distance + positive momentum
  C. 金融 vs 大盤 鐘擺      ← compute from MA data

Generates: dna_screen.json
"""

import json
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite  = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
momentum   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
ma_data    = json.loads((REPORT_DIR / "ma_refresh.json").read_text(encoding="utf-8"))
aprdata    = json.loads((REPORT_DIR / "april_revenue.json").read_text(encoding="utf-8"))
conviction = json.loads((REPORT_DIR / "conviction_data.json").read_text(encoding="utf-8"))
bwibbu     = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}
sector_map= {s["code"]: s.get("sector", "—") for s in composite}

# Build maps
mom_map  = {m["code"]: m for m in momentum.get("all_momentum", [])}
ma_map   = {r["code"]: r for r in ma_data.get("all_results", [])}

# April revenue YoY map
apr_yoy_map = {}
for r in aprdata.get("stocks", []):
    apr_yoy_map[r["code"]] = r.get("cum_yoy")

# Conviction
conv_map = {r["code"]: r for r in conviction.get("all_ranked", [])}

# BWIBBU fresh valuations
bwi_map = {r["code"]: r for r in bwibbu.get("all_refreshed", [])}

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v is not None else None
    except: return None

# ─────────────────────────────────────────────────────────────────────────────
# Financial sector detection
FIN_CODES = {"2882","2881","2886","2884","2883","2885","2887","2891","2892",
             "2880","2890","5876","5871","2801","2885","2884","2886","6013",
             "2892","2891","2820"}

results = []
for code, name in sorted(name_map.items()):
    m   = mom_map.get(code, {})
    mar = ma_map.get(code, {})
    apr = apr_yoy_map.get(code)
    cr  = conv_map.get(code, {})
    bw  = bwi_map.get(code, {})

    close       = sf(m.get("close"))
    prior_p     = sf(m.get("prior_price"))
    pct_prior   = sf(m.get("pct_vs_prior"))     # % change since baseline
    ma30        = sf(mar.get("ma30"))
    pct_ma      = sf(mar.get("pct_vs_ma"))      # % vs 30d MA
    intraday    = sf(m.get("intraday_pct"))      # 0=at low, 100=at high
    pe_new      = sf(bw.get("pe_new"))
    div_yield   = sf(bw.get("div_new") or bw.get("div_yield"))
    is_fin      = code in FIN_CODES

    # ── Signal 3: 日W%R50 proxy ──────────────────────────────────────────────
    # True W%R50 needs 50 days. Proxy: closing in bottom 20% of day range = oversold
    # W%R < 20 condition = close near low = oversold = potential base building
    wr_proxy_bull = (intraday is not None and intraday > 75)   # closing near high = up-trend
    wr_proxy_bear = (intraday is not None and intraday < 25)   # closing near low = down-trend
    wr_signal = "🟢 高收" if wr_proxy_bull else ("🔴 低收" if wr_proxy_bear else "—")

    # ── Signal 4: 日RSI60 proxy ───────────────────────────────────────────────
    # Proxy: if price > baseline AND above MA → RSI likely > 57
    rsi_proxy_bull = (pct_prior is not None and pct_prior > 5 and
                      pct_ma    is not None and pct_ma   > 0)
    rsi_proxy_bear = (pct_prior is not None and pct_prior < -5 and
                      pct_ma    is not None and pct_ma   < 0)
    rsi_signal = "🟢" if rsi_proxy_bull else ("🔴" if rsi_proxy_bear else "—")

    # ── Signal 2: 月RSI4 proxy ────────────────────────────────────────────────
    # Proxy: if April revenue cumulative YoY > +50% → strong earnings momentum → monthly RSI high
    mrsi_proxy_bull = (apr is not None and apr > 50)
    mrsi_proxy_bear = (apr is not None and apr < -10)
    mrsi_signal = "🟢" if mrsi_proxy_bull else ("🔴" if mrsi_proxy_bear else "—")

    # ── Signal A: MACD四箭頭 proxy ────────────────────────────────────────────
    # Proxy: price above MA AND positive momentum → MACD likely bullish
    macd_bull = (pct_ma is not None and pct_ma > 3 and
                 pct_prior is not None and pct_prior > 0)
    macd_bear = (pct_ma is not None and pct_ma < -5 and
                 pct_prior is not None and pct_prior < -5)
    macd_signal = "🟢" if macd_bull else ("🔴" if macd_bear else "—")

    # ── Signal B: DMI ADX proxy ───────────────────────────────────────────────
    # Proxy: strong MA deviation (> 5% above) + strong momentum → ADX trending
    adx_bull = (pct_ma is not None and pct_ma > 5)
    adx_bear = (pct_ma is not None and pct_ma < -7)
    adx_signal = "🟢" if adx_bull else ("🔴" if adx_bear else "—")

    # ── Composite 飆股 score ──────────────────────────────────────────────────
    bull_count = sum([wr_proxy_bull, rsi_proxy_bull, mrsi_proxy_bull, macd_bull, adx_bull])
    bear_count = sum([wr_proxy_bear, rsi_proxy_bear, mrsi_proxy_bear, macd_bear, adx_bear])

    verdict = "NEUTRAL"
    if bull_count >= 3: verdict = "🚀 STRONG BULL"
    elif bull_count == 2: verdict = "📈 BULL"
    elif bear_count >= 3: verdict = "💥 STRONG BEAR"
    elif bear_count == 2: verdict = "📉 BEAR"

    results.append({
        "code":          code,
        "name":          name,
        "is_fin":        is_fin,
        "close":         close,
        "pct_vs_prior":  pct_prior,
        "pct_vs_ma":     pct_ma,
        "intraday_pct":  intraday,
        "ma30":          ma30,
        "pe":            pe_new,
        "div":           div_yield,
        "apr_yoy":       apr,
        "score":         score_map.get(code),
        "conv":          cr.get("action", "—"),
        # signals
        "wr_signal":     wr_signal,
        "rsi_signal":    rsi_signal,
        "mrsi_signal":   mrsi_signal,
        "macd_signal":   macd_signal,
        "adx_signal":    adx_signal,
        "bull_count":    bull_count,
        "bear_count":    bear_count,
        "verdict":       verdict,
    })

# Sort by bull_count desc then bear_count desc
bullish = sorted([r for r in results if r["bull_count"] >= 2], key=lambda x: -x["bull_count"])
bearish = sorted([r for r in results if r["bear_count"] >= 2], key=lambda x: -x["bear_count"])
neutral = [r for r in results if r["bull_count"] < 2 and r["bear_count"] < 2]

# ── 大飆股末日: 金融 vs 大盤 鐘擺 ─────────────────────────────────────────────
fin_above_ma = [r for r in results if r["is_fin"] and (r["pct_vs_ma"] or 0) > 3]
nonfin_above_ma = [r for r in results if not r["is_fin"] and (r["pct_vs_ma"] or 0) > 3]
fin_avg_ma = (sum(r["pct_vs_ma"] for r in results if r["is_fin"] and r["pct_vs_ma"] is not None) /
              max(1, sum(1 for r in results if r["is_fin"] and r["pct_vs_ma"] is not None)))
nonfin_avg_ma = (sum(r["pct_vs_ma"] for r in results if not r["is_fin"] and r["pct_vs_ma"] is not None) /
                 max(1, sum(1 for r in results if not r["is_fin"] and r["pct_vs_ma"] is not None)))

pendulum = "金融相對強" if fin_avg_ma > nonfin_avg_ma + 2 else (
           "權值/中小型相對強" if nonfin_avg_ma > fin_avg_ma + 2 else "均衡")

print(f"\n大飆股DNA Screen Results:")
print(f"  Total: {len(results)} | Bullish (2+): {len(bullish)} | Bearish (2+): {len(bearish)}")
print(f"  金融avg MA%: {fin_avg_ma:+.1f}% | 非金融avg MA%: {nonfin_avg_ma:+.1f}%")
print(f"  鐘擺: {pendulum}")
print("\n  🚀 STRONG BULL / 📈 BULL:")
for r in bullish[:8]:
    print(f"    {r['code']} {r['name'][:6]} | bull={r['bull_count']} | {r['verdict']} | MA:{r['pct_vs_ma']:+.1f}%")
print("\n  💥 STRONG BEAR / 📉 BEAR:")
for r in bearish[:8]:
    print(f"    {r['code']} {r['name'][:6]} | bear={r['bear_count']} | {r['verdict']} | MA:{r['pct_vs_ma']:+.1f}%")

# Save
out = {
    "date":          TODAY,
    "fetch_ts":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total":         len(results),
    "bullish_count": len(bullish),
    "bearish_count": len(bearish),
    "pendulum":      pendulum,
    "fin_avg_ma":    round(fin_avg_ma, 2),
    "nonfin_avg_ma": round(nonfin_avg_ma, 2),
    "bullish":       bullish,
    "bearish":       bearish,
    "neutral":       neutral,
    "all_results":   results,
}
(REPORT_DIR / "dna_screen.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✓ dna_screen.json written")
