"""Check dashboard.html for key data objects and correct structure."""
import json, re, os

html = open('dashboard.html', encoding='utf-8').read()

checks = [
    ('STOCKS', r'const STOCKS\s*=\s*\['),
    ('DNA_FULLMKT', r'const DNA_FULLMKT\s*=\s*\{'),
    ('SERIES_MAP', r'const SERIES_MAP\s*=\s*\{'),
    ('GRAND_UNIFIED', r'const GRAND_UNIFIED\s*=\s*\{'),
    ('WATCHALERTS', r'const WATCHALERTS\s*=\s*\{'),
    ('bbModal', r'id="bbModal"'),
    ('bbChartEl', r'id="bbChartEl"'),
    ('showBBChart', r'function showBBChart'),
    ('DNA_FULLMKT.all_results', r'DNA_FULLMKT\.all_results'),
    ('ECharts', r'echarts\.init'),
]
print('=== HTML Object Checks ===')
for name, pat in checks:
    found = bool(re.search(pat, html))
    print(f'  {name}: {"OK" if found else "MISSING !!"}')

print(f'\ndashboard.html: {os.path.getsize("dashboard.html")//1024} KB')
print(f'series_map.json: {os.path.getsize("series_map.json")//1024} KB')

# Check GRAND_UNIFIED data
m = re.search(r'const GRAND_UNIFIED\s*=\s*(\{.*?\});', html, re.DOTALL)
if m:
    try:
        gu = json.loads(m.group(1))
        print(f'\n=== GRAND_UNIFIED ===')
        print(f'  Keys: {list(gu.keys())[:5]}')
        tc = gu.get('triple_confirmed', [])
        sb = gu.get('strong_buy', [])
        print(f'  triple_confirmed: {len(tc)} stocks')
        print(f'  strong_buy: {len(sb)} stocks')
        if tc:
            print(f'  Top triple: {[s.get("code") for s in tc[:3]]}')
    except Exception as e:
        print(f'  Parse error: {e}')

# Check STOCKS data
m = re.search(r'const STOCKS\s*=\s*(\[.*?\]);', html, re.DOTALL)
if m:
    try:
        stocks = json.loads(m.group(1))
        no_price = [s['code'] for s in stocks if not s.get('price')]
        no_score_non_exp = [s['code'] for s in stocks if s.get('score') is None and s['code'] in
                           ['2330','2317','2454','2382','2881','2882','2886','2891','3008','6505']]
        print(f'\n=== STOCKS ===')
        print(f'  Total: {len(stocks)}')
        print(f'  No price: {no_price or "none"}')
        print(f'  Core stocks missing score: {no_score_non_exp or "none"}')
    except Exception as e:
        print(f'  Parse error: {e}')
