import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]

# earnings_quality
eq = json.loads((rd/"earnings_quality.json").read_text(encoding="utf-8"))
all_eq = eq.get("all_stocks", [])
print(f"earnings_quality: {len(all_eq)} stocks | date={eq.get('date','?')}")
grade_dist = {}
for s in all_eq:
    g = s.get("eq_grade","?")
    grade_dist[g] = grade_dist.get(g,0) + 1
print("Grade dist:", dict(sorted(grade_dist.items())))
no_grade = [s.get("code") for s in all_eq if not s.get("eq_grade")]
print("Missing eq_grade:", no_grade[:10])
# Top A+ stocks
top = [s for s in all_eq if s.get("eq_grade") in ("A+","A")]
print(f"A/A+ stocks ({len(top)}):", [s.get("code") for s in top[:10]])

print()

# smart_money_confluence
smc = json.loads((rd/"smart_money_confluence.json").read_text(encoding="utf-8"))
all_smc = smc.get("all_results", [])
print(f"smart_money_confluence: {len(all_smc)} stocks | date={smc.get('date','?')}")
no_conf = [s.get("code") for s in all_smc if s.get("confluence") is None]
print("Missing confluence:", no_conf[:10])
top_smc = sorted(all_smc, key=lambda x: -(x.get("confluence") or 0))[:5]
print("Top confluence:")
for s in top_smc:
    print(f"  {s.get('code'):6} conf={s.get('confluence'):5.1f}  {s.get('smc_verdict','?')[:40]}")

print()

# institutional_flows
fl = json.loads((rd/"institutional_flows.json").read_text(encoding="utf-8"))
uf = fl.get("universe_flows", [])
print(f"institutional_flows: {len(uf)} stocks | data_date={fl.get('data_date','?')}")
big_buy = sorted([f for f in uf if (f.get("total_net") or 0) > 500], key=lambda x: -(x.get("total_net") or 0))[:5]
print("Top institutional buys:")
for f in big_buy:
    print(f"  {f.get('code'):6} net={f.get('total_net',0):>8,.0f}  {f.get('inst_signal','?')}")
