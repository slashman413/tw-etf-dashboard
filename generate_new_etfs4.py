#!/usr/bin/env python3
"""
Generate ETF analysis for 00905, 00850 using full_market.json data.
Holdings sourced from wantgoo.com 2026-06-12.
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
RPT = Path("reports") / TODAY
STOCK_DIR = RPT / "stocks"
STOCK_DIR.mkdir(parents=True, exist_ok=True)

with open(RPT / "full_market.json") as f:
    raw = json.load(f)
fm_data = {c["code"]: c for c in raw.get("companies", [])}
print(f"Full market: {len(fm_data)} stocks")

comp_path = RPT / "etf_comparison.json"
with open(comp_path) as f:
    comparison = json.load(f)
existing_codes = {e["etf_code"] for e in comparison.get("etfs", [])}

SECTOR_MAP = {
    "2330":"半導體","2308":"電子零組件","2454":"半導體","2317":"科技硬體",
    "3711":"半導體","2382":"科技硬體","2412":"電信","2891":"金融保險",
    "2881":"金融保險","2882":"金融保險","2360":"電子零組件","2313":"電子零組件",
    "6515":"電子零組件","2383":"電子零組件","4958":"電子零組件","3533":"電子零組件",
    "3017":"電子零組件","2603":"航運","3653":"電子零組件","2345":"網路設備",
    "2303":"半導體","3037":"電子零組件","2885":"金融保險","2887":"金融保險",
    "2884":"金融保險","2886":"金融保險","2303":"半導體",
    "2891":"金融保險","2885":"金融保險","2603":"航運","5347":"半導體",
    "2618":"航空","2609":"航運","3005":"科技硬體","2357":"科技硬體",
    "2379":"半導體","3034":"半導體","2474":"可成","2353":"科技硬體",
    "6121":"科技硬體","3036":"科技硬體","3702":"科技硬體","2385":"科技硬體",
    "5871":"金融保險","6176":"科技硬體","1402":"化纖","1477":"紡織",
    "1476":"紡織","2504":"建設","6005":"金融保險","1504":"工業機械",
    "2610":"航空","2105":"輪胎","2049":"工業機械","2890":"金融保險",
    "9904":"紡織","2886":"金融保險","2633":"交通運輸","1102":"水泥",
    "5876":"金融保險","2801":"金融保險","5880":"金融保險","8464":"家居",
    "2615":"航運","2812":"金融保險","2834":"金融保險",
    "3231":"科技硬體","2376":"科技硬體","8069":"電子零組件",
    "8046":"半導體","2356":"科技硬體","2393":"電子零組件",
    "6285":"科技硬體","2409":"顯示器","8081":"半導體","6278":"半導體",
}

ETFs = {
    "00905": {
        "name": "野村臺灣高息科技50",
        "theme": "科技高息50",
        "holdings": [
            {"code":"2330","name":"台積電","weight":30.9},
            {"code":"2308","name":"台達電","weight":6.06},
            {"code":"2454","name":"聯發科","weight":4.2},
            {"code":"2317","name":"鴻海","weight":4.0},
            {"code":"3711","name":"日月光投控","weight":3.78},
            {"code":"2382","name":"廣達","weight":2.89},
            {"code":"2412","name":"中華電","weight":2.84},
            {"code":"2891","name":"中信金","weight":2.82},
            {"code":"2881","name":"富邦金","weight":2.78},
            {"code":"2882","name":"國泰金","weight":2.68},
            {"code":"2360","name":"致茂","weight":1.44},
            {"code":"2313","name":"華通","weight":1.42},
            {"code":"6515","name":"穎崴","weight":1.19},
            {"code":"2383","name":"台光電","weight":1.06},
            {"code":"4958","name":"臻鼎-KY","weight":1.03},
            {"code":"3533","name":"嘉澤","weight":1.01},
            {"code":"3017","name":"奇鋐","weight":0.87},
            {"code":"2603","name":"長榮","weight":0.86},
            {"code":"3653","name":"健策","weight":0.86},
            {"code":"2345","name":"智邦","weight":0.85},
        ]
    },
    "00850": {
        "name": "元大臺灣ESG永續",
        "theme": "ESG永續",
        "holdings": [
            {"code":"2330","name":"台積電","weight":31.39},
            {"code":"2454","name":"聯發科","weight":5.03},
            {"code":"2308","name":"台達電","weight":6.12},
            {"code":"2317","name":"鴻海","weight":5.25},
            {"code":"3711","name":"日月光投控","weight":2.47},
            {"code":"2891","name":"中信金","weight":2.08},
            {"code":"2382","name":"廣達","weight":1.75},
            {"code":"2345","name":"智邦","weight":1.72},
            {"code":"2383","name":"台光電","weight":1.66},
            {"code":"2881","name":"富邦金","weight":1.59},
            {"code":"2303","name":"聯電","weight":1.51},
            {"code":"3017","name":"奇鋐","weight":1.48},
            {"code":"2882","name":"國泰金","weight":1.36},
            {"code":"3037","name":"欣興","weight":1.31},
            {"code":"2360","name":"致茂","weight":1.24},
            {"code":"2412","name":"中華電","weight":1.23},
            {"code":"2885","name":"元大金","weight":1.1},
            {"code":"2887","name":"台新新光金","weight":1.07},
            {"code":"2884","name":"玉山金","weight":1.05},
            {"code":"2886","name":"兆豐金","weight":1.04},
        ]
    },
}

def score_stock(s):
    score = 50
    pe = s.get("pe")
    div = s.get("yield") or 0
    eps = s.get("eps_q1")
    op_m = s.get("op_margin")
    qs = s.get("quick_score", 0)
    rev_yoy = s.get("rev_yoy")
    if pe and pe > 0:
        if pe < 15: score += 10
        elif pe < 25: score += 5
        elif pe > 50: score -= 10
    if div:
        if div > 5: score += 10
        elif div > 3: score += 5
    if eps and eps > 0: score += 5
    if op_m and op_m > 15: score += 5
    if rev_yoy and rev_yoy > 20: score += 5
    if qs: score += (qs - 3) * 3
    return min(max(score, 0), 100)

def rating_label(score):
    if score >= 75: return "🚀 TRIPLE CONFIRMED"
    elif score >= 65: return "✅ STRONG BUY"
    elif score >= 55: return "📈 BUY"
    elif score >= 45: return "👀 WATCH"
    elif score >= 35: return "⬛ HOLD"
    else: return "❌ REDUCE"

for etf_code, etf in ETFs.items():
    if etf_code in existing_codes:
        print(f"Skipping {etf_code} (already exists)")
        continue

    print(f"\n=== {etf_code} {etf['name']} ===")
    holdings_out, scores, pes, divs = [], [], [], []

    for h in etf["holdings"]:
        code = h["code"]
        s = fm_data.get(code, {})
        pe = s.get("pe")
        div = s.get("yield") or 0
        grand = score_stock(s) if s else 40
        final = rating_label(grand)
        if pe: pes.append(pe)
        if div: divs.append(div)
        scores.append(grand)

        entry = {
            "code": code, "name": h["name"], "weight_pct": h["weight"],
            "price": s.get("price"), "grand": round(grand, 1), "final": final,
            "pe": round(pe, 2) if pe else None, "div_yield": round(div, 2) if div else 0,
            "eps_q1": s.get("eps_q1"), "quick_score": s.get("quick_score", 0),
            "rev_yoy": round(s.get("rev_yoy"), 1) if s.get("rev_yoy") else None,
            "op_margin": s.get("op_margin"),
        }
        holdings_out.append(entry)

        stock_file = STOCK_DIR / f"{code}_report.json"
        if not stock_file.exists() and s:
            sector = SECTOR_MAP.get(code, s.get("sector") or "其他")
            rpt = {"code": code, "name": h["name"], "sector": sector,
                   "generated": f"{TODAY} (from full_market)",
                   "recommendation": {"final": final, "grand_score": grand},
                   "market_data": {"close": s.get("price")},
                   "valuation": {"pe": pe, "pb": s.get("pb"), "div_yield": div},
                   "fundamental": {"q1_eps": s.get("eps_q1"), "op_margin": s.get("op_margin"),
                                   "net_margin": s.get("net_margin"), "rev_yoy": s.get("rev_yoy")},
                   "alerts": []}
            with open(stock_file, "w", encoding="utf-8") as f:
                json.dump(rpt, f, ensure_ascii=False, indent=2)
            print(f"  Saved {code}")

    triple = sum(1 for h in holdings_out if "TRIPLE" in h["final"])
    strong_buy = sum(1 for h in holdings_out if "STRONG BUY" in h["final"])
    buys = sum(1 for h in holdings_out if h["final"] == "📈 BUY")
    avg_grand = round(sum(scores) / len(scores), 1) if scores else 0
    avg_pe = round(sum(pes) / len(pes), 1) if pes else None
    avg_div = round(sum(divs) / len(divs), 2) if divs else 0

    sectors = {}
    for h in holdings_out:
        sec = SECTOR_MAP.get(h["code"], "其他")
        sectors[sec] = sectors.get(sec, 0) + h["weight_pct"]
    top_sectors = sorted(sectors.items(), key=lambda x: -x[1])[:4]

    if avg_grand >= 65: rating = "🔥 強力推薦"
    elif avg_grand >= 55: rating = "📈 積極看多"
    elif avg_grand >= 45: rating = "⬜ 中性觀望"
    else: rating = "📉 偏空謹慎"

    etf_result = {
        "etf_code": etf_code, "etf_name": etf["name"], "theme": etf["theme"],
        "n_holdings": len(holdings_out), "avg_grand": avg_grand,
        "wt_pe": avg_pe, "wt_div_yield": avg_div,
        "triple_holdings": triple, "strongbuy_holdings": strong_buy, "buy_holdings": buys,
        "rating": rating,
        "top_sectors": [{"sector": s, "pct": round(p, 1)} for s, p in top_sectors],
        "top_holdings": sorted(holdings_out, key=lambda x: -x["weight_pct"])[:10],
        "all_holdings": holdings_out,
        "data_source": "full_market.json 2026-06-12",
        "holdings_source": "wantgoo.com 2026-06-12",
    }
    print(f"  avg_grand={avg_grand} triple={triple} strong={strong_buy} buy={buys} pe={avg_pe} div={avg_div}% → {rating}")

    out_path = RPT / f"{etf_code}_etf_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(etf_result, f, ensure_ascii=False, indent=2)
    print(f"  Saved {out_path}")

    comparison["etfs"].append(etf_result)
    comparison["etf_count"] = len(comparison["etfs"])

with open(comp_path, "w", encoding="utf-8") as f:
    json.dump(comparison, f, ensure_ascii=False, indent=2)
print(f"\nUpdated etf_comparison.json → {comparison['etf_count']} ETFs total")

print("\n=== FINAL 17 ETF COVERAGE ===")
print(f"{'Code':<8} {'Name':<22} {'Holdings':>8} {'Score':>6} {'PE':>6} {'Yield':>6} Rating")
print("-" * 75)
for e in comparison["etfs"]:
    print(f"{e['etf_code']:<8} {e['etf_name']:<22} {e['n_holdings']:>8} {e.get('avg_grand',0):>6.1f} {str(e.get('wt_pe') or '-'):>6} {e.get('wt_div_yield',0):>5.2f}% {e.get('rating','')}")
