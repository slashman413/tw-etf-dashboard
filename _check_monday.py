import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
mp = json.loads((rd/"monday_plan.json").read_text(encoding="utf-8"))
print("Checklist:")
for t in mp.get("checklist", []):
    tm = t.get("time", "?")
    task = t.get("task", "?")
    print(f"  [{tm}] {task}")
print()
summ = mp.get("summary", {})
print("Summary:", json.dumps(summ, ensure_ascii=False, indent=2))
cats = mp.get("categories", {})
for cat, items in cats.items():
    if isinstance(items, list) and items:
        codes = [s.get("code","?") for s in items[:5]]
        print(f"  {cat}: {codes}")
