#!/usr/bin/env python3
"""
Consolidated TPEX OTC quarterly data pipeline.
Fetches Q1 financial data for all OTC (上櫃) companies in one run.

Steps (3 API calls, 132s wait between each):
  1. t187ap14_O  — EPS, revenue, op/net income, sector (產業別)
  2. t187ap06_O_ci — full income statement (gross profit, margins)
  3. t187ap05_O   — monthly revenue (rev_now, rev_yoy, rev_mom, rev_cum)

Outputs:
  - full_market.json: updated with OTC eps_q1, margins, revenue, sector
  - quarterly_financials.json: OTC rows appended
  - otc_analysis.json: sector breakdown and top performers
"""
import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 132

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    s = str(v).replace(",","").strip()
    if not s or s in ("-","—","N/A"): return None
    try: return float(s)
    except: return None

def median(lst):
    if not lst: return None
    s = sorted(lst)
    m = len(s) // 2
    return (s[m-1]+s[m])/2 if len(s)%2==0 else s[m]

print(f"[{datetime.now():%H:%M:%S}] === TPEX OTC Quarterly Data Pipeline ===")
print(f"  Report dir: {REPORT_DIR}")

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}
print(f"  OTC companies to update: {len(otc_map)}")

# ── STEP 1: t187ap14_O — EPS + revenue + sector ───────────────────────────────
print(f"\nSTEP 1: Fetching t187ap14_O (EPS + sector)...")
data14 = fetch("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap14_O")
print(f"  Got {len(data14)} rows | Period: {data14[0].get('Date','?')}")

sec_map = {}
for row in data14:
    code = str(row.get("SecuritiesCompanyCode","")).strip()
    if not code or code not in otc_map: continue
    c = otc_map[code]
    eps  = sf(row.get("基本每股盈餘"))
    rev  = sf(row.get("營業收入"))
    op   = sf(row.get("營業利益"))
    net  = sf(row.get("稅後淨利"))
    sec  = row.get("產業別","").strip()
    if eps  is not None: c["eps_q1"]       = eps
    if rev  is not None: c["revenue_q1"]   = rev
    if op   is not None: c["op_income_q1"] = op
    if net  is not None: c["net_income_q1"]= net
    if sec:
        c["sector"] = sec
        sec_map[code] = sec
    # Compute margins from these fields
    if rev and rev > 0:
        if op  is not None: c["op_margin"]  = round(op  / rev * 100, 2)
        if net is not None: c["net_margin"] = round(net / rev * 100, 2)

s1_eps = sum(1 for c in otc_map.values() if c.get("eps_q1") is not None)
s1_sec = sum(1 for c in otc_map.values() if c.get("sector"))
print(f"  Updated: eps={s1_eps} sector={s1_sec}")

print(f"\n  ⏳ Waiting {WAIT_SEC}s...")
time.sleep(WAIT_SEC)

# ── STEP 2: t187ap06_O_ci — full income statement (gross margin) ──────────────
print(f"\nSTEP 2: Fetching t187ap06_O_ci (income statement / gross margin)...")
data06 = fetch("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap06_O_ci")
print(f"  Got {len(data06)} rows")

for row in data06:
    code = str(row.get("SecuritiesCompanyCode","")).strip()
    if not code or code not in otc_map: continue
    c = otc_map[code]
    rev       = sf(row.get("營業收入"))
    cogs      = sf(row.get("營業成本"))
    gross_net = sf(row.get("營業毛利（毛損）淨額"))
    op_inc    = sf(row.get("營業利益（損失）"))
    net_inc   = sf(row.get("本期淨利（淨損）"))
    eps       = sf(row.get("基本每股盈餘（元）"))

    if rev  is not None: c["revenue_q1"]   = rev
    if cogs is not None: c["cogs_q1"]      = cogs
    if op_inc is not None: c["op_income_q1"]= op_inc
    if net_inc is not None: c["net_income_q1"]= net_inc
    if eps  is not None: c["eps_q1"]       = eps
    if rev and rev > 0:
        if gross_net is not None: c["gross_margin"] = round(gross_net / rev * 100, 2)
        if op_inc    is not None: c["op_margin"]    = round(op_inc    / rev * 100, 2)
        if net_inc   is not None: c["net_margin"]   = round(net_inc   / rev * 100, 2)

s2_gm = sum(1 for c in otc_map.values() if c.get("gross_margin") is not None)
print(f"  Updated: gross_margin={s2_gm}")

print(f"\n  ⏳ Waiting {WAIT_SEC}s...")
time.sleep(WAIT_SEC)

