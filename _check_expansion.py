#!/usr/bin/env python3
import json
from pathlib import Path

expansion = ['1590','2912','4904','2880','3231','2383','2344','3481','2049']
stocks_dir = Path('reports/2026-06-06/stocks')
for code in expansion:
    p = stocks_dir / (code+'_report.json')
    if p.exists():
        d = json.loads(p.read_text(encoding='utf-8'))
        eps = d.get('q1_eps') or d.get('eps_q1')
        grand = d.get('grand')
        name = d.get('name','?')[:10]
        print(f'  {code} {name}: EPS={eps} grand={grand}')
    else:
        print(f'  {code}: NO REPORT')

# Also check FULL_REPORT.md for ETF breakdown
md = Path('reports/2026-06-06/FULL_REPORT.md')
if md.exists():
    lines = md.read_text(encoding='utf-8').split('\n')
    print(f'\nFULL_REPORT.md: {len(lines)} lines')
    print('First 5 lines:', lines[:5])
