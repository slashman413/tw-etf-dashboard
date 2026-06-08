#!/usr/bin/env python3
"""
Margin Trading Analysis (融資融券)
Parses MI_MARGN with correct Chinese field names, computes balance changes,
and generates a sentiment overlay for our 62-stock universe.
"""

import requests, json
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
    "3037":"欣興 Unimicron","1590":"亞德客 Airtac","2912":"統一超 President",
    "4904":"遠傳 FarEasTone","6488":"環球晶 GlobalWafers","2823":"中壽 ChinaLife",
    "2880":"華南金 HuaNan","2888":"新光金 ShinKong","3231":"緯創 Wistron",
    "2383":"台光電 Elite","2344":"華邦電 Winbond","3481":"群創 Innolux",
    "2049":"上銀 Hiwin","6743":"合一 Oneness",
}

COMPOSITE = {
    "2330":85,"2317":72,"2454":68,"6669":80,"3008":65,"2382":73,
    "2376":77,"2357":70,"2408":72,"2603":65,"2327":68,"3034":60,
    "2308":55,"4938":58,"1303":55,"2395":62,"2303":60,"2379":60,
    "2615":60,"2207":58,"2301":52,"2409":42,"1101":45,"3037":48,
    "6415":50,"2337":55,"2352":42,"6770":40,"2882":60,"2881":62,
    "2886":58,"2891":60,"2884":55,"5880":52,"2892":55,"5871":65,
    "2887":50,"2801":45,"2883":48,"2890":48,"5876":58,"2412":55,
    "2002":35,"1301":45,"1102":42,"1216":50,"3045":55,"3711":60,
    "1590":52,"2912":45,"4904":48,"6488":40,"2823":38,"2880":42,
    "2888":35,"3231":50,"2383":52,"2344":55,"3481":30,"2049":45,"6743":30,
}

def sf(v):
    try:
        f = float(str(v).replace(",",""))
        return None if f != f else f
    except: return None

def margin_signal(m_chg, s_chg, m_bal, s_bal):
    """Interpret margin/short balance changes as sentiment signal."""
    if m_chg is None or s_chg is None: return "N/A", "—"
    # Short ratio: short balance as % of margin balance
    ratio = (s_bal / m_bal * 100) if m_bal and m_bal > 0 else None

    if m_chg > 0 and s_chg < 0:
        sig = "BULLISH"
        detail = f"margin↑{m_chg:+,.0f} short↓{s_chg:+,.0f}"
    elif m_chg > 0 and s_chg > 0:
        sig = "MIXED"
        detail = f"margin↑ short↑ (both increasing)"
    elif m_chg < 0 and s_chg > 0:
        sig = "BEARISH"
        detail = f"margin↓{m_chg:+,.0f} short↑{s_chg:+,.0f}"
    elif m_chg < 0 and s_chg < 0:
        sig = "UNWINDING"
        detail = f"margin↓ short↓ (both reducing)"
    elif m_chg == 0 and s_chg == 0:
        sig = "FLAT"
        detail = "no change"
    else:
        sig = "NEUTRAL"
        detail = f"margin{m_chg:+,.0f} short{s_chg:+,.0f}"

    if ratio and ratio > 20: detail += f" [SHORT SQUEEZE RISK: {ratio:.1f}%]"
    return sig, detail

print(f"\n{'='*60}")
print(f"  Margin Trading Analysis — {TODAY}")
print(f"{'='*60}")
print("\n  Fetching MI_MARGN...", end=" ", flush=True)

r = requests.get("https://openapi.twse.com.tw/v1/fund/MI_MARGN", headers=HEADERS, timeout=20)
r.raise_for_status()
raw = r.json()
print(f"OK ({len(raw)} records)")

