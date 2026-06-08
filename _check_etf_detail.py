"""Check ETF 4Q report detail data quality."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

etf4q = json.loads((rd / 'etf_4q_report.json').read_text(encoding='utf-8'))
etfs_data = etf4q.get('etfs', {})

for etf_code in ['0050', '0056']:
    etf_info = etfs_data.get(etf_code, {})
    print(f'\n=== {etf_code} Q1 2026 ===')
    print(f'  Coverage: {etf_info.get("eps_coverage")}, avg_pe={etf_info.get("avg_pe")}, avg_div={etf_info.get("avg_div_yield")}')

    top = etf_info.get('top_stocks') or etf_info.get('stocks') or []
    if not top:
        print(f'  Keys: {list(etf_info.keys())}')
        continue

    # Show top 10 by weight or eps
    print(f'  Stocks ({len(top)} total), top 10:')
    for s in top[:10]:
        code = s.get('code', '?')
        name = s.get('name', '?')
        eps  = s.get('eps', 'N/A')
        pe   = s.get('pe', 'N/A')
        rev  = s.get('revenue')
        rev_str = f'{rev/1e8:.1f}億' if rev else 'N/A'
        margin = s.get('op_margin', 'N/A')
        print(f'    {code} {name}: eps={eps}, pe={pe}, rev={rev_str}, op_margin={margin}')

    # Check for missing eps
    no_eps = [s.get('code') for s in top if not s.get('eps')]
    print(f'  Missing EPS: {no_eps or "none"}')
