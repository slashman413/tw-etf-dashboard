import json; from pathlib import Path; from datetime import datetime
_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
D = _dirs[0] if _dirs else Path("reports") / datetime.now().strftime("%Y-%m-%d")
dna   = json.loads((D/"dna_signals.json").read_text(encoding="utf-8"))
grand = json.loads((D/"grand_unified.json").read_text(encoding="utf-8"))
dna_m = {s["code"]:s for s in dna.get("all_signals",[]) if s.get("code")}
upd = []
for r in grand.get("all_ranked",[]):
    code=r["code"]; dn=dna_m.get(code,{})
    bs=dn.get("bull_signs", r.get("bull_signs") or 0)
    cm=dn.get("core_met",   r.get("core_met")   or 0)
    new_tech=(bs/6*15)+(cm/3*10)
    delta=new_tech-r.get("tech_pts",0)
    ng=round(r["grand"]+delta,1)
    upd.append({**r,"bull_signs":bs,"core_met":cm,"tech_pts":round(new_tech,1),"grand":ng,
                "dna_verdict":dn.get("verdict",r.get("dna_verdict","—"))})
upd.sort(key=lambda x:-x["grand"])
for r in upd:
    bs=r.get("bull_signs") or 0; g=r["grand"]
    if g>=70 and bs>=3: r["final"]="🚀 TRIPLE CONFIRMED"
    elif g>=65: r["final"]="✅ STRONG BUY"
    elif g>=55: r["final"]="📈 BUY"
    elif g>=40: r["final"]="👀 WATCH"
    elif g>=25: r["final"]="⬛ HOLD"
    else:       r["final"]="❌ REDUCE"
triple=[r for r in upd if "TRIPLE" in r["final"]]
print("Triple:", len(triple), "|", [r["code"] for r in triple])
for r in upd[:5]: print(f"  {r['code']} {r['name'][:8]}: {r['grand']} | {r['final']}")
(D/"grand_unified.json").write_text(json.dumps({**grand,
    "fetch_ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
    "triple_confirmed":triple,
    "strong_buy":[r for r in upd if r["final"]=="✅ STRONG BUY"],
    "buy":[r for r in upd if r["final"]=="📈 BUY"],
    "all_ranked":upd},ensure_ascii=False,indent=2),encoding="utf-8")
print("grand_unified.json synced")