# ── STEP 3: t187ap05_O — monthly revenue ──────────────────────────────────────
print(f"\nSTEP 3: Fetching t187ap05_O (monthly revenue)...")
data05 = fetch("https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O")
print(f"  Got {len(data05)} rows | Period: {data05[0].get('資料年月','?')}")

for row in data05:
    code = str(row.get("公司代號","")).strip()
    if not code or code not in otc_map: continue
    c = otc_map[code]
    rev_now = sf(row.get("營業收入-當月營收"))
    rev_yoy = sf(row.get("營業收入-去年同月增減(%)"))
    rev_mom = sf(row.get("營業收入-上月比較增減(%)"))
    rev_cum = sf(row.get("累計營業收入-當月累計營收"))
    if rev_now is not None: c["rev_now"] = rev_now
    if rev_yoy is not None: c["rev_yoy"] = round(rev_yoy, 2)
    if rev_mom is not None: c["rev_mom"] = round(rev_mom, 2)
    if rev_cum is not None: c["rev_cum"] = rev_cum

s3_yoy = sum(1 for c in otc_map.values() if c.get("rev_yoy") is not None)
print(f"  Updated: rev_yoy={s3_yoy}")

# ── Recompute quick_score from scratch ────────────────────────────────────────
print("\nRecomputing quick_scores...")
for c in companies:
    ry  = sf(c.get("rev_yoy"))
    pe  = sf(c.get("pe"))
    pb  = sf(c.get("pb"))
    dy  = sf(c.get("yield"))
    eps = sf(c.get("eps_q1"))
    gm  = sf(c.get("gross_margin"))
    om  = sf(c.get("op_margin"))
    score = 0
    if ry is not None:
        if ry > 10:   score += 2
        elif ry > 0:  score += 1
    if pe is not None and pe > 0:
        if pe < 15:   score += 2
        elif pe < 25: score += 1
    if pb is not None and 0 < pb < 1.5: score += 1
    if dy is not None:
        if dy > 4:    score += 2
        elif dy > 2:  score += 1
    if eps is not None:
        if eps > 2:   score += 2
        elif eps > 0: score += 1
    if gm is not None and gm > 50: score += 1
    if om is not None and om > 15: score += 1
    c["quick_score"] = score
companies.sort(key=lambda x: -(x.get("quick_score") or 0))

# ── Save full_market.json ─────────────────────────────────────────────────────
fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved full_market.json")

# ── Update quarterly_financials.json ─────────────────────────────────────────
qf = json.loads((REPORT_DIR / "quarterly_financials.json").read_text(encoding="utf-8"))
existing = {c["code"] for c in qf["companies"]}
added = 0
for code, c in otc_map.items():
    if code in existing:
        # Update existing OTC entry
        for qc in qf["companies"]:
            if qc["code"] == code:
                qc.update({
                    "market": "OTC", "sector": c.get("sector",""),
                    "revenue": c.get("revenue_q1"), "eps": c.get("eps_q1"),
                    "gross_margin": c.get("gross_margin"), "op_margin": c.get("op_margin"),
                    "net_margin": c.get("net_margin"),
                    "gross_profit": round(c["revenue_q1"]*c["gross_margin"]/100, 0)
                        if c.get("revenue_q1") and c.get("gross_margin") else None,
                    "op_income": c.get("op_income_q1"), "net_income": c.get("net_income_q1"),
                })
                break
        continue
    rev = c.get("revenue_q1"); gm = c.get("gross_margin")
    qf["companies"].append({
        "code": code, "name": c.get("name",""), "market": "OTC",
        "sector": c.get("sector",""), "year": "115", "quarter": "1",
        "revenue": rev, "gross_profit": round(rev*gm/100,0) if rev and gm else None,
        "op_income": c.get("op_income_q1"), "pretax": None,
        "net_income": c.get("net_income_q1"), "eps": c.get("eps_q1"),
        "gross_margin": gm, "op_margin": c.get("op_margin"), "net_margin": c.get("net_margin"),
    })
    added += 1

