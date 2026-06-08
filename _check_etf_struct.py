"""Inspect actual ETF 4Q report stock field names."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

etf4q = json.loads((rd / 'etf_4q_report.json').read_text(encoding='utf-8'))
etfs_data = etf4q.get('etfs', {})

# Full structure of one ETF
etf0050 = etfs_data.get('0050', {})
print('0050 keys:', list(etf0050.keys()))

top = etf0050.get('top_stocks') or etf0050.get('stocks') or []
if top:
    print(f'\nFirst stock keys: {list(top[0].keys())}')
    print(f'First stock data: {top[0]}')

# Check summary fields
for k in ['summary', 'financials', 'metrics', 'top_eps', 'strong_eps']:
    if k in etf0050:
        print(f'\n{k}: {str(etf0050[k])[:200]}')

# Check what 49/49 coverage means - look for eps-like fields
if top:
    eps_fields = [k for k in top[0].keys() if 'eps' in k.lower() or 'earn' in k.lower()]
    pe_fields = [k for k in top[0].keys() if 'pe' in k.lower() or 'ratio' in k.lower()]
    print(f'\nEPS-related fields: {eps_fields}')
    print(f'PE-related fields: {pe_fields}')
    print(f'First stock all fields:')
    for k, v in top[0].items():
        print(f'  {k}: {v}')
