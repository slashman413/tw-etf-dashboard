#!/usr/bin/env python3
"""
Crawl MOPS quarterly financial data for all listed companies.
Uses TWSE OpenAPI financialStatements endpoints (batch fetch).
Rate limit: ≥130s between each endpoint call.
"""
import json, ssl, time, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

TODAY      = datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode   = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === MOPS Quarterly Financial Crawl ===")

# ── Load existing company list ──────────────────────────────────────────────
fullmkt_path = REPORT_DIR / "full_market.json"
if not fullmkt_path.exists():
    print("ERROR: full_market.json not found. Run full_market_crawl.py first.")
    exit(1)

fullmkt = json.loads(fullmkt_path.read_text(encoding="utf-8"))
companies = fullmkt.get("companies", [])
tse_codes = [c["code"] for c in companies if c.get("market") == "TSE" and c["code"].isdigit()]
print(f"  TSE companies to process: {len(tse_codes)}")

# ── Step 1: Comprehensive Income (損益表) — Q1 2025 (ROC 114Q1) ────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching comprehensive income Q1 2025 (114Q1)...")
income_map = {}
try:
    # TWSE OpenAPI: comprehensive income statements
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap06_L_ci"
    data = fetch_json(url)
    print(f"  Raw records: {len(data)}")
    if data:
        print(f"  Sample keys: {list(data[0].keys())[:10]}")
        for r in data:
            code = str(r.get("公司代號","") or r.get("Code","")).strip()
            if code:
                income_map[code] = r
    print(f"  Parsed: {len(income_map)} companies")
except Exception as e:
    print(f"  Error: {e}")
    # Try alternative endpoint
    try:
        url2 = "https://openapi.twse.com.tw/v1/financialStatements/comprehensiveIncome"
        data2 = fetch_json(url2)
        print(f"  Alt endpoint records: {len(data2)}")
        if data2:
            print(f"  Sample keys: {list(data2[0].keys())[:10]}")
    except Exception as e2:
        print(f"  Alt error: {e2}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s...")
time.sleep(132)

# ── Step 2: Balance Sheet (資產負債表) ─────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching balance sheet data...")
balance_map = {}
try:
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap06_L_bs"
    data = fetch_json(url)
    print(f"  Raw records: {len(data)}")
    if data:
        print(f"  Sample keys: {list(data[0].keys())[:10]}")
        for r in data:
            code = str(r.get("公司代號","") or r.get("Code","")).strip()
            if code:
                balance_map[code] = r
    print(f"  Parsed: {len(balance_map)} companies")
except Exception as e:
    print(f"  Error: {e}")
    try:
        url2 = "https://openapi.twse.com.tw/v1/financialStatements/balanceSheet"
        data2 = fetch_json(url2)
        print(f"  Alt endpoint records: {len(data2)}")
        if data2:
            print(f"  Sample keys: {list(data2[0].keys())[:10]}")
    except Exception as e2:
        print(f"  Alt error: {e2}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s...")
time.sleep(132)

# ── Step 3: EPS / Earnings per share ───────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching EPS data...")
eps_map = {}
try:
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap06_L_eps"
    data = fetch_json(url)
    print(f"  Raw records: {len(data)}")
    if data:
        print(f"  Sample keys: {list(data[0].keys())[:10]}")
        print(f"  Sample: {data[0]}")
        for r in data:
            code = str(r.get("公司代號","") or r.get("Code","")).strip()
            if code:
                eps_map[code] = r
    print(f"  Parsed: {len(eps_map)} companies")
except Exception as e:
    print(f"  Error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s...")
time.sleep(132)

# ── Step 4: Operating revenue / profit ─────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching operating revenue/profit...")
oper_map = {}
try:
    url = "https://openapi.twse.com.tw/v1/opendata/t187ap06_L"
    data = fetch_json(url)
    print(f"  Raw records: {len(data)}")
    if data:
        print(f"  Sample keys: {list(data[0].keys())[:12]}")
        print(f"  Sample: {dict(list(data[0].items())[:6])}")
        for r in data:
            code = str(r.get("公司代號","") or r.get("Code","")).strip()
            if code:
                oper_map[code] = r
    print(f"  Parsed: {len(oper_map)} companies")
except Exception as e:
    print(f"  Error: {e}")

# ── Merge all financial data ────────────────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Merging financial data...")

all_codes = set(income_map) | set(balance_map) | set(eps_map) | set(oper_map)
print(f"  Companies with any financial data: {len(all_codes)}")

financials = {}
for code in all_codes:
    inc = income_map.get(code, {})
    bal = balance_map.get(code, {})
    eps = eps_map.get(code, {})
    opr = oper_map.get(code, {})

    # Try to extract key metrics from whatever data we got
    entry = {"code": code}

    # EPS
    for k in eps:
        v = sf(eps[k])
        if v is not None and "eps" in k.lower():
            entry["eps_q1"] = v; break
    if not entry.get("eps_q1"):
        entry["eps_q1"] = sf(eps.get("基本每股盈餘") or eps.get("每股盈餘") or eps.get("EPS"))

    # Revenue / operating income
    entry["rev"]      = sf(opr.get("營業收入") or opr.get("收入"))
    entry["op_income"]= sf(opr.get("營業利益") or opr.get("OperatingIncome"))
    entry["net_income"]= sf(opr.get("本期淨利") or opr.get("NetIncome") or inc.get("本期淨利"))

    # Balance sheet
    entry["total_assets"]  = sf(bal.get("資產總額") or bal.get("TotalAssets"))
    entry["total_liab"]    = sf(bal.get("負債總額") or bal.get("TotalLiabilities"))
    entry["equity"]        = sf(bal.get("權益總額") or bal.get("TotalEquity"))

    # Debt ratio
    if entry.get("total_assets") and entry.get("total_liab") and entry["total_assets"] > 0:
        entry["debt_ratio"] = round(entry["total_liab"] / entry["total_assets"] * 100, 1)
    else:
        entry["debt_ratio"] = None

    financials[code] = entry

# Save
out = {
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_companies": len(financials),
    "income_count":    len(income_map),
    "balance_count":   len(balance_map),
    "eps_count":       len(eps_map),
    "oper_count":      len(oper_map),
    "data": financials,
}
out_path = REPORT_DIR / "quarterly_financials.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ Saved: {out_path}")
print(f"  Companies with financial data: {len(financials)}")
print(f"  Income stmt: {len(income_map)}  Balance: {len(balance_map)}  EPS: {len(eps_map)}  Oper: {len(oper_map)}")
print(f"\n[{datetime.now():%H:%M:%S}] === Done ===")