# Build margin map using correct Chinese field names
margin_map = {}
for rec in raw:
    code = rec.get("股票代號","")
    if code not in ALL_CODES: continue
    m_today = sf(rec.get("融資今日餘額"))
    m_yest  = sf(rec.get("融資前日餘額"))
    s_today = sf(rec.get("融券今日餘額"))
    s_yest  = sf(rec.get("融券前日餘額"))
    m_buy   = sf(rec.get("融資買進"))
    m_sell  = sf(rec.get("融資賣出"))
    s_sell  = sf(rec.get("融券賣出"))
    s_buy   = sf(rec.get("融券買進"))
    offset  = sf(rec.get("資券互抵"))

    m_chg = (m_today - m_yest) if m_today is not None and m_yest is not None else None
    s_chg = (s_today - s_yest) if s_today is not None and s_yest is not None else None

    sig, detail = margin_signal(m_chg, s_chg, m_today, s_today)

    margin_map[code] = {
        "m_today": m_today, "m_yest": m_yest, "m_chg": m_chg,
        "s_today": s_today, "s_yest": s_yest, "s_chg": s_chg,
        "m_buy": m_buy, "m_sell": m_sell,
        "s_sell": s_sell, "s_buy": s_buy,
        "offset": offset, "sig": sig, "detail": detail,
    }

print(f"  Matched {len(margin_map)} / {len(ALL_CODES)} stocks")

# ── Build ranked results ──────────────────────────────────────────────────
rows = []
for code, name in ALL_CODES.items():
    d = margin_map.get(code, {})
    score = COMPOSITE.get(code, 40)
    sig   = d.get("sig", "N/A")

    # Combined conviction: fundamental score + bullish margin signal
    if sig == "BULLISH" and score >= 65:   combo = "CONFIRMED BUY ✓"
    elif sig == "BULLISH" and score >= 50: combo = "BUY SIGNAL ↑"
    elif sig == "BEARISH" and score >= 65: combo = "DIVERGENCE ⚠"
    elif sig == "BEARISH":                 combo = "CAUTION ↓"
    elif sig == "MIXED":                   combo = "WATCH"
    elif sig == "FLAT" or sig == "N/A":   combo = "—"
    else:                                  combo = "—"

    rows.append({
        "code": code, "name": name.split()[0], "score": score,
        "sig": sig, "combo": combo,
        "m_chg": d.get("m_chg"), "s_chg": d.get("s_chg"),
        "m_today": d.get("m_today"), "s_today": d.get("s_today"),
        "detail": d.get("detail","N/A"),
    })

rows.sort(key=lambda x: (
    x["combo"] != "CONFIRMED BUY ✓",
    x["combo"] != "BUY SIGNAL ↑",
    x["combo"] != "DIVERGENCE ⚠",
    -x["score"],
))

# ── Generate report ───────────────────────────────────────────────────────
lines = [
    f"# Margin Trading Analysis (融資融券) — {TODAY}",
    f"*Source: TWSE MI_MARGN | 62-stock universe*",
    "",
    "**Legend:** Margin (融資) = leveraged longs by retail. Short (融券) = short positions.",
    "- BULLISH = margin↑ AND short↓  |  BEARISH = margin↓ AND short↑",
    "- MIXED = both rising  |  UNWINDING = both falling",
    "",
    "---",
    "",
    "## Confirmed Buy: Strong Fundamentals + Bullish Margin Flow",
    "",
    "| Code | Name | Score | Margin Sig | Margin Chg | Short Chg | Combined |",
    "|------|------|-------|-----------|-----------|----------|---------|",
]

confirmed = [r for r in rows if r["combo"] in ("CONFIRMED BUY ✓","BUY SIGNAL ↑")]
for r in confirmed:
    mc = f"{r['m_chg']:+,.0f}" if r.get("m_chg") is not None else "N/A"
    sc = f"{r['s_chg']:+,.0f}" if r.get("s_chg") is not None else "N/A"
    lines.append(
        f"| **{r['code']}** | {r['name']} | **{r['score']}** | "
        f"{r['sig']} | {mc} | {sc} | **{r['combo']}** |"
    )

if not confirmed:
    lines.append("*No stocks with both strong fundamentals and bullish margin flow today.*")

