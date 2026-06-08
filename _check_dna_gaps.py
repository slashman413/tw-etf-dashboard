import json
from pathlib import Path
today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
rd = Path("reports") / today

dna = json.loads((rd/"dna_signals.json").read_text(encoding="utf-8"))
comp = json.loads((rd/"composite_data.json").read_text(encoding="utf-8"))
exp = json.loads((rd/"expansion_stocks.json").read_text(encoding="utf-8"))

name_map = {s["code"]: s["name"] for s in comp}
name_map.update({s["code"]: s["name"] for s in exp})

all_codes = set(name_map.keys())
dna_codes = {s["code"] for s in dna.get("all_signals", []) if s.get("code")}
missing = all_codes - dna_codes
print(f"All tracked: {len(all_codes)}, In DNA: {len(dna_codes)}, Missing: {len(missing)}")
for c in sorted(missing):
    print(f"  {c} {name_map.get(c, '?')}")

bad = [s for s in dna.get("all_signals", []) if not s.get("code")]
print(f"\nMalformed entries (no code key): {len(bad)}")
if bad:
    for b in bad:
        print(f"  keys: {list(b.keys())[:8]}")
