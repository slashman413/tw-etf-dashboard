#!/usr/bin/env python3
"""
Update OTC quick_score in full_market.json using newly available Q1 EPS and margins.
Same logic as refresh_q1_eps.py: +2 if eps>2, +1 if eps>0, +1 if gross_margin>50.
"""
import json
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc = [c for c in companies if c.get("market") == "OTC"]

updated = 0
for c in otc:
    base_score = c.get("quick_score", 0) or 0
    eps  = c.get("eps_q1") or 0
    gm   = c.get("gross_margin") or 0
    op   = c.get("op_margin") or 0

    bonus = 0
    if eps > 2:  bonus += 2
    elif eps > 0: bonus += 1
    if gm > 50:   bonus += 1
    if op > 15:   bonus += 1

    c["quick_score"] = base_score + bonus
    if bonus > 0:
        updated += 1

# Re-sort
companies.sort(key=lambda x: -(x.get("quick_score") or 0))

scores_after = [c.get("quick_score", 0) for c in otc]
print(f"OTC updated: {updated} / {len(otc)}")
print(f"Score range after: {min(scores_after):.0f} – {max(scores_after):.0f}")

# Top 10 OTC by quick_score
top_otc = sorted(otc, key=lambda x: -(x.get("quick_score") or 0))[:10]
print("\nTop 10 OTC by quick_score:")
for c in top_otc:
    code = c["code"]
    name = c.get("name","?")[:10]
    qs   = c.get("quick_score", 0)
    eps  = c.get("eps_q1")
    gm   = c.get("gross_margin")
    pe   = c.get("pe")
    dy   = c.get("yield")
    print(f"  {code} {name:<12} score={qs} eps={eps} gm={gm} pe={pe} yield={dy}")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✅ Saved {REPORT_DIR}/full_market.json")
