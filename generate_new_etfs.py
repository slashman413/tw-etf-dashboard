#!/usr/bin/env python3
"""
Generate ETF analysis for 00919, 00929, 00940 using existing full_market.json data.
Holdings sourced from wantgoo.com (fetched 2026-06-12).
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
RPT = Path("reports") / TODAY
RPT.mkdir(parents=True, exist_ok=True)
STOCK_DIR = RPT / "stocks"
STOCK_DIR.mkdir(exist_ok=True)

# --- Load existing full-market data ---
fm_data = {}
with open(RPT / "full_market.json") as f:
    raw = json.load(f)
for c in raw.get("companies", []):
    fm_data[c["code"]] = c

print(f"Full market data: {len(fm_data)} stocks loaded")

# --- ETF Holdings (sourced 2026-06-12 from wantgoo.com) ---
ETFs = {
    "00919": {
        "name": "群益台灣精選高息",
        "theme": "高息精選（官告股利）",
        "holdings": [
            {"code":"2891","name":"中信金 CTBC","weight":12.85},
            {"code":"2882","name":"國泰金 Cathay","weight":12.4},
            {"code":"2881","name":"富邦金 Fubon","weight":9.93},
            {"code":"2303","name":"聯電 UMC","weight":8.67},
            {"code":"2887","name":"台新金 Taishin","weight":7.89},
            {"code":"2603","name":"長榮 Evergreen","weight":5.65},
            {"code":"2357","name":"華碩 ASUS","weight":5.24},
            {"code":"3034","name":"聯詠 Novatek","weight":3.71},
            {"code":"2609","name":"陽明 YangMing","weight":2.92},
            {"code":"3036","name":"文曄 WPG","weight":2.88},
            {"code":"5347","name":"世界 SMIC-TW","weight":2.64},
            {"code":"2618","name":"長榮航 EVA Air","weight":2.37},
            {"code":"2404","name":"漢唐 Han Tang","weight":2.06},
            {"code":"6239","name":"力成 Powertech","weight":1.89},
            {"code":"2474","name":"可成 Catcher","weight":1.42},
            {"code":"2451","name":"創見 Transcend","weight":1.29},
            {"code":"5522","name":"遠雄 Farglory","weight":1.21},
            {"code":"3702","name":"大聯大 WPG","weight":1.18},
            {"code":"6121","name":"新普 Simplo","weight":1.08},
            {"code":"2385","name":"群光 Chicony","weight":1.01},
            {"code":"2504","name":"國產 Catcher","weight":1.0},
            {"code":"6176","name":"瑞儀 Radiant","weight":0.93},
            {"code":"2637","name":"慧洋 Grindrod","weight":0.91},
            {"code":"2606","name":"裕民 U-Ming","weight":0.8},
            {"code":"1477","name":"聚陽 Eclat","weight":0.72},
            {"code":"3211","name":"順達 Simplo","weight":0.67},
            {"code":"2027","name":"大成鋼 Yieh","weight":0.64},
            {"code":"8112","name":"至上 Chih-Shang","weight":0.56},
            {"code":"6005","name":"群益證 Capital","weight":0.49},
            {"code":"1215","name":"卜蜂 CP Taiwan","weight":0.48},
            {"code":"2458","name":"義隆 Elan","weight":0.48},
            {"code":"6670","name":"復盛應用 Fu Sheng","weight":0.46},
            {"code":"2211","name":"長榮鋼 EAS","weight":0.45},
            {"code":"4915","name":"致伸 Primax","weight":0.43},
            {"code":"4763","name":"材料-KY Material","weight":0.41},
            {"code":"6278","name":"台表科 TWI PCB","weight":0.41},
            {"code":"8070","name":"長華 Changhwa","weight":0.41},
            {"code":"6412","name":"群電 Zippy","weight":0.33},
            {"code":"6757","name":"台灣虎航 Tigerair","weight":0.31},
            {"code":"8422","name":"可寧衛 Clean Earth","weight":0.23},
        ]
    },
    "00929": {
        "name": "復華台灣科技優息",
        "theme": "科技高股息",
        "holdings": [
            {"code":"2303","name":"聯電 UMC","weight":8.87},
            {"code":"2357","name":"華碩 ASUS","weight":7.08},
            {"code":"2454","name":"聯發科 MediaTek","weight":5.51},
            {"code":"3008","name":"大立光 LARGAN","weight":5.01},
            {"code":"6239","name":"力成 Powertech","weight":4.61},
            {"code":"2404","name":"漢唐 Han Tang","weight":4.36},
            {"code":"3034","name":"聯詠 Novatek","weight":3.89},
            {"code":"3036","name":"文曄 WPG","weight":3.73},
            {"code":"3260","name":"威剛 ADATA","weight":3.36},
            {"code":"3044","name":"健鼎 Tripod","weight":2.98},
            {"code":"6488","name":"環球晶 GlobalWafers","weight":2.75},
            {"code":"2324","name":"仁寶 Compal","weight":2.56},
            {"code":"5536","name":"聖暉 Holy Stone","weight":2.38},
            {"code":"3264","name":"欣銓 KYEC","weight":2.32},
            {"code":"5483","name":"中美晶 Sino-American Silicon","weight":2.29},
            {"code":"5347","name":"世界 SMIC-TW","weight":2.28},
            {"code":"2301","name":"光寶科 Lite-On","weight":2.22},
            {"code":"3702","name":"大聯大 WPG Holding","weight":2.22},
            {"code":"4938","name":"和碩 Pegatron","weight":2.2},
            {"code":"2330","name":"台積電 TSMC","weight":2.07},
            {"code":"2353","name":"宏碁 Acer","weight":1.95},
            {"code":"2474","name":"可成 Catcher","weight":1.73},
            {"code":"6257","name":"矽格 Sigurd","weight":1.67},
            {"code":"4966","name":"譜瑞-KY Parade","weight":1.56},
            {"code":"3211","name":"順達 Simplo","weight":1.54},
            {"code":"3563","name":"牧德 Machvision","weight":1.39},
            {"code":"2347","name":"聯強 Synnex","weight":1.31},
            {"code":"3680","name":"家登 Gudeng","weight":1.18},
            {"code":"2385","name":"群光 Chicony","weight":0.96},
            {"code":"6548","name":"長科 Longwell","weight":0.92},
            {"code":"3005","name":"神基 Getac","weight":0.88},
            {"code":"8422","name":"可寧衛 Clean Earth","weight":0.83},
            {"code":"3227","name":"原相 PixArt","weight":0.83},
            {"code":"6188","name":"廣明 Quanta Storage","weight":0.81},
            {"code":"2458","name":"義隆 Elan","weight":0.72},
            {"code":"6147","name":"頎邦 Chipbond","weight":0.69},
            {"code":"6176","name":"瑞儀 Radiant","weight":0.66},
            {"code":"3090","name":"日電貿 Ritek","weight":0.63},
            {"code":"6121","name":"新普 Simplo","weight":0.63},
            {"code":"4915","name":"致伸 Primax","weight":0.56},
            {"code":"2439","name":"美律 Merry","weight":0.54},
            {"code":"6278","name":"台表科 TWI PCB","weight":0.48},
            {"code":"8070","name":"長華 Changhwa","weight":0.48},
            {"code":"8016","name":"矽創 Sitronix","weight":0.41},
            {"code":"2393","name":"億光 Everlight","weight":0.31},
            {"code":"5388","name":"中磊 Sercomm","weight":0.28},
            {"code":"8454","name":"富邦媒 Fubon Media","weight":0.25},
            {"code":"6412","name":"群電 Zippy","weight":0.14},
            {"code":"6561","name":"是方 Ipro","weight":0.13},
            {"code":"6803","name":"崑鼎 Kunding","weight":0.06},
        ]
    },
    "00940": {
        "name": "元大台灣價值高息",
        "theme": "價值高息（自由現金流）",
        "holdings": [
            {"code":"2603","name":"長榮 Evergreen","weight":7.03},
            {"code":"3702","name":"大聯大 WPG","weight":3.36},
            {"code":"2891","name":"中信金 CTBC","weight":3.34},
            {"code":"2385","name":"群光 Chicony","weight":2.98},
            {"code":"3034","name":"聯詠 Novatek","weight":2.91},
            {"code":"3036","name":"文曄 WPG2","weight":2.88},
            {"code":"2618","name":"長榮航 EVA Air","weight":2.83},
            {"code":"2454","name":"聯發科 MediaTek","weight":2.79},
            {"code":"2379","name":"瑞昱 Realtek","weight":2.55},
            {"code":"3293","name":"鈊象 International Games","weight":2.50},
            {"code":"2885","name":"元大金 Yuanta","weight":2.48},
            {"code":"2303","name":"聯電 UMC","weight":2.48},
            {"code":"2382","name":"廣達 Quanta","weight":2.43},
            {"code":"9904","name":"寶成 Pou Chen","weight":2.32},
            {"code":"6285","name":"啟碁 Wistron NeWeb","weight":2.31},
            {"code":"2610","name":"華航 China Airlines","weight":2.29},
            {"code":"2357","name":"華碩 ASUS","weight":2.20},
            {"code":"4938","name":"和碩 Pegatron","weight":2.12},
            {"code":"2881","name":"富邦金 Fubon","weight":2.02},
            {"code":"6257","name":"矽格 Sigurd","weight":2.02},
            {"code":"1513","name":"中興電 CTCI","weight":1.98},
            {"code":"2890","name":"永豐金 SinoPac","weight":1.85},
            {"code":"2912","name":"統一超 7-Eleven TW","weight":1.84},
            {"code":"1216","name":"統一 Uni-President","weight":1.83},
            {"code":"3023","name":"信邦 Sinbon","weight":1.82},
            {"code":"1102","name":"亞泥 Asia Cement","weight":1.78},
            {"code":"2404","name":"漢唐 Han Tang","weight":1.77},
            {"code":"1319","name":"東陽 Tong Yang","weight":1.72},
            {"code":"3005","name":"神基 Getac","weight":1.68},
            {"code":"2892","name":"第一金 First","weight":1.67},
            {"code":"2801","name":"彰銀 Chang Hwa","weight":1.66},
            {"code":"3044","name":"健鼎 Tripod","weight":1.58},
            {"code":"2474","name":"可成 Catcher","weight":1.57},
            {"code":"2324","name":"仁寶 Compal","weight":1.56},
            {"code":"3406","name":"玉晶光 GIS","weight":1.53},
            {"code":"6176","name":"瑞儀 Radiant","weight":1.43},
            {"code":"6239","name":"力成 Powertech","weight":1.39},
            {"code":"2458","name":"義隆 Elan","weight":1.33},
            {"code":"4915","name":"致伸 Primax","weight":1.24},
            {"code":"6414","name":"樺漢 Ennoconn","weight":1.23},
            {"code":"3042","name":"晶技 TXC","weight":1.07},
            {"code":"2393","name":"億光 Everlight","weight":0.93},
            {"code":"6278","name":"台表科 TWI PCB","weight":0.84},
            {"code":"6188","name":"廣明 Quanta Storage","weight":0.84},
            {"code":"5469","name":"瀚宇博 HannsTouch","weight":0.83},
            {"code":"2439","name":"美律 Merry","weight":0.77},
            {"code":"2312","name":"金寶 Kinpo","weight":0.71},
            {"code":"2615","name":"萬海 Wan Hai","weight":0.69},
            {"code":"2915","name":"潤泰全 Ruentex","weight":0.57},
            {"code":"8016","name":"矽創 Sitronix","weight":0.52},
        ]
    }
}

SECTOR_MAP = {
    "2891":"金融保險","2882":"金融保險","2881":"金融保險","2303":"半導體","2887":"金融保險",
    "2603":"航運","2357":"科技硬體","3034":"半導體","2609":"航運","3036":"科技硬體",
    "5347":"半導體","2618":"航空","2404":"科技硬體","6239":"半導體","2474":"科技硬體",
    "2451":"科技硬體","5522":"建設","3702":"科技硬體","6121":"科技硬體","2385":"科技硬體",
    "2504":"建設","6176":"科技硬體","2637":"航運","2606":"航運","1477":"紡織",
    "3211":"科技硬體","2027":"鋼鐵","8112":"科技硬體","6005":"金融保險","1215":"食品",
    "2458":"半導體","6670":"機械","2211":"鋼鐵","4915":"科技硬體","4763":"材料",
    "6278":"半導體","8070":"科技硬體","6412":"電力設備","6757":"航空","8422":"環保",
    "2454":"半導體","3008":"光學","3260":"科技硬體","3044":"半導體","6488":"半導體",
    "2324":"科技硬體","5536":"工程","3264":"半導體","5483":"半導體","2301":"科技硬體",
    "4938":"科技硬體","2330":"半導體","2353":"科技硬體","6257":"半導體","4966":"半導體",
    "3563":"科技硬體","2347":"科技硬體","3680":"半導體","6548":"電力設備","3005":"科技硬體",
    "3227":"半導體","6188":"科技硬體","6147":"半導體","3090":"科技硬體","2439":"科技硬體",
    "8016":"半導體","2393":"光電","5388":"科技硬體","8454":"電商","6561":"電信",
    "6803":"環保","3702":"科技硬體","2379":"半導體","3293":"遊戲","2885":"金融保險",
    "2382":"科技硬體","9904":"鞋業","6285":"科技硬體","2610":"航空","1513":"工程",
    "2890":"金融保險","2912":"零售","1216":"食品","3023":"電子零組件","1102":"水泥",
    "1319":"汽車零件","3406":"光學","6414":"工業電腦","3042":"電子零組件","2393":"光電",
    "5469":"科技硬體","2312":"科技硬體","2615":"航運","2915":"零售","2892":"金融保險",
    "2801":"金融保險",
}

def score_stock(s):
    """Simple scoring: 0-100."""
    score = 50
    pe = s.get("pe")
    div = s.get("yield") or s.get("div_yield", 0)
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
    if eps and eps > 0:
        score += 5
    if op_m and op_m > 15: score += 5
    if rev_yoy and rev_yoy > 20: score += 5
    if qs:
        score += (qs - 3) * 3  # qs is 0-6, normalize around 3
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
    print(f"\n=== {etf_code} {etf['name']} ===")
    holdings_out = []
    scores = []
    pes = []
    divs = []

    for h in etf["holdings"]:
        code = h["code"]
        s = fm_data.get(code, {})
        pe = s.get("pe")
        div = s.get("yield") or s.get("div_yield", 0)
        price = s.get("price")
        eps_q1 = s.get("eps_q1")
        qs = s.get("quick_score", 0)
        rev_yoy = s.get("rev_yoy")

        grand = score_stock(s) if s else 40
        final = rating_label(grand)

        if pe: pes.append(pe)
        if div: divs.append(div)
        scores.append(grand)

        entry = {
            "code": code,
            "name": h["name"],
            "weight_pct": h["weight"],
            "price": price,
            "grand": round(grand, 1),
            "final": final,
            "pe": round(pe, 2) if pe else None,
            "div_yield": round(div, 2) if div else 0,
            "eps_q1": eps_q1,
            "quick_score": qs,
            "rev_yoy": round(rev_yoy, 1) if rev_yoy else None,
            "op_margin": s.get("op_margin"),
        }
        holdings_out.append(entry)

        # Save individual stock report if not already exists
        stock_file = STOCK_DIR / f"{code}_report.json"
        if not stock_file.exists() and s:
            sector = SECTOR_MAP.get(code, s.get("sector") or "其他")
            stock_report = {
                "code": code,
                "name": h["name"],
                "sector": sector,
                "generated": f"{TODAY} (from full_market)",
                "recommendation": {
                    "final": final,
                    "grand_score": grand,
                    "score_breakdown": {"composite": grand}
                },
                "market_data": {"close": price},
                "valuation": {"pe": pe, "pb": s.get("pb"), "div_yield": div},
                "fundamental": {
                    "q1_eps": eps_q1,
                    "op_margin": s.get("op_margin"),
                    "net_margin": s.get("net_margin"),
                    "rev_yoy": rev_yoy,
                },
                "alerts": []
            }
            with open(stock_file, "w", encoding="utf-8") as f:
                json.dump(stock_report, f, ensure_ascii=False, indent=2)
            print(f"  Saved {code}")

    # ETF-level summary
    triple = sum(1 for h in holdings_out if "TRIPLE" in h["final"])
    strong_buy = sum(1 for h in holdings_out if "STRONG BUY" in h["final"])
    buys = sum(1 for h in holdings_out if h["final"] == "📈 BUY")
    avg_grand = round(sum(scores) / len(scores), 1) if scores else 0
    avg_pe = round(sum(pes) / len(pes), 1) if pes else None
    avg_div = round(sum(divs) / len(divs), 2) if divs else 0

    # Sector breakdown
    sectors = {}
    for h in holdings_out:
        sec = SECTOR_MAP.get(h["code"], "其他")
        w = h["weight_pct"]
        sectors[sec] = sectors.get(sec, 0) + w
    top_sectors = sorted(sectors.items(), key=lambda x: -x[1])[:4]

    # Rating
    if avg_grand >= 65: etf_rating = "🔥 強力推薦"
    elif avg_grand >= 55: etf_rating = "📈 積極看多"
    elif avg_grand >= 45: etf_rating = "⬜ 中性觀望"
    else: etf_rating = "📉 偏空謹慎"

    etf_result = {
        "etf_code": etf_code,
        "etf_name": etf["name"],
        "theme": etf["theme"],
        "n_holdings": len(holdings_out),
        "avg_grand": avg_grand,
        "wt_pe": avg_pe,
        "wt_div_yield": avg_div,
        "triple_holdings": triple,
        "strongbuy_holdings": strong_buy,
        "buy_holdings": buys,
        "rating": etf_rating,
        "top_sectors": [{"sector": s, "pct": round(p, 1)} for s, p in top_sectors],
        "top_holdings": sorted(holdings_out, key=lambda x: -x["weight_pct"])[:10],
        "all_holdings": holdings_out,
        "data_source": "full_market.json 2026-06-12",
        "holdings_source": "wantgoo.com 2026-06-12",
    }
    results[etf_code] = etf_result

    print(f"  avg_grand={avg_grand} triple={triple} strong_buy={strong_buy} buys={buys}")
    print(f"  avg_pe={avg_pe} avg_div={avg_div}% rating={etf_rating}")

# Save individual ETF files
for code, data in results.items():
    out_path = RPT / f"{code}_etf_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {out_path}")

# Merge into existing etf_comparison.json
comp_path = RPT / "etf_comparison.json"
with open(comp_path) as f:
    existing = json.load(f)

# Add new ETFs to the etfs list
existing_codes = {e["etf_code"] for e in existing.get("etfs", [])}
for code, data in results.items():
    if code not in existing_codes:
        existing["etfs"].append(data)
        existing["etf_count"] = len(existing["etfs"])
        print(f"Added {code} to etf_comparison.json")

with open(comp_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"\nUpdated {comp_path} with {existing['etf_count']} ETFs total")

# Generate master report update
print("\n=== NEW ETF SUMMARY ===")
for code, data in results.items():
    print(f"\n{code} {data['etf_name']} ({data['theme']})")
    print(f"  Holdings: {data['n_holdings']} | Rating: {data['rating']}")
    print(f"  Avg score: {data['avg_grand']} | PE: {data['wt_pe']} | Yield: {data['wt_div_yield']}%")
    print(f"  🚀 Triple: {data['triple_holdings']} | ✅ Strong: {data['strongbuy_holdings']} | 📈 Buy: {data['buy_holdings']}")
    print(f"  Top 3: {', '.join(h['name'] for h in data['top_holdings'][:3])}")
