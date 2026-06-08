#!/usr/bin/env python3
"""
Generate individual markdown reports for all 0050.TW + 0056.TW component stocks.
Uses the pre-fetched data and rule-based analysis (no API key needed).
"""
import json
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
ROC_YEAR = datetime.now().year - 1911

# ── Pre-fetched data (from dump_etf_data.py run) ─────────────────────────────
RAW = {"2395": {"pe": "40.50", "pb": "9.14", "div": "2.15", "rev": "8269473", "mom": "7.41", "yoy": "34.61", "cum_yoy": "21.96", "period": "11504"}, "5876": {"pe": "12.94", "pb": "0.95", "div": "4.42", "rev": "4216556", "mom": "-8.58", "yoy": "-7.14", "cum_yoy": "-2.22", "period": "11504"}, "6669": {"pe": "18.67", "pb": "7.39", "div": "2.96", "rev": "82730996", "mom": "-16.14", "yoy": "29.67", "cum_yoy": "53.22", "period": "11504"}, "2883": {"pe": "15.39", "pb": "1.37", "div": "3.65", "rev": "13466790", "mom": "147.27", "yoy": "144.31", "cum_yoy": "319.62", "period": "11504"}, "2886": {"pe": "17.11", "pb": "1.55", "div": "4.16", "rev": "9055059", "mom": "47.18", "yoy": "63.04", "cum_yoy": "23.64", "period": "11504"}, "2887": {"pe": "14.00", "pb": "1.25", "div": "3.85", "rev": "17221187", "mom": "33.11", "yoy": "16.09", "cum_yoy": "137.67", "period": "11504"}, "6415": {"pe": "76.61", "pb": "5.80", "div": "0.45", "rev": "2014046", "mom": "13.32", "yoy": "28.14", "cum_yoy": "21.28", "period": "11504"}, "6770": {"pe": "45.76", "pb": "3.56", "div": "", "rev": "5045881", "mom": "6.64", "yoy": "32.46", "cum_yoy": "24.74", "period": "11504"}, "1102": {"pe": "11.53", "pb": "0.69", "div": "6.70", "rev": "5694459", "mom": "6.45", "yoy": "-9.27", "cum_yoy": "-10.26", "period": "11504"}, "3037": {"pe": "142.79", "pb": "13.60", "div": "0.21", "rev": "13932815", "mom": "6.53", "yoy": "27.64", "cum_yoy": "25.30", "period": "11504"}, "2412": {"pe": "28.13", "pb": "2.77", "div": "3.67", "rev": "20497863", "mom": "-1.40", "yoy": "7.61", "cum_yoy": "7.52", "period": "11504"}, "2352": {"pe": "55.24", "pb": "1.85", "div": "2.92", "rev": "16813651", "mom": "-13.81", "yoy": "-1.84", "cum_yoy": "2.21", "period": "11504"}, "2330": {"pe": "32.07", "pb": "10.50", "div": "0.92", "rev": "410725118", "mom": "-1.08", "yoy": "17.50", "cum_yoy": "29.95", "period": "11504"}, "2892": {"pe": "15.15", "pb": "1.43", "div": "4.40", "rev": "7321915", "mom": "15.40", "yoy": "41.98", "cum_yoy": "22.60", "period": "11504"}, "1303": {"pe": "48.05", "pb": "2.29", "div": "0.72", "rev": "27681309", "mom": "1.89", "yoy": "19.44", "cum_yoy": "8.51", "period": "11504"}, "2884": {"pe": "15.20", "pb": "1.90", "div": "4.19", "rev": "10046680", "mom": "19.02", "yoy": "47.82", "cum_yoy": "24.75", "period": "11504"}, "2002": {"pe": "", "pb": "0.99", "div": "0.78", "rev": "30891428", "mom": "7.93", "yoy": "2.15", "cum_yoy": "-2.96", "period": "11504"}, "3711": {"pe": "55.06", "pb": "7.42", "div": "1.11", "rev": "62247107", "mom": "1.09", "yoy": "19.22", "cum_yoy": "17.74", "period": "11504"}, "2382": {"pe": "20.31", "pb": "7.51", "div": "3.86", "rev": "339921315", "mom": "-6.31", "yoy": "120.71", "cum_yoy": "79.64", "period": "11504"}, "2609": {"pe": "17.27", "pb": "0.56", "div": "3.76", "rev": "14227637", "mom": "14.23", "yoy": "13.88", "cum_yoy": "-8.83", "period": "11504"}, "2308": {"pe": "89.42", "pb": "21.03", "div": "0.48", "rev": "58691652", "mom": "-1.82", "yoy": "43.92", "cum_yoy": "36.53", "period": "11504"}, "2615": {"pe": "7.73", "pb": "0.82", "div": "3.58", "rev": "12930770", "mom": "22.89", "yoy": "13.05", "cum_yoy": "-4.03", "period": "11504"}, "4938": {"pe": "22.30", "pb": "1.28", "div": "4.12", "rev": "87189236", "mom": "3.84", "yoy": "-15.24", "cum_yoy": "-11.73", "period": "11504"}, "2303": {"pe": "31.41", "pb": "3.87", "div": "2.08", "rev": "22663945", "mom": "8.80", "yoy": "10.80", "cum_yoy": "6.88", "period": "11504"}, "1216": {"pe": "19.89", "pb": "2.89", "div": "4.08", "rev": "57480106", "mom": "0.18", "yoy": "2.26", "cum_yoy": "3.11", "period": "11504"}, "5871": {"pe": "11.14", "pb": "1.16", "div": "5.04", "rev": "7950143", "mom": "-5.52", "yoy": "-3.87", "cum_yoy": "-3.12", "period": "11504"}, "2408": {"pe": "35.36", "pb": "6.35", "div": "0.38", "rev": "25491201", "mom": "40.29", "yoy": "717.33", "cum_yoy": "623.58", "period": "11504"}, "2327": {"pe": "58.50", "pb": "9.16", "div": "0.81", "rev": "14039098", "mom": "3.00", "yoy": "22.04", "cum_yoy": "22.53", "period": "11504"}, "2890": {"pe": "15.86", "pb": "1.81", "div": "3.92", "rev": "9512201", "mom": "13.74", "yoy": "87.36", "cum_yoy": "50.08", "period": "11504"}, "2207": {"pe": "14.22", "pb": "3.41", "div": "4.12", "rev": "30160251", "mom": "25.01", "yoy": "30.03", "cum_yoy": "5.75", "period": "11504"}, "2376": {"pe": "17.47", "pb": "3.88", "div": "3.21", "rev": "52267730", "mom": "33.92", "yoy": "73.66", "cum_yoy": "64.15", "period": "11504"}, "2891": {"pe": "16.39", "pb": "2.43", "div": "3.68", "rev": "19691968", "mom": "50.38", "yoy": "1120.57", "cum_yoy": "81.70", "period": "11504"}, "2801": {"pe": "13.38", "pb": "1.11", "div": "4.91", "rev": "4178018", "mom": "-4.93", "yoy": "8.80", "cum_yoy": "13.73", "period": "11504"}, "2357": {"pe": "15.94", "pb": "2.31", "div": "4.71", "rev": "81915499", "mom": "-4.84", "yoy": "45.71", "cum_yoy": "42.36", "period": "11504"}, "5880": {"pe": "16.93", "pb": "1.31", "div": "4.43", "rev": "6093827", "mom": "14.00", "yoy": "65.45", "cum_yoy": "21.78", "period": "11504"}, "2337": {"pe": "", "pb": "6.12", "div": "", "rev": "5912524", "mom": "33.71", "yoy": "153.71", "cum_yoy": "93.46", "period": "11504"}, "3034": {"pe": "20.04", "pb": "4.14", "div": "4.70", "rev": "9225016", "mom": "8.93", "yoy": "1.16", "cum_yoy": "-10.68", "period": "11504"}, "3008": {"pe": "23.87", "pb": "2.71", "div": "2.09", "rev": "5362271", "mom": "-1.06", "yoy": "24.48", "cum_yoy": "10.69", "period": "11504"}, "2454": {"pe": "70.60", "pb": "18.12", "div": "1.21", "rev": "46736664", "mom": "-26.07", "yoy": "-4.14", "cum_yoy": "-3.06", "period": "11504"}, "1301": {"pe": "", "pb": "0.83", "div": "0.98", "rev": "18326272", "mom": "5.60", "yoy": "13.31", "cum_yoy": "-4.83", "period": "11504"}, "2379": {"pe": "22.46", "pb": "7.12", "div": "4.01", "rev": "12719097", "mom": "2.88", "yoy": "11.28", "cum_yoy": "5.79", "period": "11504"}, "2317": {"pe": "20.81", "pb": "2.30", "div": "2.46", "rev": "832097956", "mom": "3.53", "yoy": "29.74", "cum_yoy": "29.70", "period": "11504"}, "2881": {"pe": "15.68", "pb": "1.75", "div": "3.73", "rev": "53356168", "mom": "303.05", "yoy": "219.79", "cum_yoy": "402.59", "period": "11504"}, "3045": {"pe": "23.53", "pb": "3.86", "div": "4.14", "rev": "15669304", "mom": "-8.42", "yoy": "1.79", "cum_yoy": "2.97", "period": "11504"}, "2603": {"pe": "10.31", "pb": "0.88", "div": "6.78", "rev": "31359253", "mom": "13.94", "yoy": "4.51", "cum_yoy": "-15.79", "period": "11504"}, "2301": {"pe": "36.54", "pb": "6.40", "div": "2.01", "rev": "16694759", "mom": "1.28", "yoy": "24.51", "cum_yoy": "20.63", "period": "11504"}, "1101": {"pe": "", "pb": "0.78", "div": "3.27", "rev": "12213195", "mom": "-1.61", "yoy": "-3.69", "cum_yoy": "-4.58", "period": "11504"}, "2409": {"pe": "91.41", "pb": "1.48", "div": "1.37", "rev": "22100381", "mom": "-15.07", "yoy": "-4.48", "cum_yoy": "-4.31", "period": "11504"}, "2882": {"pe": "14.32", "pb": "1.89", "div": "3.71", "rev": "30515220", "mom": "53.36", "yoy": "153.91", "cum_yoy": "577.07", "period": "11504"}}

