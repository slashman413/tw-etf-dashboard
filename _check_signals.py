"""Quick check of action signals and conviction matrix."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

# Action signal
act = json.loads((rd / 'action_signal.json').read_text(encoding='utf-8'))
print(f'=== action_signal ===')
print(f'Date: {act.get("date")}, generated: {act.get("generated")}')
buys = act.get('buy', []) or act.get('buys', [])
sells = act.get('sell', []) or act.get('sells', [])
signals = act.get('signals', []) or act.get('all_signals', [])
if signals:
    from collections import Counter
    actions = Counter(s.get('action','?') for s in signals)
    print(f'Signals: {dict(actions)}')
    buys = [s for s in signals if s.get('action') in ('STRONG BUY','BUY')]
    print(f'BUY signals: {len(buys)}')
    if buys:
        print(f'  Top buys: {[(s.get("code"), s.get("action")) for s in buys[:5]]}')
else:
    print(f'Keys: {list(act.keys())}')
    for k, v in act.items():
        if isinstance(v, list):
            print(f'  {k}: {len(v)} items')

# Conviction matrix
conv = json.loads((rd / 'conviction_data.json').read_text(encoding='utf-8'))
print(f'\n=== conviction_data ===')
print(f'Keys: {list(conv.keys())[:8]}')
if 'matrix' in conv:
    m = conv['matrix']
    print(f'Matrix type: {type(m).__name__}')
    if isinstance(m, list):
        print(f'  {len(m)} items, sample: {m[0] if m else None}')
elif 'all_stocks' in conv:
    all_s = conv['all_stocks']
    print(f'all_stocks: {len(all_s)} items')
    if all_s:
        print(f'  Sample keys: {list(all_s[0].keys())}')

# Smart money
sm = json.loads((rd / 'smart_money_confluence.json').read_text(encoding='utf-8'))
print(f'\n=== smart_money ===')
print(f'Keys: {list(sm.keys())[:8]}')
top = sm.get('top_picks') or sm.get('confluence_picks') or []
print(f'Top picks: {len(top)}')
if top:
    print(f'  {[(s.get("code"), s.get("name")) for s in top[:5]]}')
