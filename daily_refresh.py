#!/usr/bin/env python3
"""
Iteration 38: Daily Data Refresh
1. Probe May 2026 revenue
2. Wait 130s
3. Fetch STOCK_DAY_ALL — update only if new date (June 6) available
4. If new date: update price_momentum.json + grand_unified.json
"""

import json, ssl, time, urllib.request, shutil
from pathlib import Path
from datetime import datetime

TODAY      = datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 130

# Scaffold new report dir from latest if this is a new day
_existing = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])
PREV_DIR   = _existing[-1] if _existing else None
if not REPORT_DIR.exists() and PREV_DIR:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    for f in PREV_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, REPORT_DIR / f.name)
    stocks_src = PREV_DIR / "stocks"
    if stocks_src.exists():
        shutil.copytree(str(stocks_src), str(REPORT_DIR / "stocks"), dirs_exist_ok=True)
    print(f"  Scaffolded {TODAY}/ from {PREV_DIR.name}/ ({len(list(REPORT_DIR.iterdir()))} files)")

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
PREV_DATE = mom_old.get("data_date", "1150605")

# ── STEP 1: Probe May revenue ─────────────────────────────────────────────────
print("STEP 1: Probe May 2026 revenue")
try:
    rev_raw   = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap05_L")
    periods   = sorted({r.get("資料年月","") for r in rev_raw if r.get("資料年月")})
    may_avail = "11505" in periods
    print(f"  Latest period: {periods[-1]} | May 2026: {'✅ AVAILABLE!' if may_avail else '❌ Not yet'}")
except Exception as e:
    print(f"  Revenue probe failed: {e}")
    may_avail = False

print(f"\n⏳ Waiting {WAIT_SEC}s before STOCK_DAY_ALL…", flush=True)
time.sleep(WAIT_SEC)