NAMES = {
    "2330":"台積電 TSMC","2317":"鴻海 Foxconn","2454":"聯發科 MediaTek",
    "2882":"國泰金 Cathay Financial","2881":"富邦金 Fubon Financial",
    "2308":"台達電 Delta Electronics","3008":"大立光 LARGAN",
    "2412":"中華電信 Chunghwa Telecom","2382":"廣達 Quanta",
    "2303":"聯電 UMC","2886":"兆豐金 Mega Financial",
    "2891":"中信金 CTBC Financial","2357":"華碩 ASUS",
    "2603":"長榮 Evergreen Marine","2379":"瑞昱 Realtek",
    "2395":"研華 Advantech","2884":"玉山金 E.Sun Financial",
    "5880":"合庫金 Taiwan Cooperative Financial","2002":"中鋼 China Steel",
    "1301":"台塑 Formosa Plastics","1303":"南亞 Nan Ya Plastics",
    "2207":"和泰車 Hotai Motor","2615":"萬海 Wan Hai Lines",
    "2609":"陽明 Yang Ming Marine","2892":"第一金 First Financial",
    "5871":"中租 Chailease Holdings","6669":"緯穎 Wiwynn",
    "3711":"日月光 ASE Technology","2327":"國巨 Yageo",
    "2408":"南亞科 Nanya Technology","2887":"台新金 Taishin Financial",
    "1216":"統一 Uni-President","1101":"台泥 Taiwan Cement",
    "2409":"友達 AUO","3045":"台灣大 Taiwan Mobile",
    "4938":"和碩 Pegatron","2376":"技嘉 Gigabyte",
    "3034":"聯詠 Novatek","6770":"力積電 PSMC",
    "2801":"彰銀 Chang Hwa Bank","2883":"開發金 CDFH",
    "2890":"永豐金 SinoPac Financial","1102":"亞泥 Asia Cement",
    "2301":"光寶 Lite-On Technology","5876":"上海商銀 Shanghai Commercial Bank",
    "2337":"旺宏 Macronix","2352":"佳世達 Qisda",
    "6415":"矽力 Silergy","3037":"欣興 Unimicron",
}

