import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
pc = json.loads((rd/"premarket_checklist.json").read_text(encoding="utf-8"))
print("date:", pc.get("date"), "| generated:", pc.get("generated","?")[:16])
print("market_date:", pc.get("market_date","?"))
print()
# Top priority items
for section in ["immediate_action", "top_watchlist", "risk_flags"]:
    items = pc.get(section, [])
    if items:
        print(f"--- {section} ({len(items)}) ---")
        for item in items[:4]:
            if isinstance(item, dict):
                code = item.get("code","")
                note = item.get("note") or item.get("alert") or item.get("action","")
                print(f"  {code:6} {note[:70]}")
            else:
                print(f"  {str(item)[:80]}")
        print()
# Market context
ctx = pc.get("market_context", {})
if ctx:
    print("Market context:")
    for k,v in ctx.items():
        print(f"  {k}: {v}")