# ── STEP 2: STOCK_DAY_ALL ─────────────────────────────────────────────────────
print("\nSTEP 2: Fetch STOCK_DAY_ALL")
price_raw = []; data_date = PREV_DATE
try:
    price_raw = fetch("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    data_date = price_raw[0].get("Date","?") if price_raw else "?"
    print(f"  openapi: {len(price_raw)} rows | Date: {data_date}")
except Exception as e:
    print(f"  openapi failed: {e}")

# Fallback to rwd endpoint if openapi is stale
if data_date == PREV_DATE:
    print("  openapi stale — trying rwd endpoint…")
    try:
        rwd = fetch("https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=json")
        if rwd.get("stat") == "OK" and rwd.get("data"):
            fields = rwd.get("fields", [])
            fi = {f: i for i, f in enumerate(fields)}
            today_roc = f"115{datetime.now().strftime('%m%d')}"
            for row in rwd["data"]:
                code = row[fi.get("證券代號", 0)] if len(row) > 0 else ""
                price_raw.append({
                    "Code": code, "Date": today_roc,
                    "ClosingPrice": row[fi.get("收盤價", 7)] if len(row) > 7 else "",
                    "HighestPrice": row[fi.get("最高價", 5)] if len(row) > 5 else "",
                    "LowestPrice":  row[fi.get("最低價", 6)] if len(row) > 6 else "",
                    "TradeVolume":  row[fi.get("成交股數", 2)] if len(row) > 2 else "",
                })
            data_date = today_roc
            print(f"  rwd fallback: {len(price_raw)} rows | Date: {data_date}")
    except Exception as e:
        print(f"  rwd fallback failed: {e}")

if data_date <= PREV_DATE:
    print(f"\n  Data not newer ({data_date} <= {PREV_DATE}) — no price update needed")
else:
    print(f"\n  New date: {PREV_DATE} → {data_date} — updating momentum!")
    price_map = {r.get("Code","").strip(): r for r in price_raw if r.get("Code")}

    momentum = []
    for code in sorted(all_codes):
        r     = price_map.get(code, {})
        old_m = old_mom.get(code, {})
        close  = sf(r.get("ClosingPrice")) or old_m.get("close")
        high   = sf(r.get("HighestPrice"))
        low    = sf(r.get("LowestPrice"))
        volume = sf(r.get("TradeVolume"))
        prior_p= prior_map.get(code)
        ma30   = ma_map.get(code)
        pct_prior = round((close/prior_p-1)*100,1) if close and prior_p and prior_p>0 else old_m.get("pct_vs_prior")
        pct_ma    = round((close/ma30-1)*100,1)    if close and ma30   and ma30>0   else old_m.get("pct_vs_ma")
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

    valid  = [m for m in momentum if m["pct_vs_prior"] is not None]
    sc     = {k:sum(1 for m in valid if m["signal"]==k)
              for k in ["STRONG_UP","UP","NEUTRAL","DOWN","STRONG_DOWN"]}
    top_g  = sorted(valid, key=lambda x: x["pct_vs_prior"] or 0, reverse=True)[:10]
    top_l  = sorted(valid, key=lambda x: x["pct_vs_prior"] or 0)[:10]
    abv_ma = sorted([m for m in valid if (m["pct_vs_ma"] or 0)>5],  key=lambda x:-(x["pct_vs_ma"] or 0))
    blw_ma = sorted([m for m in valid if (m["pct_vs_ma"] or 0)<-5], key=lambda x: (x["pct_vs_ma"] or 0))

    (REPORT_DIR / "price_momentum.json").write_text(json.dumps(
        {**mom_old,"date":TODAY,"data_date":data_date,
         "fetch_ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
         "may_available":may_avail,"total_tracked":len(momentum),
         "valid_comparison":len(valid),"signal_counts":sc,
         "top_gainers":top_g,"top_losers":top_l,
         "above_ma":abv_ma[:10],"below_ma":blw_ma[:10],"all_momentum":momentum},
        ensure_ascii=False, indent=2), encoding="utf-8")

    mom_m2 = {m["code"]: m for m in momentum}
    grand_upd = []
    for r in grand_old.get("all_ranked",[]):
        code=r["code"]; m=mom_m2.get(code,{})
        pma=sf(m.get("pct_vs_ma")); ppr=sf(m.get("pct_vs_prior")); up=r.get("upside")
        mp=12.5
        if pma is not None: mp+=min(8, max(-8, pma*0.5))
        if ppr is not None: mp+=min(5, max(-5, ppr*0.3))
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

    print(f"  Top gainers on {data_date}:")
    for m in top_g[:5]:
        print(f"    {m['code']} {m['name'][:8]}: {m['close']} ({m['pct_vs_prior']:+.1f}%)")
    print(f"  Signals: {sc}")
    print(f"✓ price_momentum.json + grand_unified.json updated to {data_date}")

print(f"\nDone. may_available={may_avail} | data_date={data_date}")

import subprocess, sys

# Refresh BWIBBU PE/div data (TWSE API call — enforce 132s wait from STOCK_DAY_ALL call)
print(f"\n⏳ Waiting 132s before bwibbu_refresh (IP-ban prevention)…", flush=True)
time.sleep(132)
print("Running bwibbu_refresh.py to update PE/dividend data...")
subprocess.run([sys.executable, "bwibbu_refresh.py", "--skip-wait"], check=False)

# Refresh TAIEX OHLC — only current month (1 API call), merge with existing history
print(f"\n⏳ Waiting 132s before fetch_taiex (IP-ban prevention)…", flush=True)
time.sleep(132)
print("Running fetch_taiex.py to update taiex_ohlc.json...")
subprocess.run([sys.executable, "fetch_taiex.py", "--months=1", "--skip-wait"], check=False)

# Refresh 30d MA data (STOCK_DAY_AVG_ALL) — skip revenue probe (already done above)
print(f"\n⏳ Waiting 132s before ma_refresh (IP-ban prevention)…", flush=True)
time.sleep(132)
print("Running ma_refresh.py to update 30d MA data...")
subprocess.run([sys.executable, "ma_refresh.py", "--skip-wait", "--skip-revenue"], check=False)

# Refresh institutional flows (T86 三大法人) — uses DATA_DATE from price_momentum
print(f"\n⏳ Waiting 132s before institutional_flows (IP-ban prevention)…", flush=True)
time.sleep(132)
print("Running institutional_flows.py to update T86 data...")
subprocess.run([sys.executable, "institutional_flows.py", "--skip-wait"], check=False)

# Regenerate technical_data.json AFTER bwibbu, taiex, MA, and instflows are all fresh
print("\nRunning _fix_technical_data.py to sync technical_data.json...")
subprocess.run([sys.executable, "_fix_technical_data.py"], check=False)
