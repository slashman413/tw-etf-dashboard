#!/usr/bin/env python3
"""
Iteration 14: Foreign Institutional Flow + Dividend Calendar
Probes TWSE endpoints for:
  - 三大法人 (foreign/trust/dealer buys) via available endpoints
  - Ex-dividend schedule for 0050/0056/00713/00878 universe
Generates: FOREIGN_FLOW.md, DIVIDEND_CALENDAR.md
"""

import requests, json, time
from pathlib import Path
from datetime import datetime

TODAY   = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT     = Path("reports") / TODAY
OUT.mkdir(parents=True, exist_ok=True)

BASE = "https://openapi.twse.com.tw/v1"

ALL_CODES = {
    "2330":"台積電","2317":"鴻海","2454":"聯發科","2882":"國泰金","2881":"富邦金",
    "2308":"台達電","3008":"大立光","2412":"中華電","2382":"廣達","2303":"聯電",
    "2886":"兆豐金","2891":"中信金","2357":"華碩","2603":"長榮","2379":"瑞昱",
    "2395":"研華","2884":"玉山金","5880":"合庫金","2002":"中鋼","1301":"台塑",
    "1303":"南亞","2207":"和泰車","2615":"萬海","2609":"陽明","2892":"第一金",
    "5871":"中租","6669":"緯穎","3711":"日月光","2327":"國巨","2408":"南亞科",
    "2887":"台新金","1216":"統一","1101":"台泥","2409":"友達","3045":"台灣大",
    "4938":"和碩","2376":"技嘉","3034":"聯詠","6770":"力積電","2801":"彰銀",
    "2883":"開發金","2890":"永豐金","1102":"亞泥","2301":"光寶","5876":"上海商銀",
    "2337":"旺宏","2352":"佳世達","6415":"矽力","3037":"欣興",
    # expansion
    "1590":"亞德客","2912":"統一超","4904":"遠傳","6488":"環球晶","2823":"中壽",
    "2880":"華南金","2888":"新光金","3231":"緯創","2383":"台光電","2344":"華邦電",
    "3481":"群創","2049":"上銀","6743":"合一",
}

def wait(s=120):
    for r in range(s, 0, -10):
        print(f"  {r}s...", end=" ", flush=True)
        time.sleep(10)
    print()

def probe(endpoint, label):
    url = f"{BASE}/{endpoint}"
    print(f"  → {label}: ", end="", flush=True)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"OK ({len(data)} records) | fields: {list(data[0].keys())[:6]}")
                return data
            print(f"empty or non-list ({type(data).__name__})")
        else:
            print(f"HTTP {r.status_code}")
    except Exception as e:
        print(f"ERR {e}")
    return None

# ── 1. Foreign institutional endpoints ───────────────────────────────────────
print(f"\n{'='*60}")
print(f"  Foreign Institutional Flow Probe")
print(f"{'='*60}")

foreign_endpoints = [
    ("exchangeReport/TWTB4U",       "外資買賣超 (TWTB4U)"),
    ("fund/TWT84U",                  "TWT84U"),
    ("exchangeReport/MI_QFIIS",      "外資持股 (MI_QFIIS)"),
    ("exchangeReport/FMTQIK",        "外資交易 FMTQIK"),
    ("exchangeReport/FMTQIK_ALL",    "外資 ALL"),
    ("fund/TWTFDN",                  "投信買賣 TWTFDN"),
    ("exchangeReport/MI_INDEX",      "大盤指數 MI_INDEX"),
    ("exchangeReport/MI_5MINS_INDEX","5分指數 MI_5MINS"),
]

foreign_data = {}
for ep, label in foreign_endpoints:
    result = probe(ep, label)
    if result:
        foreign_data[ep] = result

# ── 2. Dividend / ex-date endpoints ──────────────────────────────────────────
print(f"\n  Waiting 120s before dividend probe...")
wait(120)

print(f"\n{'='*60}")
print(f"  Dividend & Ex-Date Calendar Probe")
print(f"{'='*60}")

div_endpoints = [
    ("fund/t187ap09_L",              "除權息 t187ap09_L"),
    ("fund/t187ap09",                "除權息 t187ap09"),
    ("exchangeReport/TWTB8U",        "TWTB8U"),
    ("exchangeReport/TWDB",          "TWDB dividend"),
    ("fund/t187ap19_L",              "t187ap19_L"),
    ("exchangeReport/MI_MARGN_TRADE","融資融券交易 TRADE"),
    ("fund/TWT44U",                  "TWT44U"),
    ("exchangeReport/STOCK_DAY_AVG_ALL","均價 STOCK_DAY_AVG_ALL"),
]

div_data = {}
for ep, label in div_endpoints:
    result = probe(ep, label)
    if result:
        div_data[ep] = result

