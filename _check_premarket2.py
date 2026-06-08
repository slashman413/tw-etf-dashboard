import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
pc = json.loads((rd/"premarket_checklist.json").read_text(encoding="utf-8"))
print("Summary:", json.dumps(pc["summary"], ensure_ascii=False, indent=2))
p1 = [c.get("code") for c in pc["checklist"] if c.get("priority")==1]
p2 = [c.get("code") for c in pc["checklist"] if c.get("priority")==2]
p3 = [c.get("code") for c in pc["checklist"] if c.get("priority")==3]
print("P1 TRIPLE:", p1)
print("P2 NEAR:  ", p2[:6])
print("P3 DNA5/6:", p3[:6])
# Check for any None in critical fields
missing = [(c.get("code"), k) for c in pc["checklist"] for k in ["close","stop","grand"] if c.get(k) is None]
if missing:
    print("WARNING - None in critical fields:", missing[:10])
else:
    print("All critical fields populated.")
