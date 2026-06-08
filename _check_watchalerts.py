"""Check watchlist alerts and screener data quality."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

# Check WATCHALERTS
m = re.search(r'const WATCHALERTS\s*=\s*(\{.*?\});', html, re.DOTALL)
if m:
    wa = json.loads(m.group(1))
    print(f'WATCHALERTS keys: {list(wa.keys())}')
    alerts = wa.get('alerts', [])
    print(f'Total alerts: {len(alerts)}')
    if alerts:
        print(f'Sample: {alerts[0]}')
        # Count by type
        from collections import Counter
        types = Counter(a.get('type','?') for a in alerts)
        for t, n in sorted(types.items(), key=lambda x: -x[1]):
            print(f'  {t}: {n}')
else:
    print('WATCHALERTS: not found or not parseable as simple JSON')

# Check FULLMKT for screener data
m2 = re.search(r'const FULLMKT\s*=\s*(\{)', html)
if m2:
    start = m2.start(1)
    snippet = html[start:start+400]
    print(f'\nFULLMKT snippet: {snippet[:300]}')

# Check that full market page stocks list is correct
from pathlib import Path
rd = Path('reports/2026-06-07')
fm = json.loads((rd / 'full_market.json').read_text(encoding='utf-8'))
print(f'\nfull_market.json: total_listed={fm.get("total_listed")}, total_otc={fm.get("total_otc")}, total={fm.get("total")}')
sectors = fm.get('sector_summary', [])
print(f'Sectors: {len(sectors)}')
print('Top 5 sectors by count:')
for s in sorted(sectors, key=lambda x: -x.get('count', 0))[:5]:
    print(f'  {s.get("sector")}: {s.get("count")} stocks, median_grand={s.get("median_grand")}')
