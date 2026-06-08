import json
from pathlib import Path
rd = Path("reports/2026-06-09")

# Grand unified top 10 and scoring
gu = json.loads((rd / "grand_unified.json").read_text(encoding="utf-8"))
all_r = gu.get("all_ranked", [])
print("=== Grand Unified Top 10 ===")
for r in all_r[:10]:
    code = r["code"]; nm = r["name"][:8]; grand = r["grand"]
    val = r.get("val_pts", 0); fund = r.get("fund_pts", 0)
    tech = r.get("tech_pts", 0); mom = r.get("mom_pts", 0)
    pe = r.get("pe"); bull = r.get("bull_signs"); final = r["final"]
    print(f"  {code} {nm:8} grand={grand:5.1f} val={val:4.1f} fund={fund:4.1f} tech={tech:4.1f} mom={mom:4.1f} PE={pe} bull={bull} {final}")

# Null PE check
no_pe = [r["code"] for r in all_r if not r.get("pe")]
print(f"\nNo PE: {len(no_pe)} stocks: {no_pe[:10]}")

# val_pts range
val_pts = [r.get("val_pts", 0) for r in all_r]
print(f"val_pts range: {min(val_pts):.1f} - {max(val_pts):.1f} | avg: {sum(val_pts)/len(val_pts):.1f}")

# action_signal top signals
ac = json.loads((rd / "action_signal.json").read_text(encoding="utf-8"))
all_ac = ac.get("all_signals", [])
print("\n=== Action Signal Top 5 (by score) ===")
top = sorted(all_ac, key=lambda x: -(x.get("action_score") or 0))[:5]
for s in top:
    code = s["code"]; nm = s.get("name","")[:8]
    score = s.get("action_score", 0); eq = s.get("eq_grade", "—")
    sig = s.get("signal", "—"); pe = s.get("pe")
    print(f"  {code} {nm:8} score={score:.1f} eq={eq} sig={sig} PE={pe}")

# Check watchlist_alerts
wa = json.loads((rd / "watchlist_alerts.json").read_text(encoding="utf-8"))
near = wa.get("near_triple", [])
print(f"\nNear-TRIPLE alerts: {len(near)}")
for s in near[:5]:
    print(f"  {s.get('code')} {s.get('name','')[:8]} grand={s.get('grand')} gap={s.get('gap_to_triple')}")
