#!/usr/bin/env python3
"""
Iteration 14b: Technical Analysis Overlay
Uses STOCK_DAY_AVG_ALL (30-day MA) + MI_INDEX (market index)
to add price-vs-MA signals to our 62-stock universe.
Generates: TECHNICAL_ANALYSIS.md, updates dashboard JSON.
"""

import requests, json, time
from pathlib import Path
from datetime import datetime

TODAY   = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
OUT     = Path("reports") / TODAY
BASE    = "https://openapi.twse.com.tw/v1"

def wait(s=120):
    for r in range(s, 0, -10):
        print(f"  {r}s...", end=" ", flush=True)
        time.sleep(10)
    print()

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
    "1590":"亞德客","2912":"統一超","4904":"遠傳","6488":"環球晶","2823":"中壽",
    "2880":"華南金","2888":"新光金","3231":"緯創","2383":"台光電","2344":"華邦電",
    "3481":"群創","2049":"上銀","6743":"合一",
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
    try: return float(str(v).replace(",",""))
    except: return None

print(f"\n{'='*60}")
print(f"  Technical Analysis — {TODAY}")
print(f"{'='*60}")

# Wait 120s since foreign_dividend.py just ran
print("\n  Waiting 120s (API cooldown)...")
wait(120)

# ── Fetch STOCK_DAY_AVG_ALL (30-day MA) ──────────────────────────────────────
print("  Fetching STOCK_DAY_AVG_ALL (30-day MA)...", end=" ", flush=True)
r = requests.get(f"{BASE}/exchangeReport/STOCK_DAY_AVG_ALL", headers=HEADERS, timeout=20)
r.raise_for_status()
avg_raw = r.json()
print(f"OK ({len(avg_raw)} records)")

# Wait 120s
print("  Waiting 120s before next API call...")
wait(120)

# ── Fetch MI_INDEX ────────────────────────────────────────────────────────────
print("  Fetching MI_INDEX (TAIEX + sector indices)...", end=" ", flush=True)
r2 = requests.get(f"{BASE}/exchangeReport/MI_INDEX", headers=HEADERS, timeout=20)
r2.raise_for_status()
idx_raw = r2.json()
print(f"OK ({len(idx_raw)} records)")

# ── Process 30-day MA data ────────────────────────────────────────────────────
ma_map = {}
for rec in avg_raw:
    code = rec.get("Code","")
    if code not in ALL_CODES: continue
    close = sf(rec.get("ClosingPrice"))
    ma30  = sf(rec.get("MonthlyAveragePrice"))
    if close is None or ma30 is None: continue
    pct_vs_ma = (close - ma30) / ma30 * 100
    signal = "ABOVE_MA" if pct_vs_ma > 0 else "BELOW_MA"
    # Strength thresholds
    if pct_vs_ma > 5:      tech_sig = "STRONG ↑"
    elif pct_vs_ma > 1:    tech_sig = "ABOVE ↑"
    elif pct_vs_ma > -1:   tech_sig = "AT MA ~"
    elif pct_vs_ma > -5:   tech_sig = "BELOW ↓"
    else:                  tech_sig = "WEAK ↓"
    ma_map[code] = {
        "close": close, "ma30": ma30,
        "pct_vs_ma": pct_vs_ma, "signal": signal, "tech_sig": tech_sig,
    }

print(f"  Matched {len(ma_map)} / {len(ALL_CODES)} stocks with MA data")

# ── Process MI_INDEX ──────────────────────────────────────────────────────────
taiex = None
sector_indices = []
for idx in idx_raw:
    name   = idx.get("指數") or idx.get("指數名稱","")
    close  = sf(idx.get("收盤指數"))
    change = sf(idx.get("漲跌點數"))
    pct    = sf(idx.get("漲跌百分比"))
    if "加權" in str(name) or "TAIEX" in str(name).upper() or "台灣加權" in str(name):
        taiex = {"name": name, "close": close, "change": change, "pct": pct}
    if close and change is not None:
        sector_indices.append({"name": name, "close": close, "change": change, "pct": pct or 0})

