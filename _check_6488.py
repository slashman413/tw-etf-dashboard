import json
from pathlib import Path
rd = Path('reports/2026-06-07')

files_to_check = ['price_momentum.json', 'bwibbu_fresh.json', 'composite_data.json']
for fname in files_to_check:
    fp = rd / fname
    if not fp.exists():
        print(f'{fname}: not found')
        continue
    data = json.loads(fp.read_text(encoding='utf-8'))
    found = False
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get('code') == '6488':
                print(f'{fname}: 6488 found - {item}')
                found = True
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, dict) and item.get('code') == '6488':
                        print(f'{fname}[{k}]: 6488 found')
                        found = True
            elif k == '6488':
                print(f'{fname}: key 6488 found')
                found = True
    if not found:
        print(f'{fname}: 6488 NOT found')
