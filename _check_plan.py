import json
from pathlib import Path
rd = Path("reports/2026-06-09")
mp = json.loads((rd / "monday_plan.json").read_text(encoding="utf-8"))
print("Plan date:", mp.get("date"))
regime = mp.get("market_regime", {})
print("Market regime:", regime.get("regime"), "| TAIEX:", regime.get("taiex"), "| Trend:", regime.get("trend"))
print()
tasks = mp.get("daily_tasks", [])
for t in tasks:
    ttime = t.get("time", "?")
    task = t.get("task", "")
    ttype = t.get("type", "")
    print(f"  [{ttime}] {task[:60]} [{ttype}]")
print()
alerts = mp.get("alerts", [])
print("Alerts:", len(alerts))
for a in alerts[:5]:
    code = a.get("code", "?")
    name = a.get("name", "")[:8]
    alert = a.get("alert", "")
    print(f"  {code} {name}: {alert}")
print()
# Check upcoming catalyst events
cc = json.loads((rd / "catalyst_calendar.json").read_text(encoding="utf-8"))
events = cc.get("all_events", cc.get("events", []))
upcoming = [e for e in events if "2026-06-09" <= e.get("date", "") <= "2026-06-15"]
print(f"Catalyst events Jun 9-15: {len(upcoming)}")
for e in sorted(upcoming, key=lambda x: x.get("date",""))[:8]:
    print(f"  {e.get('date')} {e.get('code',''):6} {str(e.get('catalyst',''))[:50]}")
