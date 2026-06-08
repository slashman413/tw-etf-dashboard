"""Check quarterly financials and ETF 4Q report coverage."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

# Check quarterly_financials structure
qf = json.loads((rd / 'quarterly_financials.json').read_text(encoding='utf-8'))
print('=== quarterly_financials ===')
print(f'Keys: {list(qf.keys())}')
print(f'Period: {qf.get("period")}')
print(f'Companies: {qf.get("total_companies")}')
print(f'Income count: {qf.get("income_count")}')
print(f'Balance count: {qf.get("balance_count")}')
print(f'OTC added: {qf.get("otc_added")}')

companies = qf.get('companies', [])
print(f'Companies data: {len(companies)} stocks')
if companies and isinstance(companies, list):
    sample = companies[0]
    print(f'Sample {sample.get("code")}: {list(sample.keys())}')
    print(f'  eps={sample.get("eps")}, revenue={sample.get("revenue")}, pe={sample.get("pe")}')
elif companies and isinstance(companies, dict):
    sample_code = list(companies.keys())[0]
    sample = companies[sample_code]
    print(f'Sample {sample_code}: {list(sample.keys())}')
    print(f'  eps={sample.get("eps")}, revenue={sample.get("revenue")}, pe={sample.get("pe")}')

# Check ETF 4Q report
etf4q = json.loads((rd / 'etf_4q_report.json').read_text(encoding='utf-8'))
print('\n=== etf_4q_report ===')
print(f'Period: {etf4q.get("data_period")}')
etfs_data = etf4q.get('etfs', {})
for etf_code, etf_info in etfs_data.items():
    print(f'\n{etf_code}:')
    print(f'  stock_count={etf_info.get("stock_count")}, eps_coverage={etf_info.get("eps_coverage")}')
    print(f'  avg_pe={etf_info.get("avg_pe")}, avg_div_yield={etf_info.get("avg_div_yield")}')
    # Check top holdings
    top = etf_info.get('top_stocks', [])
    if top:
        print(f'  Top stocks ({len(top)} total):')
        for s in top[:5]:
            print(f'    {s.get("code")} {s.get("name")}: eps={s.get("eps")}, pe={s.get("pe")}')

# Check if we need to fetch more ETF data (0056, 00878, 00713, 006208)
missing_etfs = [e for e in ['0056','00878','00713','006208'] if e not in etfs_data]
print(f'\nMissing ETF analyses: {missing_etfs or "none"}')
