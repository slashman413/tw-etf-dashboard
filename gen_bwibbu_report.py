#!/usr/bin/env python3
"""Generate BWIBBU_REFRESH.md from saved bwibbu_fresh.json — no API calls."""

import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "bwibbu_fresh.json").exists()], reverse=True)
TODAY = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

data = json.loads((REPORT_DIR / "bwibbu_fresh.json").read_text(encoding="utf-8"))

refreshed   = data["all_refreshed"]
high_div    = data["high_div_ge45"]
cheap_pe    = data["cheap_pe_lt15"]
pe_expanded = data["pe_expanded"]
pe_contracted = data["pe_contracted"]

def fv(v, fmt=".2f", fallback="—"):
    if v is None: return fallback
    return format(float(v), fmt)

# Key signals: stocks with P/E contraction that are still in our BUY universe
buy_codes = {"2408","2376","2887","5871","2801","5876","2357","1303","2883","3008","2615","6770"}
conv_changes = []
for r in refreshed:
    code = r["code"]
    if r["pe_new"] and r["pe_new"] < 20 and code not in {"2887","5876","5871","2801","2882","2883","2881","2886","2891","2892","2884","2890","5880"}:
        # Non-financial cheap P/E
        old_score = r.get("score_old")
        conv_changes.append(r)

lines = [
    f"# BWIBBU Valuation Refresh — {TODAY} (Iteration 25)",
    f"*Market data: {data.get('data_date','1150604')} (2026-06-04 close) | Refreshed: {data.get('refresh_ts','—')}*",
    f"*{data['total_matched']} stocks matched across ETF universe*",
    "",
    "---",
    "",
    "## 🔑 Key Valuation Signals vs Prior Analysis",
    "",
    "| Signal | Code | Name | Old P/E | New P/E | Change | Interpretation |",
    "|--------|------|------|---------|---------|--------|---------------|",
]

signal_rows = [
    ("📈 P/E Expanded", "3037", "欣興", 74.0, 142.8, "+68.78x", "PCB substrate price surge — now very expensive"),
    ("📈 P/E Expanded", "6770", "力積電", 6.0, 45.8, "+39.73x", "Q1 non-recurring confirmed; normalized P/E much higher"),
    ("📈 P/E Expanded", "1303", "南亞", 15.4, 48.0, "+32.63x", "Price rose significantly; original thesis weakens"),
    ("📈 P/E Expanded", "2408", "南亞科", 11.7, 35.4, "+23.62x", "Stock price re-rated up; DRAM recovery priced in"),
    ("📉 P/E Contracted", "4938", "和碩", 41.8, 22.3, "-19.51x", "Earnings turnaround; valuation much more attractive"),
    ("📉 P/E Contracted", "2609", "陽明", 32.4, 17.3, "-15.17x", "Shipping earnings improving; price dipped"),
    ("📉 P/E Contracted", "2603", "長榮", 15.4, 10.3, "-5.05x", "⭐ Now cheapest in shipping; div 6.78%"),
    ("📉 P/E Contracted", "1102", "亞泥", 15.3, 11.5, "-3.80x", "Value opportunity; div 6.70%"),
]
for s, code, name, old, new, chg, note in signal_rows:
    lines.append(f"| {s} | **{code}** | {name} | {old:.1f}x | **{new:.1f}x** | {chg} | {note} |")

lines += [
    "",
    "---",
    "",
    "## Cheapest Non-Financial Stocks (P/E < 15x)",
    "",
    "| Code | Name | P/E | Prior P/E | Δ | Div% | Score |",
    "|------|------|-----|----------|---|------|-------|",
]
for r in cheap_pe:
    delta = ""
    if r.get("pe_old") and r.get("pe_new"):
        d = r["pe_new"] - r["pe_old"]
        delta = f"{d:+.1f}x"
    div_str = fv(next((x.get("div_new") for x in data["high_div_ge45"] if x["code"]==r["code"]), None))
    if div_str == "—":
        # look in all_refreshed
        rr = next((x for x in refreshed if x["code"]==r["code"]), {})
        div_str = fv(rr.get("div_new"))
    lines.append(
        f"| **{r['code']}** | {r['name']} | **{r['pe_new']:.1f}x** | "
        f"{fv(r.get('pe_old'),'.1f')}x | {delta} | {div_str}% | — |"
    )

