import json
from pathlib import Path
rd = Path('reports/2026-06-07')

mom = json.loads((rd / 'price_momentum.json').read_text(encoding='utf-8'))
for s in mom.get('all_momentum', []):
    if s.get('code') == '6488':
        print(f'6488 in price_momentum: {s}')
        break

bwibbu = json.loads((rd / 'bwibbu_fresh.json').read_text(encoding='utf-8'))
for s in bwibbu.get('all_refreshed', []):
    if s.get('code') == '6488':
        print(f'6488 in bwibbu_fresh: {s}')
        break

exp = json.loads((rd / 'expansion_stocks.json').read_text(encoding='utf-8'))
for s in exp:
    if s.get('code') == '6488':
        print(f'6488 in expansion_stocks: {s}')
        break
