import requests, time

# Try STOCK_DAY for 0050 as TAIEX proxy - monthly data
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.twse.com.tw/'
}

# STOCK_DAY - daily trading data for 0050
for month in ['20260601', '20260501', '20260401']:
    url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={month}&stockNo=0050'
    r = requests.get(url, timeout=10, headers=headers)
    print(f"STOCK_DAY 0050 {month}: {r.status_code}")
    if r.status_code == 200:
        try:
            d = r.json()
            if d.get('stat') == 'OK':
                rows = d.get('data', [])
                print(f"  {len(rows)} rows, fields: {d.get('fields', [])[:6]}")
                if rows:
                    print(f"  First: {rows[0]}, Last: {rows[-1]}")
            else:
                print(f"  stat: {d.get('stat')}")
        except Exception as e:
            print(f"  Error: {e}, text: {r.text[:100]}")
    time.sleep(2)

print()
# Also try openapi STOCK_DAY_ALL
url2 = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
r2 = requests.get(url2, timeout=15, headers=headers)
print(f"STOCK_DAY_ALL: {r2.status_code}")
if r2.status_code == 200:
    d2 = r2.json()
    if isinstance(d2, list):
        # Find 0050
        etf = [x for x in d2 if x.get('Code') == '0050']
        print(f"  0050 in STOCK_DAY_ALL: {etf[:1]}")
