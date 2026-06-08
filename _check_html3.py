"""Check DNA_FULLMKT data and OHLCV format in series_map."""
import re, json

html = open('dashboard.html', encoding='utf-8').read()

# Check DNA_FULLMKT has actual data (not placeholder)
m = re.search(r'const DNA_FULLMKT\s*=\s*(\{)', html)
if m:
    start = m.start(1)
    # Find the key fields
    snippet = html[start:start+500]
    print('DNA_FULLMKT snippet:', snippet[:200])
    # Count all_results in the blob (approximate)
    if 'all_results' in html[start:start+200000]:
        # Find all_results array
        ar_start = html.index('"all_results"', start)
        arr_snippet = html[ar_start:ar_start+200]
        print(f'\nall_results snippet: {arr_snippet[:150]}')

# Check OHLCV format in series_map.json
sm = json.loads(open('series_map.json', encoding='utf-8').read())
print(f'\nseries_map stocks: {len(sm)}')

# Sample a known stock
sample_code = '2330'
if sample_code in sm:
    d = sm[sample_code].get('d', [])
    if d:
        print(f'\n2330 OHLCV sample (last 3):')
        for row in d[-3:]:
            date, o, c, lo, hi = row[0], row[1], row[2], row[3], row[4]
            direction = 'UP' if c >= o else 'DOWN'
            print(f'  {date}: O={o} C={c} L={lo} H={hi} → {direction}')
        # Verify format: c should be between lo and hi
        ok = all(row[3] <= row[2] <= row[4] and row[3] <= row[1] <= row[4] for row in d[-10:])
        print(f'  OHLCV sanity check: {"OK" if ok else "FAIL !!"}')

# Check renderBBChart function for correct field mapping
bb_fn_start = html.find('function renderBBChart')
if bb_fn_start >= 0:
    bb_snippet = html[bb_fn_start:bb_fn_start+800]
    print(f'\nrenderBBChart snippet:')
    # Find the ohlc line
    for line in bb_snippet.split('\n'):
        if 'ohlc' in line or 'closes' in line or 'color' in line.lower():
            print(f'  {line.strip()}')
