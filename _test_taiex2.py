import requests, time

# Try various TAIEX historical endpoints
tests = [
    'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST.json?date=20260601',
    'https://www.twse.com.tw/rwd/zh/index/TRI?date=20260601&response=json',
    'https://www.twse.com.tw/exchangeReport/MI_INDEX_ALLBUT0099?response=json&date=20260601',
    'https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX_ALLBUT0099',
    'https://www.twse.com.tw/en/indices/taiex/price-indices.json?date=1150601',
    'https://www.twse.com.tw/en/indices/taiex/price-indices.json?date=20260601',
]

for url in tests:
    try:
        r = requests.get(url, timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        print(f"  {url[-60:]}")
        print(f"  Status: {r.status_code}, CT: {r.headers.get('content-type','')[:30]}")
        if 'json' in r.headers.get('content-type','') and r.status_code == 200:
            try:
                d = r.json()
                if isinstance(d, list):
                    print(f"  List: {len(d)} items, sample: {str(d[0])[:100]}")
                elif isinstance(d, dict):
                    print(f"  Dict keys: {list(d.keys())[:6]}")
                    if 'data' in d:
                        print(f"  data: {len(d['data'])} rows, first: {d['data'][0] if d['data'] else 'empty'}")
            except Exception as e:
                print(f"  Parse error: {e}")
        else:
            print(f"  Body: {r.text[:80]}")
        print()
        time.sleep(1)
    except Exception as e:
        print(f"  Error: {e}\n")
