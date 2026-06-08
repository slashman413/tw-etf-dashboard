import json; from pathlib import Path; from datetime import datetime
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
files_to_check = [
    "sector_analysis.json","etf_comparison.json","peer_comparison.json",
    "score_sensitivity.json","action_signal.json","triple_reports.json",
    "monday_plan.json","premarket_checklist.json","watchlist_alerts.json",
    "grand_unified.json","bwibbu_fresh.json","price_momentum.json",
]
print(f"Report freshness — dir: {rd.name}")
for fn in files_to_check:
    p = rd / fn
    if not p.exists():
        print(f"  {fn:<36} MISSING")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    dt = d.get("date") or d.get("generated","")
    if dt and len(dt) > 10:
        dt = dt[:10]
    size = p.stat().st_size // 1024
    mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%H:%M")
    print(f"  {fn:<36} date={dt or '?':10} mod={mtime} {size}KB")
