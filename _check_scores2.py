#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
REPORT_DIR = _dirs[0]
fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc = [c for c in companies if c.get("market") == "OTC"]
scores = sorted([c.get("quick_score", 0) or 0 for c in otc], reverse=True)
dist = Counter(scores)
print("OTC quick_score distribution (top 10 values):")
for score, cnt in sorted(dist.items(), reverse=True)[:12]:
    print(f"  {score:>3}: {cnt} companies")
print(f"Max: {max(scores)} | Mean: {sum(scores)/len(scores):.1f}")
top5 = sorted(otc, key=lambda x: -(x.get("quick_score") or 0))[:5]
print("\nTop 5 OTC by score:")
for c in top5:
    code = c.get("code","?")
    name = c.get("name","?")[:10]
    qs   = c.get("quick_score")
    eps  = c.get("eps_q1")
    yoy  = c.get("rev_yoy")
    pe   = c.get("pe")
    print(f"  {code} {name:<12} score={qs} eps={eps} yoy={yoy} pe={pe}")

# Check listed too for comparison
listed = [c for c in companies if c.get("market") == "TSE"]
lscores = [c.get("quick_score", 0) or 0 for c in listed]
print(f"\nTSE quick_score: max={max(lscores)} mean={sum(lscores)/len(lscores):.1f}")
