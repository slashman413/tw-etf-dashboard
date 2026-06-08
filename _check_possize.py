"""Check position sizing methodology."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

ps = json.loads((rd / 'position_sizing.json').read_text(encoding='utf-8'))
print('position_sizing keys:', list(ps.keys())[:10])
print('Method:', ps.get('method') or ps.get('methodology'))
print('Total portfolio:', ps.get('total_portfolio') or ps.get('portfolio_value'))

stocks = ps.get('stocks') or ps.get('positions') or ps.get('all_positions') or []
if isinstance(stocks, list) and stocks:
    print(f'\nTop positions ({len(stocks)} total):')
    for s in sorted(stocks, key=lambda x: -(x.get('weight') or x.get('pct') or 0))[:10]:
        code = s.get('code')
        name = s.get('name', '')
        w = s.get('weight') or s.get('pct') or s.get('position_pct')
        print(f'  {code} {name}: {w}%')
elif isinstance(stocks, dict):
    print('stocks is dict, sample keys:', list(stocks.keys())[:5])

# Check methodology notes
for k in ['notes', 'methodology', 'basis', 'max_position', 'min_position', 'risk_per_trade']:
    if k in ps:
        print(f'\n{k}: {ps[k]}')
