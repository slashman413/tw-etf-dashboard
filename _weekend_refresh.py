#!/usr/bin/env python3
"""
Weekend refresh: probe for new data, rebuild dashboard, push.
No writes if no new data. Always rebuilds dashboard from latest report dir.
"""
import json, ssl, time, subprocess, sys, urllib.request
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 132

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Weekend Data Probe ===")
print(f"  Report dir: {REPORT_DIR}")

prev_date = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8")).get("data_date","1150605")
print(f"  Prev price date: {prev_date}")

# ── STEP 1: STOCK_DAY_ALL ────────────────────────────────────────────────────
print(f"\nSTEP 1: Probe STOCK_DAY_ALL...")
try:
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    data_date = price_raw[0].get("Date","?") if price_raw else "?"
    new_price = data_date != prev_date
    print(f"  Rows: {len(price_raw)} | Date: {data_date} | {'🆕 NEW!' if new_price else '↩ Same'}")
except Exception as e:
    print(f"  Failed: {e}")
    price_raw = []; data_date = prev_date; new_price = False

print(f"\n⏳ Waiting {WAIT_SEC}s...", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 2: May revenue probe ─────────────────────────────────────────────────
print(f"\nSTEP 2: Probe May revenue (period 11505)...")
try:
    rev_raw  = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods  = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    print(f"  Latest period: {periods[-1]} | May 2026: {'✅ AVAILABLE!' if may_avail else '❌ Not yet'}")
except Exception as e:
    print(f"  Failed: {e}")
    may_avail = False

# ── If new prices: update price_momentum.json and grand_unified.json ──────────
if new_price and price_raw:
    print(f"\nUpdating price data for {data_date}...")
    mom_old   = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
    grand_old = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
    ma_data   = json.loads((REPORT_DIR / "ma_refresh.json").read_text(encoding="utf-8"))
    comp      = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
    exp_data  = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))

    name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp_data}}
    prior_map = {s["code"]: sf(s.get("price")) for s in comp}
    ma_map    = {r["code"]: sf(r.get("ma30")) for r in ma_data.get("all_results", [])}
    old_mom   = {m["code"]: m for m in mom_old.get("all_momentum", [])}
    all_codes = set(name_map.keys())
    price_map = {r.get("Code","").strip(): r for r in price_raw if r.get("Code")}

    momentum = []
    for code in sorted(all_codes):
        r=price_map.get(code,{}); old_m=old_mom.get(code,{})
        close =sf(r.get("ClosingPrice")) or old_m.get("close")
        high  =sf(r.get("HighestPrice")); low=sf(r.get("LowestPrice")); volume=sf(r.get("TradeVolume"))
        prior_p=prior_map.get(code); ma30=ma_map.get(code)
        pct_prior=round((close/prior_p-1)*100,1) if close and prior_p and prior_p>0 else old_m.get("pct_vs_prior")
        pct_ma   =round((close/ma30-1)*100,1)    if close and ma30 and ma30>0 else old_m.get("pct_vs_ma")
        intraday =round((close-low)/(high-low)*100,1) if high and low and high>low else old_m.get("intraday_pct")
        sig="NEUTRAL"
        if pct_prior is not None:
            if pct_prior>20 and (pct_ma or 0)>5: sig="STRONG_UP"
            elif pct_prior>10: sig="UP"
            elif pct_prior<-15 and (pct_ma or 0)<-5: sig="STRONG_DOWN"
            elif pct_prior<-8: sig="DOWN"
        momentum.append({"code":code,"name":name_map.get(code,code),"close":close,
                         "prior_price":prior_p,"pct_vs_prior":pct_prior,"ma30":ma30,
                         "pct_vs_ma":pct_ma,"intraday_pct":intraday,"high":high,"low":low,
                         "volume":volume,"signal":sig})

    valid=[ m for m in momentum if m["pct_vs_prior"] is not None]
    sc={k:sum(1 for m in valid if m["signal"]==k) for k in ["STRONG_UP","UP","NEUTRAL","DOWN","STRONG_DOWN"]}
    top_g=sorted(valid,key=lambda x:x["pct_vs_prior"] or 0,reverse=True)[:10]
    top_l=sorted(valid,key=lambda x:x["pct_vs_prior"] or 0)[:10]
    abv_ma=sorted([m for m in valid if (m["pct_vs_ma"] or 0)>5], key=lambda x:-(x["pct_vs_ma"] or 0))
    blw_ma=sorted([m for m in valid if (m["pct_vs_ma"] or 0)<-5],key=lambda x:(x["pct_vs_ma"] or 0))

    (REPORT_DIR/"price_momentum.json").write_text(json.dumps(
        {**mom_old,"date":datetime.now().strftime("%Y-%m-%d"),"data_date":data_date,
         "fetch_ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
         "may_available":may_avail,"total_tracked":len(momentum),
         "valid_comparison":len(valid),"signal_counts":sc,
         "top_gainers":top_g,"top_losers":top_l,
         "above_ma":abv_ma[:10],"below_ma":blw_ma[:10],"all_momentum":momentum},
        ensure_ascii=False,indent=2),encoding="utf-8")

    mom_m2={m["code"]:m for m in momentum}
    grand_upd=[]
    for r in grand_old.get("all_ranked",[]):
        code=r["code"]; m=mom_m2.get(code,{})
        pma=sf(m.get("pct_vs_ma")); ppr=sf(m.get("pct_vs_prior")); up=r.get("upside")
        mp=12.5
        if pma is not None: mp+=min(8,max(-8,pma*0.5))
        if ppr is not None: mp+=min(5,max(-5,ppr*0.3))
        if up  is not None and up>0: mp+=min(5,up/30)
        mp=max(0,min(25,mp))
        ng=round(r["grand"]-r.get("mom_pts",12.5)+mp,1)
        grand_upd.append({**r,"mom_pts":round(mp,1),"grand":ng})
    grand_upd.sort(key=lambda x:-x["grand"])
    for r in grand_upd:
        bs=r.get("bull_signs") or 0; g=r["grand"]
        if g>=70 and bs>=3: r["final"]="🚀 TRIPLE CONFIRMED"
        elif g>=65: r["final"]="✅ STRONG BUY"
        elif g>=55: r["final"]="📈 BUY"
        elif g>=40: r["final"]="👀 WATCH"
        elif g>=25: r["final"]="⬛ HOLD"
        else:       r["final"]="❌ REDUCE"
    triple=[r for r in grand_upd if "TRIPLE" in r["final"]]
    (REPORT_DIR/"grand_unified.json").write_text(json.dumps(
        {**grand_old,"data_date":data_date,"fetch_ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
         "triple_confirmed":triple,
         "strong_buy":[r for r in grand_upd if r["final"]=="✅ STRONG BUY"],
         "buy":[r for r in grand_upd if r["final"]=="📈 BUY"],
         "all_ranked":grand_upd},
        ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"  ✅ Updated price_momentum + grand_unified to {data_date}")

# ── Rebuild + push only if something changed ──────────────────────────────────
if not new_price and not may_avail:
    print(f"\n[{datetime.now():%H:%M:%S}] No new data — skipping rebuild/push")
    print(f"Done | new_price=False | may_avail=False | next check in 30 min")
    sys.exit(0)

print(f"\n[{datetime.now():%H:%M:%S}] Rebuilding dashboard.html...")
result = subprocess.run(
    [sys.executable, "build_dashboard.py"],
    capture_output=True, text=True, cwd=str(Path(__file__).parent)
)
if result.returncode != 0:
    print(f"  ❌ build_dashboard.py failed:\n{result.stderr[-1000:]}")
    sys.exit(1)
dashboard = Path(__file__).parent / "dashboard.html"
print(f"  ✅ dashboard.html rebuilt ({dashboard.stat().st_size // 1024} KB)")

# ── Push to GitHub Pages ──────────────────────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Pushing to GitHub Pages...")
result = subprocess.run(
    [sys.executable, "_github_push.py"],
    capture_output=True, text=True, cwd=str(Path(__file__).parent)
)
print(result.stdout.strip())
if result.returncode != 0:
    print(f"  ❌ Push failed:\n{result.stderr[-500:]}")
else:
    print("  ✅ Dashboard pushed!")

print(f"\n[{datetime.now():%H:%M:%S}] Done | new_price={new_price} | may_avail={may_avail}")
