import json
from pathlib import Path
ma = json.loads(Path("reports/2026-06-09/ma_refresh.json").read_text(encoding="utf-8"))
print("ma_refresh data_date:", ma.get("data_date"))
print("ma_refresh generated:", ma.get("generated"))
print("above_ma:", len(ma.get("above_list", [])), "stocks")
print("below_ma:", len(ma.get("below_list", [])), "stocks")
all_r = ma.get("all_results", [])
print("total:", len(all_r))
for r in all_r[:3]:
    code = r["code"]
    ma30 = r.get("ma30")
    close = r.get("close")
    pct = r.get("pct_vs_ma")
    print(f"  {code} ma30={ma30} close={close} pct={pct}")