lines += [
    "",
    "## Divergence Alerts: Fundamental BUY but Bearish Margin Flow",
    "",
    "| Code | Name | Score | Detail |",
    "|------|------|-------|--------|",
]

diverg = [r for r in rows if r["combo"] == "DIVERGENCE ⚠"]
for r in diverg:
    lines.append(f"| {r['code']} | {r['name']} | {r['score']} | {r['detail']} |")

if not diverg:
    lines.append("*No divergence signals.*")

lines += [
    "",
    "## Full Margin Snapshot (Top 40 by Score)",
    "",
    "| Code | Name | Score | Signal | Margin Bal | Margin Chg | Short Bal | Short Chg |",
    "|------|------|-------|--------|-----------|-----------|----------|----------|",
]

for r in sorted(rows, key=lambda x: -x["score"])[:40]:
    mt = f"{int(r['m_today']):,}" if r.get("m_today") else "N/A"
    mc = f"{r['m_chg']:+,.0f}" if r.get("m_chg") is not None else "N/A"
    st = f"{int(r['s_today']):,}" if r.get("s_today") else "N/A"
    sc = f"{r['s_chg']:+,.0f}" if r.get("s_chg") is not None else "N/A"
    lines.append(
        f"| {r['code']} | {r['name']} | {r['score']} | {r['sig']} | "
        f"{mt} | {mc} | {st} | {sc} |"
    )

# Short squeeze candidates: high short ratio + rising price (from today's selloff context, interesting reversal)
squeeze = [
    r for r in rows
    if r.get("s_today") and r.get("m_today") and r["m_today"] > 0
    and (r["s_today"] / r["m_today"] * 100) > 15
]
squeeze.sort(key=lambda x: -(x.get("s_today",0) / max(x.get("m_today",1),1)))

if squeeze:
    lines += [
        "",
        "## Short Squeeze Candidates (短券餘額 > 15% of 融資)",
        "",
        "| Code | Name | Short/Margin % | Short Bal | Margin Bal | Score |",
        "|------|------|---------------|----------|----------|-------|",
    ]
    for r in squeeze[:10]:
        ratio = r["s_today"] / r["m_today"] * 100
        lines.append(
            f"| {r['code']} | {r['name']} | **{ratio:.1f}%** | "
            f"{int(r['s_today']):,} | {int(r['m_today']):,} | {r['score']} |"
        )

lines += [
    "",
    "---",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
    "Source: TWSE openapi.twse.com.tw/v1/fund/MI_MARGN*",
]

out_path = OUT / "MARGIN_ANALYSIS.md"
out_path.write_text("\n".join(lines), encoding="utf-8")

# Save JSON
json_path = OUT / "margin_data.json"
json_path.write_text(json.dumps(margin_map, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n  ✓ Report: {out_path}")
print(f"  ✓ Data:   {json_path}")

# Print key signals
print(f"\n{'='*60}")
print("  Confirmed BUY (fundamental + margin aligned):")
for r in confirmed: print(f"    {r['code']} {r['name']:15s} score={r['score']} {r['detail']}")
if not confirmed: print("    (none today)")
print("  Divergence (fundamental BUY but margin bearish):")
for r in diverg:   print(f"    {r['code']} {r['name']:15s} score={r['score']}")
if not diverg: print("    (none today)")
print(f"  Short squeeze candidates: {[r['code'] for r in squeeze[:5]]}")
print(f"{'='*60}")

# Return key data for Discord summary
print("\n__SUMMARY__")
print(json.dumps({
    "confirmed_buy": [r["code"] for r in confirmed],
    "divergence":    [r["code"] for r in diverg],
    "squeeze":       [r["code"] for r in squeeze[:5]],
    "bullish_count": len([r for r in rows if r["sig"] == "BULLISH"]),
    "bearish_count": len([r for r in rows if r["sig"] == "BEARISH"]),
    "flat_count":    len([r for r in rows if r["sig"] in ("FLAT","N/A")]),
}, ensure_ascii=False))
