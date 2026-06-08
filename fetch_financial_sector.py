#!/usr/bin/env python3
"""
Fetch Q1 2026 income statements for financial-sector companies (金融業)
from t187ap06_F_ci, merge into full_market.json and quarterly_financials.json.
Also checks 0056/00878 component coverage.
"""
import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 132

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v not in (None,"","—") else None
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Financial Sector Q1 2026 Crawl ===")
print(f"  Report dir: {REPORT_DIR}")

# ── Step 1: Fetch financial-sector income statements ────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching t187ap06_F_ci (金融業損益表)...")
fin_income = []
try:
    fin_income = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap06_F_ci")
    if fin_income:
        print(f"  ✅ {len(fin_income)} financial companies")
        print(f"  Sample keys: {list(fin_income[0].keys())[:8]}")
        yr = fin_income[0].get("年度","?"); qt = fin_income[0].get("季別","?")
        print(f"  Period: {yr}Q{qt}")
    else:
        print("  ⚠️  Empty response")
except Exception as e:
    print(f"  ❌ Error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting {WAIT_SEC}s before next call...")
time.sleep(WAIT_SEC)

# ── Step 2: Fetch insurance-sector income (壽險/產險) ───────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching t187ap06_I_ci (保險業損益表)...")
ins_income = []
try:
    ins_income = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap06_I_ci")
    if ins_income:
        print(f"  ✅ {len(ins_income)} insurance companies")
    else:
        print("  ⚠️  Empty — trying t187ap06_L_ci scope")
except Exception as e:
    print(f"  ❌ Error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting {WAIT_SEC}s before next call...")
time.sleep(WAIT_SEC)

# ── Step 3: Fetch 和泰車 (2207) via t187ap06_L_ci supplement check ─────────
# 2207 is in listed non-financial sector; check if it appeared in prior fetch
print(f"\n[{datetime.now():%H:%M:%S}] Fetching t187ap06_L_ci (re-fetch non-financial)...")
nonfin_income = []
try:
    nonfin_income = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap06_L_ci")
    if nonfin_income:
        print(f"  ✅ {len(nonfin_income)} non-financial companies")
        hotai = [r for r in nonfin_income if r.get("公司代號","").strip() == "2207"]
        print(f"  2207 和泰車 found: {bool(hotai)}")
        if hotai:
            print(f"  2207 data: eps={hotai[0].get('基本每股盈餘（元）','?')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ── Build income_map from all sources ───────────────────────────────────────
all_income = fin_income + ins_income + nonfin_income
income_map = {}
for r in all_income:
    code = str(r.get("公司代號","")).strip()
    if not code or code in income_map:
        continue
    rev  = sf(r.get("營業收入"))
    gp   = sf(r.get("營業毛利（毛損）淨額"))
    oi   = sf(r.get("營業利益（損失）"))
    ni   = sf(r.get("本期淨利（淨損）"))
    eps  = sf(r.get("基本每股盈餘（元）"))
    income_map[code] = {
        "code": code,
        "name": r.get("公司名稱",""),
        "year": r.get("年度",""),
        "quarter": r.get("季別",""),
        "revenue":      rev,
        "gross_profit": gp,
        "op_income":    oi,
        "net_income":   ni,
        "eps":          eps,
        "gross_margin": round(gp/rev*100,1) if rev and gp is not None and rev>0 else None,
        "op_margin":    round(oi/rev*100,1) if rev and oi is not None and rev>0 else None,
        "net_margin":   round(ni/rev*100,1) if rev and ni is not None and rev>0 else None,
    }

print(f"\n  Total income records: {len(income_map)}")
print(f"  From financial: {len(fin_income)}  insurance: {len(ins_income)}  non-fin: {len(nonfin_income)}")

# ── Check 0050 component coverage ───────────────────────────────────────────
etfc = json.loads((REPORT_DIR / "etf_concentration.json").read_text(encoding="utf-8"))
w0050 = etfc.get("weights_0050", {})
still_missing = [c for c in w0050 if c not in income_map]
now_covered   = [c for c in w0050 if c in income_map]
print(f"\n  0050 coverage: {len(now_covered)}/{len(w0050)} (was 36/49)")
if still_missing:
    grand = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
    gmap = {r["code"]:r.get("name","?") for r in grand.get("all_ranked",[])}
    print(f"  Still missing: {[(c, gmap.get(c,'?')) for c in still_missing]}")

# ── Merge into quarterly_financials.json ────────────────────────────────────
qf_path = REPORT_DIR / "quarterly_financials.json"
qf = json.loads(qf_path.read_text(encoding="utf-8"))
existing = {c["code"]: c for c in qf.get("companies", [])}

added = 0
for code, d in income_map.items():
    if code not in existing:
        existing[code] = d
        added += 1
    else:
        # Update if new data has eps
        if d.get("eps") is not None and existing[code].get("eps") is None:
            existing[code].update(d)
            added += 1

qf["companies"] = list(existing.values())
qf["total_companies"] = len(existing)
qf["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
qf["income_sources"] = f"L_ci:{len(nonfin_income)} F_ci:{len(fin_income)} I_ci:{len(ins_income)}"
qf_path.write_text(json.dumps(qf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ quarterly_financials.json: {len(existing)} companies (+{added} new)")

# ── Merge into full_market.json ──────────────────────────────────────────────
fm_path = REPORT_DIR / "full_market.json"
fm = json.loads(fm_path.read_text(encoding="utf-8"))
enriched = 0
for c in fm.get("companies", []):
    code = c["code"]
    d = income_map.get(code)
    if d and c.get("eps_q1") is None:
        c["eps_q1"]       = d.get("eps")
        c["gross_margin"] = d.get("gross_margin")
        c["op_margin"]    = d.get("op_margin")
        c["net_margin"]   = d.get("net_margin")
        c["revenue_q1"]   = d.get("revenue")
        # boost quick_score
        if (c.get("eps_q1") or 0) > 2:  c["quick_score"] = (c.get("quick_score") or 0) + 2
        elif (c.get("eps_q1") or 0) > 0: c["quick_score"] = (c.get("quick_score") or 0) + 1
        enriched += 1

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
fm_path.write_text(json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ full_market.json: {enriched} additional companies enriched")

# ── Print 0050 financial stocks Q1 summary ───────────────────────────────────
print(f"\n  {'代號':<6} {'名稱':<10} {'EPS':>7} {'毛利率':>8} {'淨利率':>8} {'Q':>4}")
print("  " + "─"*50)
fin_codes = ["2882","2881","2886","2891","2884","5880","2892","2887","2883","2801","2890","5876","2207"]
for code in fin_codes:
    d = income_map.get(code, {})
    eps = d.get("eps"); gm = d.get("gross_margin"); nm = d.get("net_margin")
    qp  = f"{d.get('year','?')}Q{d.get('quarter','?')}" if d else "—"
    print(f"  {code:<6} {d.get('name','?'):<10} {str(eps or '—'):>7} {str((str(gm)+'%') if gm is not None else '—'):>8} {str((str(nm)+'%') if nm is not None else '—'):>8} {qp:>6}")

print(f"\n[{datetime.now():%H:%M:%S}] === Done ===")
