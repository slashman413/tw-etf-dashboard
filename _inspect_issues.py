import json
from pathlib import Path
today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
rd = Path("reports") / today

# 1. action_signal top keys
a = json.loads((rd/"action_signal.json").read_text(encoding="utf-8"))
print("action_signal keys:", list(a.keys())[:10])
tops = a.get("top_signals") or a.get("signals") or a.get("ranked") or []
print(f"top_signals count: {len(tops)}")
if tops:
    print("first:", {k: v for k, v in tops[0].items() if k in ["code","name","score","final"]})

# 2. watchlist triple keys
w = json.loads((rd/"watchlist_alerts.json").read_text(encoding="utf-8"))
print("\nwatchlist keys:", list(w.keys()))
tc = w.get("triple_confirmed") or []
print(f"triple_confirmed count: {len(tc)}")
print("sample:", tc[:2] if tc else "empty")

# 3. dna_signals date
d = json.loads((rd/"dna_signals.json").read_text(encoding="utf-8"))
print(f"\ndna_signals date: {d.get('date')}, fetch_ts: {d.get('fetch_ts')}")
sigs = d.get("all_signals", [])
print(f"total signals: {len(sigs)}")
if sigs:
    sample = sigs[0]
    print(f"sample: code={sample.get('code')}, bull_signs={sample.get('bull_signs')}")
