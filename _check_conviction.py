import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
cm = json.loads((rd/"conviction_matrix.json").read_text(encoding="utf-8"))
all_cm = cm.get("all_results", [])
has_eq = sum(1 for s in all_cm if s.get("eq_grade"))
print(f"conviction_matrix eq_grade: {has_eq}/{len(all_cm)}")
top = sorted(all_cm, key=lambda x: -(x.get("conviction") or 0))[:5]
for s in top:
    code = s.get("code","?")
    conv = s.get("conviction", 0) or 0
    eq   = s.get("eq_grade","?")
    verd = s.get("verdict","?")
    print(f"  {code:6} conv={conv:.1f} eq={eq:4} {verd}")
# margin_of_safety check
mo = json.loads((rd/"margin_of_safety.json").read_text(encoding="utf-8"))
safe = [s for s in mo.get("all_stocks",[]) if (s.get("mos_pct") or -999) > 0]
print(f"\nmargin_of_safety: {len(mo.get('all_stocks',[]))} stocks | undervalued: {len(safe)}")
for s in safe[:5]:
    code = s.get("code","?")
    mos  = s.get("mos_pct",0)
    iv   = s.get("intrinsic_value",0)
    pe   = s.get("pe",0)
    print(f"  {code:6} MoS={mos:+.1f}% IV={iv:.1f} PE={pe}")