SECTOR = {
    "2330":"Semiconductor","2454":"Semiconductor","2303":"Semiconductor",
    "2408":"Semiconductor","6770":"Semiconductor","2337":"Semiconductor",
    "3037":"Semiconductor","6415":"Semiconductor",
    "2317":"Tech Hardware","2382":"Tech Hardware","2357":"Tech Hardware",
    "2308":"Tech Hardware","3008":"Tech Hardware","2379":"Tech Hardware",
    "2395":"Tech Hardware","6669":"Tech Hardware","4938":"Tech Hardware",
    "2376":"Tech Hardware","2301":"Tech Hardware","2409":"Display Panel",
    "3034":"Tech Hardware","2327":"Tech Hardware","3711":"Tech Hardware",
    "2352":"Tech Hardware",
    "2882":"Financial","2881":"Financial","2886":"Financial",
    "2891":"Financial","2884":"Financial","5880":"Financial",
    "2892":"Financial","2887":"Financial","2801":"Financial",
    "2883":"Financial","2890":"Financial","5876":"Financial",
    "5871":"Financial",
    "2412":"Telecom","3045":"Telecom",
    "2603":"Shipping","2609":"Shipping","2615":"Shipping",
    "1301":"Petrochemical","1303":"Petrochemical",
    "1101":"Cement","1102":"Cement",
    "1216":"Consumer","2207":"Auto","2002":"Steel",
}

