import requests, time, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for date in ['20260601', '20260501', '20260401']:
    url = f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={date}&response=json'
    r = requests.get(url, timeout=8, headers=headers)
    d = r.json()
    print(f"Date {date}: stat={d.get('stat')}, fields={d.get('fields',[][:5])}")
    rows = d.get('data', [])
    print(f"  {len(rows)} rows")
    if rows:
        print(f"  First: {rows[0]}")
        print(f"  Last: {rows[-1]}")
    time.sleep(1)