sector_indices.sort(key=lambda x: x["pct"] or 0)

# ── Build combined analysis ───────────────────────────────────────────────────
rows = []
for code, name in ALL_CODES.items():
    score = COMPOSITE.get(code, 40)
    ma    = ma_map.get(code, {})
    rows.append({
        "code": code, "name": name, "score": score,
        "close":      ma.get("close"),
        "ma30":       ma.get("ma30"),
        "pct_vs_ma":  ma.get("pct_vs_ma"),
        "tech_sig":   ma.get("tech_sig","N/A"),
        "signal":     ma.get("signal","N/A"),
    })

rows.sort(key=lambda x: -(x.get("pct_vs_ma") or -999))

# Key combos: below MA + high score = potential bounce buy
bounce_candidates = [
    r for r in rows
    if r["signal"] == "BELOW_MA"
    and r["score"] >= 60
    and r.get("pct_vs_ma") is not None
    and r["pct_vs_ma"] > -15  # not completely broken
]
bounce_candidates.sort(key=lambda x: x["score"] - abs(x["pct_vs_ma"]), reverse=True)

# Stocks strong above MA (momentum intact)
momentum_stocks = [r for r in rows if r["tech_sig"] in ("STRONG ↑","ABOVE ↑") and r["score"] >= 55]

# ── Generate TECHNICAL_ANALYSIS.md ───────────────────────────────────────────
lines = [
    f"# Technical Analysis — Price vs 30-Day MA — {TODAY}",
    f"*Source: TWSE STOCK_DAY_AVG_ALL + MI_INDEX | 62-stock universe*",
    "",
    "**Signal logic:** 30-day MA = medium-term trend benchmark.",
    "- STRONG ↑ = price > MA by >5% (momentum) | ABOVE ↑ = 1–5% above",
    "- AT MA ~ = within ±1% (decision zone) | BELOW ↓ = 1–5% below | WEAK ↓ = >5% below",
    "",
]

# Market context
if taiex:
    chg_str = f"{taiex['change']:+.2f}" if taiex['change'] else "—"
    pct_str = f"{taiex['pct']:+.2f}%" if taiex['pct'] else "—"
    lines += [
        "## Market Context",
        "",
        f"**TAIEX (加權指數):** {taiex['close']:,.2f}  Change: {chg_str} ({pct_str})",
        "",
    ]

# Sector index leaders/laggards
if sector_indices:
    lines += [
        "### Sector Index Performance",
        "",
        "| Index | Close | Change | % |",
        "|-------|-------|--------|---|",
    ]
    for idx in sector_indices[:8]:
        pct = idx.get("pct",0) or 0
        sym = "🟢" if pct > 0 else "🔴" if pct < 0 else "⚪"
        lines.append(f"| {sym} {idx['name']} | {idx['close']:,.0f} | {idx['change']:+.2f} | {pct:+.2f}% |")
    lines.append("")

# Bounce candidates
lines += [
    "---",
    "",
    "## 🔄 Mean-Reversion Candidates",
    "*Strong fundamentals (score ≥60) currently trading BELOW 30-day MA*",
    "*Today's selloff may have pushed these below fair value.*",
    "",
    "| Code | Name | Score | Price | 30d MA | Δ vs MA | Tech Signal |",
    "|------|------|-------|-------|--------|---------|------------|",
]

for r in bounce_candidates[:12]:
    pct = r["pct_vs_ma"]
    pct_str = f"{pct:+.1f}%"
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | **{r['score']}** | "
        f"¥{r['close']:,.0f} | ¥{r['ma30']:,.0f} | **{pct_str}** | {r['tech_sig']} |"
    )

if not bounce_candidates:
    lines.append("*No high-score stocks below 30-day MA today.*")

