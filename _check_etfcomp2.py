"""Check ETFCOMP structure properly (etfs is a list)."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

m = re.search(r'const ETFCOMP\s*=\s*(\{.*?\});', html, re.DOTALL)
if m:
    try:
        etfc = json.loads(m.group(1))
        etfs = etfc.get('etfs', [])
        print(f'ETFCOMP: {etfc.get("etf_count")} ETFs, date={etfc.get("date")}')
        print(f'etfs is: {type(etfs).__name__} with {len(etfs)} items')
        for e in etfs:
            code = e.get('etf_code')
            name = e.get('etf_name')
            n = e.get('n_holdings')
            avg_grand = e.get('avg_grand')
            avg_dna = e.get('avg_dna_signals')
            holdings = e.get('holdings') or e.get('stocks') or []
            print(f'\n  {code} {name}: n_holdings={n}, avg_grand={avg_grand}, avg_dna={avg_dna}')
            print(f'    Holdings list len: {len(holdings)}')
            print(f'    Keys: {list(e.keys())}')
            if holdings:
                print(f'    Sample holding: {holdings[0]}')
    except Exception as e2:
        print(f'Parse error: {e2}')
        print(m.group(1)[:500])
else:
    print('ETFCOMP not found')