qf["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
qf["total_companies"] = len(qf["companies"])
(REPORT_DIR / "quarterly_financials.json").write_text(
    json.dumps(qf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved quarterly_financials.json ({len(qf['companies'])} companies)")

# ── Generate otc_analysis.json ────────────────────────────────────────────────
otc = [c for c in companies if c.get("market") == "OTC"]
eps_all = [c["eps_q1"] for c in otc if c.get("eps_q1") is not None]
yoy_all = [c["rev_yoy"] for c in otc if c.get("rev_yoy") is not None and abs(c["rev_yoy"]) < 500]
gm_all  = [c["gross_margin"] for c in otc if c.get("gross_margin") is not None]
om_all  = [c["op_margin"] for c in otc if c.get("op_margin") is not None]
pe_all  = [c["pe"] for c in otc if c.get("pe") and 0 < c["pe"] < 200]

# Sector analysis
sec_groups = defaultdict(list)
for c in otc:
    sec_groups[c.get("sector") or "其他"].append(c)

sectors_out = []
for sec, stocks in sec_groups.items():
    eps_s = [s["eps_q1"] for s in stocks if s.get("eps_q1") is not None]
    yoy_s = [s["rev_yoy"] for s in stocks if s.get("rev_yoy") is not None and abs(s["rev_yoy"]) < 500]
    gm_s  = [s["gross_margin"] for s in stocks if s.get("gross_margin") is not None]
    prof  = sum(1 for s in stocks if (s.get("eps_q1") or 0) > 0)
    top3  = sorted([s for s in stocks if s.get("eps_q1") is not None],
                   key=lambda x: -(x["eps_q1"] or 0))[:3]
    sectors_out.append({
        "sector": sec, "count": len(stocks), "profitable": prof,
        "median_eps": round(median(eps_s), 2) if eps_s else None,
        "median_rev_yoy": round(median(yoy_s), 1) if yoy_s else None,
        "median_gm": round(median(gm_s), 1) if gm_s else None,
        "top_eps": [{"code":s["code"],"name":s.get("name",""),"eps":s["eps_q1"]} for s in top3],
    })
sectors_out.sort(key=lambda x: -(x.get("median_eps") or -999))

top_eps = sorted([c for c in otc if c.get("eps_q1") is not None], key=lambda x:-(x["eps_q1"] or 0))[:20]
top_gm  = sorted([c for c in otc if c.get("gross_margin") is not None and (c.get("rev_now") or 0) > 50000],
                 key=lambda x:-(x["gross_margin"] or 0))[:20]
top_yoy = sorted([c for c in otc if c.get("rev_yoy") is not None and 0 < c["rev_yoy"] < 500],
                 key=lambda x:-(x["rev_yoy"] or 0))[:20]

def avg(lst): return sum(lst)/len(lst) if lst else None

analysis = {
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "period": "115Q1 (2026 Q1)", "data_source": "TPEX t187ap14_O + t187ap06_O_ci + t187ap05_O",
    "overall": {
        "total": len(otc), "profitable": sum(1 for c in otc if (c.get("eps_q1") or 0) > 0),
        "loss": sum(1 for c in otc if (c.get("eps_q1") or 0) < 0),
        "median_eps": round(median(eps_all), 2) if eps_all else None,
        "avg_eps": round(avg(eps_all), 2) if eps_all else None,
        "median_rev_yoy": round(median(yoy_all), 1) if yoy_all else None,
        "pct_rev_growth": round(sum(1 for y in yoy_all if y > 0)/len(yoy_all)*100, 1) if yoy_all else None,
        "median_gross_margin": round(median(gm_all), 1) if gm_all else None,
        "median_op_margin": round(median(om_all), 1) if om_all else None,
        "median_pe": round(median(pe_all), 1) if pe_all else None,
    },
    "sectors": sectors_out,
    "top_eps": [{"code":c["code"],"name":c.get("name",""),"eps":c["eps_q1"],
                 "gross_margin":c.get("gross_margin"),"sector":c.get("sector")} for c in top_eps],
    "top_gross_margin": [{"code":c["code"],"name":c.get("name",""),"gross_margin":c["gross_margin"],
                          "eps":c.get("eps_q1"),"sector":c.get("sector")} for c in top_gm],
    "top_rev_yoy": [{"code":c["code"],"name":c.get("name",""),"rev_yoy":c["rev_yoy"],
                     "eps":c.get("eps_q1"),"sector":c.get("sector")} for c in top_yoy],
}
(REPORT_DIR / "otc_analysis.json").write_text(
    json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ Saved otc_analysis.json")

print(f"\n{'─'*60}")
ov = analysis["overall"]
print(f"  OTC Q1 2026 Summary: {ov['total']} companies")
print(f"  Profitable: {ov['profitable']} ({ov['profitable']/ov['total']*100:.1f}%)")
print(f"  Median EPS: {ov['median_eps']} | Avg EPS: {ov['avg_eps']}")
print(f"  Median Rev YoY: {ov['median_rev_yoy']:+.1f}% | Growth rate: {ov['pct_rev_growth']}%")
print(f"  Median Gross Margin: {ov['median_gross_margin']}%")
print(f"\n  Top sectors by median EPS:")
for s in sectors_out[:5]:
    print(f"    {s['sector']}: {s['count']}家 profit={s['profitable']} med_eps={s['median_eps']}")
print(f"[{datetime.now():%H:%M:%S}] Done")
