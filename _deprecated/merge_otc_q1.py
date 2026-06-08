#!/usr/bin/env python3
"""
Parse and merge TPEX OTC Q1 2026 financial data into full_market.json.
Uses data already fetched (stored in otc_q1_probe.json won't re-fetch).
Re-fetches from TPEX API since probe already ran.
Fields from TPEX t187ap14_O:
  SecuritiesCompanyCode, 基本每股盈餘, 營業收入, 營業利益, 稅後淨利
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
HEADERS = {"User-Agent": "Mozilla/5.0"}

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Merge TPEX OTC Q1 2026 ===")

# Re-fetch the TPEX data (was already fetched ~6 min ago, well within 132s reset)
print("  Fetching from TPEX...")
req = urllib.request.Request(
    "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap14_O",
    headers=HEADERS)
with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
    otc_raw = json.loads(r.read().decode("utf-8"))

print(f"  Got {len(otc_raw)} rows")
print(f"  Sample: {otc_raw[0]}")

# Load full_market.json
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}

# Parse and merge
updated = 0
eps_zero = 0
for row in otc_raw:
    code = str(row.get("SecuritiesCompanyCode", "")).strip()
    if not code or code not in otc_map:
        continue
    c = otc_map[code]

    eps = sf(row.get("基本每股盈餘"))
    rev = sf(row.get("營業收入"))
    op  = sf(row.get("營業利益"))
    net = sf(row.get("稅後淨利"))

    if eps is not None:
        c["eps_q1"] = eps
        updated += 1
        if eps == 0:
            eps_zero += 1
    if rev is not None:
        c["revenue_q1"] = rev
    if op is not None:
        c["op_income_q1"] = op
    if net is not None:
        c["net_income_q1"] = net

    # Compute net margin if we have rev
    if rev and rev > 0 and net is not None:
        c["net_margin"] = round(net / rev * 100, 2)
    if rev and rev > 0 and op is not None:
        c["op_margin"] = round(op / rev * 100, 2)

print(f"\n  OTC companies updated: {updated} / {len(otc_map)}")
print(f"  EPS = 0 (reported break-even): {eps_zero}")
print(f"  EPS > 0: {sum(1 for c in companies if c.get('market')=='OTC' and (c.get('eps_q1') or 0)>0)}")
print(f"  EPS < 0: {sum(1 for c in companies if c.get('market')=='OTC' and (c.get('eps_q1') or 0)<0)}")

# Update counts
fm["generated"]   = datetime.now().strftime("%Y-%m-%d %H:%M")
fm["q1_otc_count"] = updated

# Save
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ Saved: {REPORT_DIR}/full_market.json")

# Print top OTC EPS
top_otc = sorted(
    [c for c in companies if c.get("market") == "OTC" and c.get("eps_q1") is not None and c["eps_q1"] > 0],
    key=lambda x: -(x["eps_q1"] or 0))[:15]
print(f"\n  Top 15 OTC Q1 EPS:")
for c in top_otc:
    print(f"    {c['code']} {c.get('name','?')[:10]:<12} eps={c['eps_q1']:>8.2f}")

print(f"\n[{datetime.now():%H:%M:%S}] Done")
