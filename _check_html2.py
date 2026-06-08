"""Verify GRANDDATA and other key sections in dashboard.html."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

# Check GRANDDATA is filled (not placeholder)
m = re.search(r'const GRANDDATA\s*=\s*(\{.*?\});', html, re.DOTALL)
if m:
    try:
        gd = json.loads(m.group(1))
        print(f'GRANDDATA: OK — keys={list(gd.keys())}')
        for k, v in gd.items():
            if isinstance(v, list):
                print(f'  {k}: {len(v)} items')
            else:
                print(f'  {k}: {str(v)[:50]}')
    except Exception as e:
        print(f'GRANDDATA parse error: {e}')
        print(f'  snippet: {m.group(1)[:100]}')
else:
    print('GRANDDATA: NOT FOUND in HTML')

# Check if series_map.json is fetched
if '_smPromise' in html and "fetch('series_map.json')" in html:
    print('\nSeries map: fetched from series_map.json at runtime (OK)')

# Check DNA_FULLMKT
m2 = re.search(r'const DNA_FULLMKT\s*=\s*(\{)', html)
if m2:
    snippet = html[m2.start(1):m2.start(1)+300]
    if 'all_results' in snippet:
        print('\nDNA_FULLMKT: OK (contains all_results)')
    else:
        all_res_pos = html.find('"all_results"', m2.start(1))
        print(f'\nDNA_FULLMKT: found at char {m2.start(1)}, all_results at {all_res_pos}')

# Check showBBChart onclick
onclick_count = html.count('showBBChart(')
print(f'\nshowBBChart onclick calls: {onclick_count}')

# Check BB modal HTML
if 'id="bbModal"' in html:
    print('BB modal: OK')
if 'id="bbChartEl"' in html:
    print('BB chart element: OK')

# Check key page functions
for fn in ['initOverview', 'initScreener', 'initGrandUnified', 'initDnaScreen', 'showBBChart', 'closeBBModal', 'renderBBChart']:
    count = html.count(f'function {fn}')
    print(f'function {fn}: {"OK" if count > 0 else "MISSING !!"}')
