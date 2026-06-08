import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]

# dividend_income
di = json.loads((rd/"dividend_income.json").read_text(encoding="utf-8"))
print("dividend_income date:", di.get("date"))
print("Keys:", list(di.keys()))
holdings = di.get("holdings", di.get("all_holdings", []))
print(f"Holdings: {len(holdings)}")
total_income = di.get("total_annual_income") or di.get("total_income")
print(f"Total annual income: {total_income}")
# Top dividend stocks
sorted_h = sorted(holdings, key=lambda x: -(x.get("annual_income") or x.get("income") or 0))
for h in sorted_h[:5]:
    code = h.get("code","?")
    dy   = h.get("div_yield") or h.get("yield")
    inc  = h.get("annual_income") or h.get("income")
    print(f"  {code:6} yield={dy} income={inc}")

print()

# catalyst_calendar
cc = json.loads((rd/"catalyst_calendar.json").read_text(encoding="utf-8"))
print("catalyst_calendar date:", cc.get("date"))
events = cc.get("all_events", cc.get("events", []))
print(f"Events: {len(events)}")
upcoming = [e for e in events if e.get("date","") >= "2026-06-09"]
print(f"Upcoming (Jun 9+): {len(upcoming)}")
for e in sorted(upcoming, key=lambda x: x.get("date",""))[:5]:
    code = e.get("code","?")
    dt   = e.get("date","?")
    cat  = e.get("catalyst","?")
    print(f"  {dt} {code:6} {str(cat)[:60]}")
