"""Inspect triple report nested structure."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

tr = json.loads((rd / 'triple_reports.json').read_text(encoding='utf-8'))
# Look at first report in detail
rpt = tr['reports'][0]
code = rpt.get('code')
print(f'{code} {rpt.get("name")} - full structure:')
print(f'  grand_total: {rpt.get("grand_total")}')
print(f'  final: {rpt.get("final")}')
print(f'  bull_signs: {rpt.get("bull_signs")}')

for field in ['score_breakdown', 'valuation', 'momentum', 'relative_strength']:
    val = rpt.get(field)
    if val:
        print(f'\n  {field}: {json.dumps(val, ensure_ascii=False)[:200]}')
    else:
        print(f'\n  {field}: None')

thesis = rpt.get('thesis')
if thesis:
    print(f'\n  thesis: {str(thesis)[:300]}')

# Check if it's referenced in dashboard
import re
html = open('dashboard.html', encoding='utf-8').read()
m = re.search(r'const TRIPLEREPORTS\s*=\s*(\{|\[)', html)
if m:
    start = m.start(1)
    print(f'\nTRIPLEREPORTS in HTML: found at char {start}')
    snippet = html[start:start+300]
    print(f'Snippet: {snippet[:200]}')
else:
    print('\nTRIPLEREPORTS: not in HTML')
