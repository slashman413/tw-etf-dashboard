#!/usr/bin/env python3
"""
Generate ETF analysis for 00939, 00934, 00915 using full_market.json data.
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

# Load existing etf_comparison.json
comp_path = RPT / "etf_comparison.json"
with open(comp_path) as f:
    comparison = json.load(f)
existing_codes = {e["etf_code"] for e in comparison.get("etfs", [])}

SECTOR_MAP = {
    "2891":"金融保險","2885":"金融保險","2882":"金融保險","2881":"金融保險",
    "2887":"金融保險","2303":"半導體","3036":"科技硬體","6257":"半導體",
    "2603":"航運","3264":"半導體","6139":"工程","2883":"金融保險",
    "3044":"半導體","2404":"科技硬體","1504":"工業機械","6239":"半導體",
    "2357":"科技硬體","2379":"半導體","5347":"半導體","2618":"航空",
    "2609":"航運","3005":"科技硬體","2211":"鋼鐵","2606":"航運",
    "5871":"金融保險","3702":"科技硬體","6414":"工業電腦","3413":"半導體",
    "4915":"科技硬體","4938":"科技硬體","3034":"半導體","2385":"科技硬體",
    "3042":"電子零組件","1402":"化纖","2504":"建設","2353":"科技硬體",
    "2105":"輪胎","2204":"汽車","6176":"科技硬體","2449":"半導體",
    "2327":"科技硬體","8299":"半導體","2454":"半導體","2382":"科技硬體",
    "5483":"半導體","6409":"物流","3406":"光學","1477":"紡織","4766":"化工",
    "6670":"機械","6121":"科技硬體","6670":"機械","5434":"貿易","3023":"電子零組件",
    "4763":"材料","1476":"紡織","2542":"建設","2451":"科技硬體","2915":"零售",
    "6005":"金融保險","2597":"建設","2637":"航運","4904":"電信","2006":"鋼鐵",
    "3045":"電信","9917":"服務","2206":"汽車","1319":"汽車零件",
    "9941":"金融保險","9910":"紡織","2884":"金融保險","2347":"科技硬體",
    "1216":"食品","6278":"半導體","5904":"零售","2912":"零售","9945":"零售",
    "2395":"科技硬體","2610":"航空","2880":"金融保險",
}

ETFs = {
    "00939": {
        "name": "統一台灣高息動能",
        "theme": "高息動能",
        "holdings": [
            {"code":"2891","name":"中信金","weight":7.41},
            {"code":"2885","name":"元大金","weight":7.11},
            {"code":"2449","name":"京元電子","weight":6.56},
            {"code":"2882","name":"國泰金","weight":6.27},
            {"code":"2881","name":"富邦金","weight":5.84},
            {"code":"2887","name":"台新新光金","weight":5.55},
            {"code":"2303","name":"聯電","weight":5.13},
            {"code":"3036","name":"文曄","weight":4.7},
            {"code":"6257","name":"矽格","weight":3.78},
            {"code":"2603","name":"長榮","weight":3.75},
            {"code":"3264","name":"欣銓","weight":3.71},
            {"code":"6139","name":"亞翔","weight":3.68},
            {"code":"2883","name":"凱基金","weight":3.35},
            {"code":"3044","name":"健鼎","weight":3.19},
            {"code":"2404","name":"漢唐","weight":3.06},
            {"code":"1504","name":"東元","weight":2.66},
            {"code":"6239","name":"力成","weight":2.6},
            {"code":"2357","name":"華碩","weight":2.57},
            {"code":"2379","name":"瑞昱","weight":1.85},
            {"code":"5347","name":"世界","weight":1.71},
            {"code":"2618","name":"長榮航","weight":1.31},
            {"code":"2609","name":"陽明","weight":1.3},
            {"code":"3005","name":"神基","weight":0.99},
            {"code":"2211","name":"長榮鋼","weight":0.87},
            {"code":"2606","name":"裕民","weight":0.76},
            {"code":"5871","name":"中租-KY","weight":0.71},
            {"code":"3702","name":"大聯大","weight":0.70},
            {"code":"6414","name":"樺漢","weight":0.66},
            {"code":"3413","name":"京鼎","weight":0.59},
            {"code":"4915","name":"致伸","weight":0.55},
            {"code":"4938","name":"和碩","weight":0.52},
            {"code":"3034","name":"聯詠","weight":0.46},
            {"code":"2385","name":"群光","weight":0.45},
            {"code":"3042","name":"晶技","weight":0.43},
            {"code":"1402","name":"遠東新","weight":0.40},
            {"code":"2504","name":"國產","weight":0.37},
            {"code":"2353","name":"宏碁","weight":0.36},
            {"code":"2105","name":"正新","weight":0.33},
            {"code":"2204","name":"中華","weight":0.31},
            {"code":"6176","name":"瑞儀","weight":0.27},
        ]
    },
    "00934": {
        "name": "中信成長高股息",
        "theme": "成長高股息",
        "holdings": [
            {"code":"2327","name":"國巨","weight":10.96},
            {"code":"8299","name":"群聯","weight":7.40},
            {"code":"2454","name":"聯發科","weight":6.81},
            {"code":"2603","name":"長榮","weight":6.74},
            {"code":"2382","name":"廣達","weight":6.65},
            {"code":"6139","name":"亞翔","weight":4.0},
            {"code":"2474","name":"可成","weight":3.79},
            {"code":"2357","name":"華碩","weight":3.59},
            {"code":"2379","name":"瑞昱","weight":3.42},
            {"code":"3034","name":"聯詠","weight":3.16},
            {"code":"5871","name":"中租-KY","weight":2.92},
            {"code":"3293","name":"鈊象","weight":2.63},
            {"code":"2615","name":"萬海","weight":2.22},
            {"code":"2880","name":"華南金","weight":2.16},
            {"code":"5483","name":"中美晶","weight":2.03},
            {"code":"6409","name":"旭隼","weight":2.0},
            {"code":"3406","name":"玉晶光","weight":1.61},
            {"code":"1477","name":"聚陽","weight":1.59},
            {"code":"4766","name":"南寶","weight":1.51},
            {"code":"6670","name":"復盛應用","weight":1.37},
            {"code":"6121","name":"新普","weight":1.35},
            {"code":"6176","name":"瑞儀","weight":1.33},
            {"code":"6414","name":"樺漢","weight":1.24},
            {"code":"5434","name":"崇越","weight":1.24},
            {"code":"3023","name":"信邦","weight":1.17},
            {"code":"4763","name":"材料-KY","weight":1.16},
            {"code":"1476","name":"儒鴻","weight":1.04},
            {"code":"2542","name":"興富發","weight":0.97},
            {"code":"2451","name":"創見","weight":0.93},
            {"code":"2915","name":"潤泰全","weight":0.92},
            {"code":"3036","name":"文曄","weight":0.79},
            {"code":"6239","name":"力成","weight":0.70},
            {"code":"2303","name":"聯電","weight":0.62},
            {"code":"3702","name":"大聯大","weight":0.59},
            {"code":"5347","name":"世界","weight":0.57},
            {"code":"2891","name":"中信金","weight":0.56},
            {"code":"6005","name":"群益證","weight":0.56},
            {"code":"2597","name":"潤弘","weight":0.50},
            {"code":"2637","name":"慧洋-KY","weight":0.49},
            {"code":"4904","name":"遠傳","weight":0.49},
            {"code":"2006","name":"東和鋼鐵","weight":0.48},
            {"code":"3045","name":"台灣大","weight":0.46},
            {"code":"9917","name":"中保科","weight":0.45},
            {"code":"2504","name":"國產","weight":0.43},
            {"code":"1216","name":"統一","weight":0.41},
            {"code":"2206","name":"三陽工業","weight":0.40},
            {"code":"1319","name":"東陽","weight":0.35},
            {"code":"9941","name":"裕融","weight":0.34},
            {"code":"9910","name":"豐泰","weight":0.30},
            {"code":"3005","name":"神基","weight":0.28},
        ]
    },
    "00915": {
        "name": "凱基優選高股息30",
        "theme": "多因子高息30",
        "holdings": [
            {"code":"2303","name":"聯電","weight":8.67},
            {"code":"2891","name":"中信金","weight":8.26},
            {"code":"2887","name":"台新新光金","weight":7.79},
            {"code":"2882","name":"國泰金","weight":7.47},
            {"code":"2881","name":"富邦金","weight":6.73},
            {"code":"2884","name":"玉山金","weight":5.28},
            {"code":"3034","name":"聯詠","weight":4.85},
            {"code":"2618","name":"長榮航","weight":4.51},
            {"code":"5871","name":"中租-KY","weight":4.32},
            {"code":"2385","name":"群光","weight":4.17},
            {"code":"2347","name":"聯強","weight":3.69},
            {"code":"1216","name":"統一","weight":3.63},
            {"code":"3702","name":"大聯大","weight":3.40},
            {"code":"2379","name":"瑞昱","weight":3.03},
            {"code":"6005","name":"群益證","weight":2.84},
            {"code":"6176","name":"瑞儀","weight":2.71},
            {"code":"3045","name":"台灣大","weight":2.54},
            {"code":"2883","name":"凱基金","weight":2.35},
            {"code":"3293","name":"鈊象","weight":2.18},
            {"code":"4904","name":"遠傳","weight":1.83},
            {"code":"2610","name":"華航","weight":1.54},
            {"code":"2504","name":"國產","weight":1.45},
            {"code":"6278","name":"台表科","weight":1.38},
            {"code":"4915","name":"致伸","weight":1.14},
            {"code":"5904","name":"寶雅","weight":0.84},
            {"code":"2915","name":"潤泰全","weight":0.20},
            {"code":"2395","name":"研華","weight":0.13},
            {"code":"5434","name":"崇越","weight":0.12},
            {"code":"2912","name":"統一超","weight":0.11},
            {"code":"9945","name":"潤泰新","weight":0.10},
        ]
    }
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

results = {}
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

        # Save new stock reports
        stock_file = STOCK_DIR / f"{code}_report.json"
        if not stock_file.exists() and s:
            sector = SECTOR_MAP.get(code, s.get("sector") or "其他")
            rpt = {"code": code, "name": h["name"], "sector": sector,
                   "generated": f"{TODAY} (from full_market)",
                   "recommendation": {"final": final, "grand_score": grand, "score_breakdown": {"composite": grand}},
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
    results[etf_code] = etf_result
    print(f"  avg_grand={avg_grand} triple={triple} strong={strong_buy} buy={buys} pe={avg_pe} div={avg_div}% → {rating}")

    # Save individual ETF file
    out_path = RPT / f"{etf_code}_etf_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(etf_result, f, ensure_ascii=False, indent=2)
    print(f"  Saved {out_path}")

    # Add to comparison
    comparison["etfs"].append(etf_result)
    comparison["etf_count"] = len(comparison["etfs"])

# Save updated comparison
with open(comp_path, "w", encoding="utf-8") as f:
    json.dump(comparison, f, ensure_ascii=False, indent=2)
print(f"\nUpdated etf_comparison.json → {comparison['etf_count']} ETFs total")

# Summary
print("\n=== FULL ETF COVERAGE SUMMARY ===")
print(f"{'Code':<8} {'Name':<20} {'Holdings':>8} {'Score':>6} {'PE':>6} {'Yield':>6} Rating")
print("-" * 70)
for e in comparison["etfs"]:
    print(f"{e['etf_code']:<8} {e['etf_name']:<20} {e['n_holdings']:>8} {e.get('avg_grand',0):>6.1f} {str(e.get('wt_pe') or '-'):>6} {e.get('wt_div_yield',0):>5.2f}% {e.get('rating','')}")
