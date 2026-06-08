import requests, time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Try fetching TAIEX from the MI_INDEX in a loop for different months
# The MI_INDEX endpoint gives the current day - maybe there's a way to get monthly
for date in ['20260601', '20260501', '20260401']:
    url = f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={date}&response=json'
    r = requests.get(url, timeout=8, headers=headers)
    print(f"MI_5MINS_HIST {date}: {r.status_code}, {r.headers.get('content-type','')[:30]}, len={len(r.text)}")
    if 'json' in r.headers.get('content-type', ''):
        try:
            d = r.json()
            print(f"  Keys: {list(d.keys())[:6]}")
        except: pass
    time.sleep(1)

print()
# Also check the daily TAIEX index via a query endpoint
for date in ['20260601', '20260501']:
    url = f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS?date={date}&response=json'
    r = requests.get(url, timeout=8, headers=headers)
    print(f"MI_5MINS {date}: {r.status_code}, ct={r.headers.get('content-type','')[:30]}")
    time.sleep(1)
