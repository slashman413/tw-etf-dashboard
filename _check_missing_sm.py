import json
from pathlib import Path

sm = json.loads(open('series_map.json', encoding='utf-8').read())
gu = json.loads(open('reports/2026-06-07/grand_unified.json', encoding='utf-8').read())

all_codes = [r['code'] for r in gu['all_ranked']]
print(f"Dashboard stocks: {len(all_codes)}")
print(f"series_map stocks: {len(sm)}")

missing = []
low_data = []
for code in all_codes:
    s = sm.get(code)
    if not s or not s.get('d'):
        missing.append(code)
    elif len(s['d']) < 25:
        low_data.append((code, len(s['d'])))

print(f"\nMissing from series_map ({len(missing)}): {missing}")
print(f"\nToo few data points (<25) ({len(low_data)}): {low_data}")

# Also check GAINERS/MOVERS if stored separately
comp = json.loads(open('reports/2026-06-07/composite_data.json', encoding='utf-8').read())
exp  = json.loads(open('reports/2026-06-07/expansion_stocks.json', encoding='utf-8').read())
all_dash_codes = set(r['code'] for r in comp) | set(r['code'] for r in exp)
print(f"\nAll dashboard codes: {len(all_dash_codes)}")
missing2 = [c for c in all_dash_codes if c not in sm or not sm[c].get('d') or len(sm[c]['d']) < 25]
print(f"Missing/low from series_map: {sorted(missing2)}")
