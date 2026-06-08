#!/usr/bin/env python3
"""
Recompute quick_score from scratch for ALL companies in full_market.json.
Eliminates double-counting from incremental updates.
Score components (max ~14):
  rev_yoy > 10: +2 | > 0: +1
  pe < 15:      +2 | < 25: +1
  pb < 1.5:     +1
  yield > 4:    +2 | > 2: +1
  eps_q1 > 2:   +2 | > 0: +1
  gross_margin > 50: +1
  op_margin > 15:    +1
"""
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]

for c in companies:
    score = 0
    ry  = sf(c.get("rev_yoy"))
    pe  = sf(c.get("pe"))
    pb  = sf(c.get("pb"))
    dy  = sf(c.get("yield"))
    eps = sf(c.get("eps_q1"))
    gm  = sf(c.get("gross_margin"))
    om  = sf(c.get("op_margin"))

    if ry is not None:
        if ry > 10:  score += 2
        elif ry > 0: score += 1

    if pe is not None and pe > 0:
        if pe < 15:   score += 2
        elif pe < 25: score += 1

    if pb is not None and 0 < pb < 1.5: score += 1
    if dy is not None:
        if dy > 4:   score += 2
        elif dy > 2: score += 1

    if eps is not None:
        if eps > 2:   score += 2
        elif eps > 0: score += 1

    if gm is not None and gm > 50: score += 1
    if om is not None and om > 15: score += 1

    c["quick_score"] = score

companies.sort(key=lambda x: -(x.get("quick_score") or 0))

# Stats
otc_scores = [c.get("quick_score",0) for c in companies if c.get("market")=="OTC"]
tse_scores = [c.get("quick_score",0) for c in companies if c.get("market")=="TSE"]
print(f"TSE: max={max(tse_scores)} mean={sum(tse_scores)/len(tse_scores):.1f} (n={len(tse_scores)})")
print(f"OTC: max={max(otc_scores)} mean={sum(otc_scores)/len(otc_scores):.1f} (n={len(otc_scores)})")

# Top 10 overall
top10 = sorted(companies, key=lambda x: -(x.get("quick_score") or 0))[:10]
print("\nTop 10 overall:")
for c in top10:
    code = c.get("code","")
    name = c.get("name","?")[:10]
    qs   = c.get("quick_score",0)
    mkt  = c.get("market","?")
    eps  = c.get("eps_q1")
    yoy  = c.get("rev_yoy")
    pe   = c.get("pe")
    dy   = c.get("yield")
    print(f"  {code} {name:<12} [{mkt}] score={qs} eps={eps} yoy={yoy} pe={pe} yield={dy}")

# OTC distribution
dist = Counter(otc_scores)
print("\nOTC distribution:")
for s in sorted(dist.keys(), reverse=True)[:8]:
    print(f"  {s:>3}: {dist[s]}")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n✅ Saved {REPORT_DIR}/full_market.json")