lines += [
    "",
    "---",
    "",
    "## High Dividend Yield Stocks (≥4.5%)",
    "",
    "| Code | Name | Div% | Prior Div% | Δ | P/E | P/B |",
    "|------|------|------|-----------|---|-----|-----|",
]
for r in high_div:
    rr = next((x for x in refreshed if x["code"]==r["code"]), {})
    chg = ""
    if r.get("div_old") is not None and r.get("div_new") is not None:
        d = r["div_new"] - r["div_old"]
        chg = f"{d:+.2f}%"
    div_old_str = fv(r.get("div_old"))
    lines.append(
        f"| **{r['code']}** | {r['name']} | **{r['div_new']:.2f}%** | "
        f"{div_old_str}% | {chg} | "
        f"{fv(rr.get('pe_new'),'.1f')}x | "
        f"{fv(rr.get('pb_new'),'.2f')}x |"
    )

lines += [
    "",
    "---",
    "",
    "## Interpretation & Conviction Updates",
    "",
    "### ✅ Strengthened Cases",
    "- **長榮 2603**: P/E contracted from 15.4x → **10.3x** AND dividend yield **6.78%** — classic value+income",
    "  Shipping cycle earnings are improving. If payout sustainability is solid, this becomes a high-conviction pick.",
    "- **亞泥 1102**: P/E 11.5x + div 6.70% — cement sector but very cheap. Monitor for cyclical recovery.",
    "- **和碩 4938**: P/E compressed from 41.8x → **22.3x** — major earnings improvement signal.",
    "  Previously in our AVOID list (high payout ratio risk). The earnings jump warrants re-examination.",
    "",
    "### ⚠️ Weakened Cases",
    "- **南亞科 2408**: P/E expanded to **35.4x** — market has re-rated the stock on DRAM recovery news.",
    "  Target price still +156% upside, but entry becomes less attractive at current price.",
    "  Original conviction: STRONG BUY at ¥395, P/E 11.7x. Now 3× more expensive on P/E basis.",
    "- **南亞 1303**: P/E 48.0x — valuation has stretched significantly. Reduce position priority.",
    "- **欣興 3037**: P/E 142.8x — AI substrate premium is fully (and more) priced in. High risk.",
    "- **力積電 6770**: Non-recurring nature confirmed: P/E normalized to 45.8x vs our original 6.0x.",
    "  Reinforces our WATCH⚠️ rating — avoid until Q2 2026 clarifies sustainable earnings.",
    "",
    "### 📊 Dividend Yield Update",
    "7 stocks now yielding ≥4.5%:",
    "| Rank | Code | Name | Yield | P/E | Notes |",
    "|------|------|------|-------|-----|-------|",
    "| 1 | 6743 | 合一 | 9.90% | — | Biotech; high yield = high risk |",
    "| 2 | 2603 | 長榮 | 6.78% | 10.3x | Shipping; value+income combo |",
    "| 3 | 1102 | 亞泥 | 6.70% | 11.5x | Cement; cheap but cyclical |",
    "| 4 | 5871 | 中租 | 5.04% | 11.1x | ✅ Quality income pick |",
    "| 5 | 2801 | 彰銀 | 4.91% | 13.4x | ✅ Bank; safe payout |",
    "| 6 | 2357 | 華碩 | 4.71% | — | ✅ Tech+dividend |",
    "| 7 | 3034 | 聯詠 | 4.70% | — | IC design; high yield |",
    "",
    "---",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 25 | No new API calls*",
]

(REPORT_DIR / "BWIBBU_REFRESH.md").write_text("\n".join(lines), encoding="utf-8")
print(f"✓ BWIBBU_REFRESH.md written")
print(f"\nKey conviction updates:")
print(f"  STRENGTHENED: 2603 長榮 (P/E 10.3x + 6.78% yield), 1102 亞泥 (11.5x + 6.70% yield)")
print(f"  WEAKENED:     2408 南亞科 (P/E 35.4x, was 11.7x), 1303 南亞 (P/E 48.0x)")
print(f"  CONFIRMED⚠️:  6770 力積電 (P/E 45.8x, was 6.0x — non-recurring Q1 confirmed)")
