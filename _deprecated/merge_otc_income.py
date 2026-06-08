#!/usr/bin/env python3
"""
Parse TPEX OTC Q1 2026 income statement (t187ap06_O_ci) into full_market.json.
Provides gross margin from 營業毛利（毛損）淨額 and full income statement.
Data already fetched in memory — re-use from TPEX API (no new call needed).
"""
import json, ssl, urllib.request
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def sf(v):
    if v is None: return None
    s = str(v).replace(",","").strip()
    if not s: return None
    try: return float(s)
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Merge OTC Income Statement (t187ap06_O_ci) ===")

req = urllib.request.Request(
    "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci",
    headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
    data = json.loads(r.read().decode("utf-8"))
print(f"  Got {len(data)} rows")

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}

updated = 0
for row in data:
    code = str(row.get("SecuritiesCompanyCode", "")).strip()
    if not code or code not in otc_map:
        continue
    c = otc_map[code]

    rev        = sf(row.get("營業收入"))
    cogs       = sf(row.get("營業成本"))
    gross_net  = sf(row.get("營業毛利（毛損）淨額"))
    op_inc     = sf(row.get("營業利益（損失）"))
    pretax     = sf(row.get("稅前淨利（淨損）"))
    net_inc    = sf(row.get("本期淨利（淨損）"))
    eps        = sf(row.get("基本每股盈餘（元）"))

    if rev is not None: c["revenue_q1"] = rev
    if cogs is not None: c["cogs_q1"] = cogs
    if op_inc is not None: c["op_income_q1"] = op_inc
    if net_inc is not None: c["net_income_q1"] = net_inc

    if eps is not None:
        c["eps_q1"] = eps

    # Compute margins
    if rev and rev > 0:
        if gross_net is not None:
            c["gross_margin"] = round(gross_net / rev * 100, 2)
        if op_inc is not None:
            c["op_margin"]    = round(op_inc / rev * 100, 2)
        if net_inc is not None:
            c["net_margin"]   = round(net_inc / rev * 100, 2)

    updated += 1

with_gross = sum(1 for c in companies if c.get("market") == "OTC" and c.get("gross_margin") is not None)
print(f"  Updated: {updated} | OTC with gross_margin: {with_gross}")

# Summary
pos_eps   = sum(1 for c in companies if c.get("market") == "OTC" and (c.get("eps_q1") or 0) > 0)
neg_eps   = sum(1 for c in companies if c.get("market") == "OTC" and (c.get("eps_q1") or 0) < 0)
with_gm   = sum(1 for c in companies if c.get("market") == "OTC" and c.get("gross_margin") is not None)
print(f"  OTC: {pos_eps} profit | {neg_eps} loss | {with_gm} have gross margin")

# Top 10 by gross margin (OTC, >100M revenue)
top_gm = sorted(
    [c for c in companies if c.get("market") == "OTC"
     and c.get("gross_margin") is not None and (c.get("revenue_q1") or 0) > 100000],
    key=lambda x: -(x["gross_margin"] or 0))[:10]
print(f"\n  Top OTC gross margin (rev>100M NTD):")
for c in top_gm:
    print(f"    {c['code']} {c.get('name','?')[:10]:<12} gm={c['gross_margin']:>6.1f}% eps={c.get('eps_q1') or '—'}")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ Saved: {REPORT_DIR}/full_market.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
