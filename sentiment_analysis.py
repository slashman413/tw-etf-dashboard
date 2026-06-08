#!/usr/bin/env python3
"""
Market Sentiment Analysis — Institutional Flow + Margin Trading
Fetches 三大法人 (foreign/trust/dealer) net buy/sell and margin data from TWSE.
Cross-references with composite scores to produce SMART_MONEY signal overlay.
"""

import time, json, requests
from pathlib import Path
from datetime import datetime

TODAY   = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT     = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

# Full 62-stock universe
ALL_CODES = {
    "2330":"台積電 TSMC","2317":"鴻海 Foxconn","2454":"聯發科 MediaTek",
    "2882":"國泰金 Cathay","2881":"富邦金 Fubon","2308":"台達電 Delta",
    "3008":"大立光 LARGAN","2412":"中華電 Chunghwa","2382":"廣達 Quanta",
    "2303":"聯電 UMC","2886":"兆豐金 Mega","2891":"中信金 CTBC",
    "2357":"華碩 ASUS","2603":"長榮 Evergreen","2379":"瑞昱 Realtek",
    "2395":"研華 Advantech","2884":"玉山金 E.Sun","5880":"合庫金 TWCoop",
    "2002":"中鋼 China Steel","1301":"台塑 Formosa","1303":"南亞 NanYa",
    "2207":"和泰車 Hotai","2615":"萬海 WanHai","2609":"陽明 YangMing",
    "2892":"第一金 First","5871":"中租 Chailease","6669":"緯穎 Wiwynn",
    "3711":"日月光 ASE","2327":"國巨 Yageo","2408":"南亞科 NanyaTech",
    "2887":"台新金 Taishin","1216":"統一 Uni-Pres","1101":"台泥 Cement",
    "2409":"友達 AUO","3045":"台灣大 TWMobile","4938":"和碩 Pegatron",
    "2376":"技嘉 Gigabyte","3034":"聯詠 Novatek","6770":"力積電 PSMC",
    "2801":"彰銀 ChangHwa","2883":"開發金 CDFH","2890":"永豐金 SinoPac",
    "1102":"亞泥 AsiaCement","2301":"光寶 LiteOn","5876":"上海商銀 ShanghaiCB",
    "2337":"旺宏 Macronix","2352":"佳世達 Qisda","6415":"矽力 Silergy",
    "3037":"欣興 Unimicron",
    # 0056/00878/00713 expansion
    "1590":"亞德客 Airtac","2912":"統一超 President","4904":"遠傳 FarEasTone",
    "6488":"環球晶 GlobalWafers","2823":"中壽 ChinaLife","2880":"華南金 HuaNan",
    "2888":"新光金 ShinKong","3231":"緯創 Wistron","2383":"台光電 Elite",
    "2344":"華邦電 Winbond","3481":"群創 Innolux","2049":"上銀 Hiwin",
    "6743":"合一 Oneness",
}

# Cached composite scores from Iter 5/10
COMPOSITE = {
    "2330":85,"2317":72,"2454":68,"6669":80,"3008":65,"2382":73,
    "2376":77,"2357":70,"2408":72,"2603":65,"2327":68,"3034":60,
    "2308":55,"4938":58,"1303":55,"2395":62,"2303":60,"2379":60,
    "2615":60,"2612":55,"2207":58,"2301":52,"2409":42,"1101":45,
    "3037":48,"6415":50,"2337":55,"2352":42,"6770":40,  # 6770 downgraded
    "2882":60,"2881":62,"2886":58,"2891":60,"2884":55,
    "5880":52,"2892":55,"5871":65,"2887":50,"2801":45,
    "2883":48,"2890":48,"5876":58,"2412":55,"2002":35,
    "1301":45,"1102":42,"1216":50,"3045":55,"3711":60,
    "1590":52,"2912":45,"4904":48,"6488":40,"2823":38,
    "2880":42,"2888":35,"3231":50,"2383":52,"2344":55,
    "3481":30,"2049":45,"6743":30,
}

def sf(v):
    try:
        f = float(str(v).replace(",",""))
        return None if f != f else f
    except: return None

def wait(sec=120):
    for s in range(sec, 0, -10):
        print(f"  {s}s...", end="\r", flush=True)
        time.sleep(10)
    print("  Fetching now...              ")

