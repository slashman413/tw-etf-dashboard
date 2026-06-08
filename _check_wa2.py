"""Check WATCHALERTS sub-arrays."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

m = re.search(r'const WATCHALERTS\s*=\s*(\{.*?\});', html, re.DOTALL)
wa = json.loads(m.group(1))

print(f'WATCHALERTS date={wa.get("date")}')
for k in ['almost_triple', 'dna_5of6', 'ma_crossing', 'near_52w_high', 'triple_upside']:
    items = wa.get(k, [])
    print(f'  {k}: {len(items)} items')
    if items:
        print(f'    Sample: {items[0]}')

summary = wa.get('summary', {})
print(f'\nSummary: {summary}')

# Check per-stock report data (STOCKREPORTS or TRIPLEREPORTS)
from pathlib import Path
rd = Path('reports/2026-06-07')
tr = json.loads((rd / 'triple_reports.json').read_text(encoding='utf-8'))
print(f'\ntriple_reports keys: {list(tr.keys())[:5]}')
if isinstance(tr, list):
    print(f'  List of {len(tr)} items')
    if tr:
        print(f'  Sample keys: {list(tr[0].keys())}')
elif isinstance(tr, dict):
    print(f'  Dict with {len(tr)} keys')
    # Check a few
    for k in list(tr.keys())[:3]:
        print(f'  {k}: {str(tr[k])[:100]}')