# ── 3. Try MI_INDEX for market summary ───────────────────────────────────────
market_summary = None
if "exchangeReport/MI_INDEX" in foreign_data:
    market_summary = foreign_data["exchangeReport/MI_INDEX"]

# ── 4. Process whatever we got ───────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  Processing results...")
print(f"{'='*60}")

# Check for foreign buy data
foreign_flow_rows = []
for ep, data in foreign_data.items():
    if ep in ("exchangeReport/TWTB4U", "fund/TWT84U"):
        for rec in data:
            code = rec.get("Code") or rec.get("股票代號") or rec.get("code","")
            if code in ALL_CODES:
                foreign_flow_rows.append({
                    "code": code,
                    "name": ALL_CODES.get(code, ""),
                    "ep": ep,
                    "raw": rec,
                })
        print(f"  Foreign flow matches in {ep}: {len(foreign_flow_rows)}")

# Check for dividend data
div_rows = []
for ep, data in div_data.items():
    for rec in data:
        code = rec.get("Code") or rec.get("股票代號") or rec.get("code","")
        if code in ALL_CODES:
            div_rows.append({
                "code": code,
                "name": ALL_CODES.get(code, ""),
                "ep": ep,
                "raw": rec,
            })
    print(f"  Dividend matches in {ep}: {len([r for r in div_rows if r['ep']==ep])}")

# ── 5. Generate FOREIGN_FLOW.md ───────────────────────────────────────────────
ff_lines = [
    f"# 三大法人 Foreign Institutional Flow — {TODAY}",
    "*Source: TWSE Open API probe*",
    "",
]

if foreign_flow_rows:
    ff_lines += [
        "## Foreign Net Buy/Sell",
        "",
        "| Code | Name | Net | Endpoint |",
        "|------|------|-----|---------|",
    ]
    for r in foreign_flow_rows[:20]:
        raw = r["raw"]
        net_key = next((k for k in raw if "Net" in k or "買超" in k or "買賣" in k), None)
        net_val = raw.get(net_key, "—") if net_key else "—"
        ff_lines.append(f"| {r['code']} | {r['name']} | {net_val} | {r['ep']} |")
else:
    ff_lines += [
        "## 三大法人 — Not Available via TWSE Open API Free Tier",
        "",
        "Probed endpoints:",
    ]
    for ep, label in foreign_endpoints:
        status = "✓ Found" if ep in foreign_data else "✗ Not available"
        ff_lines.append(f"- `{ep}` — {label}: **{status}**")
    ff_lines += [
        "",
        "### Available Alternatives",
        "- **Fugle API** (`data.fugle.com.tw`) — requires paid subscription",
        "- **Shioaji (永豐金)** — broker API with institutional flow",
        "- **TWSE Data API** (`data.twse.com.tw/api`) — paid TWSE subscription",
        "- **Yahoo Finance** — yfinance does not provide 三大法人 data",
    ]

# Market index summary if available
if market_summary:
    ff_lines += ["", "## Market Index Summary (MI_INDEX)", ""]
    for idx in market_summary[:5]:
        name = idx.get("指數名稱") or idx.get("Index") or str(list(idx.values())[:1])
        val  = idx.get("收盤指數") or idx.get("Close") or "—"
        chg  = idx.get("漲跌點數") or idx.get("Change") or "—"
        ff_lines.append(f"- **{name}**: {val} ({chg})")

