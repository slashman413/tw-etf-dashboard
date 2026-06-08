#!/usr/bin/env python3
"""
Iteration 5: Multi-Factor Composite Score — Capstone Report
Synthesises all prior analysis into a single 0-100 investment score per stock.

Score breakdown (100 pts total):
  Value  (30 pts): Forward P/E + P/B
  Growth (40 pts): Revenue YoY + EPS acceleration
  Quality(20 pts): Operating margin
  Income (10 pts): Dividend yield

Crawl policy: 2-min minimum between API endpoint calls.
"""

import time, requests, json
from pathlib import Path
from datetime import datetime

TODAY  = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT    = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

TARGET_CODES = [
    "2330","2317","2454","2882","2881","2308","3008","2412","2382","2303",
    "2886","2891","2357","2603","2379","2395","2884","5880","2002","1301",
    "1303","2207","2615","2609","2892","5871","6669","3711","2327","2408",
    "2887","1216","1101","2409","3045","4938","2376","3034","6770","2801",
    "2883","2890","1102","2301","5876","2337","2352","6415","3037",
]

NAMES = {
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
}

SECTOR = {
    "2330":"Semicon","2454":"Semicon","2303":"Semicon","2408":"Semicon",
    "6770":"Semicon","2337":"Semicon","3037":"Semicon","6415":"Semicon",
    "2317":"Tech HW","2382":"Tech HW","2357":"Tech HW","2308":"Tech HW",
    "3008":"Optics","2379":"Tech HW","2395":"Tech HW","6669":"Tech HW",
    "4938":"Tech HW","2376":"Tech HW","2301":"Tech HW","2409":"Display",
    "3034":"Tech HW","2327":"Tech HW","3711":"Semicon","2352":"Tech HW",
    "2882":"Finance","2881":"Finance","2886":"Finance","2891":"Finance",
    "2884":"Finance","5880":"Finance","2892":"Finance","2887":"Finance",
    "2801":"Finance","2883":"Finance","2890":"Finance","5876":"Finance",
    "5871":"Finance","2412":"Telecom","3045":"Telecom",
    "2603":"Shipping","2609":"Shipping","2615":"Shipping",
    "1301":"Petrochem","1303":"Petrochem","2002":"Steel",
    "1216":"Consumer","2207":"Auto","1101":"Cement","1102":"Cement",
}

FINANCIAL = {"2882","2881","2886","2891","2884","5880","2892","2887",
             "2801","2883","2890","5876","5871"}

def sf(v):
    try: return float(str(v).replace(",","").replace("--",""))
    except: return None

def fetch(url, label):
    print(f"  [{label}] Fetching... ", end="", flush=True)
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    d = r.json()
    print(f"OK ({len(d)} records)")
    return d

def wait(sec=120):
    for s in range(sec, 0, -10):
        print(f"  {s}s...", end="\r", flush=True)
        time.sleep(10)
    print("  Fetching now...              ")

# ── Scoring functions ─────────────────────────────────────────────────────────

def score_value(fwd_pe, pb, is_fin):
    """Value: 30 pts. Financial sector uses P/B only."""
    pts = 0
    if is_fin:
        if pb and pb < 1.0:  pts += 30
        elif pb and pb < 1.3: pts += 22
        elif pb and pb < 1.7: pts += 15
        elif pb and pb < 2.2: pts += 8
        else: pts += 2
        return min(pts, 30)
    # Non-financial: fwd P/E (20 pts) + P/B (10 pts)
    if fwd_pe:
        if   fwd_pe < 10:  pts += 20
        elif fwd_pe < 15:  pts += 17
        elif fwd_pe < 20:  pts += 13
        elif fwd_pe < 28:  pts += 8
        elif fwd_pe < 40:  pts += 4
        else: pts += 0
    if pb:
        if   pb < 1.5:  pts += 10
        elif pb < 2.5:  pts += 7
        elif pb < 4.0:  pts += 4
        elif pb < 6.0:  pts += 2
        else: pts += 0
    return min(pts, 30)

