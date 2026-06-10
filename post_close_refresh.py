#!/usr/bin/env python3
"""
Post-close data refresh (Phase 1 of 2).
Handles: price momentum + BWIBBU + TAIEX + MA + institutional flows.
Designed to run within ~8 minutes (three 132s waits + fetch times).
Phase 2 (dna_refresh + build_dashboard) must be run separately.

Usage: python post_close_refresh.py
"""
import json, ssl, time, subprocess, sys, urllib.request, shutil
from pathlib import Path
from datetime import datetime

def fetch(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

def run(script, *args):
    cmd = [sys.executable, script] + list(args)
    r = subprocess.run(cmd, text=True)
    print(f"  {'OK' if r.returncode == 0 else 'FAILED'}: {script} {' '.join(args)}")
    return r.returncode == 0

START = datetime.now()
print(f"=== Post-close refresh: {START:%Y-%m-%d %H:%M:%S} ===")

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])
REPORT_DIR = Path("reports") / _dirs[-1].name
TODAY = datetime.now().strftime("%Y-%m-%d")

# Scaffold new report dir if needed (new calendar day)
NEW_DIR = Path("reports") / TODAY
if not NEW_DIR.exists() and NEW_DIR.name != REPORT_DIR.name:
    NEW_DIR.mkdir(parents=True, exist_ok=True)
    for f in REPORT_DIR.iterdir():
        if f.is_file(): shutil.copy2(f, NEW_DIR / f.name)
    stocks_src = REPORT_DIR / "stocks"
    if stocks_src.exists():
        shutil.copytree(str(stocks_src), str(NEW_DIR / "stocks"), dirs_exist_ok=True)
    REPORT_DIR = NEW_DIR
    print(f"  Scaffolded {TODAY}/ from prior dir")

mom_old  = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
PREV_DATE = mom_old.get("data_date", "")
ma_data  = json.loads((REPORT_DIR / "ma_refresh.json").read_text(encoding="utf-8"))
comp     = json.loads((REPORT_DIR / "composite_data.json").read_text(encoding="utf-8"))
exp_data = json.loads((REPORT_DIR / "expansion_stocks.json").read_text(encoding="utf-8"))
grand_old = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))

name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in exp_data}}
prior_map = {s["code"]: sf(s.get("price")) for s in comp}
ma_map    = {r["code"]: sf(r.get("ma30")) for r in ma_data.get("all_results", [])}
old_mom   = {m["code"]: m for m in mom_old.get("all_momentum", [])}
all_codes = set(name_map.keys())

# ── Step 0: Probe May revenue ─────────────────────────────────────────────────
print("\n[0] Probing May 2026 revenue...")
may_avail = False
try:
    rev_raw = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    print(f"  Latest period: {periods[-1] if periods else '?'} | May 2026: {'✅' if may_avail else '❌ Not yet'}")
except Exception as e:
    print(f"  Revenue probe failed: {e}")

# ── Step 1: STOCK_DAY_ALL price update ────────────────────────────────────────
print("\n[1] Fetching STOCK_DAY_ALL (no initial wait — caller ensures timing)...")
price_raw = []; data_date = PREV_DATE
try:
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    data_date = price_raw[0].get("Date","?") if price_raw else "?"
    print(f"  {len(price_raw)} rows | Date: {data_date}")
except Exception as e:
    print(f"  openapi failed: {e}")

