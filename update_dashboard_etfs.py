#!/usr/bin/env python3
"""
Inject the 19-ETF comparison data into dashboard.html ETFCOMP constant.
"""
import json, re
from pathlib import Path
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
RPT = Path("reports") / TODAY

# Load the 19-ETF comparison
with open(RPT / "etf_comparison.json", encoding="utf-8") as f:
    comp = json.load(f)

# Sort by avg_grand descending
comp["etfs"].sort(key=lambda e: -(e.get("avg_grand") or 0))
comp["etf_count"] = len(comp["etfs"])
comp["date"] = TODAY
comp["fetch_ts"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# For ETFs missing avg_dna_signals / avg_rs_60d / pct_above_ma, fill None
for e in comp["etfs"]:
    e.setdefault("avg_dna_signals", None)
    e.setdefault("avg_rs_60d", None)
    e.setdefault("pct_above_ma", None)

new_json = json.dumps(comp, ensure_ascii=False, separators=(",", ":"))
new_line = f"const ETFCOMP        = {new_json};"

# Read dashboard.html
dash = Path("dashboard.html")
content = dash.read_text(encoding="utf-8")

# Replace the ETFCOMP line
pattern = r"const ETFCOMP\s+=\s+\{[^\n]+\};"
if not re.search(pattern, content):
    print("ERROR: Could not find ETFCOMP pattern in dashboard.html")
    exit(1)

new_content = re.sub(pattern, new_line, content)
dash.write_text(new_content, encoding="utf-8")

n = len(comp["etfs"])
print(f"✅ dashboard.html updated with {n} ETFs")
print(f"   ETFs: {', '.join(e['etf_code'] for e in comp['etfs'])}")
print(f"   Top 3: {comp['etfs'][0]['etf_code']} ({comp['etfs'][0]['avg_grand']}) | "
      f"{comp['etfs'][1]['etf_code']} ({comp['etfs'][1]['avg_grand']}) | "
      f"{comp['etfs'][2]['etf_code']} ({comp['etfs'][2]['avg_grand']})")