def score_growth(rev_yoy, eps_accel, is_fin):
    """Growth: 40 pts. Revenue YoY (25) + EPS accel (15)."""
    pts = 0
    if is_fin:
        # Financial: EPS accel only (revenue distorted by IFRS 17)
        if eps_accel:
            if   eps_accel > 50:  pts += 40
            elif eps_accel > 25:  pts += 30
            elif eps_accel > 10:  pts += 20
            elif eps_accel > 0:   pts += 10
            else: pts += 0
        return min(pts, 40)
    # Revenue YoY (25 pts)
    if rev_yoy is not None:
        if   rev_yoy > 100: pts += 25
        elif rev_yoy > 50:  pts += 22
        elif rev_yoy > 30:  pts += 18
        elif rev_yoy > 15:  pts += 13
        elif rev_yoy > 5:   pts += 8
        elif rev_yoy > 0:   pts += 4
        else: pts += 0   # negative = 0
    # EPS acceleration (15 pts)
    if eps_accel is not None:
        if   eps_accel > 150: pts += 15
        elif eps_accel > 80:  pts += 12
        elif eps_accel > 40:  pts += 9
        elif eps_accel > 15:  pts += 6
        elif eps_accel > 0:   pts += 3
        else: pts += 0
    return min(pts, 40)

def score_quality(op_margin, is_fin):
    """Quality: 20 pts. Operating margin."""
    if is_fin:
        return 10  # financial sector baseline
    if op_margin is None: return 0
    if   op_margin > 40: return 20
    elif op_margin > 25: return 17
    elif op_margin > 15: return 13
    elif op_margin > 8:  return 9
    elif op_margin > 3:  return 5
    elif op_margin > 0:  return 2
    else: return 0

def score_income(div_yield):
    """Income: 10 pts. Dividend yield."""
    if not div_yield: return 0
    if   div_yield > 6:   return 10
    elif div_yield > 4.5: return 8
    elif div_yield > 3.5: return 6
    elif div_yield > 2.0: return 4
    elif div_yield > 0.5: return 2
    else: return 0

def verdict(score, is_fin, fwd_pe, op_margin):
    if score >= 75: return "STRONG BUY"
    if score >= 60: return "BUY"
    if score >= 45: return "HOLD"
    if score >= 30: return "REDUCE"
    if not is_fin and fwd_pe and fwd_pe > 70: return "AVOID"
    if not is_fin and op_margin and op_margin < 0: return "AVOID"
    return "REDUCE"