# Fallback: RWD endpoint when OpenAPI is stale
if not price_raw or data_date <= PREV_DATE:
    try:
        from datetime import date as _date
        _today = _date.today().strftime("%Y%m%d")
        _rwd = fetch(f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=json&date={_today}")
        _rwd_date = _rwd.get("date","")  # e.g. "20260610"
        if _rwd_date and len(_rwd_date)==8:
            _roc = f"{int(_rwd_date[:4])-1911}{_rwd_date[4:]}"  # "1150610"
            _rows = _rwd.get("data",[])
            if _roc > PREV_DATE and _rows:
                price_raw = [
                    {"Date":_roc,"Code":row[0],"Name":row[1],
                     "TradeVolume":row[2].replace(",",""),"TradeValue":row[3].replace(",",""),
                     "OpeningPrice":row[4],"HighestPrice":row[5],"LowestPrice":row[6],
                     "ClosingPrice":row[7],"Change":row[8],"Transaction":row[9].replace(",","")}
                    for row in _rows if len(row)>=10
                ]
                data_date = _roc
                print(f"  RWD fallback: {len(price_raw)} rows | Date: {data_date}")
    except Exception as e2:
        print(f"  RWD fallback failed: {e2}")

if data_date > PREV_DATE:
    price_map = {r.get("Code","").strip(): r for r in price_raw if r.get("Code")}
    momentum = []
    for code in sorted(all_codes):
        r = price_map.get(code, {}); old_m = old_mom.get(code, {})
        close = sf(r.get("ClosingPrice")) or old_m.get("close")
        high  = sf(r.get("HighestPrice")); low = sf(r.get("LowestPrice"))
        volume = sf(r.get("TradeVolume"))
        prior_p = prior_map.get(code); ma30 = ma_map.get(code)
        pct_prior = round((close/prior_p-1)*100,1) if close and prior_p and prior_p>0 else old_m.get("pct_vs_prior")
        pct_ma    = round((close/ma30-1)*100,1)    if close and ma30 and ma30>0 else old_m.get("pct_vs_ma")
        intraday  = round((close-low)/(high-low)*100,1) if high and low and high>low else old_m.get("intraday_pct")
        sig = "NEUTRAL"
        if pct_prior is not None:
            if pct_prior>20 and (pct_ma or 0)>5: sig="STRONG_UP"
            elif pct_prior>10: sig="UP"
            elif pct_prior<-15 and (pct_ma or 0)<-5: sig="STRONG_DOWN"
            elif pct_prior<-8: sig="DOWN"
        momentum.append({"code":code,"name":name_map.get(code,code),"close":close,
                         "prior_price":prior_p,"pct_vs_prior":pct_prior,"ma30":ma30,
                         "pct_vs_ma":pct_ma,"intraday_pct":intraday,"high":high,"low":low,
                         "volume":volume,"signal":sig})
    valid = [m for m in momentum if m["pct_vs_prior"] is not None]
    sc = {k:sum(1 for m in valid if m["signal"]==k) for k in ["STRONG_UP","UP","NEUTRAL","DOWN","STRONG_DOWN"]}
    (REPORT_DIR/"price_momentum.json").write_text(json.dumps(
        {**mom_old,"date":TODAY,"data_date":data_date,
         "fetch_ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
         "may_available":may_avail,"total_tracked":len(momentum),
         "valid_comparison":len(valid),"signal_counts":sc,
         "top_gainers":sorted(valid,key=lambda x:-(x["pct_vs_prior"]or 0))[:10],
         "top_losers":sorted(valid,key=lambda x:(x["pct_vs_prior"]or 0))[:10],
         "above_ma":[m for m in sorted(valid,key=lambda x:-(x["pct_vs_ma"]or 0)) if (m["pct_vs_ma"]or 0)>5][:10],
         "below_ma":[m for m in sorted(valid,key=lambda x:(x["pct_vs_ma"]or 0)) if (m["pct_vs_ma"]or 0)<-5][:10],
         "all_momentum":momentum},
        ensure_ascii=False, indent=2), encoding="utf-8")
    # Quick mom_pts update in grand_unified
    mom_m2 = {m["code"]: m for m in momentum}
    grand_upd = []
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
        bs=r.get("bull_signs")or 0; g=r["grand"]
        if g>=70 and bs>=3: r["final"]="🚀 TRIPLE CONFIRMED"
        elif g>=65: r["final"]="✅ STRONG BUY"
        elif g>=55: r["final"]="📈 BUY"
        elif g>=40: r["final"]="👀 WATCH"
        elif g>=25: r["final"]="⬛ HOLD"
        else: r["final"]="❌ REDUCE"
    triple=[r for r in grand_upd if "TRIPLE" in r["final"]]
    (REPORT_DIR/"grand_unified.json").write_text(json.dumps(
        {**grand_old,"data_date":data_date,"fetch_ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
         "triple_confirmed":triple,"all_ranked":grand_upd},
        ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"  price_momentum + grand_unified → {data_date}")
    gainers = sorted(valid, key=lambda x: -(x["pct_vs_prior"] or 0))[:5]
    for m in gainers: print(f"    {m['code']} {m['name'][:8]}: {m['close']} ({(m['pct_vs_prior'] or 0):+.1f}%)")
    print(f"  Signals: {sc}")
else:
    print(f"  No new data ({data_date} <= {PREV_DATE})")

# ── Step 2: BWIBBU (no wait — caller ensures 132s from last TWSE call) ────────
print("\n[2] BWIBBU refresh (no wait — caller manages timing)...")
run("bwibbu_refresh.py", "--skip-wait")

# ── Step 3: TAIEX ──────────────────────────────────────────────────────────────
print("\n⏳ 132s wait before TAIEX..."); time.sleep(132)
print("[3] TAIEX OHLC...")
run("fetch_taiex.py", "--months=1", "--skip-wait")

# ── Step 4: MA ────────────────────────────────────────────────────────────────
print("\n⏳ 132s wait before MA..."); time.sleep(132)
print("[4] MA30 refresh...")
run("ma_refresh.py", "--skip-wait", "--skip-revenue")

# ── Step 5: Institutional flows ───────────────────────────────────────────────
print("\n⏳ 132s wait before instflows..."); time.sleep(132)
print("[5] Institutional flows...")
run("institutional_flows.py", "--skip-wait")

# ── Fix technical data ────────────────────────────────────────────────────────
print("\n[6] Fix technical_data.json...")
run("_fix_technical_data.py")

elapsed = round((datetime.now() - START).total_seconds(), 0)
print(f"\n=== Phase 1 complete in {int(elapsed)}s ===")
print(f"  data_date: {PREV_DATE} → {data_date}")
print(f"  May revenue available: {may_avail}")
print(f"\nNext: run  python dna_refresh.py  then  python build_dashboard.py")
