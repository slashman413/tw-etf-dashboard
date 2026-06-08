import requests, json, time

# Get June 2026 data
for date in ['20260601', '20260501']:
    url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date}&type=MS'
    r = requests.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
    d = r.json()
    print(f"Date: {date}, tables: {len(d.get('tables',[]))}")
    for i, t in enumerate(d.get('tables', [])):
        title = t.get('title', '')
        fields = t.get('fields', [])
        rows = t.get('data', [])
        print(f"  Table {i}: {title[:40]}, fields: {fields[:5]}, rows: {len(rows)}")
        if rows:
            print(f"    First row: {rows[0]}")
            print(f"    Last row: {rows[-1]}")
    time.sleep(2)
