"""Check ETFCOMP data in dashboard HTML."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

m = re.search(r'const ETFCOMP\s*=\s*(\{.*?\});', html, re.DOTALL)
if m:
    try:
        etfc = json.loads(m.group(1))
        print(f'ETFCOMP keys: {list(etfc.keys())}')
        etfs = etfc.get('etfs', {})
        print(f'ETFs: {list(etfs.keys())}')
        for code, info in etfs.items():
            print(f'\n{code}:')
            print(f'  stock_count={info.get("stock_count")}')
            print(f'  avg_eps_q1={info.get("avg_eps_q1")}, avg_pe={info.get("avg_pe")}')
            print(f'  avg_div_yield={info.get("avg_div_yield")}')
            print(f'  buy_count={info.get("buy_count")}, triple_confirmed={len(info.get("triple_confirmed", []))}')
            top_eps = info.get('top_eps', [])[:3]
            print(f'  top_eps: {[(s.get("code"), s.get("eps")) for s in top_eps]}')
    except Exception as e:
        print(f'Parse error: {e}')
        print(f'  snippet: {m.group(1)[:200]}')
else:
    print('ETFCOMP: not found in HTML')

# Check FULLMKT
m2 = re.search(r'const FULLMKT\s*=\s*(\{)', html)
if m2:
    start = m2.start(1)
    snippet = html[start:start+300]
    print(f'\nFULLMKT found: {snippet[:150]}')
    # Count stocks
    import re as _re
    count = len(_re.findall(r'"code":', html[start:start+5000000]))
    print(f'FULLMKT approximate stock count: {count}')
else:
    print('FULLMKT: not found')
