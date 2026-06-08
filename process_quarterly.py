#!/usr/bin/env python3
"""
Process Q1 2026 income statements and balance sheet from TWSE OpenAPI.
Merges into full_market.json and saves quarterly_financials.json.
"""
import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime

TODAY      = datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode   = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v else None
    except: return None

print(f"[{datetime.now():%H:%M:%S}] Fetching Q1 2026 income statements...")
income = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap06_L_ci")
print(f"  ✅ {len(income)} companies | Quarter: {income[0].get('年度','?')}Q{income[0].get('季別','?')}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s before balance sheet fetch...")
time.sleep(132)

print(f"[{datetime.now():%H:%M:%S}] Fetching balance sheet...")
balance = []
for url in [
    "https://openapi.twse.com.tw/v1/opendata/t187ap06_L_bs",
    "https://openapi.twse.com.tw/v1/opendata/t187ap04_L",
    "https://openapi.twse.com.tw/v1/opendata/t187ap06_L_b",
]:
    try:
        balance = fetch(url)
        if balance:
            print(f"  ✅ {len(balance)} companies from {url.split('/')[-1]}")
            print(f"  Keys: {list(balance[0].keys())[:8]}")
            break
        else:
            print(f"  Empty: {url.split('/')[-1]}")
    except Exception as e:
        print(f"  ❌ {url.split('/')[-1]}: {e}")

# ── Build income map ────────────────────────────────────────────────────────
income_map = {}
for r in income:
    code = str(r.get("公司代號","")).strip()
    if not code: continue
    income_map[code] = {
        "code":         code,
        "name":         r.get("公司名稱",""),
        "year":         r.get("年度",""),
        "quarter":      r.get("季別",""),
        "revenue":      sf(r.get("營業收入")),
        "gross_profit": sf(r.get("營業毛利（毛損）淨額")),
        "op_income":    sf(r.get("營業利益（損失）")),
        "pretax":       sf(r.get("稅前淨利（淨損）")),
        "net_income":   sf(r.get("本期淨利（淨損）")),
        "eps":          sf(r.get("基本每股盈餘（元）")),
        # Derived ratios
        "gross_margin": None,
        "op_margin":    None,
        "net_margin":   None,
    }
    d = income_map[code]
    if d["revenue"] and d["revenue"] > 0:
        if d["gross_profit"] is not None:
            d["gross_margin"] = round(d["gross_profit"] / d["revenue"] * 100, 1)
        if d["op_income"] is not None:
            d["op_margin"]    = round(d["op_income"]    / d["revenue"] * 100, 1)
        if d["net_income"] is not None:
            d["net_margin"]   = round(d["net_income"]   / d["revenue"] * 100, 1)

# ── Build balance map ───────────────────────────────────────────────────────
balance_map = {}
for r in balance:
    code = str(r.get("公司代號","")).strip()
    if not code: continue
    ta = sf(r.get("資產總額") or r.get("TotalAssets"))
    tl = sf(r.get("負債總額") or r.get("TotalLiabilities"))
    eq = sf(r.get("權益總額") or r.get("TotalEquity"))
    dr = round(tl/ta*100, 1) if ta and tl and ta > 0 else None
    balance_map[code] = {"total_assets": ta, "total_liab": tl, "equity": eq, "debt_ratio": dr}

# ── Merge into full_market ──────────────────────────────────────────────────
fullmkt_src = REPORT_DIR / "full_market.json"
fullmkt = json.loads(fullmkt_src.read_text(encoding="utf-8"))

enriched = 0
for c in fullmkt["companies"]:
    code = c["code"]
    inc  = income_map.get(code, {})
    bal  = balance_map.get(code, {})
    if inc:
        c["eps_q1"]       = inc.get("eps")
        c["net_income_q1"]= inc.get("net_income")
        c["gross_margin"] = inc.get("gross_margin")
        c["op_margin"]    = inc.get("op_margin")
        c["net_margin"]   = inc.get("net_margin")
        c["revenue_q1"]   = inc.get("revenue")
        enriched += 1
    if bal:
        c["debt_ratio"] = bal.get("debt_ratio")
        c["total_assets"] = bal.get("total_assets")

    # Update quick score with EPS
    score = c.get("quick_score", 0)
    if (c.get("eps_q1") or 0) > 2:  score += 2
    elif (c.get("eps_q1") or 0) > 0: score += 1
    if (c.get("gross_margin") or 0) > 30: score += 1
    c["quick_score"] = score

fullmkt["generated"]     = datetime.now().strftime("%Y-%m-%d %H:%M")
fullmkt["q1_income_count"] = len(income_map)
fullmkt["q1_balance_count"]= len(balance_map)
fullmkt["q1_data_period"]  = f"{income[0].get('年度','?')}Q{income[0].get('季別','?')}" if income else "?"

out_path = REPORT_DIR / "full_market.json"
out_path.write_text(json.dumps(fullmkt, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ full_market.json updated: {enriched} companies enriched with Q1 financials")

# Also save standalone quarterly file
qf_out = {
    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "period": f"{income[0].get('年度','?')}Q{income[0].get('季別','?')}" if income else "?",
    "income_count": len(income_map),
    "balance_count": len(balance_map),
    "companies": list(income_map.values()),
}
(REPORT_DIR / "quarterly_financials.json").write_text(
    json.dumps(qf_out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ quarterly_financials.json: {len(income_map)} companies")

# Print top 10 by EPS
top_eps = sorted([v for v in income_map.values() if v.get("eps")], key=lambda x: -(x["eps"] or 0))[:10]
print(f"\n  Top 10 EPS (Q1 2026):")
print(f"  {'代號':<6} {'名稱':<10} {'EPS':>7} {'毛利率':>8} {'淨利率':>8}")
print("  " + "-"*50)
for c in top_eps:
    print(f"  {c['code']:<6} {c['name']:<10} {c['eps']:>7.2f} {str(c['gross_margin'])+'%':>8} {str(c['net_margin'])+'%':>8}")

print(f"\n[{datetime.now():%H:%M:%S}] === Done ===")
