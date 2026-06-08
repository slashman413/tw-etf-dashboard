import json
from pathlib import Path
rd = Path("reports/2026-06-09")

# Check why 2002 has no PE
bw = json.loads((rd / "bwibbu_fresh.json").read_text(encoding="utf-8"))
bw_map = {x["code"]: x for x in bw.get("stocks", [])}
for code in ["2002", "2823", "2888"]:
    b = bw_map.get(code, {})
    print(f"{code}: pe_new={b.get('pe_new')} pe_old={b.get('pe_old')} in_bwibbu={code in bw_map}")

# Check action_signal sig field distribution
ac = json.loads((rd / "action_signal.json").read_text(encoding="utf-8"))
all_ac = ac.get("all_signals", [])
sig_counts = {}
for s in all_ac:
    sig = s.get("signal") or "EMPTY"
    sig_counts[sig] = sig_counts.get(sig, 0) + 1
print("\naction_signal sig distribution:", sig_counts)

# Check 2002 in composite/expansion
comp = json.loads((rd / "composite_data.json").read_text(encoding="utf-8"))
exp = json.loads((rd / "expansion_stocks.json").read_text(encoding="utf-8"))
comp_map = {s["code"]: s for s in comp}
exp_map = {s["code"]: s for s in exp}
for code in ["2002"]:
    c = comp_map.get(code) or exp_map.get(code, {})
    print(f"\n{code} composite: pe={c.get('pe')} fwd_pe={c.get('fwd_pe')} name={c.get('name')}")

# Score sensitivity upgrade gaps
ss = json.loads((rd / "score_sensitivity.json").read_text(encoding="utf-8"))
gaps = ss.get("upgrade_gaps", [])
print(f"\nUpgrade gaps top 5:")
for g in gaps[:5]:
    code = g.get("code"); nm = g.get("name","")[:8]
    gap = g.get("gap"); current = g.get("current_grand"); target = g.get("target")
    print(f"  {code} {nm} gap={gap} current={current} target={target}")
