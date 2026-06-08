import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]

# smart_money_confluence
smc = json.loads((rd/"smart_money_confluence.json").read_text(encoding="utf-8"))
all_smc = smc.get("all_results", [])
print("SMC fields:", list(all_smc[0].keys()) if all_smc else "EMPTY")
for fld in ["confluence", "inst_net", "inst_signal", "divergence", "eq_grade"]:
    n = sum(1 for s in all_smc if s.get(fld) is not None and s.get(fld) != "")
    print(f"  {fld:20}: {n}/{len(all_smc)}")

print()

# institutional_flows: check field names vs what action_signal reads
fl = json.loads((rd/"institutional_flows.json").read_text(encoding="utf-8"))
uf = fl.get("universe_flows", [])
print("institutional_flows fields:", list(uf[0].keys()) if uf else "EMPTY")
for fld in ["total_net", "inst_signal", "divergence"]:
    n = sum(1 for s in uf if s.get(fld) is not None and s.get(fld) != "")
    print(f"  {fld:20}: {n}/{len(uf)}")

print()

# dna_signals: check bull_signs coverage
dna = json.loads((rd/"dna_signals.json").read_text(encoding="utf-8"))
all_dna = dna.get("all_signals", [])
for fld in ["bull_signs", "core_met", "verdict"]:
    n = sum(1 for s in all_dna if s.get(fld) is not None)
    print(f"  dna.{fld:20}: {n}/{len(all_dna)}")
