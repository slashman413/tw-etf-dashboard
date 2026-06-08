"""Check financial stock data coverage in etf_4q_report."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

etf4q = json.loads((rd / 'etf_4q_report.json').read_text(encoding='utf-8'))
etfs_data = etf4q.get('etfs', {})
stocks_0050 = etfs_data.get('0050', {}).get('stocks', [])

fin_codes = ['2881', '2882', '2883', '2884', '2886', '2887', '2891', '2892']
print('Financial stocks in 0050 ETF 4Q report:')
for s in stocks_0050:
    if s.get('code') in fin_codes:
        code = s.get('code')
        print(f'\n  {code} {s.get("name")}:')
        te = s.get("trail_eps")
        te_str = f'{te:.2f}' if te else 'None'
        print(f'    eps_q1={s.get("eps_q1")}, trail_eps={te_str}')
        print(f'    trail_pe={s.get("trail_pe")}, fwd_pe={s.get("fwd_pe")}')
        print(f'    div_yield={s.get("div_yield")}, pb={s.get("pb")}')
        print(f'    op_margin={s.get("op_margin")}, net_margin={s.get("net_margin")}')
        print(f'    verdict={s.get("verdict")}, grand={s.get("grand")}')

# Check non-financial top picks
print('\nTop picks (non-financial):')
non_fin = [s for s in stocks_0050 if s.get('code') not in fin_codes and s.get('eps_q1')]
non_fin.sort(key=lambda x: -(x.get('grand') or 0))
for s in non_fin[:5]:
    print(f'  {s["code"]} {s["name"]}: eps_q1={s["eps_q1"]}, grand={s["grand"]}, verdict={s["verdict"]}')
