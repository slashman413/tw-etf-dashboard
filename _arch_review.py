"""Architecture review — check key report files for data quality."""
import json
from pathlib import Path
from datetime import datetime

today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
rd = Path("reports") / today

key_files = {
    "grand_unified.json":     lambda d: f"stocks={len(d.get('all_ranked',[]))}, data_date={d.get('data_date')}, triple={len(d.get('triple_confirmed',[]))}",
    "price_momentum.json":    lambda d: f"tracked={d.get('total_tracked')}, data_date={d.get('data_date')}, valid={d.get('valid_comparison')}",
    "bwibbu_fresh.json":      lambda d: f"matched={len(d.get('all_refreshed',[]))}, date={d.get('date')}",
    "etf_4q_report.json":     lambda d: f"etfs={list(d.get('etfs',{}).keys())}, generated={d.get('generated')}",
    "dna_signals.json":       lambda d: f"signals={len(d.get('all_signals',[]))}, data_date={d.get('data_date')}, fetch_ts={d.get('fetch_ts','')}",
    "action_signal.json":     lambda d: f"buy_now={len(d.get('buy_now',[]))}, buy={len(d.get('buy',[]))}, top3={[(x.get('code'),round(x.get('action_score',x.get('score',0)),1)) for x in (d.get('buy_now') or d.get('buy') or [])[:3]]}",
    "watchlist_alerts.json":  lambda d: f"triple={len(d.get('triple_upside',[]))}, near={len(d.get('almost_triple',[]))}, dna56={len(d.get('dna_5of6',[]))}",
    "quarterly_financials.json": lambda d: f"companies={len(d.get('companies',[]))}, source={d.get('source','')}",
    "composite_data.json":    lambda d: f"stocks={len(d)}, sample={d[0].get('code') if d else 'empty'}",
    "premarket_checklist.json": lambda d: f"positions={len(d.get('checklist',[]))}, p1={d.get('summary',{}).get('p1_triple')}, p2={d.get('summary',{}).get('p2_near')}",
}

print(f"=== Architecture Review {datetime.now().strftime('%H:%M')} | Report: {today} ===")
issues = []
for fname, summarize in key_files.items():
    fpath = rd / fname
    if not fpath.exists():
        print(f"  MISSING: {fname}")
        issues.append(f"missing: {fname}")
        continue
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
        size = fpath.stat().st_size // 1024
        summary = summarize(data)
        print(f"  OK ({size:4}KB): {fname} — {summary}")
    except Exception as e:
        print(f"  ERROR: {fname} — {e}")
        issues.append(f"error: {fname}: {e}")

print()
if issues:
    print(f"ISSUES FOUND: {len(issues)}")
    for i in issues:
        print(f"  - {i}")
else:
    print("All key files healthy — no issues detected")
