import json
from pathlib import Path
rd = Path('reports/2026-06-07')

exp = json.loads((rd / 'expansion_stocks.json').read_text(encoding='utf-8'))
mom = json.loads((rd / 'price_momentum.json').read_text(encoding='utf-8'))
mom_map = {s['code']: s.get('close') for s in mom.get('all_momentum', [])}

print('Expansion stocks price coverage:')
for s in exp:
    code = s['code']
    existing = s.get('price')
    from_mom = mom_map.get(code)
    print(f'  {code} {s["name"]}: existing={existing}, momentum={from_mom}')

# Also check MOVERS/GAINERS structure
bwibbu = json.loads((rd / 'bwibbu_fresh.json').read_text(encoding='utf-8'))
print(f'\nbwibbu_fresh keys: {list(bwibbu.keys())[:5]}')
if isinstance(bwibbu, list):
    print(f'  bwibbu is a list of {len(bwibbu)}')
    print(f'  sample: {bwibbu[0]}')
elif isinstance(bwibbu, dict):
    for k,v in bwibbu.items():
        if isinstance(v, list) and len(v) > 0:
            print(f'  {k}: list of {len(v)}, sample={v[0]}')
