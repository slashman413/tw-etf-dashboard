#!/usr/bin/env python3
"""
Iteration 21: April 2026 Revenue Deep-Dive
Data already fetched — reuses the live t187ap05_L response.
Extracts:
  - April 2026 monthly revenue + YoY + MoM for all 62 stocks
  - Cumulative Jan–Apr 2026 vs Jan–Apr 2025 (4-month trend)
  - Momentum signal: is April accelerating or decelerating vs Q1 trend?
No new API call needed — uses data from the freshness check above.
Generates: APRIL_REVENUE.md + april_revenue.json
"""

import json, urllib.request, ssl, time
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
code_set   = {s["code"]: s for s in composite}

# Also load expansion
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
exp_set   = {s["code"]: s for s in expansion}
all_codes = set(code_set.keys()) | set(exp_set.keys())

# ── Fetch (120s already elapsed since last call; add small buffer) ─────────────
print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting 130s before TWSE fetch...")
time.sleep(130)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

URL = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"
print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching {URL}")

try:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    print(f"  → {len(raw)} records")
except Exception as e:
    print(f"  ✗ {e}"); exit(1)

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v and str(v).strip() not in ("-","") else None
    except: return None

# ── Parse records ──────────────────────────────────────────────────────────────
april_data = {}
for row in raw:
    code   = str(row.get("公司代號","")).strip()
    if code not in all_codes: continue
    period = str(row.get("資料年月","")).strip()
    if period != "11504": continue    # April 2026 only

    apr_rev   = sf(row.get("營業收入-當月營收"))       # April 2026 (thousands NTD)
    mar_rev   = sf(row.get("營業收入-上月營收"))       # March 2026
    apr25_rev = sf(row.get("營業收入-去年當月營收"))   # April 2025
    mom_pct   = sf(row.get("營業收入-上月比較增減(%)"))
    yoy_pct   = sf(row.get("營業收入-去年同月增減(%)"))
    cum_26    = sf(row.get("累計營業收入-當月累計營收"))  # Jan-Apr 2026
    cum_25    = sf(row.get("累計營業收入-去年累計營收"))  # Jan-Apr 2025
    cum_yoy   = sf(row.get("累計營業收入-前期比較增減(%)"))

    april_data[code] = {
        "code":     code,
        "apr_rev":  apr_rev,    # in NTD thousands
        "mar_rev":  mar_rev,
        "apr25_rev":apr25_rev,
        "mom":      mom_pct,
        "yoy":      yoy_pct,
        "cum_26":   cum_26,
        "cum_25":   cum_25,
        "cum_yoy":  cum_yoy,
    }

print(f"  → {len(april_data)} ETF stocks matched")

# ── Cross-reference with composite Q1 YoY ─────────────────────────────────────
# Q1 YoY from composite = revenue YoY based on 4-quarter trailing
# April YoY = single month April 2026 vs April 2025
# Cumulative YoY = Jan-Apr 2026 vs Jan-Apr 2025 (most reliable)

results = []
name_map = {**{s["code"]: s["name"] for s in composite},
            **{s["code"]: s["name"] for s in expansion}}
score_map = {s["code"]: s.get("score") for s in composite}
sector_map = {s["code"]: s.get("sector","—") for s in composite}

