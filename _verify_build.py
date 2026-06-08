"""Verify the built dashboard.html has prices for expansion stocks."""
import json, re

html = open('dashboard.html', encoding='utf-8').read()
# Find STOCKS JSON in the dashboard
m = re.search(r'const STOCKS\s*=\s*(\[.*?\]);', html, re.DOTALL)
if not m:
    print("ERROR: STOCKS not found in dashboard.html")
    exit(1)

stocks = json.loads(m.group(1))
print(f"STOCKS in dashboard: {len(stocks)}")

expansion_codes = ['1590','2912','4904','2880','3231','2383','6743','2344','3481','2049']
print("\nExpansion stock prices in dashboard:")
for s in stocks:
    if s['code'] in expansion_codes:
        print(f"  {s['code']} {s['name']}: price={s.get('price')}, score={s.get('score')}, verdict={s.get('verdict')}")

# Check verdict distribution
from collections import Counter
verdicts = Counter(s.get('verdict','?') for s in stocks)
print(f"\nVerdict distribution:")
for v, n in sorted(verdicts.items(), key=lambda x: -x[1]):
    print(f"  {v}: {n}")

# Check overview picks
picks = [s for s in stocks if s.get('verdict') in ('STRONG BUY','BUY','WATCH⚠') and s.get('score') is not None]
picks.sort(key=lambda x: -(x.get('score') or 0))
print(f"\nOverview picks ({len(picks)} total, showing top 5):")
for s in picks[:5]:
    print(f"  {s['code']} {s['name']}: score={s['score']}, price={s.get('price')}")
