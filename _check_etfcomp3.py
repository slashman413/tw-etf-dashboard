"""Check top_holdings and all_holdings in ETFCOMP."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

m = re.search(r'const ETFCOMP\s*=\s*(\{.*?\});', html, re.DOTALL)
if not m:
    print('ETFCOMP not found')
    exit()

etfc = json.loads(m.group(1))
etfs = etfc.get('etfs', [])

for e in etfs:
    code = e.get('etf_code')
    top = e.get('top_holdings', [])
    all_h = e.get('all_holdings', [])
    print(f'\n{code}: n_holdings={e.get("n_holdings")}, top_holdings={len(top)}, all_holdings={len(all_h)}')
    print(f'  triple={e.get("triple_holdings")}, sbuy={e.get("strongbuy_holdings")}, buy={e.get("buy_holdings")}')
    print(f'  rating={e.get("rating")}')
    if top:
        print(f'  top_holdings sample: {top[0]}')
    elif all_h:
        print(f'  all_holdings sample: {all_h[0]}')