# Momentum stocks
lines += [
    "",
    "## 📈 Momentum Intact (Above 30d MA + Score ≥55)",
    "",
    "| Code | Name | Score | Price | 30d MA | Δ vs MA | Signal |",
    "|------|------|-------|-------|--------|---------|--------|",
]

for r in momentum_stocks[:10]:
    pct = r["pct_vs_ma"]
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | {r['score']} | "
        f"¥{r['close']:,.0f} | ¥{r['ma30']:,.0f} | **{pct:+.1f}%** | {r['tech_sig']} |"
    )

if not momentum_stocks:
    lines.append("*No strong-fundamental stocks above 30d MA today.*")

# Full snapshot
lines += [
    "",
    "## Full Technical Snapshot",
    "",
    "| Code | Name | Score | Price | 30d MA | Δ vs MA | Signal |",
    "|------|------|-------|-------|--------|---------|--------|",
]

for r in sorted(rows, key=lambda x: -(x["score"])):
    if r.get("close") is None: continue
    pct = r["pct_vs_ma"]
    pct_str = f"{pct:+.1f}%" if pct is not None else "—"
    lines.append(
        f"| {r['code']} | {r['name'].split()[0]} | {r['score']} | "
        f"¥{r['close']:,.0f} | ¥{r['ma30']:,.0f} | {pct_str} | {r['tech_sig']} |"
    )

# Combined conviction (fundamental + technical)
lines += [
    "",
    "---",
    "",
    "## ⭐ Triple-Confirmed BUY (Score ≥65 + Below MA + BULLISH Margin)",
    "",
    "Stocks where: (1) strong fundamentals, (2) price below 30d MA (oversold on selloff),",
    "(3) retail margin flow is bullish (dip-buying confirmed).",
    "",
]

# Load margin data
margin_path = OUT / "margin_data.json"
margin = {}
if margin_path.exists():
    margin = json.loads(margin_path.read_text(encoding="utf-8"))

triple = []
for r in rows:
    code = r["code"]
    m = margin.get(code, {})
    if (r["score"] >= 65
        and r.get("signal") == "BELOW_MA"
        and m.get("sig") == "BULLISH"):
        triple.append({**r, "margin_sig": m.get("sig"), "m_chg": m.get("m_chg"), "detail": m.get("detail","")})

if triple:
    lines += [
        "| Code | Name | Score | Δ vs MA | Margin Detail |",
        "|------|------|-------|---------|---------------|",
    ]
    for r in triple:
        lines.append(
            f"| **{r['code']}** | {r['name'].split()[0]} | **{r['score']}** | "
            f"**{r['pct_vs_ma']:+.1f}%** | {r['detail']} |"
        )
else:
    lines.append("*No stocks meet all three criteria today — market conditions may not create this alignment.*")

lines += [
    "",
    "---",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Source: TWSE STOCK_DAY_AVG_ALL*",
]

out_path = OUT / "TECHNICAL_ANALYSIS.md"
out_path.write_text("\n".join(lines), encoding="utf-8")
print(f"\n  ✓ TECHNICAL_ANALYSIS.md: {out_path}")

# Print summary
above = sum(1 for r in rows if r["signal"] == "ABOVE_MA" and r.get("close"))
below = sum(1 for r in rows if r["signal"] == "BELOW_MA" and r.get("close"))
print(f"\n  Above 30d MA: {above} stocks | Below: {below} stocks")
print(f"  Bounce candidates (score≥60, below MA): {len(bounce_candidates)}")
if bounce_candidates:
    for r in bounce_candidates[:5]:
        print(f"    {r['code']} {r['name'].split()[0]:12s} score={r['score']} MA_delta={r['pct_vs_ma']:+.1f}%")
print(f"  Triple confirmed BUY: {len(triple)}")
if triple:
    for r in triple:
        print(f"    {r['code']} {r['name'].split()[0]:12s} score={r['score']}")

if taiex:
    print(f"\n  TAIEX: {taiex['close']:,.2f}  ({taiex.get('pct',''):+}%)")

print(f"\n{'='*60}")