ETF_0050 = ["2330","2317","2454","2882","2881","2308","3008","2412","2382","2303","2886","2891","2357","2603","2379","2395","2884","5880","2002","1301","1303","2207","2615","2609","2892","5871","6669","3711","2327","2408","2887","1216","1101","2409","3045","4938","2376","3034","6770","2801","2883","2890","1102","2301","5876","2337","2352","6415","3037"]
ETF_0056 = ["2887","2892","2886","5880","2884","2890","2801","2883","1101","1102","1216","2002","2207","2301","2327","2352","2357","2379","2395","2412","2603","2609","2615","3034","3045","5871","6415","2303","3711","2408"]

# ── Analysis logic ────────────────────────────────────────────────────────────

FINANCIAL_CODES = {"2882","2881","2886","2891","2884","5880","2892","2887","2801","2883","2890","5876","5871"}
IFRS17_DISTORTED = {"2882","2881","2891","2883","2887"}  # extreme YoY base effects

def safe_float(v):
    try: return float(v)
    except: return None

def val_label(pe):
    if pe is None: return "No P/E (loss or N/A)"
    if pe < 12: return "Very cheap"
    if pe < 18: return "Cheap"
    if pe < 28: return "Fair"
    if pe < 45: return "Expensive"
    if pe < 70: return "Very expensive"
    return "Extreme valuation"

def growth_label(yoy):
    if yoy is None: return "N/A"
    if yoy < -10: return "Declining sharply"
    if yoy < 0: return "Declining slightly"
    if yoy < 5: return "Flat"
    if yoy < 15: return "Modest growth"
    if yoy < 30: return "Solid growth"
    if yoy < 60: return "Strong growth"
    if yoy < 120: return "Exceptional growth"
    return "Extraordinary growth (verify base effect)"

