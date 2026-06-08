"""Check triple-confirmed stocks have complete financial and technical data."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

# Get GRANDDATA triple_confirmed list
m = re.search(r'const GRANDDATA\s*=\s*(\{.*?\});', html, re.DOTALL)
gd = json.loads(m.group(1))
triple = gd.get('triple_confirmed', [])
strong = gd.get('strong_buy', [])
print(f'Triple confirmed: {[s.get("code") for s in triple]}')
print(f'Strong buy: {[s.get("code") for s in strong]}')

# Check each triple against STOCKS
m2 = re.search(r'const STOCKS\s*=\s*(\[.*?\]);', html, re.DOTALL)
stocks = json.loads(m2.group(1))
stocks_map = {s['code']: s for s in stocks}

print('\n=== Triple Confirmed Detail ===')
for s in triple:
    code = s.get('code')
    st = stocks_map.get(code, {})
    print(f'\n{code} {s.get("name")}:')
    print(f'  grand={s.get("grand")}, bull_signs={s.get("bull_signs")}, verdict={s.get("verdict")}')
    print(f'  STOCKS: price={st.get("price")}, score={st.get("score")}, verdict={st.get("verdict")}')
    print(f'  financial: pe={s.get("pe")}, eps_q1={s.get("eps_q1")}, div={s.get("div_yield")}')

# Get series_map coverage for triple stocks
sm = json.loads(open('series_map.json', encoding='utf-8').read())
print('\n=== K-line coverage for top picks ===')
top_codes = [s.get('code') for s in triple + strong]
for code in top_codes:
    if code in sm and sm[code].get('d'):
        last = sm[code]['d'][-1]
        print(f'  {code}: {len(sm[code]["d"])} bars, last={last[0]}, close={last[2]}')
    else:
        print(f'  {code}: NO K-LINE DATA')
