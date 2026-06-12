#!/usr/bin/env python3
"""
Generate ETF analysis for 00900 (富邦特選高股息30) and 00892 (富邦台灣半導體).
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
    "2881":"金融保險","2882":"金融保險","2887":"金融保險","2884":"金融保險",
    "2886":"金融保險","2880":"金融保險","2885":"金融保險","2883":"金融保險",
    "2303":"半導體","3034":"半導體","2379":"半導體","6239":"半導體",
    "5871":"金融保險","3702":"科技硬體","2474":"科技硬體","6121":"科技硬體",
    "8299":"半導體","6139":"工程","2404":"科技硬體","4763":"材料",
    "1477":"紡織","3023":"電子零組件","2542":"建設","6691":"工程",
    "1210":"食品","5536":"工程","5483":"半導體","3406":"光學","1102":"水泥",
    "4966":"半導體","3008":"光學","2301":"科技硬體","1216":"食品",
    "2890":"金融保險","3702":"科技硬體",
    # 00892 semiconductor specific
    "6223":"半導體","5274":"半導體","6515":"電子零組件","3443":"半導體",
    "3529":"半導體","6510":"半導體","6187":"電子零組件","5434":"貿易",
    "2455":"半導體","1560":"電子零組件","2467":"電子零組件","2458":"半導體",
    "4991":"電子零組件","3413":"半導體","3374":"半導體","6526":"半導體",
    "5314":"電子零組件","3014":"半導體","4919":"半導體","6138":"半導體",
    "3592":"半導體","6640":"電子零組件","6937":"電子零組件","3227":"半導體",
}

ETFs = {
    "00900": {
        "name": "富邦特選高股息30",
        "theme": "特選高股息30",
        "holdings": [
            {"code":"2887","name":"台新新光金","weight":6.12},
            {"code":"2330","name":"台積電","weight":5.83},
            {"code":"3702","name":"大聯大","weight":5.58},
            {"code":"2890","name":"永豐金","weight":5.43},
            {"code":"2880","name":"華南金","weight":5.38},
            {"code":"2454","name":"聯發科","weight":5.1},
            {"code":"5871","name":"中租-KY","weight":5.07},
            {"code":"2884","name":"玉山金","weight":4.99},
            {"code":"3008","name":"大立光","weight":4.66},
            {"code":"2886","name":"兆豐金","weight":4.57},
            {"code":"1216","name":"統一","weight":4.43},
            {"code":"2379","name":"瑞昱","weight":4.38},
            {"code":"2404","name":"漢唐","weight":4.31},
            {"code":"4763","name":"材料-KY","weight":3.61},
            {"code":"6121","name":"新普","weight":3.29},
            {"code":"8299","name":"群聯","weight":3.26},
            {"code":"2474","name":"可成","weight":3.16},
            {"code":"6239","name":"力成","weight":2.98},
            {"code":"2301","name":"光寶科","weight":2.92},
            {"code":"6139","name":"亞翔","weight":2.33},
            {"code":"1477","name":"聚陽","weight":1.82},
            {"code":"3023","name":"信邦","weight":1.71},
            {"code":"2542","name":"興富發","weight":1.56},
            {"code":"6691","name":"洋基工程","weight":1.25},
            {"code":"1210","name":"大成","weight":1.0},
            {"code":"5536","name":"聖暉","weight":1.0},
            {"code":"5483","name":"中美晶","weight":0.98},
            {"code":"3406","name":"玉晶光","weight":0.93},
            {"code":"1102","name":"亞泥","weight":0.85},
            {"code":"4966","name":"譜瑞-KY","weight":0.69},
        ]
    },
    "00892": {
        "name": "富邦台灣半導體",
        "theme": "台灣半導體",
        "holdings": [
            {"code":"2330","name":"台積電","weight":22.36},
            {"code":"6223","name":"旺矽","weight":8.66},
            {"code":"5274","name":"信驊","weight":8.46},
            {"code":"3711","name":"日月光投控","weight":7.38},
            {"code":"6515","name":"穎崴","weight":6.83},
            {"code":"3443","name":"創意","weight":6.42},
            {"code":"3529","name":"力旺","weight":5.25},
            {"code":"2454","name":"聯發科","weight":4.92},
            {"code":"3034","name":"聯詠","weight":4.12},
            {"code":"2379","name":"瑞昱","weight":3.95},
            {"code":"6510","name":"精測","weight":2.35},
            {"code":"6187","name":"萬潤","weight":2.28},
            {"code":"5434","name":"崇越","weight":1.89},
            {"code":"2455","name":"全新","weight":1.70},
            {"code":"1560","name":"中砂","weight":1.63},
            {"code":"2467","name":"志聖","weight":1.41},
            {"code":"2458","name":"義隆","weight":1.34},
            {"code":"4991","name":"環宇-KY","weight":1.17},
            {"code":"3413","name":"京鼎","weight":0.94},
            {"code":"3227","name":"原相","weight":0.91},
            {"code":"3374","name":"精材","weight":0.89},
            {"code":"6526","name":"達發","weight":0.70},
            {"code":"5314","name":"世紀","weight":0.68},
            {"code":"3014","name":"聯陽","weight":0.65},
            {"code":"4919","name":"新唐","weight":0.64},
            {"code":"8081","name":"致新","weight":0.57},
            {"code":"6138","name":"茂達","weight":0.55},
            {"code":"3592","name":"瑞鼎","weight":0.50},
            {"code":"6640","name":"均華","weight":0.37},
            {"code":"6937","name":"天虹","weight":0.28},
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

print("\n=== FINAL 19 ETF COVERAGE ===")
print(f"{'Code':<8} {'Name':<22} {'Holdings':>8} {'Score':>6} {'PE':>6} {'Yield':>6} Rating")
print("-" * 75)
for e in sorted(comparison["etfs"], key=lambda x: -x.get("avg_grand", 0)):
    print(f"{e['etf_code']:<8} {e['etf_name']:<22} {e['n_holdings']:>8} {e.get('avg_grand',0):>6.1f} {str(e.get('wt_pe') or '-'):>6} {e.get('wt_div_yield',0):>5.2f}% {e.get('rating','')}")
