import json
from pathlib import Path
rd = Path("reports/2026-06-09")

# Check 2887 per-stock report
f = rd / "stocks" / "2887_report.json"
if not f.exists():
    print("2887_report.json NOT FOUND")
else:
    r = json.loads(f.read_text(encoding="utf-8"))
    print("2887 stock report fields:", list(r.keys()))
    print("  name:", r.get("name"))
    print("  grand:", r.get("grand"))
    print("  final:", r.get("final"))
    print("  pe:", r.get("pe"))
    print("  div_yield:", r.get("div_yield"))
    print("  eq_grade:", r.get("eq_grade"))
    print("  bull_signs:", r.get("bull_signs"))
    print("  action:", r.get("action"))
    print("  rationale:", r.get("rationale"))
    print("  close:", r.get("close"))
    print("  ma30:", r.get("ma30"))
    print("  thesis:", str(r.get("thesis",""))[:80])

# Count all stock reports
stocks_dir = rd / "stocks"
reports = list(stocks_dir.glob("*_report.json")) if stocks_dir.exists() else []
print(f"\nTotal stock reports: {len(reports)}")

# Check for missing key fields
missing_pe = [f.stem.split("_")[0] for f in reports
              if not json.loads(f.read_text(encoding="utf-8")).get("pe")]
missing_eq = [f.stem.split("_")[0] for f in reports
              if not json.loads(f.read_text(encoding="utf-8")).get("eq_grade")]
print(f"Missing PE: {len(missing_pe)} — {missing_pe[:5]}")
print(f"Missing eq_grade: {len(missing_eq)} — {missing_eq[:5]}")