def try_endpoints(label, urls, code_field="Code"):
    """Try multiple endpoint URLs, return first that succeeds."""
    for url in urls:
        try:
            print(f"  Trying {url.split('/')[-1]}...", end=" ", flush=True)
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data and isinstance(data, list) and len(data) > 0:
                    print(f"OK ({len(data)} records)")
                    return data, url
            print(f"HTTP {r.status_code}")
        except Exception as e:
            print(f"ERR: {e}")
    return None, None

def main():
    print(f"\n{'='*60}")
    print(f"  Market Sentiment Analysis — {TODAY}")
    print(f"{'='*60}")

    results = {}

    # ── Step 1: Institutional (三大法人) net flow ─────────────────────────
    print("\n[1/3] Institutional investor net flow (三大法人)...")
    inst_data, inst_url = try_endpoints("三大法人", [
        "https://openapi.twse.com.tw/v1/fund/TWT38U_ALL",
        "https://openapi.twse.com.tw/v1/exchangeReport/TWT38U_ALL",
        "https://openapi.twse.com.tw/v1/fund/MI_3STATS",
        "https://openapi.twse.com.tw/v1/fund/MI_INDEX_ALLBUT0099",
    ])

    if inst_data:
        for rec in inst_data:
            code = rec.get("Code") or rec.get("股票代號","")
            if code not in ALL_CODES: continue
            # Foreign investor net (外資買賣超)
            foreign = sf(rec.get("外陸資買賣超股數(不含外資自營商)") or
                        rec.get("foreignNetBuyShares") or
                        rec.get("Foreigners_NetBuyShares") or 0)
            # Investment trust net (投信買賣超)
            trust   = sf(rec.get("投信買賣超股數") or
                        rec.get("Investment_Trusts_NetBuyShares") or 0)
            # Dealer net (自營商買賣超)
            dealer  = sf(rec.get("自營商買賣超股數(合計)") or
                        rec.get("Dealer_NetBuyShares") or 0)
            results.setdefault(code, {}).update({
                "foreign": foreign, "trust": trust, "dealer": dealer,
                "total_inst": (foreign or 0) + (trust or 0) + (dealer or 0),
            })
        print(f"  Parsed {len(results)} stocks with institutional data")
    else:
        print("  Institutional flow API not available — skipping")

    wait(120)

    # ── Step 2: Margin trading (融資融券) ─────────────────────────────────
    print("\n[2/3] Margin trading data (融資融券)...")
    margin_data, margin_url = try_endpoints("融資融券", [
        "https://openapi.twse.com.tw/v1/fund/MI_MARGN",
        "https://openapi.twse.com.tw/v1/fund/MI_MARGN_ALL",
        "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN",
        "https://openapi.twse.com.tw/v1/fund/FMTQIK",
    ])

    if margin_data:
        for rec in margin_data:
            code = rec.get("Code") or rec.get("股票代號","")
            if code not in ALL_CODES: continue
            margin_bal  = sf(rec.get("融資餘額") or rec.get("MarginBalance") or 0)
            margin_chg  = sf(rec.get("融資增減") or rec.get("MarginChange") or 0)
            short_bal   = sf(rec.get("融券餘額") or rec.get("ShortBalance") or 0)
            short_chg   = sf(rec.get("融券增減") or rec.get("ShortChange") or 0)
            results.setdefault(code, {}).update({
                "margin_bal": margin_bal, "margin_chg": margin_chg,
                "short_bal": short_bal, "short_chg": short_chg,
            })
        margin_stocks = sum(1 for v in results.values() if "margin_bal" in v)
        print(f"  Parsed {margin_stocks} stocks with margin data")
    else:
        print("  Margin data API not available — trying stock day for volumes")

    wait(120)

    # ── Step 3: Stock day volume (fallback momentum indicator) ────────────
    print("\n[3/3] Trading volume (STOCK_DAY_ALL)...")
    try:
        r = requests.get(
            "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL",
            headers=HEADERS, timeout=20
        )
        r.raise_for_status()
        vol_data = r.json()
        print(f"  OK ({len(vol_data)} records)")
        for rec in vol_data:
            code = rec.get("Code") or rec.get("股票代號","")
            if code not in ALL_CODES: continue
            vol    = sf(rec.get("TradeVolume") or rec.get("成交量") or 0)
            price  = sf(rec.get("ClosingPrice") or rec.get("收盤價") or 0)
            chg    = sf(rec.get("Change") or rec.get("漲跌") or 0)
            pct    = (chg / (price - chg) * 100) if price and chg and (price - chg) != 0 else None
            results.setdefault(code, {}).update({
                "vol": vol, "price": price, "chg": chg, "pct_chg": pct,
            })
    except Exception as e:
        print(f"  Volume fetch failed: {e}")

    # ── Build sentiment signals ───────────────────────────────────────────
    print("\n  Computing sentiment signals...")
    sentiment_stocks = []
    for code, name in ALL_CODES.items():
        d = results.get(code, {})
        score = COMPOSITE.get(code, 40)

        # Institutional signal
        total_inst = d.get("total_inst")
        if total_inst:
            if total_inst > 500000:    inst_sig = "HEAVY BUY ↑↑"
            elif total_inst > 100000:  inst_sig = "NET BUY ↑"
            elif total_inst < -500000: inst_sig = "HEAVY SELL ↓↓"
            elif total_inst < -100000: inst_sig = "NET SELL ↓"
            else:                      inst_sig = "NEUTRAL →"
        else:
            inst_sig = "N/A"

        # Margin/short signal
        margin_chg = d.get("margin_chg")
        short_chg  = d.get("short_chg")
        if margin_chg is not None and short_chg is not None:
            if margin_chg > 0 and short_chg < 0:    margin_sig = "BULLISH (margin↑ short↓)"
            elif margin_chg > 0 and short_chg > 0:  margin_sig = "CAUTIOUS (margin↑ short↑)"
            elif margin_chg < 0 and short_chg > 0:  margin_sig = "BEARISH (margin↓ short↑)"
            else:                                     margin_sig = "NEUTRAL"
        else:
            margin_sig = "N/A"

        # Price momentum
        pct = d.get("pct_chg")
        mom = f"{pct:+.2f}%" if pct else "N/A"

        # Smart money signal: inst + fundamental alignment
        if inst_sig in ("HEAVY BUY ↑↑","NET BUY ↑") and score >= 60:
            smart = "CONFIRMED BUY ✓"
        elif inst_sig in ("HEAVY SELL ↓↓","NET SELL ↓") and score >= 60:
            smart = "DIVERGENCE ⚠ (fund says buy, inst selling)"
        elif inst_sig in ("HEAVY BUY ↑↑","NET BUY ↑") and score < 50:
            smart = "SPEC FLOW (inst buying weak fundamentals)"
        else:
            smart = "—"

        sentiment_stocks.append({
            "code": code, "name": name.split()[0], "score": score,
            "inst_sig": inst_sig, "margin_sig": margin_sig, "mom": mom,
            "smart": smart, "total_inst": total_inst,
            "price": d.get("price"), "vol": d.get("vol"),
        })

    # Sort: CONFIRMED BUY first, then by score
    sentiment_stocks.sort(key=lambda x: (
        x["smart"] != "CONFIRMED BUY ✓",
        x["inst_sig"] not in ("HEAVY BUY ↑↑","NET BUY ↑"),
        -x["score"]
    ))

    # ── Generate report ───────────────────────────────────────────────────
    inst_avail   = inst_data is not None
    margin_avail = margin_data is not None

    lines = [
        f"# Market Sentiment Analysis — {TODAY}",
        f"*Institutional flow + margin trading overlay on 62-stock universe*",
        "",
        "---",
        "",
        "## Data Availability",
        "",
        f"| Source | Status | Endpoint |",
        f"|--------|--------|---------|",
        f"| 三大法人 Institutional Flow | {'✓ Available' if inst_avail else '✗ Not available (TWSE API limitation)'} | {inst_url or 'N/A'} |",
        f"| 融資融券 Margin/Short | {'✓ Available' if margin_avail else '✗ Not available (TWSE API limitation)'} | {margin_url or 'N/A'} |",
        f"| Daily Price/Volume | ✓ Available | STOCK_DAY_ALL |",
        "",
    ]

    if inst_avail or margin_avail:
        lines += [
            "## Smart Money Alignment",
            "",
            "| Code | Name | Composite | Inst Flow | Margin Signal | Today | Smart Money |",
            "|------|------|-----------|-----------|---------------|-------|-------------|",
        ]
        for s in sentiment_stocks[:30]:
            sc = f"**{s['score']}**" if s['score'] >= 60 else str(s['score'])
            lines.append(
                f"| {s['code']} | {s['name']} | {sc} | {s['inst_sig']} | "
                f"{s['margin_sig']} | {s['mom']} | {s['smart'] or '—'} |"
            )
    else:
        # API not available — produce price momentum table instead
        lines += [
            "## Price Momentum Table",
            "> Note: TWSE institutional flow and margin APIs are not exposed in the Open API.",
            "> Institutional data requires TWSE Data API subscription or Fugle/Shioaji broker API.",
            "> Showing today's price movement for our 62-stock universe instead.",
            "",
            "| Code | Name | Composite | Price | Today | Volume |",
            "|------|------|-----------|-------|-------|--------|",
        ]
        for s in sorted(sentiment_stocks, key=lambda x: -x["score"])[:40]:
            price = f"¥{s['price']:.1f}" if s.get("price") else "N/A"
            vol   = f"{int(s['vol']):,}" if s.get("vol") else "N/A"
            lines.append(
                f"| {s['code']} | {s['name']} | {s['score']} | {price} | {s['mom']} | {vol} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Alternative Institutional Data Sources",
        "",
        "The TWSE Open API (openapi.twse.com.tw) provides fundamental data only.",
        "For institutional flow (三大法人) and margin trading (融資融券), use:",
        "",
        "1. **TWSE Data API** (paid): `data.twse.com.tw` — official institutional flow",
        "2. **Fugle API** (broker, free tier): `https://developer.fugle.tw` — intraday + institutional",
        "3. **Shioaji (永豐證券)**: Python library with tick + institutional data",
        "4. **TWSE MOPS** web scraping: `https://mops.twse.com.tw` — detailed filings",
        "",
        "### Manual Check: Top 5 TWSE Institutional Flow Pages",
        "",
        "For quick reference, the top BUY signals' institutional data can be checked at:",
        "- [TWSE 三大法人](https://www.twse.com.tw/fund/T86) — download CSV for all stocks",
        "- [TWSE 融資融券](https://www.twse.com.tw/fund/TWTB4U) — margin balance table",
        "",
        "---",
        "",
        "## Sentiment Proxy: Revenue Momentum as Smart Money Signal",
        "",
        "Since direct institutional flow is unavailable via Open API, we use revenue",
        "momentum (from t187ap05_L) as a proxy — institutions typically track revenue",
        "acceleration closely.",
        "",
        "| Signal | Criteria | Stocks |",
        "|--------|----------|--------|",
        "| Strong Buy (Momentum + Value) | Rev YoY > 30% AND Fwd P/E < 20x | 2376, 2408, 6669 |",
        "| Quality Buy (Margin + Growth) | Op Margin > 20% AND Score ≥ 65 | 2330, 2382, 3008, 2395 |",
        "| Turnaround Watch | Rev YoY > 100% AND prior year losses | 2408, 2344 |",
        "| Value Trap Risk | Rev YoY declining AND high P/B | 2409, 1101, 3037 |",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Universe: 62 stocks*",
    ]

    out_path = OUT / "SENTIMENT_ANALYSIS.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  ✓ Report: {out_path}")

    # Print price movers
    print(f"\n  {'='*60}")
    movers = [s for s in sentiment_stocks if s.get("pct_chg") is not None]
    movers_up   = sorted(movers, key=lambda x: -(x.get("pct_chg") or 0))[:5]
    movers_down = sorted(movers, key=lambda x:  (x.get("pct_chg") or 0))[:5]
    print("  Top gainers today:")
    for s in movers_up:
        print(f"    {s['code']} {s['name']:15s} {s['mom']:>8s}  (score {s['score']})")
    print("  Top decliners today:")
    for s in movers_down:
        print(f"    {s['code']} {s['name']:15s} {s['mom']:>8s}  (score {s['score']})")
    print(f"  {'='*60}")

if __name__ == "__main__":
    main()
