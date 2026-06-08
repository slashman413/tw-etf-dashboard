import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
ss = json.loads((rd/"score_sensitivity.json").read_text(encoding="utf-8"))
print("date:", ss["date"], "| total:", ss["total"])
print("near_upgrade:", ss["near_upgrade_count"], "| already_triple:", len(ss["already_triple"]))
for s in ss["near_upgrade"][:5]:
    code = s.get("code","?")
    cur  = s.get("current", 0)
    pts  = s.get("pts_to_next", 0)
    tier = s.get("next_tier","?")
    levers = [l.get("name","?") for l in s.get("levers",[])[:2]]
    print(f"  {code:6} grand={cur:.1f} need {pts:.1f}pts → {tier} | levers={levers}")
print("already_triple:", [s.get("code") for s in ss["already_triple"]])
