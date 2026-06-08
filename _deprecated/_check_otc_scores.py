#!/usr/bin/env python3
import json; from pathlib import Path
_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d/"grand_unified.json").exists()], reverse=True)
REPORT_DIR = _dirs[0]
fm = json.loads((REPORT_DIR/"full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc = [c for c in companies if c.get("market") == "OTC"]
scores = [c.get("quick_score") for c in otc if c.get("quick_score") is not None]
no_score = sum(1 for c in otc if c.get("quick_score") is None)
print(f"OTC with quick_score: {len(scores)} | without: {no_score}")
if scores:
    print(f"Score range: {min(scores):.0f} - {max(scores):.0f}")
for c in otc[:3]:
    code = c["code"]
    name = c.get("name","?")[:10]
    qs   = c.get("quick_score")
    eps  = c.get("eps_q1")
    gm   = c.get("gross_margin")
    pe   = c.get("pe")
    print(f"  {code} {name}: quick={qs} eps={eps} gm={gm} pe={pe}")
