import json
from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])
print("Report dirs:", [d.name for d in rd])
latest = rd[-1]
print("Latest:", latest.name)
gu = json.loads((latest / "grand_unified.json").read_text(encoding="utf-8"))
triple = gu.get("triple_confirmed", [])
sbuy = gu.get("strong_buy", [])
print("TRIPLE:", len(triple), "| STRONG BUY:", len(sbuy))
for r in triple[:5]:
    print("  ", r["code"], r["name"][:8], "grand=" + str(r["grand"]), "bull=" + str(r.get("bull_signs")))
pm = json.loads((latest / "price_momentum.json").read_text(encoding="utf-8"))
print("price_momentum data_date:", pm.get("data_date"), "| fetch_ts:", pm.get("fetch_ts"))
taiex = json.loads(Path("taiex_ohlc.json").read_text(encoding="utf-8"))
print("taiex_ohlc date:", taiex.get("current", {}).get("date"), "close:", taiex.get("current", {}).get("close"))
ac_path = latest / "action_signal.json"
if ac_path.exists():
    ac = json.loads(ac_path.read_text(encoding="utf-8"))
    all_ac = ac.get("all_signals", [])
    has_eq = sum(1 for s in all_ac if s.get("eq_grade") and s["eq_grade"] not in ["", "—"])
    print("action_signal eq_grade filled:", has_eq, "/", len(all_ac))
    print("action_signal generated:", ac.get("generated") or ac.get("fetch_ts"))
