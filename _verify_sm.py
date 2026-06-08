import json
sm = json.loads(open('series_map.json', encoding='utf-8').read())
check = ['2615','5876','2890','2603','2801','5871','6669','2886']
for code in check:
    s = sm.get(code)
    if s and s.get('d'):
        print(f"{code}: OK ({len(s['d'])} rows, last={s['d'][-1][0]})")
    else:
        print(f"{code}: MISSING")
print(f"\nTotal stocks: {len(sm)}")
