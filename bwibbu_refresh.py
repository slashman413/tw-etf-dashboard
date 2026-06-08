#!/usr/bin/env python3
"""
Iteration 25b: BWIBBU_ALL Valuation Refresh (corrected field names)
Fields: Code, PEratio, DividendYield, PBratio
Data date: ROC 1150604 = 2026-06-04 (yesterday's close)
Waits 130s before calling to respect IP-ban constraint.
"""

import json, ssl, time, urllib.request, sys
from pathlib import Path
from datetime import datetime

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 0 if "--skip-wait" in sys.argv else 130

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

composite = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
expansion = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
name_map  = {**{s["code"]: s["name"] for s in composite},
             **{s["code"]: s["name"] for s in expansion}}
all_codes = set(name_map.keys())
prior_comp = {s["code"]: s for s in composite}

# Prior financial lookup from expansion
fin_codes = {s["code"] for s in expansion if s.get("is_fin")}

print(f"⏳ Waiting {WAIT_SEC}s before BWIBBU_ALL call (IP-ban guard)…", flush=True)
time.sleep(WAIT_SEC)

print("Fetching BWIBBU_ALL…", flush=True)
bwi_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
print(f"Got {len(bwi_raw)} rows | Data date: {bwi_raw[0].get('Date','?') if bwi_raw else 'N/A'}")

def sf(v):
    if v is None: return None
    s = str(v).replace(",","").strip()
    try: return float(s) if s else None
    except: return None

bwi_map = {r["Code"]: r for r in bwi_raw if r.get("Code")}

refreshed = []
for code in sorted(all_codes):
    r    = bwi_map.get(code, {})
    if not r: continue
    prior = prior_comp.get(code, {})
    is_fin = code in fin_codes

    pe_new  = sf(r.get("PEratio"))
    div_new = sf(r.get("DividendYield"))
    pb_new  = sf(r.get("PBratio"))
    pe_old  = sf(prior.get("fwd_pe"))
    div_old = sf(prior.get("div_yield"))
    pb_old  = sf(prior.get("pb"))

    if pe_new is None and pb_new is None and div_new is None:
        continue

    delta_pe  = round(pe_new  - pe_old,  2) if pe_new  is not None and pe_old  is not None else None
    delta_div = round(div_new - div_old, 2) if div_new is not None and div_old is not None else None
    delta_pb  = round(pb_new  - pb_old,  2) if pb_new  is not None and pb_old  is not None else None

    # Re-score value dimension with new data
    v_pts = 0
    if is_fin:
        if pb_new and pb_new < 1.2: v_pts += 15
        elif pb_new and pb_new < 1.5: v_pts += 8
        if div_new and div_new >= 5: v_pts += 15
        elif div_new and div_new >= 4: v_pts += 10
        elif div_new and div_new >= 3: v_pts += 5
    else:
        if pe_new and pe_new < 15:   v_pts += 15
        elif pe_new and pe_new < 25: v_pts += 8
        if pb_new and pb_new < 1.5:  v_pts += 8
        elif pb_new and pb_new < 2.5: v_pts += 4
        if div_new and div_new >= 4:  v_pts += 7
        elif div_new and div_new >= 2: v_pts += 3

    prior_v = prior.get("v_pts", prior.get("score", 0) * 0.3)  # fallback estimate

    refreshed.append({
        "code": code,
        "name": name_map.get(code, code),
        "is_fin": is_fin,
        "pe_old": pe_old, "pe_new": pe_new, "delta_pe": delta_pe,
        "div_old": div_old, "div_new": div_new, "delta_div": delta_div,
        "pb_old": pb_old, "pb_new": pb_new, "delta_pb": delta_pb,
        "v_pts_new": v_pts,
        "score_old": prior.get("score"),
    })

print(f"Matched {len(refreshed)} stocks")

# ── Analysis ───────────────────────────────────────────────────────────────────
pe_changed   = [r for r in refreshed if r["delta_pe"] is not None]
div_changed  = [r for r in refreshed if r["delta_div"] is not None]
high_div     = sorted([r for r in refreshed if (r["div_new"] or 0) >= 4.5],
                      key=lambda x: x["div_new"] or 0, reverse=True)

pe_expanded   = sorted(pe_changed, key=lambda x: x["delta_pe"] or 0, reverse=True)[:5]
pe_contracted = sorted(pe_changed, key=lambda x: x["delta_pe"] or 0)[:5]
div_up        = sorted([r for r in div_changed if (r["delta_div"] or 0) > 0.1],
                       key=lambda x: x["delta_div"] or 0, reverse=True)[:5]
cheap_pe      = sorted([r for r in refreshed if r["pe_new"] and r["pe_new"] < 15 and not r["is_fin"]],
                       key=lambda x: x["pe_new"] or 999)[:8]

print("\n  Cheapest P/E (non-financial, <15x):")
for r in cheap_pe:
    print(f"    {r['code']} {r['name'][:6]}: P/E {r['pe_new']:.1f}x (prior {r['pe_old']:.1f}x)" if r['pe_old'] else
          f"    {r['code']} {r['name'][:6]}: P/E {r['pe_new']:.1f}x")

print(f"\n  High div yield (≥4.5%): {len(high_div)}")
for r in high_div[:8]:
    d = f" ({r['delta_div']:+.2f}%)" if r["delta_div"] else ""
    print(f"    {r['code']} {r['name'][:6]}: {r['div_new']:.2f}%{d}")

