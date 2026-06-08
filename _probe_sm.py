import json
sm = json.loads(open('series_map.json', encoding='utf-8').read())
for code, s in sm.items():
    d = s.get('d', [])
    if len(d) > 5:
        print(f'Code: {code}')
        for r in d[:3]:
            print(f'  {r}')
        # Show which makes sense: [date, open, high, low, close] ?
        r = d[-1]
        print(f'\nLast row: {r}')
        print(f'  r[0]=date, r[1]=open={r[1]}, r[2]={r[2]}, r[3]={r[3]}, r[4]=close={r[4]}')
        # check: high should be >= open and close, low should be <= both
        o, h, l, c = r[1], r[2], r[3], r[4]
        print(f'  If [open,high,low,close]: high>=open? {h>=o}, high>=close? {h>=c}, low<=open? {l<=o}, low<=close? {l<=c}')
        o2, c2, l2, h2 = r[1], r[2], r[3], r[4]
        print(f'  If [open,close,low,high]: high>=open? {h2>=o2}, high>=close? {h2>=c2}, low<=open? {l2<=o2}, low<=close? {l2<=c2}')
        break