def verdict(code, pe, yoy, div, pb, cum_yoy):
    if code in FINANCIAL_CODES:
        if div and div > 4.5: return "BUY — High-yield income stock, cheap valuation"
        if pb and pb < 1.2: return "BUY — Below-book value with sustainable dividend"
        return "HOLD — Solid financials franchise; verify IFRS 17 revenue distortion"
    if pe and pe > 80 and yoy and yoy < 10: return "AVOID — Extreme valuation with weak/declining revenue"
    if pe and pe > 60 and yoy and yoy < 0: return "AVOID — Very expensive and revenue declining"
    if yoy and yoy > 80 and pe and pe < 25: return "STRONG BUY — Explosive growth at reasonable price"
    if yoy and yoy > 30 and pe and pe < 22: return "BUY — Strong growth at cheap valuation"
    if yoy and yoy > 30 and pe and pe < 30: return "BUY — Strong revenue growth justifies valuation"
    if div and div > 5: return "BUY — High dividend yield with value characteristics"
    if pb and pb < 0.9: return "BUY (value) — Below book value; contrarian opportunity"
    if yoy and yoy < -8: return "REDUCE — Revenue declining; monitor trend"
    if pe and pe > 50: return "CAUTION — Expensive valuation; watch for earnings miss"
    return "HOLD — Adequate performance at current valuation"

def make_report(code):
    d = RAW.get(code, {})
    name = NAMES.get(code, code)
    sector = SECTOR.get(code, "Other")
    pe  = safe_float(d.get("pe"))
    pb  = safe_float(d.get("pb"))
    div = safe_float(d.get("div"))
    yoy = safe_float(d.get("yoy"))
    mom = safe_float(d.get("mom"))
    cum = safe_float(d.get("cum_yoy"))
    rev = d.get("rev","N/A")
    period = d.get("period","N/A")

    is_financial = code in FINANCIAL_CODES
    ifrs_note = "\n> ⚠️ Revenue YoY % may reflect IFRS 17 base effect, not operational growth. Use P/E and P/B for valuation." if code in IFRS17_DISTORTED else ""

    # Risk flag
    risks = []
    if pe and pe > 70: risks.append(f"P/E of {pe}x is extreme — zero margin for earnings disappointment")
    if pe and pe > 40 and yoy and yoy < 10: risks.append(f"High P/E {pe}x with weak growth ({yoy:.1f}% YoY) = poor risk/reward")
    if yoy and yoy < -8: risks.append(f"Revenue declining {yoy:.1f}% YoY — monitor for sustained trend")
    if cum and cum < -10: risks.append(f"Cumulative YTD revenue down {cum:.1f}% — structural headwind")
    if pb and pb > 15: risks.append(f"P/B of {pb}x is very high — stock requires sustained premium growth")
    if not risks: risks.append("No major near-term red flags at current valuation")

    # Opportunity
    opps = []
    if yoy and yoy > 80 and pe and pe < 25: opps.append(f"Best GARP setup: {yoy:.0f}% revenue growth at only {pe:.1f}x P/E")
    elif yoy and yoy > 30: opps.append(f"Strong revenue momentum: +{yoy:.1f}% YoY, cumulative YTD +{cum:.1f}%")
    if div and div > 4.5: opps.append(f"High dividend yield of {div}% provides income floor")
    if pb and pb < 1.0: opps.append(f"Trading below book value (P/B {pb}x) — deep value entry")
    if not opps: opps.append("Steady compounder; limited near-term catalyst visible in revenue data")

    ver = verdict(code, pe, yoy, div, pb, cum)

    rev_m = float(rev.replace(",","")) / 1_000_000 if rev != "N/A" else None
    rev_str = f"NTD {rev_m:.1f}B" if rev_m else "N/A"

    return f"""# {code} {name}
**Sector:** {sector} | **Date:** {TODAY} | **Period:** ROC {period}

| Metric | Value |
|--------|-------|
| P/E Ratio | {pe if pe else 'N/A (no earnings)'} |
| P/B Ratio | {pb if pb else 'N/A'} |
| Dividend Yield | {div if div else 'N/A'}% |
| Apr 2026 Revenue | {rev_str} |
| Revenue MoM | {f'{mom:+.1f}%' if mom else 'N/A'} |
| Revenue YoY | {f'{yoy:+.1f}%' if yoy else 'N/A'} |
| Cumulative YTD YoY | {f'{cum:+.1f}%' if cum else 'N/A'} |

---

## Snapshot

{name} is a {sector.lower()} company. Valuation: **{val_label(pe)}** (P/E {pe if pe else 'N/A'}, P/B {pb if pb else 'N/A'}).
Revenue trend: **{growth_label(yoy)}** ({f'{yoy:+.1f}%' if yoy else 'N/A'} YoY in April 2026).{ifrs_note}

## Growth Opportunity 🚀

{opps[0]}
{opps[1] if len(opps) > 1 else ''}

## Key Risk 🚩

{risks[0]}

## Verdict

**{ver}**

---
*Data: TWSE Open API | Analysis date: {TODAY} | Values in thousands of NTD*
"""

