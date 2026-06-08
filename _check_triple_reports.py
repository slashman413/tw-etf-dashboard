"""Check triple reports content quality."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

tr = json.loads((rd / 'triple_reports.json').read_text(encoding='utf-8'))
reports = tr.get('reports', [])
print(f'Triple reports type: {type(reports).__name__}, count: {len(reports)}')

if isinstance(reports, list):
    for rpt in reports:
        code = rpt.get('code')
        print(f'\n=== {code} {rpt.get("name")} ===')
        print(f'  Grand: {rpt.get("grand")}, Bull: {rpt.get("bull_signs")}, Final: {rpt.get("final")}')
        print(f'  Price: {rpt.get("price")}, PE: {rpt.get("pe")}, Div: {rpt.get("div_yield")}')
        print(f'  EPS Q1: {rpt.get("eps_q1")}, Trail EPS: {rpt.get("trail_eps")}')
        print(f'  Keys: {list(rpt.keys())}')
elif isinstance(reports, dict):
    for code, rpt in reports.items():
        print(f'\n=== {code} {rpt.get("name")} ===')
        print(f'  Grand: {rpt.get("grand")}, Bull: {rpt.get("bull_signs")}')
        print(f'  Keys: {list(rpt.keys())}')