print("\n  P/E expansions (price rose vs earnings):")
for r in pe_expanded:
    print(f"    {r['code']} {r['name'][:6]}: {r['pe_old']:.1f}→{r['pe_new']:.1f}x ({r['delta_pe']:+.2f}x)")

print("\n  P/E contractions (earnings improved or price fell):")
for r in pe_contracted:
    print(f"    {r['code']} {r['name'][:6]}: {r['pe_old']:.1f}→{r['pe_new']:.1f}x ({r['delta_pe']:+.2f}x)")

# ── Save ──────────────────────────────────────────────────────────────────────
result = {
    "date": TODAY,
    "data_date": bwi_raw[0].get("Date","") if bwi_raw else "",
    "refresh_ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_matched": len(refreshed),
    "high_div_ge45": [{"code":r["code"],"name":r["name"].split()[0],
                       "div_new":r["div_new"],"div_old":r["div_old"]} for r in high_div],
    "cheap_pe_lt15": [{"code":r["code"],"name":r["name"].split()[0],
                       "pe_new":r["pe_new"],"pe_old":r["pe_old"]} for r in cheap_pe],
    "pe_expanded": [{"code":r["code"],"name":r["name"].split()[0],
                     "pe_old":r["pe_old"],"pe_new":r["pe_new"],"delta":r["delta_pe"]} for r in pe_expanded],
    "pe_contracted": [{"code":r["code"],"name":r["name"].split()[0],
                       "pe_old":r["pe_old"],"pe_new":r["pe_new"],"delta":r["delta_pe"]} for r in pe_contracted],
    "all_refreshed": refreshed,
}
(REPORT_DIR / "bwibbu_fresh.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

# ── BWIBBU_REFRESH.md ─────────────────────────────────────────────────────────
data_date_str = bwi_raw[0].get("Date","") if bwi_raw else ""

lines = [
    f"# BWIBBU Valuation Refresh — {TODAY} (Iteration 25)",
    f"*Market data date: {data_date_str} (ROC calendar) | Refreshed: {datetime.now().strftime('%H:%M')}*",
    f"*Source: TWSE BWIBBU_ALL | {len(refreshed)} stocks matched*",
    "",
    "---",
    "",
    "## Cheapest Non-Financial Stocks (Fwd P/E < 15x)",
    "",
    "| Code | Name | P/E Now | P/E Prior | Change | Div% | Score |",
    "|------|------|---------|----------|--------|------|-------|",
]

for r in cheap_pe:
    pe_chg = f"{r['delta_pe']:+.2f}x" if r["delta_pe"] is not None else "—"
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | **{r['pe_new']:.1f}x** | "
        f"{r['pe_old']:.1f}x | {pe_chg} | "
        f"{r['div_new']:.2f}% | "
        f"{r['score_old'] if r['score_old'] else '—'} |"
    )

lines += [
    "",
    "## High Dividend Yield (≥4.5%)",
    "",
    "| Code | Name | Div% Now | Div% Prior | Change | P/E | P/B |",
    "|------|------|----------|-----------|--------|-----|-----|",
]
for r in high_div[:12]:
    chg = f"{r['delta_div']:+.2f}%" if r["delta_div"] is not None else "—"
    div_old_str = f"{r['div_old']:.2f}%" if r['div_old'] is not None else "—%"
    lines.append(
        f"| **{r['code']}** | {r['name'].split()[0]} | **{r['div_new']:.2f}%** | "
        f"{div_old_str} | {chg} | "
        f"{r['pe_new']:.1f}x | "
        f"{r['pb_new']:.2f}x |"
    )

lines += [
    "",
    "## P/E Changes vs Prior Analysis",
    "",
    "### Expansions (price rose faster than earnings justified)",
    "",
    "| Code | Name | Old P/E | New P/E | Δ |",
    "|------|------|---------|---------|---|",
]
for r in pe_expanded:
    lines.append(f"| **{r['code']}** | {r['name'].split()[0]} | {r['pe_old']:.1f}x | **{r['pe_new']:.1f}x** | **+{r['delta_pe']:.2f}x** |")

lines += [
    "",
    "### Contractions (earnings improved or price fell — potential value)",
    "",
    "| Code | Name | Old P/E | New P/E | Δ |",
    "|------|------|---------|---------|---|",
]
for r in pe_contracted:
    lines.append(f"| **{r['code']}** | {r['name'].split()[0]} | {r['pe_old']:.1f}x | **{r['pe_new']:.1f}x** | **{r['delta_pe']:.2f}x** |")

lines += [
    "",
    "---",
    "",
    "## Interpretation",
    "",
    "- **P/E expansion**: stock price has risen relative to earnings — valuation stretched",
    "- **P/E contraction**: potential value opportunity if fundamentals are intact",
    "- **High div + low P/E**: classic income+value combination (watch for dividend safety)",
    "",
    f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Iteration 25*",
]

(REPORT_DIR / "BWIBBU_REFRESH.md").write_text("\n".join(lines), encoding="utf-8")
print(f"\n✓ BWIBBU_REFRESH.md + bwibbu_fresh.json")
print(f"  High div (≥4.5%): {len(high_div)} stocks")
print(f"  Cheap P/E (<15x non-fin): {len(cheap_pe)} stocks")
