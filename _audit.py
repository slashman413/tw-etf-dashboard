import json, re
from pathlib import Path
from datetime import datetime
from collections import Counter

rd = Path('reports/2026-06-07')

print('=== 1. composite_data Integrity ===')
comp = json.loads((rd / 'composite_data.json').read_text(encoding='utf-8'))
print(f'Stocks: {len(comp)}')
no_price  = [s['code'] for s in comp if not s.get('price')]
no_score  = [s['code'] for s in comp if s.get('score') is None]
no_verdict= [s['code'] for s in comp if not s.get('verdict')]
print(f'Missing price: {no_price or "none"}')
print(f'Missing score: {no_score or "none"}')
print(f'Missing verdict: {no_verdict or "none"}')
verdicts = Counter(s.get('verdict','?') for s in comp)
for v,n in sorted(verdicts.items(), key=lambda x:-x[1]):
    print(f'  {v}: {n}')
scores = [s['score'] for s in comp if s.get('score') is not None]
if scores:
    print(f'Score range: {min(scores)}–{max(scores)}, avg={sum(scores)/len(scores):.1f}')

print('\n=== 2. Expansion stocks (effective prices via mom_price_map) ===')
exp = json.loads((rd / 'expansion_stocks.json').read_text(encoding='utf-8'))
mom = json.loads((rd / 'price_momentum.json').read_text(encoding='utf-8'))
mom_map = {s['code']: s.get('close') for s in mom.get('all_momentum', [])}
# Effective price = s.price OR mom_map (same logic as build_dashboard.py)
no_effective_price = [(s['code'], s['name']) for s in exp
                      if not s.get('price') and not mom_map.get(s['code'])]
has_effective_price = [(s['code'], s['name']) for s in exp
                       if s.get('price') or mom_map.get(s['code'])]
print(f'Expansion stocks with effective price: {len(has_effective_price)}/{len(exp)}')
print(f'No price anywhere (known limitation): {[(c,n) for c,n in no_effective_price] or "none"}')

print('\n=== 3. series_map Coverage ===')
sm = json.loads(open('series_map.json', encoding='utf-8').read())
all_codes = [s['code'] for s in comp] + [s['code'] for s in exp]
missing = [c for c in all_codes if c not in sm or not sm[c].get('d') or len(sm[c]['d']) < 10]
print(f'series_map: {len(sm)} | dashboard: {len(all_codes)} | missing: {missing or "none"}')
stale = [(c, sm[c]['d'][-1][0]) for c in all_codes if c in sm and sm[c].get('d') and
         (datetime.now() - datetime.strptime(sm[c]['d'][-1][0], '%Y-%m-%d')).days > 7]
print(f'Stale K-line (>7d): {stale or "none"}')

print('\n=== 4. DNA Full Market ===')
dna = json.loads((rd / 'dna_full_market.json').read_text(encoding='utf-8'))
results = dna.get('all_results', [])
print(f'Stocks scanned: {len(results)} | Bull count: {dna.get("bull_count",0)} | Date: {dna.get("data_date")}')
bull3 = [r for r in results if r.get('bull_signs', 0) >= 3]
print(f'Bull signs >=3: {len(bull3)}')

print('\n=== 5. build_dashboard.py SyntaxWarnings ===')
src = open('build_dashboard.py', encoding='utf-8').read()
# Find invalid escape sequences in non-raw strings
bad_escapes = re.findall(r'(?<!r)"[^"]*\\d[^"]*"', src)
print(f'Lines with \\d in string: {len(bad_escapes)} occurrences (non-critical, Python warning only)')

print('\n=== 6. Overview verdicts match ===')
# initOverview filters for STRONG BUY, BUY, WATCH⚠ — verify those exist
valid_verdicts = {'STRONG BUY', 'BUY', 'WATCH⚠', 'HOLD', 'REDUCE'}
actual = set(s.get('verdict','') for s in comp)
print(f'Composite verdicts: {actual}')
print(f'Overview filter covers: {actual & {"STRONG BUY","BUY","WATCH⚠"}}')
