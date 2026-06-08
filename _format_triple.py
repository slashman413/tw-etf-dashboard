"""Format complete triple reports for Discord."""
import json
from pathlib import Path
rd = Path('reports/2026-06-07')

tr = json.loads((rd / 'triple_reports.json').read_text(encoding='utf-8'))
etf4q = json.loads((rd / 'etf_4q_report.json').read_text(encoding='utf-8'))
stocks_0050 = etf4q.get('etfs', {}).get('0050', {}).get('stocks', [])
fin_map = {s['code']: s for s in stocks_0050}

reports = tr.get('reports', [])
for rpt in reports:
    code = rpt.get('code')
    name = rpt.get('name', '')
    sector = rpt.get('sector', '')
    grand = rpt.get('grand_total')
    final = rpt.get('final', '')
    bull = rpt.get('bull_signs', 0)
    sb = rpt.get('score_breakdown', {})
    va = rpt.get('valuation', {})
    mo = rpt.get('momentum', {})
    rv = rpt.get('relative_strength', {})
    bt = rpt.get('backtest', {})
    my = rpt.get('may_outlook', {})
    dna = rpt.get('dna_signals', [])
    thesis = rpt.get('thesis', '')
    pw = rpt.get('portfolio_weight', {})

    # Get financial data from etf4q
    fin = fin_map.get(code, {})
    eps_q1 = fin.get('eps_q1')
    trail_eps = fin.get('trail_eps')
    fwd_eps = fin.get('fwd_eps')
    trail_pe = fin.get('trail_pe')
    fwd_pe = fin.get('fwd_pe')
    pb = fin.get('pb') or va.get('pb')
    div = fin.get('div_yield') or va.get('div_yield')
    op_m = fin.get('op_margin')
    net_m = fin.get('net_margin')
    rev_yoy = fin.get('rev_yoy')
    price = va.get('close') or fin.get('price')

    print(f"=== {code} {name} ({sector}) ===")
    print(f"綜合評分: {grand}/100 | {final} | DNA {bull}/6訊號")
    print(f"現價: {price} | 本益比: {trail_pe} (預估:{round(fwd_pe,1) if fwd_pe else 'N/A'}) | 股價淨值比: {pb}")
    print(f"殖利率: {div}% | 月均線: {va.get('ma30')} ({'+' if (va.get('pct_vs_ma') or 0)>=0 else ''}{va.get('pct_vs_ma')}%)")
    print(f"EPS Q1: {eps_q1} | 近12月EPS: {round(trail_eps,2) if trail_eps else 'N/A'} | 預估EPS: {round(fwd_eps,2) if fwd_eps else 'N/A'}")
    print(f"淨利率: {round(net_m,1) if net_m else 'N/A'}% | 營收YoY: {round(rev_yoy,1) if rev_yoy else 'N/A'}%")
    print(f"\n得分分解:")
    print(f"  基本面: {sb.get('fundamental',0):.0f}/25 | 技術DNA: {sb.get('technical',0):.0f}/25")
    print(f"  估值:   {sb.get('valuation',0):.0f}/25 | 動能:    {sb.get('momentum',0):.0f}/25")
    print(f"\nDNA訊號:")
    for s in dna:
        mark = '✅' if s.get('ok') else '❌'
        val = f" ({s.get('value')})" if s.get('value') is not None else ''
        print(f"  {mark} {s.get('signal')}{val}")
    print(f"\n動能: vs月均{'+' if (mo.get('pct_vs_ma') or 0)>=0 else ''}{mo.get('pct_vs_ma')}% | 訊號:{mo.get('signal')}")
    print(f"相對強度: RS20d={rv.get('rs_20d')} RS60d={rv.get('rs_60d')} | 距52W高點:{rv.get('pct_from_52w_high')}%")
    if bt:
        print(f"回測: {bt}")
    if my:
        print(f"6月展望: {my}")
    if pw:
        print(f"建議倉位: {pw}")
    print(f"\n投資論點: {thesis}")
    print()
