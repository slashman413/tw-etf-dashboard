import json; from pathlib import Path
rd = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()], reverse=True)[0]
po = json.loads((rd/"portfolio_optimizer.json").read_text(encoding="utf-8"))
print("date:", po.get("date"), "| method:", po.get("method","?"))
ms = po.get("max_sharpe", {})
print(f"max_sharpe: sharpe={ms.get('sharpe')} ret={ms.get('expected_return')} vol={ms.get('volatility')}")
allocs = ms.get("allocations", [])
print(f"Allocations ({len(allocs)} stocks):")
for a in sorted(allocs, key=lambda x: -(x.get("weight_pct") or 0))[:10]:
    code = a.get("code","?")
    name = a.get("name","")[:10]
    wt   = a.get("weight_pct", 0) or 0
    grand= a.get("grand", 0) or 0
    print(f"  {code:6} {name:12} {wt:.1f}%  grand={grand:.0f}")

# Check position_sizing
ps = json.loads((rd/"position_sizing.json").read_text(encoding="utf-8"))
print()
print("position_sizing date:", ps.get("date"))
positions = ps.get("positions", [])
print(f"Active positions: {len(positions)}")
for p in sorted(positions, key=lambda x: -(x.get("alloc_pct_norm") or 0))[:8]:
    code  = p.get("code","?")
    alloc = p.get("alloc_pct_norm", 0) or 0
    size  = p.get("position_size_ntd", 0) or 0
    signal= p.get("signal","?")
    print(f"  {code:6} {alloc:.1f}%  NTD={size:,.0f}  {signal}")
