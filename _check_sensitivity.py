import json
from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
ss = json.loads((rd/"score_sensitivity.json").read_text(encoding="utf-8"))
print("date:", ss.get("date"))
all_s = ss.get("all_sensitivities", [])
print("total stocks:", len(all_s))
bad = [s for s in all_s if s.get("grand") is None]
print("Stocks with None grand:", len(bad), [s["code"] for s in bad])
# Check pe_range_impact
no_pe_sens = [s["code"] for s in all_s if s.get("pe_range_impact") is None]
print("No pe_range_impact:", len(no_pe_sens), no_pe_sens[:8])
# Top sensitive
sens = sorted(all_s, key=lambda x: abs(x.get("pe_range_impact") or 0), reverse=True)
for s in sens[:5]:
    print(f"  {s['code']:6} pe_impact={s.get('pe_range_impact')} dna_impact={s.get('dna_range_impact')}")