ff_lines += ["", f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"]
(OUT / "FOREIGN_FLOW.md").write_text("\n".join(ff_lines), encoding="utf-8")
print(f"\n  ✓ FOREIGN_FLOW.md written")

# ── 6. Generate DIVIDEND_CALENDAR.md ─────────────────────────────────────────
# Use the dividend yield data we already have from daily_scores.json
daily_scores_path = OUT / "daily_scores.json"
composite_path    = OUT / "composite_data.json"
scores = []
if daily_scores_path.exists():
    scores = json.loads(daily_scores_path.read_text(encoding="utf-8"))

# Sort by dividend yield desc — these are the ones approaching ex-date
high_div = sorted(
    [s for s in scores if s.get("div") and s["div"] > 2.0],
    key=lambda x: -x["div"]
)

dc_lines = [
    f"# Dividend Calendar & High-Yield Focus — {TODAY}",
    f"*Source: TWSE BWIBBU_ALL (殖利率) | Q1 2026 EPS*",
    "",
    "## Taiwan Dividend Season Context",
    "",
    "Most listed companies pay **one annual dividend** with ex-dates clustered **June–August**.",
    "Taiwan tax on dividends: **8.84% withholding** for foreign holders.",
    "",
    "⚠️ **Real-time ex-dates** require TWSE Data API (paid). Below shows forward yield ranking",
    "   to identify stocks most relevant to the 0056 / 00713 high-dividend ETF thesis.",
    "",
    "---",
    "",
    "## High-Dividend Universe (殖利率 > 2%)",
    "",
    "| Rank | Code | Name | Div Yield | Fwd P/E | Q1 EPS | Price | Score | Note |",
    "|------|------|------|----------|---------|--------|-------|-------|------|",
]

WATCH_NOTES = {
    "2603": "Shipping cycle risk",
    "6770": "PSMC anomaly — non-recurring OP",
    "1102": "Rev declining -9.3%",
    "4938": "Rev declining -15.2%",
    "2308": "P/E 77x — overvalued",
}

for i, s in enumerate(high_div[:25], 1):
    code   = s["code"]
    name   = s["name"].split()[0]
    div    = f"{s['div']:.2f}%"
    fpe    = f"{s['fwd_pe']:.1f}x" if s.get("fwd_pe") else "—"
    eps    = f"¥{s['q1_eps']}" if s.get("q1_eps") else "—"
    price  = f"¥{s['price']}" if s.get("price") else "—"
    score  = s.get("score", "—")
    note   = WATCH_NOTES.get(code, "")
    # Star high yield + high score combos
    star = "⭐" if (s.get("div",0) > 4.0 and (s.get("score") or 0) >= 50) else ""
    dc_lines.append(
        f"| {i} | **{code}** | {name} | **{div}** {star} | {fpe} | {eps} | {price} | {score} | {note} |"
    )

# ETF-specific focus
dc_lines += [
    "",
    "---",
    "",
    "## 0056 / 00713 High-Dividend ETF Component Focus",
    "",
    "These ETFs select stocks by **forward dividend yield** — stocks ranking high here",
    "are most likely to remain in or enter the ETF on next rebalancing.",
    "",
    "### Top Candidates (Yield > 4% + Score ≥ 45)",
    "",
]

top_div_qual = [s for s in high_div if s.get("div",0) > 4.0 and (s.get("score") or 0) >= 45]
if top_div_qual:
    dc_lines.append("| Code | Name | Yield | Score | Verdict |")
    dc_lines.append("|------|------|-------|-------|---------|")
    for s in top_div_qual:
        dc_lines.append(
            f"| **{s['code']}** | {s['name'].split()[0]} | **{s['div']:.2f}%** | {s.get('score','—')} | {s.get('conviction','—')} |"
        )
else:
    dc_lines.append("*No stocks meet combined yield >4% + score ≥45 threshold.*")

# Div data from probe
if div_rows:
    dc_lines += ["", "### Live Ex-Date Data Found", ""]
    for r in div_rows[:20]:
        dc_lines.append(f"- **{r['code']}** {r['name']}: {r['raw']}")
else:
    dc_lines += [
        "",
        "### Ex-Date Probe Results",
        "",
    ]
    for ep, label in div_endpoints:
        status = "✓ Data found" if ep in div_data else "✗ Not available"
        dc_lines.append(f"- `{ep}` — {label}: **{status}**")
    dc_lines += [
        "",
        "> Ex-dividend date data is available via **TWSE Data API** (`data.twse.com.tw`)",
        "> or from financial data providers (Goodinfo, MoneyDJ, CMoney).",
    ]

dc_lines += [
    "",
    "---",
    "",
    "## Dividend Capture Strategy Notes",
    "",
    "1. **Buy before ex-date** to receive dividend; stock drops ~dividend amount on ex-date",
    "2. **High-yield + low-P/E** (e.g. 5876 上海商銀 4.42% @ 9.7x fwd P/E) offers total return buffer",
    "3. **Financial stocks** (banks/insurance) — use P/B ≤ 1.5 + yield > 4% as entry criteria",
    "4. **Watch IFRS 17 distortion** in insurance revenue figures — dividend sustainability",
    "   should be checked via EPS payout ratio, not revenue growth",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Loop iteration 14*",
]

(OUT / "DIVIDEND_CALENDAR.md").write_text("\n".join(dc_lines), encoding="utf-8")
print(f"  ✓ DIVIDEND_CALENDAR.md written")

# Print summary
print(f"\n{'='*60}")
print(f"  Foreign flow endpoints found: {len(foreign_data)}")
print(f"  Dividend endpoints found:     {len(div_data)}")
print(f"  High-div stocks (>4%+≥45):   {len(top_div_qual)}")
if top_div_qual:
    for s in top_div_qual:
        print(f"    {s['code']} {s['name'].split()[0]:15s} {s['div']:.2f}% yield  score={s.get('score','?')}")
print(f"{'='*60}")

# Output for summary
print("\n__SUMMARY__")
print(json.dumps({
    "foreign_endpoints_found": list(foreign_data.keys()),
    "div_endpoints_found":     list(div_data.keys()),
    "high_div_qual":           [s["code"] for s in top_div_qual],
    "top_5_yield":             [{"code":s["code"],"div":round(s["div"],2)} for s in high_div[:5]],
}, ensure_ascii=False))
