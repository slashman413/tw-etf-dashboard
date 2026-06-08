import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]

# conviction_matrix structure
cm = json.loads((rd/"conviction_matrix.json").read_text(encoding="utf-8"))
first = cm.get("all_results",[{}])[0]
print("conviction_matrix stock keys:", list(first.keys()))
print("Sample:", {k:v for k,v in first.items() if v is not None and k not in ["code","name"]})

print()

# margin_of_safety undervalued stocks
mo = json.loads((rd/"margin_of_safety.json").read_text(encoding="utf-8"))
all_r = mo.get("all_results",[])
safe = sorted([s for s in all_r if (s.get("mos_pct") or -999) > 0], key=lambda x: -(x.get("mos_pct") or 0))
total = len(all_r)
print(f"MoS: {total} stocks | undervalued: {len(safe)} | overvalued: {len(mo.get('overvalued',[]))}")
for s in safe[:5]:
    code = s.get("code","?")
    mos  = s.get("mos_pct", 0) or 0
    iv   = s.get("intrinsic_value", 0) or 0
    pe   = s.get("pe") or "?"
    print(f"  {code:6} MoS={mos:+.1f}%  IV={iv:.1f}  PE={pe}")
print("high_safety:", [s.get("code") for s in mo.get("high_safety",[])[:8]])
