import json, ssl, urllib.request
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
req = urllib.request.Request('https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL',
                             headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
    data = json.loads(r.read().decode())
    date = data[0].get('Date','?') if data else '?'
    print(f'Records: {len(data)} | Date: {date}')
