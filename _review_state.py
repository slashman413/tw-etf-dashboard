import json
from pathlib import Path

rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]

if_path = rd / "institutional_flows.json"
if if_path.exists():
    ifl = json.loads(if_path.read_text(encoding="utf-8"))
    print("instflows data_date:", ifl.get("data_date"))
    print("instflows fetch_ts:", ifl.get("fetch_ts"))
    print("instflows stocks:", len(ifl.get("all_flows", [])))
else:
    print("institutional_flows.json NOT FOUND")

gu = json.loads((rd / "grand_unified.json").read_text(encoding="utf-8"))
print("\ngrand data_date:", gu.get("data_date"))
print("Top 5:")
for r in gu.get("all_ranked", [])[:5]:
    print(" ", r["code"], r["name"][:8], "grand=%.1f" % r["grand"],
          "bull=%d" % r.get("bull_signs", 0), r["final"])

# Check watchlist alerts
wa = json.loads((rd / "watchlist_alerts.json").read_text(encoding="utf-8"))
print("\nAlmost TRIPLE:", len(wa.get("almost_triple", [])))
for s in wa.get("almost_triple", [])[:3]:
    print(" ", s["code"], s["name"][:8], "gap=%.1f" % s.get("grand_gap", 0))

# Check score distribution
print("\nScore distribution:")
for bucket, label in [(70, "TRIPLE"), (65, "STRONG BUY"), (55, "BUY"), (40, "WATCH")]:
    count = sum(1 for r in gu.get("all_ranked", []) if r["grand"] >= bucket)
    print(f"  >= {bucket}: {count}")
