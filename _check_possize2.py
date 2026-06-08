"""Check actual position fields."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

ps = json.loads((rd / 'position_sizing.json').read_text(encoding='utf-8'))
positions = ps.get('positions', [])
if positions:
    print(f'Sample position keys: {list(positions[0].keys())}')
    # Find TRIPLE stocks
    triple_codes = ['2883','2887','2882','2881']
    for p in positions:
        if p.get('code') in triple_codes:
            print(f'\n{p.get("code")} {p.get("name")}:')
            for k, v in p.items():
                if v is not None:
                    print(f'  {k}: {v}')

# Check portfolio_summary
summary = ps.get('portfolio_summary', {})
print(f'\nPortfolio summary: {summary}')

# Check core/investable
core = ps.get('core', [])
print(f'\nCore positions: {len(core)}')
if core:
    print(f'Sample: {core[0]}')
