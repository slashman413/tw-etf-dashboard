import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
smc = json.loads((rd/"smart_money_confluence.json").read_text(encoding="utf-8"))
has_grade = sum(1 for s in smc["all_results"] if s.get("eq_grade"))
total_smc = len(smc["all_results"])
print(f"SMC eq_grade populated: {has_grade}/{total_smc}")
act = json.loads((rd/"action_signal.json").read_text(encoding="utf-8"))
has_eq = sum(1 for s in act["all_signals"] if s.get("eq_grade"))
total_act = len(act["all_signals"])
print(f"Action eq_grade populated: {has_eq}/{total_act}")
for s in act["all_signals"][:5]:
    code  = s.get("code","?")
    score = s.get("action_score",0)
    grade = s.get("eq_grade","?")
    action= s.get("action","?")
    print(f"  {code:6} score={score:5.1f} eq={grade:4} {action}")
