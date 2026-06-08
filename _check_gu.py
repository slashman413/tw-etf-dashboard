"""Check grand_unified top ranked stocks."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

gu = json.loads((rd / 'grand_unified.json').read_text(encoding='utf-8'))
print('grand_unified keys:', list(gu.keys())[:8])
print('Generated:', gu.get('generated'))
all_r = gu.get('all_ranked', [])
print('Total ranked:', len(all_r))

print('\nTop 10 by grand score:')
for s in all_r[:10]:
    code = s.get('code')
    name = s.get('name')
    grand = s.get('grand')
    final = s.get('final')
    bull = s.get('bull_signs')
    print(f'  {code} {name}: grand={grand}, final={final}, bull_signs={bull}')

# Check distribution of ratings
from collections import Counter
ratings = Counter(s.get('final', '?').split()[1] if s.get('final') else '?' for s in all_r)
print('\nRating distribution:')
for r, n in sorted(ratings.items(), key=lambda x: -x[1]):
    print(f'  {r}: {n}')
