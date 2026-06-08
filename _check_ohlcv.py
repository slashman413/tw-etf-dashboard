import json
from pathlib import Path

data = json.loads(Path('expansion_ohlcv.json').read_text(encoding='utf-8'))
codes = list(data.keys())
print(f"expansion_ohlcv: {len(codes)} stocks")
code = codes[0]
v = data[code]
dates = v.get('d', [])
last = dates[-1] if dates else 'empty'
wr = v.get('wr', [])
rsi = v.get('rsi60', [])
print(f"Sample [{code}]: dates={len(dates)} last={last}")
print(f"  WR len={len(wr)} RSI len={len(rsi)}")

# Check crawl_ohlcv.py output file
ohlcv = Path('reports')
rd = sorted([d for d in ohlcv.iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
ohlcv_path = rd / 'ohlcv_data.json'
if ohlcv_path.exists():
    import os
    from datetime import datetime
    mtime = datetime.fromtimestamp(os.path.getmtime(ohlcv_path)).strftime('%Y-%m-%d %H:%M')
    od = json.loads(ohlcv_path.read_text(encoding='utf-8'))
    print(f"\nohlcv_data.json: mtime={mtime}")
    sigs = od.get('all_signals', [])
    if sigs:
        s0 = sigs[0]
        print(f"  data_date: {od.get('data_date')} stocks={len(sigs)}")
        print(f"  Keys: {list(s0.keys())[:10]}")
else:
    print("\nohlcv_data.json: NOT FOUND in report dir")
