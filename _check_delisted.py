import json
from pathlib import Path
comp = json.loads(Path("reports/2026-06-09/composite_data.json").read_text(encoding="utf-8"))
exp = json.loads(Path("reports/2026-06-09/expansion_stocks.json").read_text(encoding="utf-8"))
print("Total comp:", len(comp), "| exp:", len(exp))
for code in ["2823", "2888", "2002"]:
    c = next((s for s in comp if s["code"] == code), None)
    e = next((s for s in exp if s["code"] == code), None)
    in_c = c is not None; in_e = e is not None
    name = (c or e or {}).get("name", "?")
    score = (c or e or {}).get("score")
    print(f"{code} {name}: in_comp={in_c} in_exp={in_e} score={score}")
