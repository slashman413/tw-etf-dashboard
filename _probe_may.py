import json
from pathlib import Path
from collections import Counter

d = Path('reports/2026-06-06')
raw = json.loads((d/'may_revenue_raw.json').read_text(encoding='utf-8'))
records = raw['raw']

periods = Counter(r.get('資料年月') for r in records)
print('Data periods:', dict(sorted(periods.items())))

filing = Counter(r.get('出表日期','')[:6] for r in records)
print('Filing months:', dict(sorted(filing.items())))

may_recs = [r for r in records if r.get('資料年月') == '11505']
print(f'May 2026 revenue records (11505): {len(may_recs)}')
if may_recs:
    for r in may_recs[:5]:
        print(f"  {r['公司代號']} {r['公司名稱']}: May YoY = {r['營業收入-去年同月增減(%)']}%")
