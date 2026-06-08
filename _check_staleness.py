import json, os
from pathlib import Path
from datetime import datetime

rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
files_to_check = [
    "portfolio_data.json", "risk_data.json", "price_targets.json",
    "dividend_sustainability.json", "conviction_data.json",
    "etf_rebalance.json", "sector_analysis.json", "scenario_analysis.json",
    "peer_comparison.json", "earnings_quality.json", "margin_data.json",
    "composite_data.json", "april_revenue.json", "may_preview.json",
]
for fname in files_to_check:
    p = rd / fname
    if p.exists():
        mtime = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M")
        sz = p.stat().st_size // 1024
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            date_val = d.get("date") or d.get("generated") or d.get("fetch_ts") or "?"
            if isinstance(date_val, list):
                date_val = str(date_val[0])[:16]
        except Exception:
            date_val = "?"
        print(f"{fname:<38} mtime={mtime} {sz:>4}KB date={str(date_val)[:16]}")
    else:
        print(f"{fname:<38} MISSING")