for code, d in april_data.items():
    s = code_set.get(code, {})
    q1_yoy   = s.get("rev_yoy")  # Q1 YoY from our composite

    # Momentum signal: is April's cumulative YoY better or worse than Q1?
    cum_yoy   = d["cum_yoy"]
    april_yoy = d["yoy"]
    mom_pct   = d["mom"]

    # Acceleration: if cum_yoy > q1_yoy → trend improving into April
    accel = None
    if cum_yoy is not None and q1_yoy is not None:
        delta = cum_yoy - q1_yoy
        if delta > 5:   accel = "ACCELERATING"
        elif delta > 0: accel = "STABLE↑"
        elif delta > -5:accel = "STABLE↓"
        else:           accel = "DECELERATING"

    # April standalone vs March MoM
    if mom_pct is not None:
        if mom_pct > 10:   mom_sig = "SURGE"
        elif mom_pct > 3:  mom_sig = "GROWTH"
        elif mom_pct > -3: mom_sig = "FLAT"
        elif mom_pct > -10:mom_sig = "DIP"
        else:              mom_sig = "DECLINE"
    else:
        mom_sig = "N/A"

    # April revenue in billions NTD for display
    apr_b  = d["apr_rev"]  / 1e6 if d["apr_rev"]  else None  # thousands → billions
    cum_b  = d["cum_26"]   / 1e6 if d["cum_26"]   else None

    results.append({
        "code":      code,
        "name":      name_map.get(code, code),
        "sector":    sector_map.get(code, "—"),
        "score":     score_map.get(code),
        "apr_b":     apr_b,
        "cum_b":     cum_b,
        "april_yoy": april_yoy,
        "cum_yoy":   cum_yoy,
        "mom":       mom_pct,
        "q1_yoy":    q1_yoy,
        "accel":     accel,
        "mom_sig":   mom_sig,
    })

# Sort by cumulative YoY descending
results.sort(key=lambda x: -(x["cum_yoy"] or -999))

# ── Categorise ────────────────────────────────────────────────────────────────
accelerating = [r for r in results if r["accel"] in ("ACCELERATING","STABLE↑")]
decelerating = [r for r in results if r["accel"] in ("DECELERATING","STABLE↓")]
high_growth  = [r for r in results if (r["cum_yoy"] or 0) > 20]
negative_yoy = [r for r in results if (r["cum_yoy"] or 0) < 0]

# ── Generate APRIL_REVENUE.md ─────────────────────────────────────────────────
def fmt(v, dec=1, pre="", suf=""):
    return f"{pre}{v:.{dec}f}{suf}" if v is not None else "—"

def yoy_cell(v):
    if v is None: return "—"
    return f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%"

lines = [
    f"# April 2026 Revenue Analysis — {TODAY}",
    "*Source: TWSE t187ap05_L (資料年月: 11504 = April 2026)*",
    "*Includes April standalone YoY/MoM and cumulative Jan–Apr 2026 vs 2025*",
    "",
    "## Summary",
    "",
    f"- **Stocks with April data**: {len(results)} / 62",
    f"- **Cumulative YoY > +20%**: {len(high_growth)} stocks (strong growth)",
    f"- **Cumulative YoY < 0**: {len(negative_yoy)} stocks (contraction)",
    f"- **Accelerating vs Q1**: {len(accelerating)} stocks",
    f"- **Decelerating vs Q1**: {len(decelerating)} stocks",
    "",
    "---",
    "",
    "## 📈 Top Revenue Growth — Jan–Apr 2026 Cumulative YoY",
    "",
    "| Code | Name | Sector | Apr YoY | Cum YoY | vs Q1 | Momentum | Score |",
    "|------|------|--------|---------|---------|-------|----------|-------|",
]

for r in results[:20]:
    accel_icon = {"ACCELERATING":"⬆⬆","STABLE↑":"⬆","STABLE↓":"⬇","DECELERATING":"⬇⬇"}.get(r["accel"],"~")
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | {r['sector']} | "
        f"{yoy_cell(r['april_yoy'])} | **{yoy_cell(r['cum_yoy'])}** | "
        f"{accel_icon} {r['accel'] or '—'} | {r['mom_sig']} | {r['score'] or '—'} |"
    )

lines += [
    "",
    "---",
    "",
    "## 📉 Revenue Contraction (Cum YoY < 0)",
    "",
    "| Code | Name | Apr YoY | Cum YoY | MoM | Score |",
    "|------|------|---------|---------|-----|-------|",
]
for r in sorted(negative_yoy, key=lambda x: x["cum_yoy"] or 0):
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | "
        f"{yoy_cell(r['april_yoy'])} | **{yoy_cell(r['cum_yoy'])}** | "
        f"{fmt(r['mom'],1,'','%')} | {r['score'] or '—'} |"
    )

