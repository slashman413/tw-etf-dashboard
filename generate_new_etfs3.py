#!/usr/bin/env python3
"""
Generate ETF analysis for 00907, 00918, 00936, 00943 using full_market.json data.
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
    "6670":"機械","6121":"科技硬體","5434":"貿易","3023":"電子零組件",
    "4763":"材料","1476":"紡織","2542":"建設","2451":"科技硬體","2915":"零售",
    "6005":"金融保險","2597":"建設","2637":"航運","4904":"電信","2006":"鋼鐵",
    "3045":"電信","9917":"服務","2206":"汽車","1319":"汽車零件",
    "9941":"金融保險","9910":"紡織","2884":"金融保險","2347":"科技硬體",
    "1216":"食品","6278":"半導體","5904":"零售","2912":"零售","9945":"零售",
    "2395":"科技硬體","2610":"航空","2880":"金融保險","6188":"科技硬體",
    "6147":"半導體","3293":"娛樂","2439":"電子零組件","8454":"電商",
    "6803":"金融保險","3260":"半導體","3680":"網路","6548":"科技硬體",
    "3227":"電子零組件","6561":"科技硬體","2312":"科技硬體","3563":"半導體",
    # Wave 3 new entries
    "2890":"金融保險","9904":"紡織","2886":"金融保險","2633":"交通運輸",
    "1102":"水泥","5876":"金融保險","2801":"金融保險","5880":"金融保險",
    "8464":"家居","2615":"航運","2812":"金融保險","2834":"金融保險",
    "2049":"工業機械","3231":"科技硬體","2376":"科技硬體","8069":"電子零組件",
    "6691":"工程","8046":"半導體","2356":"科技硬體","2393":"電子零組件",
    "9907":"食品","8436":"保健","2530":"建設","2331":"科技硬體","5515":"建設",
    "6285":"科技硬體","1582":"電子零組件","3265":"半導體","2409":"顯示器",
    "3209":"電子零組件","8091":"電子零組件","3455":"電子零組件","8081":"半導體",
    "6613":"電子零組件","6206":"工業電腦","8016":"半導體","3592":"半導體",
    "3033":"電子零組件","3213":"電子零組件","2420":"電子零組件","3010":"電子零組件",
    "6189":"電子零組件","6245":"工業電腦","2480":"科技硬體","8050":"工業電腦",
    "6214":"科技硬體","3617":"電子零組件","2377":"科技硬體","3483":"電子零組件",
    "6412":"電子零組件","3078":"電子零組件","3217":"電子零組件","3022":"工業電腦",
    "5425":"半導體","3015":"電子零組件","8070":"電子零組件","2027":"鋼鐵",
}

ETFs = {
    "00907": {
        "name": "永豐優息",
        "theme": "優質高息",
        "holdings": [
            {"code":"2603","name":"長榮","weight":8.69},
            {"code":"2885","name":"元大金","weight":5.91},
            {"code":"2891","name":"中信金","weight":5.75},
            {"code":"2609","name":"陽明","weight":5.0},
            {"code":"2881","name":"富邦金","weight":4.81},
            {"code":"2890","name":"永豐金","weight":4.46},
            {"code":"1477","name":"聚陽","weight":4.15},
            {"code":"9904","name":"寶成","weight":4.02},
            {"code":"2618","name":"長榮航","weight":3.97},
            {"code":"1504","name":"東元","weight":3.86},
            {"code":"6005","name":"群益證","weight":3.56},
            {"code":"2884","name":"玉山金","weight":3.52},
            {"code":"2886","name":"兆豐金","weight":3.18},
            {"code":"2633","name":"台灣高鐵","weight":2.78},
            {"code":"1102","name":"亞泥","weight":2.66},
            {"code":"5876","name":"上海商銀","weight":2.63},
            {"code":"2801","name":"彰銀","weight":2.61},
            {"code":"2912","name":"統一超","weight":2.52},
            {"code":"1476","name":"儒鴻","weight":2.45},
            {"code":"5880","name":"合庫金","weight":2.39},
            {"code":"2610","name":"華航","weight":2.37},
            {"code":"2105","name":"正新","weight":2.35},
            {"code":"1513","name":"中興電","weight":2.33},
            {"code":"9910","name":"豐泰","weight":2.25},
            {"code":"8464","name":"億豐","weight":2.08},
            {"code":"1319","name":"東陽","weight":2.04},
            {"code":"2615","name":"萬海","weight":1.88},
            {"code":"2812","name":"台中銀","weight":1.66},
            {"code":"2834","name":"臺企銀","weight":1.19},
            {"code":"2049","name":"上銀","weight":0.88},
        ]
    },
    "00918": {
        "name": "大華優利高填息30",
        "theme": "優利高填息30",
        "holdings": [
            {"code":"2603","name":"長榮","weight":8.67},
            {"code":"2891","name":"中信金","weight":6.85},
            {"code":"2887","name":"台新新光金","weight":5.77},
            {"code":"2303","name":"聯電","weight":5.77},
            {"code":"2382","name":"廣達","weight":5.64},
            {"code":"2327","name":"國巨","weight":5.51},
            {"code":"2357","name":"華碩","weight":4.75},
            {"code":"2881","name":"富邦金","weight":4.56},
            {"code":"2618","name":"長榮航","weight":4.52},
            {"code":"2882","name":"國泰金","weight":4.38},
            {"code":"2884","name":"玉山金","weight":3.84},
            {"code":"2379","name":"瑞昱","weight":3.59},
            {"code":"3036","name":"文曄","weight":3.58},
            {"code":"3231","name":"緯創","weight":3.27},
            {"code":"2610","name":"華航","weight":3.25},
            {"code":"3044","name":"健鼎","weight":3.24},
            {"code":"2376","name":"技嘉","weight":3.12},
            {"code":"2474","name":"可成","weight":2.81},
            {"code":"1102","name":"亞泥","weight":2.68},
            {"code":"2404","name":"漢唐","weight":2.53},
            {"code":"8069","name":"元太","weight":2.02},
            {"code":"2353","name":"宏碁","weight":1.66},
            {"code":"6121","name":"新普","weight":1.64},
            {"code":"1476","name":"儒鴻","weight":1.41},
            {"code":"9904","name":"寶成","weight":1.38},
            {"code":"2027","name":"大成鋼","weight":1.21},
            {"code":"3005","name":"神基","weight":0.98},
            {"code":"6409","name":"旭隼","weight":0.60},
            {"code":"9910","name":"豐泰","weight":0.39},
            {"code":"6691","name":"洋基工程","weight":0.12},
        ]
    },
    "00936": {
        "name": "台新臺灣智慧30",
        "theme": "智慧多因子30",
        "holdings": [
            {"code":"8046","name":"南電","weight":6.97},
            {"code":"3036","name":"文曄","weight":5.6},
            {"code":"3702","name":"大聯大","weight":5.49},
            {"code":"5347","name":"世界","weight":4.76},
            {"code":"2385","name":"群光","weight":4.44},
            {"code":"4938","name":"和碩","weight":4.09},
            {"code":"2618","name":"長榮航","weight":4.07},
            {"code":"3034","name":"聯詠","weight":4.06},
            {"code":"5871","name":"中租-KY","weight":4.03},
            {"code":"8422","name":"可寧衛","weight":3.93},
            {"code":"5876","name":"上海商銀","weight":3.91},
            {"code":"2353","name":"宏碁","weight":3.9},
            {"code":"6005","name":"群益證","weight":3.83},
            {"code":"6121","name":"新普","weight":3.54},
            {"code":"1402","name":"遠東新","weight":3.47},
            {"code":"2376","name":"技嘉","weight":3.46},
            {"code":"2356","name":"英業達","weight":3.43},
            {"code":"6176","name":"瑞儀","weight":3.12},
            {"code":"3005","name":"神基","weight":2.99},
            {"code":"2474","name":"可成","weight":2.98},
            {"code":"1477","name":"聚陽","weight":2.53},
            {"code":"2006","name":"東和鋼鐵","weight":2.24},
            {"code":"2393","name":"億光","weight":2.21},
            {"code":"6670","name":"復盛應用","weight":2.15},
            {"code":"2504","name":"國產","weight":2.06},
            {"code":"9907","name":"統一實","weight":1.1},
            {"code":"8436","name":"大江","weight":1.04},
            {"code":"2530","name":"華建","weight":0.72},
            {"code":"2331","name":"精英","weight":0.62},
            {"code":"5515","name":"建國","weight":0.34},
        ]
    },
    "00943": {
        "name": "新光台灣半導體50",
        "theme": "半導體生態50",
        "holdings": [
            {"code":"6285","name":"啟碁","weight":3.2},
            {"code":"1582","name":"信錦","weight":2.78},
            {"code":"3265","name":"台星科","weight":2.75},
            {"code":"3702","name":"大聯大","weight":2.52},
            {"code":"2393","name":"億光","weight":2.48},
            {"code":"6147","name":"頎邦","weight":2.46},
            {"code":"2409","name":"友達","weight":2.41},
            {"code":"2347","name":"聯強","weight":2.33},
            {"code":"3209","name":"全科","weight":2.33},
            {"code":"8091","name":"翔名","weight":2.3},
            {"code":"3455","name":"由田","weight":2.3},
            {"code":"2303","name":"聯電","weight":2.14},
            {"code":"8081","name":"致新","weight":2.07},
            {"code":"6613","name":"朋億","weight":2.07},
            {"code":"4938","name":"和碩","weight":2.04},
            {"code":"6206","name":"飛捷","weight":1.99},
            {"code":"8016","name":"矽創","weight":1.97},
            {"code":"3592","name":"瑞鼎","weight":1.96},
            {"code":"3033","name":"威健","weight":1.94},
            {"code":"2385","name":"群光","weight":1.92},
            {"code":"5483","name":"中美晶","weight":1.92},
            {"code":"2353","name":"宏碁","weight":1.91},
            {"code":"2327","name":"國巨","weight":1.91},
            {"code":"3213","name":"茂訊","weight":1.89},
            {"code":"3034","name":"聯詠","weight":1.88},
            {"code":"2420","name":"新巨","weight":1.85},
            {"code":"3010","name":"華立","weight":1.85},
            {"code":"8112","name":"至上","weight":1.85},
            {"code":"6189","name":"豐藝","weight":1.84},
            {"code":"2474","name":"可成","weight":1.83},
            {"code":"3090","name":"日電貿","weight":1.81},
            {"code":"6245","name":"立端","weight":1.75},
            {"code":"2480","name":"敦陽科","weight":1.74},
            {"code":"6278","name":"台表科","weight":1.73},
            {"code":"8070","name":"長華","weight":1.73},
            {"code":"6121","name":"新普","weight":1.73},
            {"code":"3217","name":"優群","weight":1.73},
            {"code":"3022","name":"威強電","weight":1.72},
            {"code":"5388","name":"中磊","weight":1.7},
            {"code":"3015","name":"全漢","weight":1.69},
            {"code":"5425","name":"台半","weight":1.69},
            {"code":"8050","name":"廣積","weight":1.66},
            {"code":"6214","name":"精誠","weight":1.61},
            {"code":"3617","name":"碩天","weight":1.61},
            {"code":"2377","name":"微星","weight":1.6},
            {"code":"2439","name":"美律","weight":1.57},
            {"code":"3483","name":"力致","weight":1.52},
            {"code":"6412","name":"群電","weight":1.5},
            {"code":"6176","name":"瑞儀","weight":1.49},
            {"code":"3078","name":"僑威","weight":1.48},
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

    out_path = RPT / f"{etf_code}_etf_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(etf_result, f, ensure_ascii=False, indent=2)
    print(f"  Saved {out_path}")

    comparison["etfs"].append(etf_result)
    comparison["etf_count"] = len(comparison["etfs"])

with open(comp_path, "w", encoding="utf-8") as f:
    json.dump(comparison, f, ensure_ascii=False, indent=2)
print(f"\nUpdated etf_comparison.json → {comparison['etf_count']} ETFs total")

print("\n=== FULL ETF COVERAGE SUMMARY ===")
print(f"{'Code':<8} {'Name':<22} {'Holdings':>8} {'Score':>6} {'PE':>6} {'Yield':>6} Rating")
print("-" * 75)
for e in comparison["etfs"]:
    print(f"{e['etf_code']:<8} {e['etf_name']:<22} {e['n_holdings']:>8} {e.get('avg_grand',0):>6.1f} {str(e.get('wt_pe') or '-'):>6} {e.get('wt_div_yield',0):>5.2f}% {e.get('rating','')}")

# Cross-ETF consensus for wave 3
print("\n=== WAVE 3 CROSS-ETF CONSENSUS (stocks in ≥2 of 4 new ETFs) ===")
from collections import Counter
all_new_codes = []
for etf_code, etf in ETFs.items():
    for h in etf["holdings"]:
        all_new_codes.append((h["code"], h["name"]))
code_count = Counter(c for c, n in all_new_codes)
name_map = {c: n for c, n in all_new_codes}
consensus = [(c, count, name_map[c]) for c, count in code_count.items() if count >= 2]
consensus.sort(key=lambda x: -x[1])
print(f"{'Code':<8} {'Name':<12} {'ETFs':>5}")
for code, cnt, name in consensus[:20]:
    s = fm_data.get(code, {})
    grand = score_stock(s) if s else 40
    print(f"  {code:<8} {name:<12} {cnt:>3}x  score={grand:.0f}")
