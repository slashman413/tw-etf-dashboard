#!/usr/bin/env python3
"""
Extend quarterly_financials.json with OTC companies from full_market.json.
OTC data was fetched from TPEX t187ap06_O_ci (Q1 2026 income statements).
No API calls — pure data merge.
"""
import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

qf = json.loads((REPORT_DIR / "quarterly_financials.json").read_text(encoding="utf-8"))
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))

existing_codes = {c["code"] for c in qf["companies"]}
otc_companies  = [c for c in fm["companies"] if c.get("market") == "OTC"]

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

added = 0
for c in otc_companies:
    code = c.get("code","")
    if code in existing_codes:
        continue  # skip if already listed (shouldn't happen for OTC)

    rev  = sf(c.get("revenue_q1"))
    op   = sf(c.get("op_income_q1"))
    net  = sf(c.get("net_income_q1"))
    eps  = sf(c.get("eps_q1"))
    gm   = sf(c.get("gross_margin"))
    om   = sf(c.get("op_margin"))
    nm   = sf(c.get("net_margin"))

    # Compute gross_profit from gross_margin and revenue
    gross_profit = round(rev * gm / 100, 0) if rev and gm else None

    entry = {
        "code":         code,
        "name":         c.get("name",""),
        "market":       "OTC",
        "year":         "115",
        "quarter":      "1",
        "revenue":      rev,
        "gross_profit": gross_profit,
        "op_income":    op,
        "pretax":       None,  # not separately available from t187ap14_O
        "net_income":   net,
        "eps":          eps,
        "gross_margin": gm,
        "op_margin":    om,
        "net_margin":   nm,
    }
    qf["companies"].append(entry)
    added += 1

# Mark TSE companies too
for c in qf["companies"]:
    if "market" not in c:
        c["market"] = "TSE"

qf["generated"]       = datetime.now().strftime("%Y-%m-%d %H:%M")
qf["total_companies"] = len(qf["companies"])
qf["otc_added"]       = added
qf["income_sources"]  = (qf.get("income_sources","") or "") + " + TPEX t187ap06_O_ci (OTC)"

# Summary
with_eps = sum(1 for c in qf["companies"] if c.get("eps") is not None)
pos_eps  = sum(1 for c in qf["companies"] if (c.get("eps") or 0) > 0)
print(f"TSE companies:    {len(existing_codes)}")
print(f"OTC added:        {added}")
print(f"Total:            {len(qf['companies'])}")
print(f"With Q1 EPS:      {with_eps}")
print(f"Profitable (EPS>0): {pos_eps}")

# Top 20 by EPS across all markets
top_eps = sorted([c for c in qf["companies"] if c.get("eps") is not None],
                 key=lambda x: -(x["eps"] or 0))[:20]
print("\nTop 20 Q1 EPS (all markets):")
for c in top_eps:
    mkt = c.get("market","?")
    print(f"  {c['code']} {c.get('name','?')[:10]:<12} [{mkt}] eps={c['eps']:.2f} gm={c.get('gross_margin','—')}")

(REPORT_DIR / "quarterly_financials.json").write_text(
    json.dumps(qf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✅ Saved {REPORT_DIR}/quarterly_financials.json ({len(qf['companies'])} companies)")