def main():
    out = Path("reports") / TODAY
    out.mkdir(parents=True, exist_ok=True)

    # Individual reports
    all_codes = list(dict.fromkeys(ETF_0050 + ETF_0056))
    print(f"Generating {len(all_codes)} individual stock reports...")
    for code in all_codes:
        name = NAMES.get(code, code)
        text = make_report(code)
        fname = f"{code}_{name.split()[0]}.md"
        (out / fname).write_text(text, encoding="utf-8")
        print(f"  ✓ {fname}")

    # 0050.TW summary
    def etf_table(codes):
        rows = ["| Code | Name | Sector | P/E | P/B | Div% | YoY% | Verdict |",
                "|------|------|--------|-----|-----|------|------|---------|"]
        for c in codes:
            d = RAW.get(c, {})
            pe = safe_float(d.get("pe")); yoy = safe_float(d.get("yoy"))
            pb = safe_float(d.get("pb")); div = safe_float(d.get("div"))
            cum = safe_float(d.get("cum_yoy"))
            ver = verdict(c, pe, yoy, div, pb, cum).split(" — ")[0]
            rows.append(f"| {c} | {NAMES.get(c,c).split()[0]} | {SECTOR.get(c,'Other')} | {pe or 'N/A'} | {pb or 'N/A'} | {div or 'N/A'} | {f'{yoy:+.1f}' if yoy else 'N/A'} | {ver} |")
        return "\n".join(rows)

    for etf_name, codes in [("0050.TW", ETF_0050), ("0056.TW", ETF_0056)]:
        summary = f"""# {etf_name} ETF — Component Analysis Summary
**Date:** {TODAY} | **Revenue Period:** April 2026 (ROC 11504)
**Source:** TWSE Open API (BWIBBU_ALL + t187ap05_L)

---

{etf_table(codes)}

---

## Top Picks

### 🚀 Strong Buy
- **2382 廣達 Quanta** — Revenue +120.7% YoY at P/E 20x. AI server rack leader.
- **2317 鴻海 Foxconn** — Revenue +29.7% YoY at P/E 20.8x. Nvidia rack builder.
- **2376 技嘉 Gigabyte** *(0050 only)* — Revenue +73.7% YoY at P/E 17.5x. GPU/AI server boards.

### ✅ Buy
- **2357 華碩 ASUS** — P/E 15.9x, +45.7% YoY, 4.71% dividend
- **2207 和泰車 Hotai** — P/E 14.2x, +30% YoY, 4.12% dividend
- **2801 彰銀** — P/E 13.4x, 4.91% dividend, cheapest financials
- **2615 萬海** — P/E 7.7x (cheapest in basket!), recovery play

### 🚩 Avoid
- **2454 聯發科 MediaTek** — P/E 70.6x + revenue -4.1% YoY
- **2308 台達電 Delta** — P/E 89.4x; great business, terrible entry price
- **2409 友達 AUO** — P/E 91.4x + revenue -4.5% YoY
- **3037 欣興 Unimicron** — P/E 142.8x; extreme even for AI substrate

---
*Individual stock reports saved to this folder. Crawl policy: 2-min intervals between API calls.*
"""
        sname = f"{etf_name.replace('.','_')}_SUMMARY.md"
        (out / sname).write_text(summary, encoding="utf-8")
        print(f"\n  ✓ Summary: {sname}")

    print(f"\nAll reports saved: {out}/")

if __name__ == "__main__":
    main()
