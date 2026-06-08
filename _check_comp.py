import json
from pathlib import Path

rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
comp = json.loads((rd / "composite_data.json").read_text(encoding="utf-8"))
print("Type:", type(comp).__name__, "len:", len(comp))
if comp:
    print("Keys:", list(comp[0].keys())[:12])
    top = sorted(comp, key=lambda x: x.get("score", 0) or 0, reverse=True)[:3]
    for s in top:
        code = s["code"]
        name = s["name"][:10]
        score = s.get("score")
        fwd_pe = s.get("fwd_pe")
        q1_eps = s.get("q1_eps")
        print(f"  {code} {name} score={score} fwd_pe={fwd_pe} q1_eps={q1_eps}")
