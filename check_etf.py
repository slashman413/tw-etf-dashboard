import json; from pathlib import Path; from datetime import datetime
_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "etf_concentration.json").exists()], reverse=True)
D = _dirs[0] if _dirs else Path("reports") / datetime.now().strftime("%Y-%m-%d")
etfc = json.loads((D/"etf_concentration.json").read_text(encoding="utf-8"))
# Show blended_top20 sample
top20 = etfc.get("blended_top20",[])
print(f"blended_top20: {len(top20)} stocks")
for r in top20[:5]:
    print(f"  {r['code']} {r['name'][:12]}: wt={r.get('wt')} etfs={r.get('etfs')}")
# Show unique ETFs mentioned
all_etfs = set()
for r in top20:
    for e in r.get("etfs",[]):
        all_etfs.add(e)
print("ETFs in dataset:", sorted(all_etfs))
# Weights_0050
w0050 = etfc.get("weights_0050",{})
print(f"weights_0050: {len(w0050)} stocks, e.g. {list(w0050.items())[:3]}")