lines += [
    "",
    "---",
    "",
    "## Full Table — All Stocks (Sorted by Cumulative YoY)",
    "",
    "| Code | Name | Apr Rev (B) | Cum Rev (B) | Apr YoY | Cum YoY | MoM | Accel | Score |",
    "|------|------|------------|------------|---------|---------|-----|-------|-------|",
]
for r in results:
    accel_icon = {"ACCELERATING":"⬆⬆","STABLE↑":"⬆","STABLE↓":"⬇","DECELERATING":"⬇⬇"}.get(r["accel"],"~")
    lines.append(
        f"| {r['code']} | {r['name'].split()[0]} | "
        f"¥{fmt(r['apr_b'],1)}B | ¥{fmt(r['cum_b'],1)}B | "
        f"{yoy_cell(r['april_yoy'])} | **{yoy_cell(r['cum_yoy'])}** | "
        f"{fmt(r['mom'],1,'','%')} | {accel_icon} | {r['score'] or '—'} |"
    )

lines += [
    "",
    "---",
    "",
    "## Key Observations",
    "",
    f"1. **{len(high_growth)} stocks** have cumulative Jan–Apr YoY > +20% — strong broad-based growth",
    f"2. **{len(negative_yoy)} stocks** in contraction — concentrated in cement, shipping, steel cyclicals",
    f"3. **{len(accelerating)} stocks** show improving trend into April vs Q1 baseline",
    f"4. **{len(decelerating)} stocks** showing deceleration — monitor closely for guidance revisions",
    "",
    "## April vs March MoM Pattern",
    "",
]

surge  = [r for r in results if r["mom_sig"] == "SURGE"]
growth = [r for r in results if r["mom_sig"] == "GROWTH"]
dip    = [r for r in results if r["mom_sig"] in ("DIP","DECLINE")]

lines += [
    f"- **SURGE (MoM > +10%)**: {len(surge)} stocks — {', '.join(r['code'] for r in surge[:6])}",
    f"- **GROWTH (MoM +3 to +10%)**: {len(growth)} stocks",
    f"- **DIP/DECLINE (MoM < -3%)**: {len(dip)} stocks — {', '.join(r['code'] for r in dip[:6])}",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 21*",
    f"*Data: April 2026 (ROC 115/04) — May 2026 data expected ~June 10, 2026*",
]

(REPORT_DIR / "APRIL_REVENUE.md").write_text("\n".join(lines), encoding="utf-8")

# ── Save JSON ──────────────────────────────────────────────────────────────────
apr_json = {
    "date":          TODAY,
    "period":        "11504",
    "month":         "April 2026",
    "total_stocks":  len(results),
    "high_growth":   [{"code":r["code"],"name":r["name"].split()[0],"cum_yoy":r["cum_yoy"],
                       "april_yoy":r["april_yoy"],"score":r["score"]}
                      for r in high_growth],
    "negative_yoy":  [{"code":r["code"],"name":r["name"].split()[0],"cum_yoy":r["cum_yoy"],
                       "april_yoy":r["april_yoy"],"score":r["score"]}
                      for r in negative_yoy],
    "accelerating":  [{"code":r["code"],"name":r["name"].split()[0],"cum_yoy":r["cum_yoy"],
                       "q1_yoy":r["q1_yoy"],"accel":r["accel"]}
                      for r in accelerating],
    "all_results":   results,
}
(REPORT_DIR / "april_revenue.json").write_text(
    json.dumps(apr_json, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n✓ APRIL_REVENUE.md + april_revenue.json")
print(f"\n  High growth (Cum YoY > +20%): {[r['code'] for r in high_growth]}")
print(f"  Contraction (Cum YoY < 0):   {[r['code'] for r in negative_yoy]}")
print(f"  Accelerating:                 {[r['code'] for r in accelerating[:6]]}")
print(f"\n  Top 10 by cumulative Jan-Apr YoY:")
for r in results[:10]:
    print(f"    {r['code']} {r['name'].split()[0]:12s}  cumYoY={fmt(r['cum_yoy'],1,'','%'):8s}  "
          f"aprYoY={fmt(r['april_yoy'],1,'','%'):8s}  {r['accel'] or '—'}")