def main():
    print(f"\n{'='*60}")
    print(f"  Iteration 5: Composite Score Capstone — {TODAY}")
    print(f"{'='*60}")

    # ── Fetch 1: Q1 2026 quarterly earnings ───────────────────────────────
    print("\n[1/3] Q1 2026 quarterly earnings (t187ap14_L)...")
    q1_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap14_L", "t187ap14_L")
    q1_map  = {r["公司代號"]: r for r in q1_raw if r.get("公司代號") in TARGET_CODES}

    # ── Fetch 2: Trailing valuation ────────────────────────────────────────
    print("\n[2/3] Trailing valuation + prices (2-min wait)...")
    wait()
    val_raw  = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL", "BWIBBU_ALL")
    val_map  = {r["Code"]: r for r in val_raw}
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL", "STOCK_DAY_ALL")
    price_map = {(r.get("Code") or r.get("股票代號","")): r for r in price_raw}

    # ── Fetch 3: Monthly revenue ───────────────────────────────────────────
    print("\n[3/3] Monthly revenue YoY (2-min wait)...")
    wait()
    rev_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L", "t187ap05_L")
    rev_map  = {r["公司代號"]: r for r in rev_raw}

    # ── Compute metrics and composite score ───────────────────────────────
    print("\nComputing composite scores...")
    all_stocks = []

    for code in TARGET_CODES:
        name    = NAMES.get(code, code)
        sector  = SECTOR.get(code, "Other")
        is_fin  = code in FINANCIAL
        q       = q1_map.get(code, {})
        v       = val_map.get(code, {})
        pr      = price_map.get(code, {})
        rv      = rev_map.get(code, {})

        # Raw values
        q1_eps    = sf(q.get("基本每股盈餘(元)"))
        q1_rev    = sf(q.get("營業收入"))
        q1_op     = sf(q.get("營業利益"))
        q1_net    = sf(q.get("稅後淨利"))
        trail_pe  = sf(v.get("PEratio"))
        pb        = sf(v.get("PBratio"))
        div_yield = sf(v.get("DividendYield"))
        rev_yoy   = sf(rv.get("營業收入-去年同月增減(%)"))
        cum_yoy   = sf(rv.get("累計營業收入-前期比較增減(%)"))
        price     = (sf(pr.get("ClosingPrice")) or sf(pr.get("收盤價")) or sf(pr.get("close")))

        # Derived
        fwd_eps    = q1_eps * 4 if q1_eps else None
        fwd_pe     = price / fwd_eps if (price and fwd_eps and fwd_eps > 0) else None
        trail_eps  = price / trail_pe if (price and trail_pe and trail_pe > 0) else None
        eps_accel  = ((fwd_eps - trail_eps) / abs(trail_eps) * 100
                      if (fwd_eps and trail_eps and trail_eps != 0) else None)
        op_margin  = (q1_op / q1_rev * 100 if q1_op and q1_rev and q1_rev > 0 else None)
        net_margin = (q1_net / q1_rev * 100 if q1_net and q1_rev and q1_rev > 0 else None)

        # Composite score
        v_pts = score_value(fwd_pe, pb, is_fin)
        g_pts = score_growth(rev_yoy, eps_accel, is_fin)
        q_pts = score_quality(op_margin, is_fin)
        i_pts = score_income(div_yield)
        total = v_pts + g_pts + q_pts + i_pts
        verd  = verdict(total, is_fin, fwd_pe, op_margin)

        all_stocks.append({
            "code": code, "name": name, "sector": sector, "is_fin": is_fin,
            "score": total, "v_pts": v_pts, "g_pts": g_pts, "q_pts": q_pts, "i_pts": i_pts,
            "verdict": verd,
            "q1_eps": q1_eps, "fwd_eps": fwd_eps, "trail_eps": trail_eps,
            "eps_accel": eps_accel, "trail_pe": trail_pe, "fwd_pe": fwd_pe,
            "pb": pb, "div_yield": div_yield, "price": price,
            "op_margin": op_margin, "net_margin": net_margin,
            "rev_yoy": rev_yoy, "cum_yoy": cum_yoy,
        })

    # Sort by score descending
    all_stocks.sort(key=lambda x: -x["score"])

    # ── Save raw data JSON ─────────────────────────────────────────────────
    json_path = OUT / "composite_data.json"
    json_path.write_text(json.dumps(all_stocks, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── Generate Composite Score Report ───────────────────────────────────
    buys    = [s for s in all_stocks if s["verdict"] in ("STRONG BUY","BUY")]
    holds   = [s for s in all_stocks if s["verdict"] == "HOLD"]
    avoids  = [s for s in all_stocks if s["verdict"] in ("AVOID","REDUCE")]

    def r(v, fmt=".1f", suffix=""):
        if v is None: return "N/A"
        try: return f"{v:{fmt}}{suffix}"
        except: return "N/A"
    def rp(v): return r(v, ".1f", "%")
    def rx(v): return r(v, ".1f", "x")
    def rt(v): return r(v, ".2f")

    lines = [
        "# Taiwan ETF Universe — Multi-Factor Composite Score",
        f"**Date:** {TODAY} | **Stocks Scored:** {len(all_stocks)} | **Data:** Q1 2026 actual + April 2026 revenue",
        "",
        "## Scoring Methodology (100 pts total)",
        "| Factor | Max | Basis |",
        "|--------|-----|-------|",
        "| Value  | 30  | Forward P/E (non-fin) or P/B (fin) + P/B |",
        "| Growth | 40  | Revenue YoY + EPS Acceleration (Q1×4 vs TTM) |",
        "| Quality| 20  | Operating margin (actual Q1 2026) |",
        "| Income | 10  | Dividend yield |",
        "",
        "---",
        "",
        "## Full Rankings",
        "",
        "| Score | Verdict | Code | Name | Sector | FwdPE | RevYoY | OpMgn | Div% |",
        "|-------|---------|------|------|--------|-------|--------|-------|------|",
    ]

    for s in all_stocks:
        fpe = rx(s["fwd_pe"])
        yoy = f"+{s['rev_yoy']:.1f}%" if s['rev_yoy'] and s['rev_yoy'] > 0 else rp(s['rev_yoy'])
        om  = rp(s["op_margin"])
        div = rp(s["div_yield"])
        lines.append(
            f"| **{s['score']}** | {s['verdict']} | {s['code']} | {s['name'].split()[0]} | "
            f"{s['sector']} | {fpe} | {yoy} | {om} | {div} |"
        )

    # ── Strong Buy Section ─────────────────────────────────────────────────
    lines += ["", "---", "", "## 🟢 STRONG BUY / BUY", ""]
    for s in buys:
        eps_s  = rt(s["q1_eps"])
        fpe_s  = rx(s["fwd_pe"])
        yoy_s  = f"+{s['rev_yoy']:.1f}%" if s['rev_yoy'] and s['rev_yoy'] > 0 else rp(s['rev_yoy'])
        accel  = f"+{s['eps_accel']:.0f}%" if s['eps_accel'] and s['eps_accel'] > 0 else rp(s['eps_accel'])
        thesis_parts = []
        if s["rev_yoy"] and s["rev_yoy"] > 30:
            thesis_parts.append(f"Revenue surging {s['rev_yoy']:.0f}% YoY")
        if s["fwd_pe"] and s["fwd_pe"] < 15:
            thesis_parts.append(f"cheap at {s['fwd_pe']:.1f}x forward P/E")
        if s["div_yield"] and s["div_yield"] > 4:
            thesis_parts.append(f"{s['div_yield']:.1f}% dividend yield")
        if s["op_margin"] and s["op_margin"] > 20:
            thesis_parts.append(f"{s['op_margin']:.0f}% operating margin")
        thesis = ". ".join(thesis_parts) if thesis_parts else "Multi-factor outperformer."
        lines.append(
            f"**{s['code']} {s['name']}** (Score: {s['score']}/100 | {s['verdict']}) — "
            f"Q1 EPS: ¥{eps_s} | Fwd P/E: {fpe_s} | Rev YoY: {yoy_s} | EPS Accel: {accel}\n"
            f"  → {thesis}\n"
        )

    # ── Avoid Section ──────────────────────────────────────────────────────
    lines += ["---", "", "## 🔴 AVOID / REDUCE", ""]
    for s in avoids:
        reason_parts = []
        if s["fwd_pe"] and s["fwd_pe"] > 60:
            reason_parts.append(f"extremely expensive at {s['fwd_pe']:.0f}x forward P/E")
        if s["rev_yoy"] and s["rev_yoy"] < -5:
            reason_parts.append(f"revenue declining {s['rev_yoy']:.1f}% YoY")
        if s["op_margin"] and s["op_margin"] < 0:
            reason_parts.append(f"operating losses ({s['op_margin']:.1f}% margin)")
        reason = ". ".join(reason_parts) if reason_parts else "Poor multi-factor ranking."
        lines.append(
            f"**{s['code']} {s['name'].split()[0]}** (Score: {s['score']}/100 | {s['verdict']}) — {reason}\n"
        )

    # ── Sector Summary ────────────────────────────────────────────────────
    sector_groups = {}
    for s in all_stocks:
        sector_groups.setdefault(s["sector"], []).append(s)
    sector_avgs = sorted(
        [(sec, sum(x["score"] for x in stocks)/len(stocks), stocks)
         for sec, stocks in sector_groups.items()],
        key=lambda x: -x[1]
    )

    lines += ["---", "", "## Sector Composite Scores (average)", "",
              "| Rank | Sector | Avg Score | Verdict |",
              "|------|--------|-----------|---------|"]
    for i, (sec, avg, stocks) in enumerate(sector_avgs, 1):
        v = "BUY" if avg >= 55 else ("HOLD" if avg >= 40 else "REDUCE")
        lines.append(f"| {i} | {sec} | {avg:.1f} | {v} |")

    # ── Top 3 Portfolio ───────────────────────────────────────────────────
    top3 = all_stocks[:3]
    lines += [
        "",
        "---",
        "",
        "## Model Portfolio Top 3 (highest composite score)",
        "",
    ]
    for i, s in enumerate(top3, 1):
        yoy_s = f"+{s['rev_yoy']:.1f}%" if s['rev_yoy'] and s['rev_yoy'] > 0 else rp(s['rev_yoy'])
        lines.append(
            f"{i}. **{s['code']} {s['name']}** — Score {s['score']}/100 | "
            f"Fwd P/E {rx(s['fwd_pe'])} | Rev YoY {yoy_s} | EPS ¥{rt(s['q1_eps'])}"
        )

    lines += [
        "",
        "---",
        f"*Generated: {TODAY} | Composite score v1.0 | Loop: af8a5b5d*",
    ]

    out_path = OUT / "COMPOSITE_SCORE.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ Saved: {out_path}")
    print(f"  ✓ Data:  {json_path}")

    # Console summary
    print(f"\n{'='*60}")
    print("  TOP 10 COMPOSITE SCORES:")
    for s in all_stocks[:10]:
        fpe = f"{s['fwd_pe']:.1f}x" if s['fwd_pe'] else " N/A "
        yoy = f"{s['rev_yoy']:+.1f}%" if s['rev_yoy'] else " N/A"
        print(f"    [{s['score']:2d}] {s['code']} {s['name'].split()[0]:15} "
              f"{s['verdict']:10} FwdPE={fpe:6} RevYoY={yoy}")
    print()
    print("  BOTTOM 5:")
    for s in all_stocks[-5:]:
        print(f"    [{s['score']:2d}] {s['code']} {s['name'].split()[0]:15} {s['verdict']}")
    print(f"{'='*60}")

    return all_stocks

if __name__ == "__main__":
    main()
